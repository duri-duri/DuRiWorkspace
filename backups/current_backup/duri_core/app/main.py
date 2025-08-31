#!/usr/bin/env python3
"""
🎯 DuRi Core 모듈 - FastAPI 앱
판단 및 강화학습 기능 담당
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import logging
from datetime import datetime

from app.schemas import BaseResponse, ErrorResponse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DuRi-Core")

# FastAPI 인스턴스 생성
app = FastAPI(
    title="DuRi Core API",
    description="DuRi Core 모듈 - 판단 및 강화학습 시스템",
    version="1.0.0"
)

# CORS 정책 허용 (개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🔹 판단 엔드포인트
# -------------------------------
@app.post("/judge", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def process_judgment(judgment_data: Dict[str, Any]):
    """
    판단 데이터 수신 및 처리
    """
    try:
        logger.info(f"📥 판단 입력: {judgment_data}")

        # TODO: 판단 로직 구현
        return BaseResponse(
            status="success",
            message="판단 처리 완료",
            data=None
        ).dict()
    except Exception as e:
        logger.exception("❌ 판단 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 강화학습 엔드포인트
# -------------------------------
@app.post("/learn", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def process_learning(learning_data: Dict[str, Any]):
    """
    강화학습 데이터 수신 및 처리
    """
    try:
        logger.info(f"📥 학습 입력: {learning_data}")

        # TODO: 학습 로직 구현
        return BaseResponse(
            status="success",
            message="학습 처리 완료",
            data=None
        ).dict()
    except Exception as e:
        logger.exception("❌ 학습 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 상태 확인 엔드포인트
# -------------------------------
@app.get("/status", response_model=BaseResponse)
async def core_status():
    """
    Core 모듈 상태 확인
    """
    return BaseResponse(
        status="ok",
        message="DuRi Core 모듈 정상 작동 중",
        data={
            "module": "core",
            "process": "running",
            "timestamp": datetime.now().isoformat()
        }
    ).dict()


# -------------------------------
# 🔹 실행
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
