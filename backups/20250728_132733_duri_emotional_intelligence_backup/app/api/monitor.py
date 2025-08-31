from fastapi import APIRouter, Request
from datetime import datetime
from typing import Dict, Any

from ..services.monitor_service import MonitorService
from ..models.monitor import ServicesResponse, SummaryResponse

router = APIRouter()

# 모니터링 서비스 인스턴스
monitor_service = MonitorService()

@router.get("/services", response_model=ServicesResponse)
async def get_services_status(request: Request):
    """모든 서비스 상태 조회"""
    services_info = monitor_service.get_services_status()
    
    return ServicesResponse(
        services=services_info,
        timestamp=datetime.now()
    )

@router.get("/services/summary", response_model=SummaryResponse)
async def get_system_summary(request: Request):
    """시스템 전체 요약 정보 조회"""
    summary = monitor_service.get_system_summary_status()
    
    return SummaryResponse(
        summary=summary,
        timestamp=datetime.now()
    )

@router.get("/health", response_model=Dict[str, Any])
async def monitor_health_check(request: Request):
    """모니터링 서비스 자체 헬스 체크"""
    return {
        "status": "healthy",
        "service": "duri-control-monitor",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    } 