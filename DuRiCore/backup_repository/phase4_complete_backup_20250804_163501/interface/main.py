#!/usr/bin/env python3
"""
DuRiCore - FastAPI 메인 애플리케이션
새로운 엔진들과 연동된 API 서버
"""

from datetime import datetime
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from DuRiCore.DuRiCore.interface.api import router as api_router

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="DuRiCore API",
    description="DuRiCore - 자율적이고 지속 가능한 진화 AI 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "DuRiCore API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "phase": "Phase 3 - Interface Separation",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/api/v1/health/",
    }


@app.get("/info")
async def get_system_info():
    """시스템 정보"""
    return {
        "system": "DuRiCore",
        "version": "1.0.0",
        "description": "자율적이고 지속 가능한 진화 AI 시스템",
        "architecture": "Hybrid Structure (기존 자산 + 새로운 AI 기능)",
        "completed_engines": [
            "감정 엔진 (EmotionEngine)",
            "자기 진화 엔진 (SelfEvolutionEngine)",
            "학습 엔진 (LearningEngine)",
            "윤리 판단 엔진 (EthicalReasoningEngine)",
        ],
        "api_endpoints": {
            "emotion": "/api/v1/emotion/",
            "learning": "/api/v1/learning/",
            "ethical": "/api/v1/ethical/",
            "evolution": "/api/v1/evolution/",
            "health": "/api/v1/health/",
        },
        "features": [
            "LLM 기반 감정 분석",
            "다양한 콘텐츠 타입 학습 처리",
            "윤리적 딜레마 분석",
            "자기 성능 분석 및 개선",
            "배치 처리 지원",
            "실시간 통계 및 모니터링",
        ],
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 DuRiCore API 서버가 시작되었습니다!")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🔍 시스템 정보: http://localhost:8000/info")
    print("💚 헬스체크: http://localhost:8000/api/v1/health/")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("👋 DuRiCore API 서버가 종료되었습니다.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
