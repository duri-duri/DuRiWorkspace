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
from app.api.self_evolution import router as self_evolution_router
from app.api.emotional_intelligence import router as emotional_intelligence_router
from app.api.creative_thinking import router as creative_thinking_router
from app.api.social_intelligence import router as social_intelligence_router

app = FastAPI(
    title="DuRi Brain API",
    description="DuRi Brain - 고급 뇌 기능 시스템",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우터 연결
app.include_router(emotion_router, prefix="/emotion", tags=["emotion"])
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(process_router, prefix="/process", tags=["process"])
app.include_router(decision_input_router, prefix="/decision_input", tags=["decision"])

# 고급 뇌 기능 라우터 연결
app.include_router(self_evolution_router, prefix="/self-evolution", tags=["self_evolution"])
app.include_router(emotional_intelligence_router, prefix="/emotional-intelligence", tags=["emotional_intelligence"])
app.include_router(creative_thinking_router, prefix="/creative-thinking", tags=["creative_thinking"])
app.include_router(social_intelligence_router, prefix="/social-intelligence", tags=["social_intelligence"])

# Extension용 엔드포인트 (임시)
from fastapi import HTTPException
from typing import Dict, Any
from datetime import datetime

@app.post("/automated-learning/process")
async def process_automated_learning(conversation_data: Dict[str, Any]):
    """
    자동화 학습 데이터 수신 및 처리 (Cursor Extension용 - 임시)
    """
    try:
        print(f"📥 자동화 학습 입력: {conversation_data}")
        
        # TODO: 실제 학습 로직 구현
        # 현재는 기본 응답만 반환
        
        return {
            "status": "success",
            "message": "자동화 학습 처리 완료",
            "data": {
                "package_id": "auto_learn_001",
                "summary": "대화 내용 요약",
                "learning_value": 0.8
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ 자동화 학습 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/adaptive-learning/process")
async def process_adaptive_learning(adaptive_data: Dict[str, Any]):
    """
    적응적 학습 데이터 수신 및 처리 (Cursor Extension용 - 임시)
    """
    try:
        print(f"📥 적응적 학습 입력: {adaptive_data}")
        
        # TODO: 실제 학습 로직 구현
        # 현재는 기본 응답만 반환
        
        return {
            "status": "success",
            "message": "적응적 학습 처리 완료",
            "data": {
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
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ 적응적 학습 처리 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
