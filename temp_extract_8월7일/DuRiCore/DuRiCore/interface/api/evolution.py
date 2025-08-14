#!/usr/bin/env python3
"""
DuRiCore - 자기 진화 API 엔드포인트
새로운 자기 진화 엔진과 연동
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
import os

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from DuRiCore.DuRiCore.modules.self_evolution import SelfEvolutionEngine

router = APIRouter()

class EvolutionRequest(BaseModel):
    """자기 진화 분석 요청"""
    context: Optional[Dict[str, Any]] = None

class EvolutionResponse(BaseModel):
    """자기 진화 분석 응답"""
    evolution_score: float
    improvement_areas: List[Dict[str, Any]]
    evolution_directions: List[Dict[str, Any]]
    improvement_actions: List[Dict[str, Any]]
    success: bool
    message: str

@router.post("/analyze", response_model=EvolutionResponse)
async def analyze_self_evolution(request: EvolutionRequest):
    """자기 진화 분석 API"""
    try:
        # 자기 진화 엔진 초기화
        evolution_engine = SelfEvolutionEngine()
        
        # 자기 진화 분석 실행
        result = evolution_engine.analyze_and_evolve()
        
        return EvolutionResponse(
            evolution_score=result.evolution_score,
            improvement_areas=result.improvement_areas,
            evolution_directions=result.evolution_directions,
            improvement_actions=result.improvement_actions,
            success=True,
            message="자기 진화 분석이 성공적으로 완료되었습니다."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"자기 진화 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/stats")
async def get_evolution_stats():
    """자기 진화 통계"""
    try:
        evolution_engine = SelfEvolutionEngine()
        stats = evolution_engine.get_evolution_stats()
        
        return {
            "success": True,
            "stats": stats,
            "message": "자기 진화 통계를 성공적으로 조회했습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/improve")
async def trigger_self_improvement(request: EvolutionRequest):
    """자기 개선 트리거 API"""
    try:
        evolution_engine = SelfEvolutionEngine()
        
        # 자기 개선 실행
        improvement_result = evolution_engine.trigger_improvement(
            context=request.context or {}
        )
        
        return {
            "success": True,
            "improvement_result": improvement_result,
            "message": "자기 개선이 성공적으로 실행되었습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"자기 개선 실행 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/improvement-areas")
async def get_improvement_areas():
    """개선 영역 조회"""
    try:
        evolution_engine = SelfEvolutionEngine()
        areas = evolution_engine.get_improvement_areas()
        
        return {
            "success": True,
            "improvement_areas": areas,
            "message": "개선 영역을 성공적으로 조회했습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"개선 영역 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/evolution-directions")
async def get_evolution_directions():
    """진화 방향 조회"""
    try:
        evolution_engine = SelfEvolutionEngine()
        directions = evolution_engine.get_evolution_directions()
        
        return {
            "success": True,
            "evolution_directions": directions,
            "message": "진화 방향을 성공적으로 조회했습니다."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"진화 방향 조회 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/health")
async def evolution_health_check():
    """자기 진화 엔진 상태 확인"""
    try:
        evolution_engine = SelfEvolutionEngine()
        
        # 간단한 테스트 실행
        test_result = evolution_engine.analyze_and_evolve()
        
        return {
            "status": "healthy",
            "engine": "self_evolution_engine",
            "test_result": {
                "evolution_score": test_result.evolution_score,
                "improvement_areas_count": len(test_result.improvement_areas),
                "evolution_directions_count": len(test_result.evolution_directions)
            },
            "message": "자기 진화 엔진이 정상적으로 작동하고 있습니다."
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "engine": "self_evolution_engine",
            "error": str(e),
            "message": "자기 진화 엔진에 문제가 있습니다."
        } 
 
 