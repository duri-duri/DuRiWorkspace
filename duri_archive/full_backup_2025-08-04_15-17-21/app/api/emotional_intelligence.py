"""
Day 8: 감정 지능 API
DuRi의 고급 감정 이해 및 공감 능력 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime

from ..database.database import get_db_session
from ..services.emotional_intelligence_service import EmotionalIntelligenceService

router = APIRouter()

@router.get("/status")
async def get_emotional_intelligence_status():
    """감정 지능 시스템 상태 확인"""
    try:
        return {
            "success": True,
            "status": "operational",
            "service": "Emotional Intelligence System",
            "version": "1.0.0",
            "features": {
                "complex_emotion_analysis": True,
                "emotion_reason_balance": True,
                "empathy_generation": True,
                "emotional_stability": True,
                "contextual_emotion": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }

@router.post("/analyze-complex")
async def analyze_complex_emotion(
    emotion_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """복합 감정 분석"""
    try:
        service = EmotionalIntelligenceService(db)
        result = service.analyze_complex_emotion(emotion_data)
        return {
            "success": True,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion-reason-balance")
async def calculate_emotion_reason_balance(
    emotion_data: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """감정-이성 균형 계산"""
    try:
        service = EmotionalIntelligenceService(db)
        analysis = service.analyze_complex_emotion(emotion_data)
        balance = analysis.get('emotion_reason_balance', {})
        return {
            "success": True,
            "balance": balance,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/empathetic-response")
async def generate_empathetic_response(
    emotion_analysis: Dict[str, Any],
    db: Session = Depends(get_db_session)
):
    """공감적 응답 생성"""
    try:
        service = EmotionalIntelligenceService(db)
        result = service.generate_empathetic_response(emotion_analysis)
        return {
            "success": True,
            "empathetic_response": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_emotional_intelligence_stats(db: Session = Depends(get_db_session)):
    """감정 지능 통계 조회"""
    try:
        service = EmotionalIntelligenceService(db)
        stats = service.get_emotional_intelligence_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 