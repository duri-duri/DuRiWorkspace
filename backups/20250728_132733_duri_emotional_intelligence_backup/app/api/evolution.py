"""
Day 6-2: 진화 API
Truth Memory 자동 진화 및 패턴 기반 학습 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..database.database import get_db_session
from ..services.evolution_service import EvolutionService
# from ..schemas.base import BaseResponse, ErrorResponse

router = APIRouter(prefix="/evolution", tags=["Evolution"])

@router.post("/auto-evolve", response_model=Dict[str, Any])
async def auto_evolve_truth_memories(db: Session = Depends(get_db_session)):
    """Truth Memory 자동 진화 실행"""
    try:
        evolution_service = EvolutionService(db)
        result = evolution_service.auto_evolve_truth_memories()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "Truth Memory 진화 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=Dict[str, Any])
async def get_evolution_statistics(db: Session = Depends(get_db_session)):
    """진화 통계 조회"""
    try:
        evolution_service = EvolutionService(db)
        stats = evolution_service.get_evolution_statistics()
        
        return {
            "success": True,
            "message": "진화 통계 조회 완료",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual-evolve", response_model=Dict[str, Any])
async def manual_evolution_trigger(evolution_params: Dict[str, Any], db: Session = Depends(get_db_session)):
    """수동 진화 트리거 (고급 파라미터 설정)"""
    try:
        evolution_service = EvolutionService(db)
        
        # 파라미터 설정
        if "pattern_threshold" in evolution_params:
            evolution_service.pattern_threshold = evolution_params["pattern_threshold"]
        if "evolution_confidence" in evolution_params:
            evolution_service.evolution_confidence = evolution_params["evolution_confidence"]
        
        result = evolution_service.auto_evolve_truth_memories()
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": "수동 진화 완료",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 