from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """로그 엔트리 모델"""
    
    id: Optional[str] = Field(None, description="로그 엔트리 고유 ID")
    timestamp: datetime = Field(..., description="로그 생성 시간")
    service_name: str = Field(..., description="서비스 이름")
    level: str = Field(..., description="로그 레벨 (INFO, WARNING, ERROR, DEBUG)")
    message: str = Field(..., description="로그 메시지")
    source: str = Field(..., description="로그 소스 (file, container, api)")
    container_id: Optional[str] = Field(None, description="컨테이너 ID (컨테이너 로그인 경우)")
    file_path: Optional[str] = Field(None, description="로그 파일 경로 (파일 로그인 경우)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LogStreamConfig(BaseModel):
    """로그 스트림 설정"""
    
    services: list[str] = Field(default_factory=list, description="모니터링할 서비스 목록")
    levels: list[str] = Field(default_factory=lambda: ["INFO", "WARNING", "ERROR"], description="필터링할 로그 레벨")
    max_entries: int = Field(default=1000, description="최대 저장 로그 엔트리 수")
    stream_interval: float = Field(default=1.0, description="스트림 업데이트 간격 (초)")


class LogQueryParams(BaseModel):
    """로그 조회 파라미터"""
    
    limit: int = Field(default=50, ge=1, le=10000, description="조회할 로그 수")
    service_name: Optional[str] = Field(None, description="특정 서비스 필터")
    level: Optional[str] = Field(None, description="로그 레벨 필터")
    since: Optional[datetime] = Field(None, description="이후 시간부터 조회")
    until: Optional[datetime] = Field(None, description="이전 시간까지 조회") 