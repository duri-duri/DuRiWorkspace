#!/usr/bin/env python3
"""
⚙️ DuRi Brain 프로세스 API 라우터

/process 엔드포인트를 관리합니다.
"""

from fastapi import APIRouter, Request
from schemas.responses import BaseResponse
from utils.error_handler import handle_internal_error
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=BaseResponse)
async def process_status(request: Request):
    try:
        return BaseResponse(
            status="active",
            message="Brain 프로세스가 실행 중입니다.",
            data={
                "module": "brain",
                "process": "running",
                "status": "active",
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now()
        )
    except Exception as exc:
        return handle_internal_error(request, exc) 