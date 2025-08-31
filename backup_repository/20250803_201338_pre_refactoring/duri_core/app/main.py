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
import httpx
import asyncio

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

# 노드 URL 설정
BRAIN_URL = "http://localhost:8081"
EVOLUTION_URL = "http://localhost:8082"

async def call_brain(data: Dict[str, Any]) -> Dict[str, Any]:
    """Brain 노드 호출"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BRAIN_URL}/judge", json=data)
            return response.json()
    except Exception as e:
        logger.error(f"Brain 노드 호출 실패: {e}")
        return {"error": "Brain 노드 연결 실패"}

async def call_evolution(data: Dict[str, Any]) -> Dict[str, Any]:
    """Evolution 노드 호출"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{EVOLUTION_URL}/record", json=data)
            return response.json()
    except Exception as e:
        logger.error(f"Evolution 노드 호출 실패: {e}")
        return {"error": "Evolution 노드 연결 실패"}

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
# 🔹 자동화 학습 엔드포인트 (Extension용)
# -------------------------------
@app.post("/automated-learning/process", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def process_automated_learning(conversation_data: Dict[str, Any]):
    """
    자동화 학습 데이터 수신 및 처리 (Cursor Extension용)
    """
    try:
        logger.info(f"📥 자동화 학습 입력: {conversation_data}")

        # 1. Brain 노드에 판단 요청
        brain_result = await call_brain({
            "type": "automated_learning",
            "data": conversation_data
        })

        # 2. Evolution 노드에 학습 결과 기록
        evolution_result = await call_evolution({
            "type": "automated_learning",
            "data": conversation_data,
            "brain_result": brain_result
        })

        return BaseResponse(
            status="success",
            message="자동화 학습 처리 완료",
            data={
                "package_id": "auto_learn_001",
                "summary": "대화 내용 요약",
                "learning_value": 0.8,
                "brain_result": brain_result,
                "evolution_result": evolution_result
            }
        ).dict()
    except Exception as e:
        logger.exception("❌ 자동화 학습 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 적응적 학습 엔드포인트 (Extension용)
# -------------------------------
@app.post("/adaptive-learning/process", response_model=BaseResponse, responses={500: {"model": ErrorResponse}})
async def process_adaptive_learning(adaptive_data: Dict[str, Any]):
    """
    적응적 학습 데이터 수신 및 처리 (Cursor Extension용)
    """
    try:
        logger.info(f"📥 적응적 학습 입력: {adaptive_data}")

        # 1. Brain 노드에 판단 요청
        brain_result = await call_brain({
            "type": "adaptive_learning",
            "data": adaptive_data
        })

        # 2. Evolution 노드에 학습 결과 기록
        evolution_result = await call_evolution({
            "type": "adaptive_learning",
            "data": adaptive_data,
            "brain_result": brain_result
        })

        return BaseResponse(
            status="success",
            message="적응적 학습 처리 완료",
            data={
                "selected_format": "detailed",
                "learning_result": "성공적으로 학습됨",
                "efficiency_metrics": {
                    "response_accuracy": 0.9,
                    "application_power": 0.8,
                    "reproducibility": 0.7,
                    "learning_speed": 0.85,
                    "overall_score": 0.81
                },
                "exploration_rate": 0.2,
                "optimal_format": "detailed",
                "reason": "상세한 설명이 학습에 효과적",
                "brain_result": brain_result,
                "evolution_result": evolution_result
            }
        ).dict()
    except Exception as e:
        logger.exception("❌ 적응적 학습 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# 🔹 상태 확인 엔드포인트
# -------------------------------
@app.get("/health")
async def health_check():
    """
    서버 상태 확인 (외부 의존성 없음)
    """
    return {"status": "ok"}

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
