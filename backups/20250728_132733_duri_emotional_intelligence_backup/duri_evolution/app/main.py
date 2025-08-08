#!/usr/bin/env python3
"""
🎯 DuRi Evolution 모듈 - FastAPI 앱
학습 결과 기록 및 진화 기능을 담당
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
logger = logging.getLogger("DuRi-Evolution")

# FastAPI 앱 초기화
app = FastAPI(
    title="DuRi Evolution API",
    description="DuRi Evolution 모듈 - 학습 결과 기록 및 진화 시스템",
    version="1.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🔹 학습 결과 기록
# -------------------------------
@app.post("/record", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def record_learning_result(result_data: Dict[str, Any]):
    """
    학습 결과 기록
    """
    try:
        logger.info(f"📥 학습 결과 수신: {result_data}")

        # TODO: DB 저장, 로그 기록, 성능 분석 등 구현

        return BaseResponse(
            status="success",
            message="학습 결과 기록 완료",
            data=None
        ).dict()
    except Exception as e:
        logger.exception("❌ 학습 결과 기록 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 진화 처리
# -------------------------------
@app.post("/evolve", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def process_evolution(evolution_data: Dict[str, Any]):
    """
    진화 처리
    """
    try:
        logger.info(f"📥 진화 데이터 수신: {evolution_data}")

        # TODO: 정책 업데이트, 모델 개선 등 구현

        return BaseResponse(
            status="success",
            message="진화 처리 완료",
            data=None
        ).dict()
    except Exception as e:
        logger.exception("❌ 진화 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 상태 확인
# -------------------------------
@app.get("/status", response_model=BaseResponse)
async def evolution_status():
    """
    Evolution 모듈 상태 확인
    """
    return BaseResponse(
        status="ok",
        message="DuRi Evolution 모듈 정상 작동 중",
        data={
            "module": "evolution",
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
        port=8082,
        reload=True,
        log_level="info"
    )
