#!/usr/bin/env python3
"""
🎯 DuRi Brain FastAPI 진입점

FastAPI 앱 초기화 및 라우터 연결만 담당합니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.emotion import router as emotion_router
from app.api.health import router as health_router
from app.api.process import router as process_router
from app.api.receive_decision_input import router as decision_input_router

app = FastAPI(
    title="DuRi Brain API",
    description="DuRi Brain 모듈 - 감정 처리 및 학습 시스템",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 연결
app.include_router(emotion_router, prefix="/emotion")
app.include_router(health_router, prefix="/health")
app.include_router(process_router, prefix="/process")
app.include_router(decision_input_router, prefix="/decision_input")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
