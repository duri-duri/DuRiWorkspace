#!/usr/bin/env python3
"""
❗ DuRi Brain 공통 에러 핸들러

이 파일은 API 예외 발생 시 ErrorResponse 스키마로 변환하는 공통 함수입니다.
"""

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from schemas.responses import ErrorResponse


def handle_internal_error(request: Request, exc: Exception):
    logging.error(f"[ERROR] {request.url}: {exc}")
    err = ErrorResponse(error="Internal Server Error", detail=str(exc), status_code=500)
    return JSONResponse(status_code=500, content=err.dict())
