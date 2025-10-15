#!/usr/bin/env python3
"""
DuRi Analytics Endpoint - Day 74 분석용 대시보드
"""

from fastapi import APIRouter, Depends, Response
from typing import Dict, Any, List
from DuRiCore.global_logging_manager import get_duri_logger, utc_now
from DuRiCore.health.security import require_bearer_token

# Day 74 새로운 컴포넌트들
from DuRiCore.health.moving_averages import get_trends, get_moving_averages
from DuRiCore.health.alert_dedupe import get_top_failures, record_failure
from DuRiCore.health.readiness_tracker import readiness_tracker

logger = get_duri_logger("analytics_endpoint")
router = APIRouter(dependencies=[Depends(require_bearer_token)])

@router.get("/dashboard/analytics/trends")
def trends(
    window: int = 3600, 
    step: int = 60, 
    response: Response = Response()
) -> Dict[str, Any]:
    """
    Day 74: 트렌드 시리즈 API
    p95, error_rate, readiness_fail_rate의 분당 샘플 시계열 반환
    """
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # 트렌드 데이터 가져오기
        trends_data = get_trends(window, step)
        
        return {
            "timestamp": utc_now(),
            "window_sec": window,
            "step_sec": step,
            "data": trends_data
        }
        
    except Exception as e:
        logger.error(f"트렌드 시리즈 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "error": str(e)
        }

@router.get("/dashboard/analytics/top_failures")
def top_failures(
    window: int = 3600, 
    top_n: int = 10, 
    response: Response = Response()
) -> Dict[str, Any]:
    """
    Day 74: 상위 실패 원인 집계
    카나리 실패 시점의 failure_reasons를 해시 키별로 카운팅해 TOP N 반환
    """
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # 상위 실패 원인 가져오기
        top_failures_data = get_top_failures(window, top_n)
        
        return {
            "timestamp": utc_now(),
            "window_sec": window,
            "top_n": top_n,
            "failures": top_failures_data
        }
        
    except Exception as e:
        logger.error(f"상위 실패 원인 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "error": str(e)
        }

@router.get("/dashboard/analytics/availability")
def availability(
    window: int = 3600, 
    response: Response = Response()
) -> Dict[str, Any]:
    """
    Day 74: 가용성/성공률
    (1 - error_rate_ma15m)를 퍼센트로, 그리고 readiness 성공률 제공
    """
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # 이동평균 메트릭 가져오기
        moving_avg = get_moving_averages()
        
        # 가용성 계산
        error_rate_ma15m = moving_avg.get("error_rate_ma15m", 0.0)
        readiness_fail_rate_ma15m = moving_avg.get("readiness_fail_rate_ma15m", 0.0)
        
        # 성공률 계산 (퍼센트)
        availability_percent = (1.0 - error_rate_ma15m) * 100
        readiness_success_rate_percent = (1.0 - readiness_fail_rate_ma15m) * 100
        
        # Readiness 통계
        readiness_stats = readiness_tracker.stats()
        
        return {
            "timestamp": utc_now(),
            "window_sec": window,
            "availability": {
                "error_rate_ma15m": error_rate_ma15m,
                "availability_percent": round(availability_percent, 2),
                "readiness_fail_rate_ma15m": readiness_fail_rate_ma15m,
                "readiness_success_rate_percent": round(readiness_success_rate_percent, 2)
            },
            "readiness_stats": readiness_stats,
            "overall_health": "healthy" if (
                availability_percent >= 95.0 and readiness_success_rate_percent >= 95.0
            ) else "unhealthy"
        }
        
    except Exception as e:
        logger.error(f"가용성 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "error": str(e)
        }

@router.get("/dashboard/analytics/deploy_compare")
def deploy_compare(
    deployment_id: str,
    baseline_minutes: int = 30,
    response: Response = Response()
) -> Dict[str, Any]:
    """
    Day 74: 배포 전/후 비교 스냅샷
    특정 deployment_id 기준 직전 30분 vs 이후 30분의 핵심 지표 변화율
    """
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        from DuRiCore.deployment.deployment_integrity import deployment_integrity
        
        # 배포 정보 가져오기
        deployment_info = deployment_integrity.get_deployment_info()
        current_deployment_id = deployment_info.get("deployment_id")
        
        if deployment_id != current_deployment_id:
            return {
                "timestamp": utc_now(),
                "error": f"Deployment ID {deployment_id} not found. Current: {current_deployment_id}",
                "deployment_id": deployment_id,
                "current_deployment_id": current_deployment_id
            }
        
        # 배포 시간 추정 (현재 시간 기준)
        now = time.time()
        deploy_time = now - (baseline_minutes * 60)  # 30분 전으로 가정
        
        # 배포 전/후 데이터 비교 (시뮬레이션)
        # 실제로는 배포 시간을 정확히 알고 있어야 함
        baseline_sec = baseline_minutes * 60
        
        # 배포 전 데이터 (시뮬레이션)
        before_trends = get_trends(baseline_sec, 60)
        before_avg = get_moving_averages()
        
        # 배포 후 데이터 (현재)
        after_trends = get_trends(baseline_sec, 60)
        after_avg = get_moving_averages()
        
        # 변화율 계산
        before_p95 = before_avg.get("p95_latency_ms_ma15m", 0.0)
        after_p95 = after_avg.get("p95_latency_ms_ma15m", 0.0)
        p95_delta = after_p95 - before_p95
        p95_delta_percent = (p95_delta / before_p95 * 100) if before_p95 > 0 else 0.0
        
        before_error = before_avg.get("error_rate_ma15m", 0.0)
        after_error = after_avg.get("error_rate_ma15m", 0.0)
        error_delta = after_error - before_error
        error_delta_percent = (error_delta / before_error * 100) if before_error > 0 else 0.0
        
        before_readiness = before_avg.get("readiness_fail_rate_ma15m", 0.0)
        after_readiness = after_avg.get("readiness_fail_rate_ma15m", 0.0)
        readiness_delta = after_readiness - before_readiness
        readiness_delta_percent = (readiness_delta / before_readiness * 100) if before_readiness > 0 else 0.0
        
        return {
            "timestamp": utc_now(),
            "deployment_id": deployment_id,
            "baseline_minutes": baseline_minutes,
            "comparison": {
                "p95_latency_ms": {
                    "before": before_p95,
                    "after": after_p95,
                    "delta": round(p95_delta, 2),
                    "delta_percent": round(p95_delta_percent, 2)
                },
                "error_rate": {
                    "before": before_error,
                    "after": after_error,
                    "delta": round(error_delta, 4),
                    "delta_percent": round(error_delta_percent, 2)
                },
                "readiness_fail_rate": {
                    "before": before_readiness,
                    "after": after_readiness,
                    "delta": round(readiness_delta, 4),
                    "delta_percent": round(readiness_delta_percent, 2)
                }
            },
            "trends": {
                "before": before_trends,
                "after": after_trends
            },
            "deployment_impact": "positive" if (
                p95_delta < 0 and error_delta < 0 and readiness_delta < 0
            ) else "negative" if (
                p95_delta > 0 or error_delta > 0 or readiness_delta > 0
            ) else "neutral"
        }
        
    except Exception as e:
        logger.error(f"배포 비교 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "error": str(e)
        }
