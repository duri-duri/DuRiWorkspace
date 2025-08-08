#!/usr/bin/env python3
"""
간단한 테스트 서버 - Extension 통신 테스트용
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import uvicorn
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DuRi-Test-Server")

# FastAPI 인스턴스 생성
app = FastAPI(
    title="DuRi Test Server",
    description="Extension 통신 테스트용 서버",
    version="1.0.0"
)

# CORS 정책 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🔹 상태 확인 엔드포인트
# -------------------------------
@app.get("/")
async def root():
    return {"message": "DuRi Test Server is running!"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "duri-test-server"}

# -------------------------------
# 🔹 자동화 학습 엔드포인트 (Extension용)
# -------------------------------
@app.post("/automated-learning/process")
async def process_automated_learning(conversation_data: Dict[str, Any]):
    """
    자동화 학습 데이터 수신 및 처리 (Cursor Extension용)
    """
    try:
        logger.info(f"📥 자동화 학습 입력: {conversation_data}")

        return {
            "success": True,
            "package_id": "auto_learn_001",
            "summary": "대화 내용 요약",
            "learning_value": 0.8
        }
    except Exception as e:
        logger.exception("❌ 자동화 학습 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# 🔹 적응적 학습 엔드포인트 (Extension용)
# -------------------------------
@app.post("/adaptive-learning/process")
async def process_adaptive_learning(adaptive_data: Dict[str, Any]):
    """
    적응적 학습 데이터 수신 및 처리 (Cursor Extension용)
    """
    try:
        logger.info(f"📥 적응적 학습 입력: {adaptive_data}")

        return {
            "success": True,
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
            "reason": "상세한 설명이 학습에 효과적"
        }
    except Exception as e:
        logger.exception("❌ 적응적 학습 처리 오류")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081) 