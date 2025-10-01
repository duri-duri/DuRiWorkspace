#!/usr/bin/env python3
"""
🎭 DuRi Brain 감정 API 라우터

/emotion 엔드포인트를 관리합니다.
"""

from fastapi import APIRouter, Request, status
from schemas.emotion import EmotionData
from schemas.responses import BaseResponse
from services.emotion_service import (
    analyze_emotion,
    generate_recommendation,
    store_emotion_data,
)

from utils.error_handler import handle_internal_error

router = APIRouter()


@router.post("/", response_model=BaseResponse)
async def emotion_endpoint(request: Request, payload: EmotionData):
    try:
        # 감정 분석
        analysis = analyze_emotion(payload.emotion.value, payload.intensity)
        # 데이터 저장
        store_emotion_data(payload.dict())
        # 추천 생성
        recommendation = generate_recommendation(payload.dict())
        return BaseResponse(
            status="success",
            message="감정 데이터가 성공적으로 처리되었습니다",
            data={"analysis": analysis, "recommendation": recommendation},
        )
    except Exception as exc:
        return handle_internal_error(request, exc)
