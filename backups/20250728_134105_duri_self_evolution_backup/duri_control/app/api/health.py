from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from ..services.service_manager import get_service_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", tags=["health"])
async def health_check():
    """기본 헬스 체크"""
    return {
        "status": "healthy",
        "service": "DuRi Control API",
        "version": "1.0.0"
    }

@router.get("/services", tags=["health"])
async def service_status():
    """서비스 초기화 상태 확인"""
    try:
        service_manager = get_service_manager()
        status = service_manager.get_initialization_status()
        
        return {
            "status": "success",
            "service_initialization": status,
            "all_services_ready": len(status["pending_services"]) == 0
        }
    except Exception as e:
        logger.error(f"서비스 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 상태 확인 실패: {str(e)}")

@router.post("/services/retry", tags=["health"])
async def retry_service_initialization():
    """서비스 초기화 재시도"""
    try:
        service_manager = get_service_manager()
        success = service_manager.initialize_all_services()
        
        if success:
            return {
                "status": "success",
                "message": "모든 서비스 초기화 완료",
                "details": service_manager.get_initialization_status()
            }
        else:
            return {
                "status": "error",
                "message": "서비스 초기화 실패",
                "details": service_manager.get_initialization_status()
            }
    except Exception as e:
        logger.error(f"서비스 초기화 재시도 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서비스 초기화 재시도 실패: {str(e)}") 