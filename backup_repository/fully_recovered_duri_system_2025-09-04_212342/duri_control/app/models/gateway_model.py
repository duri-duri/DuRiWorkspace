from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    """서비스 상태"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class GatewayHealthResponse(BaseModel):
    """게이트웨이 헬스 응답"""
    overall_status: ServiceStatus
    services: Dict[str, Dict[str, Any]]
    timestamp: datetime
    gateway_version: str = "1.0.0"

class ProxyRequest(BaseModel):
    """프록시 요청"""
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    timeout: int = 30

class ProxyResponse(BaseModel):
    """프록시 응답"""
    status_code: int
    headers: Dict[str, str]
    body: Any
    response_time_ms: float
    service_name: str
    original_path: str

class ServiceConfig(BaseModel):
    """서비스 설정"""
    name: str
    host: str
    port: int
    health_path: str = "/health"
    timeout: int = 30
    retries: int = 3
    enabled: bool = True

class GatewayConfig(BaseModel):
    """게이트웨이 설정"""
    services: Dict[str, ServiceConfig]
    default_timeout: int = 30
    default_retries: int = 3
    enable_caching: bool = True
    cache_ttl: int = 300  # 5분

# 기본 서비스 설정
DEFAULT_SERVICES = {
    "core": ServiceConfig(
        name="duri_core",
        host="duri_core",
        port=8080,
        health_path="/health"
    ),
    "brain": ServiceConfig(
        name="duri_brain", 
        host="duri_brain",
        port=8081,
        health_path="/health"
    ),
    "evolution": ServiceConfig(
        name="duri_evolution",
        host="duri_evolution", 
        port=8082,
        health_path="/health"
    ),
    "control": ServiceConfig(
        name="duri_control",
        host="duri_control",
        port=8083,
        health_path="/health"
    )
} 