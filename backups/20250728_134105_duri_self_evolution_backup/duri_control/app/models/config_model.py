from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ConfigType(str, Enum):
    """설정 타입"""
    SERVICE = "service"
    SYSTEM = "system"
    GLOBAL = "global"


class ServiceConfig(BaseModel):
    """서비스별 설정 모델"""
    
    # 기본 설정
    log_level: str = Field(default="INFO", description="로그 레벨")
    max_threads: int = Field(default=4, description="최대 스레드 수")
    timeout: int = Field(default=30, description="타임아웃 (초)")
    retry_count: int = Field(default=3, description="재시도 횟수")
    
    # 서비스별 특화 설정
    port: Optional[int] = Field(None, description="서비스 포트")
    host: str = Field(default="0.0.0.0", description="서비스 호스트")
    debug: bool = Field(default=False, description="디버그 모드")
    
    # 데이터베이스 설정
    db_host: str = Field(default="duri-postgres", description="데이터베이스 호스트")
    db_port: int = Field(default=5432, description="데이터베이스 포트")
    db_name: str = Field(default="duri_db", description="데이터베이스 이름")
    db_user: str = Field(default="duri", description="데이터베이스 사용자")
    
    # Redis 설정
    redis_host: str = Field(default="duri-redis", description="Redis 호스트")
    redis_port: int = Field(default=6379, description="Redis 포트")
    
    # 커스텀 설정
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="커스텀 설정")


class ConfigUpdateRequest(BaseModel):
    """설정 업데이트 요청 모델"""
    
    log_level: Optional[str] = Field(None, description="로그 레벨")
    max_threads: Optional[int] = Field(None, description="최대 스레드 수")
    timeout: Optional[int] = Field(None, description="타임아웃 (초)")
    retry_count: Optional[int] = Field(None, description="재시도 횟수")
    port: Optional[int] = Field(None, description="서비스 포트")
    host: Optional[str] = Field(None, description="서비스 호스트")
    debug: Optional[bool] = Field(None, description="디버그 모드")
    db_host: Optional[str] = Field(None, description="데이터베이스 호스트")
    db_port: Optional[int] = Field(None, description="데이터베이스 포트")
    db_name: Optional[str] = Field(None, description="데이터베이스 이름")
    db_user: Optional[str] = Field(None, description="데이터베이스 사용자")
    redis_host: Optional[str] = Field(None, description="Redis 호스트")
    redis_port: Optional[int] = Field(None, description="Redis 포트")
    custom_config: Optional[Dict[str, Any]] = Field(None, description="커스텀 설정")


class ConfigResponse(BaseModel):
    """설정 응답 모델"""
    
    service_name: str = Field(description="서비스 이름")
    config: ServiceConfig = Field(description="서비스 설정")
    last_updated: datetime = Field(description="마지막 업데이트 시간")
    version: str = Field(default="1.0", description="설정 버전")


class ConfigListResponse(BaseModel):
    """설정 목록 응답 모델"""
    
    services: list[str] = Field(description="사용 가능한 서비스 목록")
    total_services: int = Field(description="총 서비스 수")


class ConfigValidationResponse(BaseModel):
    """설정 검증 응답 모델"""
    
    is_valid: bool = Field(description="설정 유효성")
    errors: list[str] = Field(default_factory=list, description="검증 오류 목록")
    warnings: list[str] = Field(default_factory=list, description="경고 목록")


# 기본 서비스별 설정
DEFAULT_SERVICE_CONFIGS = {
    "duri_core": ServiceConfig(
        log_level="INFO",
        max_threads=8,
        timeout=60,
        retry_count=5,
        port=8080,
        host="0.0.0.0",
        debug=False,
        custom_config={
            "evolution_url": "http://localhost:8082/evolve",
            "brain_url": "http://localhost:8081/brain",
            "control_url": "http://localhost:8083/control"
        }
    ),
    "duri_brain": ServiceConfig(
        log_level="INFO",
        max_threads=4,
        timeout=30,
        retry_count=3,
        port=8081,
        host="0.0.0.0",
        debug=False,
        custom_config={
            "model_path": "/app/models",
            "cache_size": 1000,
            "prediction_timeout": 10
        }
    ),
    "duri_evolution": ServiceConfig(
        log_level="INFO",
        max_threads=6,
        timeout=45,
        retry_count=4,
        port=8082,
        host="0.0.0.0",
        debug=False,
        custom_config={
            "population_size": 100,
            "generation_limit": 50,
            "mutation_rate": 0.1,
            "crossover_rate": 0.8
        }
    ),
    "duri_control": ServiceConfig(
        log_level="INFO",
        max_threads=4,
        timeout=30,
        retry_count=3,
        port=8083,
        host="0.0.0.0",
        debug=False,
        custom_config={
            "monitor_interval": 5,
            "log_retention_days": 7,
            "max_log_entries": 10000,
            "health_check_interval": 10
        }
    )
} 