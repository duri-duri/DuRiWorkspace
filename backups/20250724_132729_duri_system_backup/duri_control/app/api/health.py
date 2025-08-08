from fastapi import APIRouter, Request
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def health_check(request: Request):
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "duri-control",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/status", response_model=Dict[str, Any])
async def get_status(request: Request):
    """전체 시스템 상태 조회"""
    return {
        "status": "operational",
        "service": "duri-control",
        "timestamp": datetime.now().isoformat(),
        "system_status": "running",
        "version": "1.0.0"
    } 