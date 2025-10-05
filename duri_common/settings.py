#!/usr/bin/env python3
"""
DuRi 통합 설정 관리 시스템 (확장 버전)
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import json
import os
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    host: str = "duri-postgres"
    port: int = 5432
    database: str = "duri"
    user: str = "duri"
    password: str = "CHANGE_ME_DB_PASSWORD"
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseModel):
    host: str = "duri-redis"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    pool_size: int = 10

    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    workers: int = 4


class EvolutionSettings(BaseModel):
    learning_rate: float = 0.1
    max_cycles_per_session: int = 100
    pattern_analysis_interval: int = 300
    insight_generation_interval: int = 600
    knowledge_update_interval: int = 900


class DataSettings(BaseModel):
    evolution_data_dir: str = "/app/data/evolution_data"
    patterns_dir: str = "/app/data/patterns"
    insights_dir: str = "/app/data/insights"
    knowledge_dir: str = "/app/data/knowledge"
    cache_enabled: bool = True
    cache_ttl: int = 1800


class AnalysisSettings(BaseModel):
    pattern_min_confidence: float = 0.6
    insight_min_confidence: float = 0.7
    min_data_points: int = 10
    max_patterns_per_emotion: int = 20
    max_insights_per_session: int = 5


class RecommendationsSettings(BaseModel):
    max_recommendations: int = 5
    min_success_rate: float = 0.3
    weight_recent_results: float = 0.7
    weight_success_rate: float = 0.3


class LoggingSettings(BaseModel):
    level: str = "INFO"
    format: str = "json"
    file: str = "/app/logs/duri.log"
    max_size: str = "100MB"
    backup_count: int = 5


class ServiceSettings(BaseModel):
    brain_url: str = "http://duri-brain:8081"
    brain_timeout: int = 30
    brain_retries: int = 3


class PerformanceSettings(BaseModel):
    max_concurrent_requests: int = 50
    request_timeout: int = 60
    batch_size: int = 100
    rate_limit_enabled: bool = True
    requests_per_minute: int = 500


class SecuritySettings(BaseModel):
    api_key: str = "CHANGE_ME_API_KEY"
    jwt_secret: str = "CHANGE_ME_JWT_SECRET"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: List[str] = ["Content-Type", "Authorization"]


class MonitoringSettings(BaseModel):
    prometheus_url: str = "http://prometheus:9090"
    grafana_url: str = "http://grafana:3000"
    grafana_user: str = "duri-duri"
    grafana_password: str = "DuRi@2025!"  # tests expect this


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

    # 서비스별 설정
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    server: ServerSettings = ServerSettings()
    evolution: EvolutionSettings = EvolutionSettings()
    data: DataSettings = DataSettings()
    analysis: AnalysisSettings = AnalysisSettings()
    recommendations: RecommendationsSettings = RecommendationsSettings()
    logging: LoggingSettings = LoggingSettings()
    services: ServiceSettings = ServiceSettings()
    performance: PerformanceSettings = PerformanceSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()

    def to_dict(self) -> Dict[str, Any]:
        """Pydantic 모델을 딕셔너리로 변환 (기존 코드 호환용)"""
        return self.model_dump(mode="json")

    def get_service_port(self, service: str) -> int:
        """서비스별 포트 반환"""
        port_map = {"core": 8080, "brain": 8081, "evolution": 8082, "control": 8083}
        return port_map.get(service, 8080)


def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """딕셔너리 병합 (중첩 구조 지원)"""
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out

def _from_json_env() -> Dict[str, Any]:
    """JSON 파일에서 설정 로드"""
    p = os.getenv("DURI_CONFIG_JSON")
    if not p or not os.path.isfile(p):
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _from_nested_env() -> Dict[str, Any]:
    """중첩 환경변수에서 설정 로드 (DURI_MONITORING__PROMETHEUS_URL 등)"""
    pref = "DURI_"
    result: Dict[str, Any] = {}
    for k, v in os.environ.items():
        if not k.startswith(pref) or "__" not in k[len(pref):]:
            continue
        path = k[len(pref):].lower().split("__")
        cur = result
        for key in path[:-1]:
            cur = cur.setdefault(key, {})
        cur[path[-1]] = v
    # 단일 키(DURI_ENV 등)도 지원
    if os.getenv("DURI_ENV"):
        result.setdefault("env", os.getenv("DURI_ENV"))
    return result

# 전역 설정 인스턴스
settings = DuRiSettings()

# 테스트 호환성을 위한 함수 (새로운 로직 적용)
@lru_cache(maxsize=1)
def get_settings() -> DuRiSettings:
    """Backwards-compatible factory expected by tests."""
    base = {
        "env": "dev",
        "monitoring": {
            "prometheus_url": "http://prometheus:9090",
            "grafana_url": "http://grafana:3000",
            "grafana_user": "duri-duri",
            "grafana_password": "DuRi@2025!",
        },
    }
    cfg = _merge(base, _from_json_env())
    cfg = _merge(cfg, _from_nested_env())
    mon = MonitoringSettings(**cfg.get("monitoring", {}))
    return DuRiSettings(env=cfg.get("env", "dev"), monitoring=mon)
