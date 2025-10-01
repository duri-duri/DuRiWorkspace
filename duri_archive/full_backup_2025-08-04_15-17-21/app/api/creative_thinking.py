"""
Day 9: 창의적 사고 API
DuRi의 혁신적 아이디어 생성 및 창의적 문제 해결 능력 API
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database.database import get_db_session
from ..services.creative_thinking_service import CreativeThinkingService

router = APIRouter()


@router.get("/status")
async def get_creative_thinking_status():
    """창의적 사고 시스템 상태 확인"""
    try:
        return {
            "success": True,
            "status": "operational",
            "service": "Creative Thinking System",
            "version": "1.0.0",
            "features": {
                "innovative_idea_generation": True,
                "pattern_analysis": True,
                "innovation_assessment": True,
                "feasibility_analysis": True,
                "creative_synthesis": True,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)}


@router.post("/generate-ideas")
async def generate_creative_ideas(
    context: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """창의적 아이디어 생성"""
    try:
        service = CreativeThinkingService(db)
        result = service.generate_creative_ideas(context)
        return {
            "success": True,
            "ideas": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_creative_thinking_stats(db: Session = Depends(get_db_session)):
    """창의적 사고 통계 조회"""
    try:
        service = CreativeThinkingService(db)
        stats = service.get_creative_thinking_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-context")
async def analyze_creative_context(
    context: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """창의적 맥락 분석"""
    try:
        service = CreativeThinkingService(db)
        creative_context = service._analyze_creative_context(context)
        return {
            "success": True,
            "creative_context": creative_context,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assess-innovation")
async def assess_innovation(ideas: list, db: Session = Depends(get_db_session)):
    """혁신성 평가"""
    try:
        service = CreativeThinkingService(db)
        assessment = service._assess_innovation(ideas)
        return {
            "success": True,
            "assessment": assessment,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-feasibility")
async def analyze_feasibility(
    ideas: list, context: Dict[str, Any], db: Session = Depends(get_db_session)
):
    """실현 가능성 분석"""
    try:
        service = CreativeThinkingService(db)
        feasibility = service._analyze_feasibility(ideas, context)
        return {
            "success": True,
            "feasibility": feasibility,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
