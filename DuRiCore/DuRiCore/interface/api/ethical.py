#!/usr/bin/env python3
"""
DuRiCore - 윤리 API 엔드포인트
새로운 윤리 판단 엔진과 연동
"""

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from DuRiCore.DuRiCore.modules.ethical_reasoning import EthicalReasoningEngine  # noqa: E402

router = APIRouter()


class EthicalRequest(BaseModel):
    """윤리 분석 요청"""

    situation: str
    context: Optional[Dict[str, Any]] = None


class EthicalResponse(BaseModel):
    """윤리 분석 응답"""

    ethical_dilemma: str
    ethical_score: float
    reasoning_process: List[str]
    ethical_principles: List[str]
    stakeholder_analysis: Dict[str, Any]
    recommended_action: str
    confidence: float
    success: bool
    message: str


@router.post("/analyze", response_model=EthicalResponse)
async def analyze_ethical_dilemma(request: EthicalRequest):
    """윤리 딜레마 분석 API"""
    try:
        # 윤리 판단 엔진 초기화
        ethical_engine = EthicalReasoningEngine()

        # 윤리 분석 실행
        result = ethical_engine.analyze_ethical_dilemma(situation=request.situation, context=request.context or {})

        return EthicalResponse(
            ethical_dilemma=result.ethical_dilemma,
            ethical_score=result.ethical_score,
            reasoning_process=result.reasoning_process,
            ethical_principles=result.ethical_principles,
            stakeholder_analysis=result.stakeholder_analysis,
            recommended_action=result.recommended_action,
            confidence=result.confidence,
            success=True,
            message="윤리 분석이 성공적으로 완료되었습니다.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"윤리 분석 중 오류가 발생했습니다: {str(e)}")  # noqa: B904


@router.get("/stats")
async def get_ethical_stats():
    """윤리 분석 통계"""
    try:
        ethical_engine = EthicalReasoningEngine()
        stats = ethical_engine.get_ethical_stats()

        return {
            "success": True,
            "stats": stats,
            "message": "윤리 분석 통계를 성공적으로 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")  # noqa: B904


@router.post("/batch-analyze")
async def batch_analyze_ethical_dilemmas(requests: List[EthicalRequest]):
    """배치 윤리 분석 API"""
    try:
        ethical_engine = EthicalReasoningEngine()
        results = []

        for request in requests:
            result = ethical_engine.analyze_ethical_dilemma(situation=request.situation, context=request.context or {})

            results.append(
                {
                    "situation": request.situation,
                    "ethical_score": result.ethical_score,
                    "confidence": result.confidence,
                    "ethical_principles": result.ethical_principles,
                    "recommended_action": result.recommended_action,
                }
            )

        return {
            "success": True,
            "results": results,
            "total_analyzed": len(results),
            "average_score": (sum(r["ethical_score"] for r in results) / len(results) if results else 0),
            "message": f"{len(results)}개의 윤리적 상황에 대한 분석이 완료되었습니다.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 분석 중 오류가 발생했습니다: {str(e)}")  # noqa: B904


@router.get("/principles")
async def get_ethical_principles():
    """지원되는 윤리 원칙 조회"""
    try:
        return {
            "success": True,
            "principles": [
                "autonomy",
                "beneficence",
                "non-maleficence",
                "justice",
                "utilitarianism",
                "deontology",
                "virtue_ethics",
                "rights_based",
            ],
            "message": "지원되는 윤리 원칙을 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"윤리 원칙 조회 중 오류가 발생했습니다: {str(e)}")  # noqa: B904


@router.get("/frameworks")
async def get_ethical_frameworks():
    """지원되는 윤리적 프레임워크 조회"""
    try:
        return {
            "success": True,
            "frameworks": [
                "utilitarianism",
                "deontology",
                "virtue_ethics",
                "rights_based",
                "care_ethics",
                "feminist_ethics",
            ],
            "message": "지원되는 윤리적 프레임워크를 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(  # noqa: B904
            status_code=500,
            detail=f"윤리적 프레임워크 조회 중 오류가 발생했습니다: {str(e)}",
        )


@router.get("/health")
async def ethical_health_check():
    """윤리 판단 엔진 상태 확인"""
    try:
        ethical_engine = EthicalReasoningEngine()

        # 간단한 테스트 실행
        test_result = ethical_engine.analyze_ethical_dilemma(
            situation="친구가 시험에서 부정행위를 했는데, 이를 고발해야 할지 망설이고 있습니다.",
            context={"complexity": "medium", "stakeholders": 2},
        )

        return {
            "status": "healthy",
            "engine": "ethical_reasoning_engine",
            "test_result": {
                "ethical_score": test_result.ethical_score,
                "confidence": test_result.confidence,
                "principles_count": len(test_result.ethical_principles),
            },
            "message": "윤리 판단 엔진이 정상적으로 작동하고 있습니다.",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "engine": "ethical_reasoning_engine",
            "error": str(e),
            "message": "윤리 판단 엔진에 문제가 있습니다.",
        }
