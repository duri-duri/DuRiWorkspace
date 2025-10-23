#!/usr/bin/env python3
"""
DuRiCore - 학습 API 엔드포인트
새로운 학습 엔진과 연동
"""

import os
import sys
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from DuRiCore.DuRiCore.modules.learning_engine import LearningEngine

router = APIRouter()


class LearningRequest(BaseModel):
    """학습 처리 요청"""

    content: str
    learning_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class LearningResponse(BaseModel):
    """학습 처리 응답"""

    content_type: str
    learning_score: float
    insights: List[str]
    knowledge_gained: Dict[str, Any]
    skills_improved: List[str]
    next_steps: List[str]
    success: bool
    message: str


@router.post("/process", response_model=LearningResponse)
async def process_learning(request: LearningRequest):
    """학습 처리 API"""
    try:
        # 학습 엔진 초기화
        learning_engine = LearningEngine()

        # 학습 처리 실행
        result = learning_engine.process_learning(
            content=request.content,
            learning_type=request.learning_type or "auto",
            context=request.context or {},
        )

        return LearningResponse(
            content_type=result.content_type,
            learning_score=result.learning_score,
            insights=result.insights,
            knowledge_gained=result.knowledge_gained,
            skills_improved=result.skills_improved,
            next_steps=result.next_steps,
            success=True,
            message="학습 처리가 성공적으로 완료되었습니다.",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"학습 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/stats")
async def get_learning_stats():
    """학습 통계 조회"""
    try:
        learning_engine = LearningEngine()
        stats = learning_engine.get_learning_stats()

        return {
            "success": True,
            "stats": stats,
            "message": "학습 통계를 성공적으로 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/batch-process")
async def batch_process_learning(requests: List[LearningRequest]):
    """배치 학습 처리 API"""
    try:
        learning_engine = LearningEngine()
        results = []

        for request in requests:
            result = learning_engine.process_learning(
                content=request.content,
                learning_type=request.learning_type or "auto",
                context=request.context or {},
            )

            results.append(
                {
                    "content": request.content,
                    "content_type": result.content_type,
                    "learning_score": result.learning_score,
                    "insights": result.insights,
                    "skills_improved": result.skills_improved,
                }
            )

        return {
            "success": True,
            "results": results,
            "total_processed": len(results),
            "average_score": (
                sum(r["learning_score"] for r in results) / len(results)
                if results
                else 0
            ),
            "message": f"{len(results)}개의 콘텐츠에 대한 학습 처리가 완료되었습니다.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"배치 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/content-types")
async def get_supported_content_types():
    """지원되는 콘텐츠 타입 조회"""
    try:
        return {
            "success": True,
            "content_types": [
                "text",
                "video",
                "family",
                "metacognitive",
                "autonomous",
                "social",
            ],
            "message": "지원되는 콘텐츠 타입을 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"콘텐츠 타입 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def learning_health_check():
    """학습 엔진 상태 확인"""
    try:
        learning_engine = LearningEngine()

        # 간단한 테스트 실행
        test_result = learning_engine.process_learning(
            content="인공지능에 대한 기본 개념을 학습했습니다.",
            learning_type="text",
            context={"domain": "technology"},
        )

        return {
            "status": "healthy",
            "engine": "learning_engine",
            "test_result": {
                "content_type": test_result.content_type,
                "learning_score": test_result.learning_score,
                "insights_count": len(test_result.insights),
            },
            "message": "학습 엔진이 정상적으로 작동하고 있습니다.",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "engine": "learning_engine",
            "error": str(e),
            "message": "학습 엔진에 문제가 있습니다.",
        }
