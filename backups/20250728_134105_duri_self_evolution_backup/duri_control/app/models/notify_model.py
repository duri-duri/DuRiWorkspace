from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """알림 타입 정의"""
    SLACK = "slack"
    EMAIL = "email"
    LOG = "log"
    WEBHOOK = "webhook"


class AlertLevel(str, Enum):
    """알림 레벨 정의"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ServiceStatus(str, Enum):
    """서비스 상태 정의"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class ResourceType(str, Enum):
    """리소스 타입 정의"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class NotificationConfig(BaseModel):
    """알림 설정"""
    # 기본 설정
    enabled: bool = True
    notification_types: List[NotificationType] = [NotificationType.LOG]
    
    # Slack 설정
    slack_webhook_url: Optional[HttpUrl] = None
    slack_channel: Optional[str] = "#general"
    slack_username: Optional[str] = "DuRi Alert Bot"
    
    # 이메일 설정
    email_smtp_server: Optional[str] = None
    email_smtp_port: Optional[int] = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_recipients: List[str] = []
    email_from: Optional[str] = None
    
    # 임계값 설정
    thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "cpu": 80.0,
            "memory": 85.0,
            "disk": 90.0,
            "network": 70.0
        }
    )
    
    # 서비스 상태 알림 설정
    service_status_alerts: bool = True
    resource_alerts: bool = True
    error_alerts: bool = True
    
    # 알림 간격 설정 (초)
    alert_cooldown: int = 300  # 5분
    max_alerts_per_hour: int = 10


class AlertMessage(BaseModel):
    """알림 메시지"""
    id: str
    timestamp: datetime
    level: AlertLevel
    title: str
    message: str
    service_name: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationRequest(BaseModel):
    """알림 요청"""
    level: AlertLevel
    title: str
    message: str
    service_name: Optional[str] = None
    resource_type: Optional[ResourceType] = None
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NotificationResponse(BaseModel):
    """알림 응답"""
    success: bool
    message: str
    sent_to: List[str]
    failed_to: List[str]
    timestamp: datetime


class NotificationStatus(BaseModel):
    """알림 상태"""
    enabled: bool
    active_config: Optional[NotificationConfig] = None
    total_alerts_sent: int
    alerts_last_hour: int
    last_alert_time: Optional[datetime] = None
    cooldown_active: bool
    cooldown_remaining: Optional[int] = None


class ServiceAlert(BaseModel):
    """서비스 알림"""
    service_name: str
    previous_status: ServiceStatus
    current_status: ServiceStatus
    timestamp: datetime
    details: str


class ResourceAlert(BaseModel):
    """리소스 알림"""
    resource_type: ResourceType
    current_value: float
    threshold_value: float
    service_name: Optional[str] = None
    timestamp: datetime
    details: str


class AlertHistory(BaseModel):
    """알림 히스토리"""
    alerts: List[AlertMessage]
    total_alerts: int
    alerts_by_level: Dict[AlertLevel, int]
    alerts_by_service: Dict[str, int]


# 기본 알림 설정
DEFAULT_NOTIFICATION_CONFIG = NotificationConfig(
    enabled=True,
    notification_types=[NotificationType.LOG],
    thresholds={
        "cpu": 80.0,
        "memory": 85.0,
        "disk": 90.0,
        "network": 70.0
    },
    service_status_alerts=True,
    resource_alerts=True,
    error_alerts=True,
    alert_cooldown=300,
    max_alerts_per_hour=10
) 