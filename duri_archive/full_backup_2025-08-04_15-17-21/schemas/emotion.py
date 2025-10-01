#!/usr/bin/env python3
"""
🎭 DuRi Brain 감정 스키마

이 파일은 감정 처리 관련 Pydantic 스키마를 정의합니다.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


# 감정 타입 열거형
class EmotionType(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


# 감정 데이터 스키마
class EmotionData(BaseModel):
    """감정 데이터 스키마"""

    emotion: EmotionType = Field(..., description="감정 타입")
    intensity: float = Field(..., ge=0.0, le=1.0, description="감정 강도 (0.0-1.0)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="감정 인식 신뢰도")
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")
    meta_info: Optional[Dict[str, Any]] = Field(
        default=None, description="추가 메타데이터"
    )
