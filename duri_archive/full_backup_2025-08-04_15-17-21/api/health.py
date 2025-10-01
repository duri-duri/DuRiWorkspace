#!/usr/bin/env python3
"""
🩺 DuRi Brain 헬스체크/정보 API 라우터

/health, /info 엔드포인트를 관리합니다.
"""

from datetime import datetime

from fastapi import APIRouter, Request
from schemas.responses import BaseResponse

from utils.error_handler import handle_internal_error

router = APIRouter()


@router.get("/", response_model=BaseResponse)
async def health_check(request: Request):
    try:
        return BaseResponse(
            status="healthy",
            message="DuRi Brain 모듈 정상 동작 중",
            data=None,
            timestamp=datetime.now(),
        )
    except Exception as exc:
        return handle_internal_error(request, exc)


@router.get("/info", response_model=BaseResponse)
async def info(request: Request):
    try:
        return BaseResponse(
            status="info",
            message="DuRi Brain API 정보",
            data={
                "name": "DuRi Brain API",
                "version": "1.0.0",
                "description": "DuRi Brain 모듈 - 감정 처리 및 학습 시스템",
                "module": "brain",
                "endpoints": ["/health", "/info", "/emotion", "/process"],
                "timestamp": datetime.now().isoformat(),
            },
            timestamp=datetime.now(),
        )
    except Exception as exc:
        return handle_internal_error(request, exc)
