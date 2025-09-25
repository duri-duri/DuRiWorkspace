#!/usr/bin/env python3
"""
DuRi 통합 설정 관리 시스템
Pydantic Settings 기반으로 모든 서비스의 설정을 통합 관리합니다.
기존 JSON 설정 파일과 환경변수 모두 지원합니다.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """데이터베이스 설정"""
    host: str = Field(default="duri-postgres", env="POSTGRES_HOST")
    port: int = Field(default=5432, env="POSTGRES_PORT")
    database: str = Field(default="duri", env="POSTGRES_DB")
    user: str = Field(default="duri", env="POSTGRES_USER")
    password: str = Field(default="duri", env="POSTGRES_PASSWORD")
    pool_size: int = Field(default=10, env="POSTGRES_POOL_SIZE")
    max_overflow: int = Field(default=20, env="POSTGRES_MAX_OVERFLOW")
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisSettings(BaseSettings):
    """Redis 설정"""
    host: str = Field(default="duri-redis", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    db: int = Field(default=0, env="REDIS_DB")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ServiceSettings(BaseSettings):
    """서비스 포트 설정"""
    core_port: int = Field(default=8080, env="DURI_CORE_PORT")
    brain_port: int = Field(default=8081, env="DURI_BRAIN_PORT")
    evolution_port: int = Field(default=8082, env="DURI_EVOLUTION_PORT")
    control_port: int = Field(default=8083, env="DURI_CONTROL_PORT")
    
    # 서비스 URL들
    @property
    def core_url(self) -> str:
        return f"http://duri-core:{self.core_port}"
    
    @property
    def brain_url(self) -> str:
        return f"http://duri-brain:{self.brain_port}"
    
    @property
    def evolution_url(self) -> str:
        return f"http://duri-evolution:{self.evolution_port}"
    
    @property
    def control_url(self) -> str:
        return f"http://duri-control:{self.control_port}"


class LoggingSettings(BaseSettings):
    """로깅 설정"""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    file_path: str = Field(default="/app/logs", env="LOG_FILE_PATH")
    max_size: str = Field(default="100MB", env="LOG_MAX_SIZE")
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")


class SecuritySettings(BaseSettings):
    """보안 설정"""
    jwt_secret_key: str = Field(default="your_super_secret_jwt_key_for_production_2024", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # API 키들
    brain_api_key: Optional[str] = Field(default=None, env="BRAIN_API_KEY")
    evolution_api_key: Optional[str] = Field(default=None, env="EVOLUTION_API_KEY")
    
    # 관리자 계정
    admin_username: str = Field(default="admin", env="ADMIN_USERNAME")
    admin_password: str = Field(default="secure_admin_password_2024", env="ADMIN_PASSWORD")
    admin_email: str = Field(default="admin@duri.system", env="ADMIN_EMAIL")


class MonitoringSettings(BaseSettings):
    """모니터링 설정"""
    prometheus_url: str = Field(default="http://prometheus:9090", env="PROMETHEUS_URL")
    grafana_url: str = Field(default="http://grafana:3000", env="GRAFANA_URL")
    grafana_user: str = Field(default="duri-duri", env="GRAFANA_USER")
    grafana_password: str = Field(default="DuRi@2025!", env="GRAFANA_PASSWORD")


class BackupSettings(BaseSettings):
    """백업 설정"""
    enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    schedule: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")
    retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    path: str = Field(default="/app/backups", env="BACKUP_PATH")


class DuRiSettings(BaseSettings):
    """DuRi 통합 설정 클래스"""
    
    # 환경 설정
    env: str = Field(default="dev", env="DURI_ENV")
    debug: bool = Field(default=False, env="DURI_DEBUG")
    version: str = Field(default="latest", env="DURI_VERSION")
    
    # 하위 설정들
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    services: ServiceSettings = Field(default_factory=ServiceSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    backup: BackupSettings = Field(default_factory=BackupSettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 추가 필드 무시
        
    @validator('env')
    def validate_env(cls, v):
        allowed_envs = ['dev', 'staging', 'prod']
        if v not in allowed_envs:
            raise ValueError(f'env must be one of {allowed_envs}')
        return v
    
    def load_from_json(self, json_path: str) -> None:
        """기존 JSON 설정 파일에서 설정 로드 (호환성 보장)"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # JSON 설정을 현재 설정에 병합
            if 'database' in config_data:
                db_config = config_data['database']
                if 'url' in db_config:
                    # URL에서 개별 필드 추출
                    url = db_config['url']
                    if url.startswith('postgresql://'):
                        parts = url.replace('postgresql://', '').split('@')
                        if len(parts) == 2:
                            user_pass, host_db = parts
                            user, password = user_pass.split(':')
                            host_port, database = host_db.split('/')
                            host, port = host_port.split(':')
                            self.database.host = host
                            self.database.port = int(port)
                            self.database.database = database
                            self.database.user = user
                            self.database.password = password
                
                if 'pool_size' in db_config:
                    self.database.pool_size = db_config['pool_size']
                if 'max_overflow' in db_config:
                    self.database.max_overflow = db_config['max_overflow']
            
            if 'redis' in config_data:
                redis_config = config_data['redis']
                if 'url' in redis_config:
                    url = redis_config['url']
                    if url.startswith('redis://'):
                        # Redis URL 파싱
                        url = url.replace('redis://', '')
                        if '@' in url:
                            auth, rest = url.split('@')
                            if ':' in auth:
                                password = auth.split(':')[1]
                                self.redis.password = password
                            url = rest
                        if '/' in url:
                            host_port, db = url.split('/')
                            self.redis.db = int(db)
                        else:
                            host_port = url
                        if ':' in host_port:
                            host, port = host_port.split(':')
                            self.redis.host = host
                            self.redis.port = int(port)
                
                if 'pool_size' in redis_config:
                    self.redis.pool_size = redis_config['pool_size']
            
            if 'server' in config_data:
                server_config = config_data['server']
                if 'port' in server_config:
                    # 포트에 따라 서비스 타입 추정
                    port = server_config['port']
                    if port == 8080:
                        self.services.core_port = port
                    elif port == 8081:
                        self.services.brain_port = port
                    elif port == 8082:
                        self.services.evolution_port = port
                    elif port == 8083:
                        self.services.control_port = port
                
                if 'debug' in server_config:
                    self.debug = server_config['debug']
            
            if 'logging' in config_data:
                log_config = config_data['logging']
                if 'level' in log_config:
                    self.logging.level = log_config['level']
                if 'format' in log_config:
                    self.logging.format = log_config['format']
                if 'file' in log_config:
                    self.logging.file_path = log_config['file']
                if 'max_size' in log_config:
                    self.logging.max_size = log_config['max_size']
                if 'backup_count' in log_config:
                    self.logging.backup_count = log_config['backup_count']
            
            if 'security' in config_data:
                sec_config = config_data['security']
                if 'api_key' in sec_config:
                    self.security.evolution_api_key = sec_config['api_key']
            
        except Exception as e:
            print(f"Warning: Could not load JSON config from {json_path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환 (기존 코드 호환성)"""
        return {
            'env': self.env,
            'debug': self.debug,
            'version': self.version,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database,
                'user': self.database.user,
                'password': self.database.password,
                'url': self.database.url,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db,
                'password': self.redis.password,
                'url': self.redis.url,
                'pool_size': self.redis.pool_size,
            },
            'services': {
                'core_port': self.services.core_port,
                'brain_port': self.services.brain_port,
                'evolution_port': self.services.evolution_port,
                'control_port': self.services.control_port,
                'core_url': self.services.core_url,
                'brain_url': self.services.brain_url,
                'evolution_url': self.services.evolution_url,
                'control_url': self.services.control_url,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_path': self.logging.file_path,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count,
            },
            'security': {
                'jwt_secret_key': self.security.jwt_secret_key,
                'jwt_algorithm': self.security.jwt_algorithm,
                'jwt_access_token_expire_minutes': self.security.jwt_access_token_expire_minutes,
                'jwt_refresh_token_expire_days': self.security.jwt_refresh_token_expire_days,
                'brain_api_key': self.security.brain_api_key,
                'evolution_api_key': self.security.evolution_api_key,
                'admin_username': self.security.admin_username,
                'admin_password': self.security.admin_password,
                'admin_email': self.security.admin_email,
            },
            'monitoring': {
                'prometheus_url': self.monitoring.prometheus_url,
                'grafana_url': self.monitoring.grafana_url,
                'grafana_user': self.monitoring.grafana_user,
                'grafana_password': self.monitoring.grafana_password,
            },
            'backup': {
                'enabled': self.backup.enabled,
                'schedule': self.backup.schedule,
                'retention_days': self.backup.retention_days,
                'path': self.backup.path,
            },
        }


# 전역 설정 인스턴스
settings = DuRiSettings()

# 기존 JSON 설정 파일들 자동 로드 (호환성 보장)
config_paths = [
    "config/config_app.json",
    "config/core/app.json", 
    "config/core_app.json",
    "config/common/config.py",
    "duri_common/config/config.py"
]

for config_path in config_paths:
    if Path(config_path).exists():
        settings.load_from_json(config_path)
        break  # 첫 번째로 찾은 설정 파일만 로드
