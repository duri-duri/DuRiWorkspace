#!/usr/bin/env python3
"""
DuRi 통합 설정 관리 시스템 (확장 버전)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
    grafana_password: str = "DuRi@2025!"  # tests expect this - 로컬/테스트 전용, 실제 배포시 ENV로 오버라이드 필수


# 간단한 dataclass 기반 설정 (테스트 호환성 우선)
@dataclass(frozen=True)
class DuRiSettings:
    env: str
    debug: bool
    version: str
    database: DatabaseSettings
    redis: RedisSettings
    server: ServerSettings
    evolution: EvolutionSettings
    data: DataSettings
    analysis: AnalysisSettings
    recommendations: RecommendationsSettings
    logging: LoggingSettings
    services: ServiceSettings
    performance: PerformanceSettings
    security: SecuritySettings
    monitoring: MonitoringSettings

    def __init__(self, **kwargs):
        # 기본값 설정
        base = {
            "env": "dev",
            "debug": False,
            "version": "latest",
            "monitoring": {
                "prometheus_url": "http://prometheus:9090",
                "grafana_url": "http://grafana:3000",
                "grafana_user": "duri-duri",
                "grafana_password": "DuRi@2025!",  # 로컬/테스트 전용
            },
            "database": {
                "host": "duri-postgres",
                "port": 5432,
                "database": "duri",
                "user": "duri",
                "password": "CHANGE_ME_DB_PASSWORD",
                "pool_size": 10,
                "max_overflow": 20,
            },
        }

        # JSON 파일에서 설정 로드
        cfg = _merge(base, _from_json_env())
        # 중첩 환경변수에서 설정 로드
        cfg = _merge(cfg, _from_nested_env())

        # 객체 초기화
        object.__setattr__(self, "env", cfg.get("env", "dev"))
        object.__setattr__(self, "debug", cfg.get("debug", False))
        object.__setattr__(self, "version", cfg.get("version", "latest"))
        object.__setattr__(self, "monitoring", MonitoringSettings(**cfg.get("monitoring", {})))
        object.__setattr__(self, "database", DatabaseSettings(**cfg.get("database", {})))
        object.__setattr__(self, "redis", RedisSettings())
        object.__setattr__(self, "server", ServerSettings())
        object.__setattr__(self, "evolution", EvolutionSettings())
        object.__setattr__(self, "data", DataSettings())
        object.__setattr__(self, "analysis", AnalysisSettings())
        object.__setattr__(self, "recommendations", RecommendationsSettings())
        object.__setattr__(self, "logging", LoggingSettings())
        object.__setattr__(self, "services", ServiceSettings())
        object.__setattr__(self, "performance", PerformanceSettings())
        object.__setattr__(self, "security", SecuritySettings())

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (기존 코드 호환용)"""
        return {
            "env": self.env,
            "debug": self.debug,
            "version": self.version,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "user": self.database.user,
                "password": self.database.password,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "db": self.redis.db,
                "password": self.redis.password,
                "pool_size": self.redis.pool_size,
            },
            "services": {
                "brain_url": self.services.brain_url,
                "brain_timeout": self.services.brain_timeout,
                "brain_retries": self.services.brain_retries,
            },
            "monitoring": {
                "prometheus_url": self.monitoring.prometheus_url,
                "grafana_url": self.monitoring.grafana_url,
                "grafana_user": self.monitoring.grafana_user,
                "grafana_password": self.monitoring.grafana_password,
            },
        }

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
        if not k.startswith(pref) or "__" not in k[len(pref) :]:
            continue
        path = k[len(pref) :].lower().split("__")
        cur = result
        for key in path[:-1]:
            cur = cur.setdefault(key, {})
        cur[path[-1]] = v
    # 단일 키(DURI_ENV 등)도 지원
    if os.getenv("DURI_ENV"):
        result.setdefault("env", os.getenv("DURI_ENV"))
    return result


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


# 전역 설정 인스턴스 (새로운 로직 사용)
settings = get_settings()
