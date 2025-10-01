"""
Day 10: 사회적 지능 API
DuRi의 자연스러운 대화, 사회적 맥락 이해, 협업 능력 API
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.database import get_db_session
from ..services.social_intelligence_service import SocialIntelligenceService

router = APIRouter()


@router.get("/status")
async def get_social_intelligence_status():
    """사회적 지능 시스템 상태 확인"""
    try:
        return {
            "success": True,
            "status": "operational",
            "service": "Social Intelligence System",
            "version": "1.0.0",
            "features": {
                "natural_conversation": True,
                "context_understanding": True,
                "collaboration_detection": True,
                "appropriate_response": True,
                "social_adaptation": True,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)}


@router.post("/conversation")
async def process_conversation(
    conversation_data: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """대화 처리 및 응답 생성"""
    try:
        service = SocialIntelligenceService(db)
        result = service.process_conversation(conversation_data)
        return {
            "success": True,
            "conversation_result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_social_intelligence_stats(db: Session = Depends(get_db_session)):
    """사회적 지능 통계 조회"""
    try:
        service = SocialIntelligenceService(db)
        stats = service.get_social_intelligence_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-context")
async def analyze_context(
    conversation_data: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """맥락 이해"""
    try:
        service = SocialIntelligenceService(db)
        context = service._understand_context(conversation_data)
        return {
            "success": True,
            "context_understanding": context,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-response")
async def generate_appropriate_response(
    user_input_analysis: Dict[str, Any],
    context_understanding: Dict[str, Any],
    db: Session = Depends(get_db_session),
):
    """적절한 응답 생성"""
    try:
        service = SocialIntelligenceService(db)
        response = service._generate_appropriate_response(
            user_input_analysis, context_understanding
        )
        return {
            "success": True,
            "appropriate_response": response,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-collaboration")
async def detect_collaboration_opportunity(
    conversation_data: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """협업 기회 감지"""
    try:
        service = SocialIntelligenceService(db)
        collaboration = service._detect_collaboration_opportunity(conversation_data)
        return {
            "success": True,
            "collaboration_opportunity": collaboration,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
