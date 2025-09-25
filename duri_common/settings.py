#!/usr/bin/env python3
"""
DuRi 통합 설정 관리 시스템 (간단 버전)
"""

import os
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "duri-postgres"
    port: int = 5432
    database: str = "duri"
    user: str = "duri"
    password: str = "duri"
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseModel):
    host: str = "duri-redis"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class MonitoringSettings(BaseModel):
    prometheus_url: str = "http://prometheus:9090"
    grafana_url: str = "http://grafana:3000"
    grafana_user: str = "duri-duri"
    grafana_password: str = "CHANGE_ME_GRAFANA_PASSWORD"


class DuRiSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DURI_",
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )
    
    env: Literal["dev", "ops", "prod", "test"] = "dev"
    debug: bool = False
    version: str = "latest"
    
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    def to_dict(self) -> Dict[str, Any]:
        """Pydantic 모델을 딕셔너리로 변환 (기존 코드 호환용)"""
        return self.model_dump(mode='json')


# 전역 설정 인스턴스
settings = DuRiSettings()