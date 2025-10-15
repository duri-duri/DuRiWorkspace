#!/usr/bin/env python3
"""
DuRi 대시보드 엔드포인트 - Day 73 업데이트
"""

from fastapi import APIRouter, Depends, Response
from typing import Dict, Any
from DuRiCore.health.slo_monitor import slo_monitor
from DuRiCore.deployment.deployment_integrity import deployment_integrity
from DuRiCore.health.periodic_verification import get_verification_stats
from DuRiCore.global_logging_manager import get_duri_logger, utc_now
from DuRiCore.health.security import require_bearer_token

# Day 73 새로운 컴포넌트들
from DuRiCore.health.moving_averages import get_moving_averages, get_metrics_stats
from DuRiCore.health.alert_dedupe import get_alert_stats
from DuRiCore.health.rate_limiter import get_rate_limit_stats
from DuRiCore.health.config import get_health_config

logger = get_duri_logger("dashboard_endpoint")
router = APIRouter(dependencies=[Depends(require_bearer_token)])

@router.get("/dashboard/canary_overview")
def canary_overview(response: Response = Response()) -> Dict[str, Any]:
    """카나리 전체 상태 개요 - Day 73 업데이트"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        from DuRiCore.health.canary_endpoint import canary_check
        canary_result = canary_check()
        
        # Day 73: 이동평균 메트릭 추가
        moving_averages = get_moving_averages()
        
        return {
            "timestamp": utc_now(),
            "overall_status": "healthy" if canary_result.canary_ok else "unhealthy",
            "canary_ok": canary_result.canary_ok,
            "recommendation": canary_result.recommendation,
            "rollback_required": canary_result.rollback_required,
            "checks": canary_result.checks,
            "metrics": canary_result.metrics,
            "thresholds": canary_result.thresholds,
            "failure_reasons": canary_result.failure_reasons,
            "moving_averages": moving_averages  # Day 73 추가
        }
        
    except Exception as e:
        logger.error(f"카나리 개요 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "overall_status": "error",
            "error": str(e)
        }

@router.get("/dashboard/integrity_details")
def integrity_details(response: Response = Response()) -> Dict[str, Any]:
    """무결성 상세 정보 - Day 73 업데이트"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        integrity_result = deployment_integrity.verify_integrity()
        verification_stats = get_verification_stats()
        
        return {
            "timestamp": utc_now(),
            "integrity_status": integrity_result.get("status", "unknown"),
            "integrity_verified": integrity_result.get("integrity_verified", False),
            "summary": integrity_result.get("summary", {}),
            "deployment_id": integrity_result.get("deployment_id"),
            "schema_version": integrity_result.get("schema_version", "unknown"),
            "modified_files": integrity_result.get("modified_files", []),
            "missing_files": integrity_result.get("missing_files", []),
            "ignore_info": integrity_result.get("ignore_info", {}),
            "verification_stats": verification_stats
        }
        
    except Exception as e:
        logger.error(f"무결성 상세 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "integrity_status": "error",
            "error": str(e)
        }

@router.get("/dashboard/health_summary")
def health_summary(response: Response = Response()) -> Dict[str, Any]:
    """헬스 상태 요약 - Day 73 업데이트"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # SLO 상태
        slo_status = slo_monitor.check_slo_compliance()
        metrics_summary = slo_monitor.get_metrics_summary()
        
        # 무결성 상태
        integrity_result = deployment_integrity.verify_integrity()
        
        # 카나리 상태
        from DuRiCore.health.canary_endpoint import canary_check
        canary_result = canary_check()
        
        # 검증 통계
        verification_stats = get_verification_stats()
        
        # Day 73: 새로운 메트릭들 추가
        moving_averages = get_moving_averages()
        metrics_stats = get_metrics_stats()
        alert_stats = get_alert_stats()
        rate_limit_stats = get_rate_limit_stats()
        config_stats = get_health_config().get_config()
        
        return {
            "timestamp": utc_now(),
            "overall_health": "healthy" if (
                slo_status.get("status") == "healthy" and 
                integrity_result.get("integrity_verified", False) and
                canary_result.canary_ok
            ) else "unhealthy",
            "slo_status": slo_status.get("status", "unknown"),
            "integrity_status": integrity_result.get("status", "unknown"),
            "canary_status": "healthy" if canary_result.canary_ok else "unhealthy",
            "metrics": {
                "cpu_usage": metrics_summary.get("current_values", {}).get("cpu_usage_percent", 0),
                "memory_usage": metrics_summary.get("current_values", {}).get("memory_usage_percent", 0),
                "disk_usage": metrics_summary.get("current_values", {}).get("disk_usage_percent", 0)
            },
            "verification_stats": verification_stats,
            "deployment_info": deployment_integrity.get_deployment_info(),
            "moving_averages": moving_averages,  # Day 73 추가
            "metrics_stats": metrics_stats,      # Day 73 추가
            "alert_stats": alert_stats,          # Day 73 추가
            "rate_limit_stats": rate_limit_stats, # Day 73 추가
            "config_stats": config_stats         # Day 73 추가
        }
        
    except Exception as e:
        logger.error(f"헬스 요약 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "overall_health": "error",
            "error": str(e)
        }

@router.get("/dashboard/system_stats")
def system_stats(response: Response = Response()) -> Dict[str, Any]:
    """시스템 통계 - Day 73 새로운 엔드포인트"""
    
    # 캐시 금지 헤더
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    try:
        # Day 73: 모든 새로운 컴포넌트 통계
        moving_averages = get_moving_averages()
        metrics_stats = get_metrics_stats()
        alert_stats = get_alert_stats()
        rate_limit_stats = get_rate_limit_stats()
        config_stats = get_health_config().get_config()
        
        return {
            "timestamp": utc_now(),
            "moving_averages": moving_averages,
            "metrics_stats": metrics_stats,
            "alert_stats": alert_stats,
            "rate_limit_stats": rate_limit_stats,
            "config_stats": config_stats
        }
        
    except Exception as e:
        logger.error(f"시스템 통계 조회 실패: {e}")
        return {
            "timestamp": utc_now(),
            "error": str(e)
        }
