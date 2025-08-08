from fastapi import APIRouter, Request
from datetime import datetime
from typing import Dict, Any

from ..services.resource_service import ResourceService
from ..models.monitor import ResourcesResponse, ContainersResponse

router = APIRouter()

# 리소스 서비스 인스턴스
resource_service = ResourceService()

@router.get("/resources", response_model=ResourcesResponse)
async def get_system_resources(request: Request):
    """시스템 전체 리소스 정보 조회"""
    resources = resource_service.get_system_resources()
    
    return ResourcesResponse(
        resources=resources,
        timestamp=datetime.now()
    )

@router.get("/containers", response_model=ContainersResponse)
async def get_container_resources(request: Request):
    """컨테이너별 리소스 정보 조회"""
    containers = resource_service.get_container_resources()
    
    return ContainersResponse(
        containers=containers,
        timestamp=datetime.now()
    )

@router.get("/resources/summary", response_model=Dict[str, Any])
async def get_resources_summary(request: Request):
    """리소스 요약 정보 조회"""
    summary = resource_service.get_resources_summary()
    
    return {
        "status": "success",
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health", response_model=Dict[str, Any])
async def resource_health_check(request: Request):
    """리소스 모니터링 서비스 헬스 체크"""
    return {
        "status": "healthy",
        "service": "duri-control-resource",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    } 