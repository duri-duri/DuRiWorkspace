#!/usr/bin/env python3
"""
DuRi 카나리 배포 체크 엔드포인트 - Day 75 업데이트
"""

from fastapi import APIRouter, Depends, Response
from typing import Dict, Any
from DuRiCore.health.slo_monitor import slo_monitor
from DuRiCore.deployment.deployment_integrity import deployment_integrity
from DuRiCore.global_logging_manager import get_duri_logger, utc_now
from DuRiCore.health.schemas import CanaryResponse, CanaryStatusResponse, IntegritySummary, RunbookInfo
from DuRiCore.health.security import require_canary_token

# Day 73 새로운 컴포넌트들
from DuRiCore.health.readiness_tracker import get_readiness_fail_rate
from DuRiCore.health.config import get_slo_thresholds
from DuRiCore.health.alert_dedupe import should_send_alert, canary_failure_key, integrity_failure_key, record_failure
from DuRiCore.health.moving_averages import record_metrics, get_moving_averages

# Day 75 새로운 컴포넌트들
from DuRiCore.health.runbook_map import map_runbooks, generate_runbook_summary

logger = get_duri_logger("canary_endpoint")
router = APIRouter()

@router.get("/canary_check", response_model=CanaryResponse, response_model_exclude_none=True)
def canary_check(
    latency_p95_ms_threshold: int = None,
    error_rate_threshold: float = None,
    readiness_fail_threshold: float = None,
    token: bool = Depends(require_canary_token),
    response: Response = Response()
) -> CanaryResponse:
    """카나리 배포 체크 - Day 75 업데이트"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # SLO 임계치 가져오기 (ENV 우선, 쿼리 파라미터 override)
        default_thresholds = get_slo_thresholds()
        latency_threshold = latency_p95_ms_threshold or default_thresholds["latency_p95_ms_threshold"]
        error_threshold = error_rate_threshold or default_thresholds["error_rate_threshold"]
        readiness_threshold = readiness_fail_threshold or default_thresholds["readiness_fail_threshold"]
        
        # SLO 메트릭 가져오기
        slo_status = slo_monitor.check_slo_compliance()
        metrics_summary = slo_monitor.get_metrics_summary()
        
        # 실제 메트릭 값 추출
        current_metrics = slo_status.get("current_metrics", {})
        p95_latency = current_metrics.get("response_time_ms", 0)
        error_rate = slo_status.get("summary", {}).get("error_rate_percent", 0) / 100
        
        # Day 73: 실제 readiness fail rate 계산
        readiness_fail_rate = get_readiness_fail_rate()
        
        # 임계치 비교
        latency_ok = p95_latency <= latency_threshold
        error_rate_ok = error_rate <= error_threshold
        readiness_ok = readiness_fail_rate <= readiness_threshold
        
        # SLO 기반 카나리 상태
        canary_ok = latency_ok and error_rate_ok and readiness_ok
        
        # 배포 무결성 체크 (상세 정보 포함)
        integrity_check = deployment_integrity.verify_integrity()
        integrity_ok = integrity_check.get("integrity_verified", False)
        ignore_info = integrity_check.get("ignore_info", {})
        
        # 최종 판단
        overall_ok = canary_ok and integrity_ok
        
        # 권장사항 결정
        if not integrity_ok:
            recommendation = "rollback_integrity_failure"
        elif not canary_ok:
            recommendation = "rollback_slo_failure"
        else:
            recommendation = "proceed"
        
        # 상세 실패 이유 수집
        failure_reasons = []
        if not latency_ok:
            failure_reasons.append(f"p95 latency {p95_latency:.1f}ms > {latency_threshold}ms")
        if not error_rate_ok:
            failure_reasons.append(f"error rate {error_rate:.3f} > {error_threshold}")
        if not readiness_ok:
            failure_reasons.append(f"readiness fail rate {readiness_fail_rate:.3f} > {readiness_threshold}")
        if not integrity_ok:
            integrity_summary = integrity_check.get("summary", {})
            modified_count = integrity_summary.get("modified_files", 0)
            missing_count = integrity_summary.get("missing_files", 0)
            failure_reasons.append(f"integrity: {modified_count} modified, {missing_count} missing files")
            
            # ignore 스냅샷 불일치도 실패 사유에 포함
            if ignore_info.get("mismatch"):
                failure_reasons.append(
                    f"ignore snapshot mismatch (current={ignore_info.get('current_hash', 'unknown')}, "
                    f"stored={ignore_info.get('stored_hash', 'unknown')})"
                )
        
        # Day 73: 메트릭 기록 (이동평균용)
        record_metrics(p95_latency, error_rate, readiness_fail_rate)
        
        # Day 75: 런북 매핑
        runbooks = []
        if failure_reasons:
            runbook_summary = generate_runbook_summary(failure_reasons)
            runbooks = [RunbookInfo(**rb) for rb in runbook_summary["runbooks"]]
        
        # Day 73: 알람 디듀프 처리
        canary_alert_key = canary_failure_key(overall_ok, recommendation, failure_reasons)
        integrity_alert_key = integrity_failure_key(
            integrity_ok, 
            integrity_check.get("status", "unknown"),
            integrity_check.get("modified_files", []),
            integrity_check.get("missing_files", [])
        )
        
        # Day 74: 실패 기록 (상위 실패 원인 집계용)
        if failure_reasons:
            record_failure(failure_reasons, canary_alert_key)
        
        # 무결성 상세 정보
        integrity_details = IntegritySummary(
            status=integrity_check.get("status", "unknown"),
            summary=integrity_check.get("summary", {}),
            deployment_id=integrity_check.get("deployment_id"),
            modified_files=integrity_check.get("modified_files", []),
            missing_files=integrity_check.get("missing_files", [])
        )
        
        # Pydantic 응답 모델 생성
        response_data = CanaryResponse(
            timestamp=utc_now(),
            canary_ok=overall_ok,
            recommendation=recommendation,
            rollback_required=not overall_ok,
            failure_reasons=failure_reasons,
            metrics={
                "p95_latency_ms": p95_latency,
                "error_rate": error_rate,
                "readiness_fail_rate": readiness_fail_rate
            },
            thresholds={
                "latency_p95_ms": latency_threshold,
                "error_rate": error_threshold,
                "readiness_fail_rate": readiness_threshold
            },
            checks={
                "latency_ok": latency_ok,
                "error_rate_ok": error_rate_ok,
                "readiness_ok": readiness_ok,
                "integrity_ok": integrity_ok
            },
            slo_status=slo_status.get("status", "unknown"),
            integrity=integrity_details,
            deployment_info=deployment_integrity.get_deployment_info(),
            runbooks=runbooks  # Day 75 추가
        )
        
        # Day 75: 로깅 (런북 정보 포함)
        if overall_ok:
            logger.info(f"카나리 체크 통과: {recommendation}")
        else:
            # 카나리 실패 알람
            if should_send_alert("canary", canary_alert_key, {
                "recommendation": recommendation,
                "failure_reasons": failure_reasons,
                "runbooks": [rb.id for rb in runbooks]
            }):
                runbook_ids = [rb.id for rb in runbooks]
                action_hints = [rb.action_hint for rb in runbooks]
                logger.warning(f"[ALERT] 카나리 실패: {recommendation} - {'; '.join(failure_reasons)} | runbooks={runbook_ids} | actions={action_hints}")
            
            # 무결성 실패 알람
            if should_send_alert("integrity", integrity_alert_key, {
                "integrity_status": integrity_check.get("status", "unknown"),
                "modified_files": len(integrity_check.get("modified_files", [])),
                "missing_files": len(integrity_check.get("missing_files", []))
            }):
                logger.warning(f"[ALERT] 무결성 실패: {integrity_check.get('status', 'unknown')}")
            
            # 변경 파일 로그 노이즈 완화
            if integrity_details.modified_files:
                preview = integrity_details.modified_files[:20]
                more = len(integrity_details.modified_files) - len(preview)
                logger.warning(f"수정된 파일(최대 20개): {preview}" + (f" (+{more} more)" if more > 0 else ""))
            if integrity_details.missing_files:
                preview = integrity_details.missing_files[:20]
                more = len(integrity_details.missing_files) - len(preview)
                logger.warning(f"누락된 파일(최대 20개): {preview}" + (f" (+{more} more)" if more > 0 else ""))
        
        return response_data
        
    except Exception as e:
        logger.error(f"카나리 체크 실패: {e}")
        # 오류 시에도 Pydantic 모델 반환
        return CanaryResponse(
            timestamp=utc_now(),
            canary_ok=False,
            recommendation="rollback_check_failure",
            rollback_required=True,
            failure_reasons=[f"check failure: {str(e)}"],
            metrics={"p95_latency_ms": 0, "error_rate": 0, "readiness_fail_rate": 0},
            thresholds={"latency_p95_ms": latency_threshold, "error_rate": error_threshold, "readiness_fail_rate": readiness_threshold},
            checks={"latency_ok": False, "error_rate_ok": False, "readiness_ok": False, "integrity_ok": False},
            slo_status="error",
            integrity=IntegritySummary(status="error", summary={}, modified_files=[], missing_files=[]),
            deployment_info={},
            runbooks=[]  # Day 75 추가
        )

@router.get("/canary_status", response_model=CanaryStatusResponse, response_model_exclude_none=True)
def canary_status(
    token: bool = Depends(require_canary_token),
    response: Response = Response()
) -> CanaryStatusResponse:
    """카나리 상태 요약 - Bearer 토큰 보호 + 캐시 금지"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        canary_result = canary_check()
        deployment_info = deployment_integrity.get_deployment_info()
        
        return CanaryStatusResponse(
            timestamp=utc_now(),
            status="healthy" if canary_result.canary_ok else "unhealthy",
            deployment_id=deployment_info.get("deployment_id"),
            version=deployment_info.get("version"),
            git_sha=deployment_info.get("git_sha"),
            canary_ok=canary_result.canary_ok,
            recommendation=canary_result.recommendation,
            rollback_required=canary_result.rollback_required,
            failure_reasons=canary_result.failure_reasons,
            integrity_details=canary_result.integrity.dict()
        )
        
    except Exception as e:
        logger.error(f"카나리 상태 확인 실패: {e}")
        return CanaryStatusResponse(
            timestamp=utc_now(),
            status="error",
            canary_ok=False,
            recommendation="rollback_check_failure",
            rollback_required=True,
            failure_reasons=[f"status check failure: {str(e)}"]
        )
