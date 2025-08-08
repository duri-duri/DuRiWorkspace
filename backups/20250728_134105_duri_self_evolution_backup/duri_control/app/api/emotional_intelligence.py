"""
Day 8: 감정 지능 API
복합 감정 분석, 감정-이성 균형, 공감 능력 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database.database import get_db_session
from ..services.emotional_intelligence_service import EmotionalIntelligenceService

router = APIRouter(prefix="/emotional-intelligence", tags=["Emotional Intelligence"])

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_complex_emotion(
    emotion_data: Dict[str, Any], 
    db: Session = Depends(get_db_session)
):
    """복합 감정 분석"""
    try:
        ei_service = EmotionalIntelligenceService(db)
        result = ei_service.analyze_complex_emotion(emotion_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "복합 감정 분석 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_emotional_intelligence_stats(db: Session = Depends(get_db_session)):
    """감정 지능 통계 조회"""
    try:
        ei_service = EmotionalIntelligenceService(db)
        stats = ei_service.get_emotional_intelligence_stats()
        
        return {
            "success": True,
            "message": "감정 지능 통계 조회 완료",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/empathetic-response", response_model=Dict[str, Any])
async def generate_empathetic_response(
    emotion_context: Dict[str, Any], 
    db: Session = Depends(get_db_session)
):
    """공감적 반응 생성"""
    try:
        ei_service = EmotionalIntelligenceService(db)
        
        # 감정 데이터 준비
        emotion_data = {
            "primary_emotion": emotion_context.get("primary_emotion", "neutral"),
            "secondary_emotions": emotion_context.get("secondary_emotions", []),
            "intensity": emotion_context.get("intensity", 0.5),
            "context": emotion_context.get("context", {})
        }
        
        result = ei_service.analyze_complex_emotion(emotion_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "공감적 반응 생성 완료",
            "data": {
                "empathetic_response": result.get("empathetic_response", {}),
                "emotion_analysis": result.get("complex_emotion", {}),
                "balance_analysis": result.get("emotion_reason_balance", {})
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/emotion-reason-balance", response_model=Dict[str, Any])
async def analyze_emotion_reason_balance(
    balance_data: Dict[str, Any], 
    db: Session = Depends(get_db_session)
):
    """감정-이성 균형 분석"""
    try:
        ei_service = EmotionalIntelligenceService(db)
        
        # 감정 데이터 준비
        emotion_data = {
            "primary_emotion": balance_data.get("primary_emotion", "neutral"),
            "secondary_emotions": balance_data.get("secondary_emotions", []),
            "intensity": balance_data.get("intensity", 0.5),
            "context": balance_data.get("context", {})
        }
        
        result = ei_service.analyze_complex_emotion(emotion_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "감정-이성 균형 분석 완료",
            "data": {
                "balance_analysis": result.get("emotion_reason_balance", {}),
                "recommendation": result.get("emotion_reason_balance", {}).get("recommendation", ""),
                "confidence": result.get("confidence", 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 