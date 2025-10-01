#!/usr/bin/env python3
"""
📤 DuRi Brain 응답 스키마

이 파일은 API 응답 관련 Pydantic 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# 기본 응답 스키마
class BaseResponse(BaseModel):
    """기본 응답 스키마"""

    status: str = Field(..., description="응답 상태")
    message: str = Field(..., description="응답 메시지")
    data: Optional[Any] = Field(default=None, description="응답 데이터 (선택적)")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="응답 타임스탬프"
    )


# 에러 응답 스키마
class ErrorResponse(BaseModel):
    """에러 응답 스키마"""

    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(default=None, description="상세 에러 정보")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="에러 발생 시간"
    )
    status_code: int = Field(..., description="HTTP 상태 코드")
