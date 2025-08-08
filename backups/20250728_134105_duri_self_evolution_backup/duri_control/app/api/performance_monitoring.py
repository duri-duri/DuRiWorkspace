"""
DuRi Memory System - Performance Monitoring API
기본 성능 모니터링 API 엔드포인트
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.performance_monitoring_service import performance_monitoring_service
from ..services.config_service import get_db_session
from ..decorators.memory_logger import log_api_request

router = APIRouter(prefix="/metrics", tags=["performance_monitoring"])

@router.get("/basic", response_model=Dict[str, Any])
async def get_basic_metrics():
    """기본 성능 메트릭 조회"""
    try:
        metrics = performance_monitoring_service.get_comprehensive_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return {
            "success": True,
            "basic_metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"기본 메트릭 조회 실패: {str(e)}")

@router.get("/system", response_model=Dict[str, Any])
async def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        system_metrics = performance_monitoring_service.get_system_metrics()
        
        return {
            "success": True,
            "system_metrics": {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "memory_available_mb": system_metrics.memory_available_mb,
                "disk_percent": system_metrics.disk_percent,
                "disk_free_gb": system_metrics.disk_free_gb,
                "network_io": system_metrics.network_io,
                "timestamp": system_metrics.timestamp.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시스템 메트릭 조회 실패: {str(e)}")

@router.get("/application", response_model=Dict[str, Any])
async def get_application_metrics():
    """애플리케이션 메트릭 조회"""
    try:
        app_metrics = performance_monitoring_service.get_application_metrics()
        
        return {
            "success": True,
            "application_metrics": {
                "total_memories": app_metrics.total_memories,
                "avg_importance": app_metrics.avg_importance,
                "memory_compression_ratio": app_metrics.memory_compression_ratio,
                "analysis_queue_size": app_metrics.analysis_queue_size,
                "active_connections": app_metrics.active_connections,
                "response_time_ms": app_metrics.response_time_ms,
                "timestamp": app_metrics.timestamp.isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"애플리케이션 메트릭 조회 실패: {str(e)}")

@router.get("/health/resources", response_model=Dict[str, Any])
async def get_health_resources():
    """리소스 건강도 조회"""
    try:
        health_status = performance_monitoring_service.get_health_status()
        
        if "error" in health_status:
            raise HTTPException(status_code=500, detail=health_status["error"])
        
        return {
            "success": True,
            "health_resources": health_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"리소스 건강도 조회 실패: {str(e)}")

@router.get("/history", response_model=Dict[str, Any])
async def get_metrics_history(
    hours: int = Query(24, description="조회 시간 범위 (시간)")
):
    """메트릭 히스토리 조회"""
    try:
        history = performance_monitoring_service.get_metrics_history(hours=hours)
        
        return {
            "success": True,
            "metrics_history": {
                "history": history,
                "total_records": len(history),
                "time_range_hours": hours
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 히스토리 조회 실패: {str(e)}")

@router.get("/summary", response_model=Dict[str, Any])
async def get_performance_summary():
    """성능 요약 정보 조회"""
    try:
        summary = performance_monitoring_service.get_performance_summary()
        
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        return {
            "success": True,
            "performance_summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 요약 조회 실패: {str(e)}")

@router.get("/alerts", response_model=Dict[str, Any])
async def get_performance_alerts():
    """성능 알림 조회"""
    try:
        health_status = performance_monitoring_service.get_health_status()
        system_metrics = performance_monitoring_service.get_system_metrics()
        
        alerts = []
        
        # CPU 알림
        if system_metrics.cpu_percent > 80:
            alerts.append({
                "type": "critical",
                "metric": "cpu_usage",
                "value": system_metrics.cpu_percent,
                "threshold": 80,
                "message": "CPU 사용률이 높습니다"
            })
        elif system_metrics.cpu_percent > 60:
            alerts.append({
                "type": "warning",
                "metric": "cpu_usage",
                "value": system_metrics.cpu_percent,
                "threshold": 60,
                "message": "CPU 사용률이 증가하고 있습니다"
            })
        
        # 메모리 알림
        if system_metrics.memory_percent > 90:
            alerts.append({
                "type": "critical",
                "metric": "memory_usage",
                "value": system_metrics.memory_percent,
                "threshold": 90,
                "message": "메모리 사용률이 매우 높습니다"
            })
        elif system_metrics.memory_percent > 80:
            alerts.append({
                "type": "warning",
                "metric": "memory_usage",
                "value": system_metrics.memory_percent,
                "threshold": 80,
                "message": "메모리 사용률이 높습니다"
            })
        
        # 디스크 알림
        if system_metrics.disk_percent > 90:
            alerts.append({
                "type": "critical",
                "metric": "disk_usage",
                "value": system_metrics.disk_percent,
                "threshold": 90,
                "message": "디스크 사용률이 매우 높습니다"
            })
        elif system_metrics.disk_percent > 80:
            alerts.append({
                "type": "warning",
                "metric": "disk_usage",
                "value": system_metrics.disk_percent,
                "threshold": 80,
                "message": "디스크 사용률이 높습니다"
            })
        
        return {
            "success": True,
            "performance_alerts": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "critical_count": len([a for a in alerts if a["type"] == "critical"]),
                "warning_count": len([a for a in alerts if a["type"] == "warning"]),
                "timestamp": health_status.get("timestamp", "")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"성능 알림 조회 실패: {str(e)}")

@router.post("/collect", response_model=Dict[str, Any])
async def trigger_metrics_collection():
    """메트릭 수집 트리거"""
    try:
        metrics = performance_monitoring_service.get_comprehensive_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=500, detail=metrics["error"])
        
        return {
            "success": True,
            "collection_triggered": {
                "message": "메트릭 수집이 완료되었습니다",
                "timestamp": metrics["timestamp"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 수집 트리거 실패: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        # 기본 상태 정보
        status_info = {
            "monitoring_active": True,
            "collection_interval_seconds": performance_monitoring_service.collection_interval,
            "metrics_history_size": len(performance_monitoring_service.metrics_history),
            "last_collection": performance_monitoring_service.last_collection.isoformat(),
            "service_status": "running"
        }
        
        return {
            "success": True,
            "monitoring_status": status_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"모니터링 상태 조회 실패: {str(e)}") 