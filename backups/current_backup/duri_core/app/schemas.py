#!/usr/bin/env python3
"""
📋 DuRi 공통 스키마

DuRi 프로젝트의 Pydantic 스키마 정의 파일.
공통 감정 데이터 구조 및 응답 스키마 포함.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Generic, TypeVar
from datetime import datetime

# ✅ StrEnum 호환 처리 (Python 3.11 이상만 지원)
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        pass

# -----------------------------
# 🔹 공통 Enum 및 베이스 모델
# -----------------------------

class EmotionType(StrEnum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"

class TimestampedModel(BaseModel):
    """공통 timestamp 포함 베이스 모델"""
    timestamp: datetime = Field(default_factory=datetime.now, description="타임스탬프")


# -----------------------------
# 🔹 감정 데이터 모델
# -----------------------------

class EmotionData(TimestampedModel):
    """감정 데이터 스키마"""
    emotion: EmotionType = Field(..., description="감정 타입")
    intensity: float = Field(..., ge=0.0, le=1.0, description="감정 강도 (0.0~1.0)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="감정 인식 신뢰도")
    meta_info: Optional[Dict[str, Any]] = Field(None, description="추가 메타데이터")


# -----------------------------
# 🔹 응답 스키마
# -----------------------------

T = TypeVar("T")

class BaseResponse(TimestampedModel, Generic[T]):
    """성공 응답 공통 스키마"""
    status: str = Field(..., description="응답 상태")
    message: str = Field(..., description="응답 메시지")
    data: Optional[T] = Field(None, description="응답 데이터")


class ErrorResponse(TimestampedModel):
    """에러 응답 스키마"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    status_code: int = Field(..., description="HTTP 상태 코드")
