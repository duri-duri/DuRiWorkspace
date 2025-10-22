#!/usr/bin/env python3
"""
DuRiCore - 감정 API 엔드포인트
새로운 감정 엔진과 연동
"""

import os
import sys
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from DuRiCore.DuRiCore.modules.emotion_engine import EmotionEngine, InputData

router = APIRouter()


class EmotionRequest(BaseModel):
    """감정 분석 요청"""

    text: str
    context: Optional[Dict[str, Any]] = None


class EmotionResponse(BaseModel):
    """감정 분석 응답"""

    primary_emotion: str
    secondary_emotions: list
    intensity: float
    confidence: float
    context_fit: float
    emotion_reason_balance: Dict[str, Any]
    empathetic_response: str
    success: bool
    message: str


@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(request: EmotionRequest):
    """감정 분석 API"""
    try:
        # 감정 엔진 초기화
        emotion_engine = EmotionEngine()

        # 입력 데이터 생성
        input_data = InputData(text=request.text, context=request.context or {})

        # 감정 분석 실행
        analysis = emotion_engine.analyze_complex_emotion(input_data)

        return EmotionResponse(
            primary_emotion=analysis.primary_emotion.value,
            secondary_emotions=[emotion.value for emotion in analysis.secondary_emotions],
            intensity=analysis.intensity,
            confidence=analysis.confidence,
            context_fit=analysis.context_fit,
            emotion_reason_balance=analysis.emotion_reason_balance,
            empathetic_response=analysis.empathetic_response,
            success=True,
            message="감정 분석이 성공적으로 완료되었습니다.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/stats")
async def get_emotion_stats():
    """감정 분석 통계"""
    try:
        emotion_engine = EmotionEngine()
        stats = emotion_engine.get_emotion_stats()

        return {
            "success": True,
            "stats": stats,
            "message": "감정 분석 통계를 성공적으로 조회했습니다.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}")


@router.post("/batch-analyze")
async def batch_analyze_emotions(requests: list[EmotionRequest]):
    """배치 감정 분석 API"""
    try:
        emotion_engine = EmotionEngine()
        results = []

        for request in requests:
            input_data = InputData(text=request.text, context=request.context or {})

            analysis = emotion_engine.analyze_complex_emotion(input_data)

            results.append(
                {
                    "text": request.text,
                    "primary_emotion": analysis.primary_emotion.value,
                    "intensity": analysis.intensity,
                    "confidence": analysis.confidence,
                    "empathetic_response": analysis.empathetic_response,
                }
            )

        return {
            "success": True,
            "results": results,
            "total_analyzed": len(results),
            "message": f"{len(results)}개의 텍스트에 대한 감정 분석이 완료되었습니다.",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/health")
async def emotion_health_check():
    """감정 엔진 상태 확인"""
    try:
        emotion_engine = EmotionEngine()

        # 간단한 테스트 실행
        test_input = InputData(
            text="안녕하세요! 오늘 기분이 좋습니다.", context={"type": "greeting"}
        )

        analysis = emotion_engine.analyze_complex_emotion(test_input)

        return {
            "status": "healthy",
            "engine": "emotion_engine",
            "test_result": {
                "primary_emotion": analysis.primary_emotion.value,
                "confidence": analysis.confidence,
            },
            "message": "감정 엔진이 정상적으로 작동하고 있습니다.",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "engine": "emotion_engine",
            "error": str(e),
            "message": "감정 엔진에 문제가 있습니다.",
        }
