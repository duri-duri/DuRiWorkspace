from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class BackupType(str, Enum):
    """백업 타입 정의"""
    FULL = "full"
    CONFIG_ONLY = "config_only"
    DB_ONLY = "db_only"


class BackupStatus(str, Enum):
    """백업 상태 정의"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ServiceStatus(BaseModel):
    """서비스 상태 정보"""
    service_name: str
    status: str  # running, stopped, error
    port: int
    health_check: bool
    last_check: datetime


class DatabaseSnapshot(BaseModel):
    """데이터베이스 스냅샷 정보"""
    tables: List[str]
    record_counts: Dict[str, int]
    size_mb: float
    backup_time: datetime


class ConfigSnapshot(BaseModel):
    """설정 스냅샷 정보"""
    service_configs: Dict[str, Any]
    total_services: int
    backup_time: datetime


class FullBackupData(BaseModel):
    """전체 백업 데이터"""
    backup_id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # 백업 구성 요소
    config_snapshot: Optional[ConfigSnapshot] = None
    database_snapshot: Optional[DatabaseSnapshot] = None
    service_statuses: List[ServiceStatus] = []
    
    # 메타데이터
    description: Optional[str] = None
    created_by: str = "system"
    size_mb: Optional[float] = None
    error_message: Optional[str] = None


class BackupCreateRequest(BaseModel):
    """백업 생성 요청"""
    backup_type: BackupType = BackupType.FULL
    description: Optional[str] = None
    include_config: bool = True
    include_database: bool = True
    include_service_status: bool = True


class BackupResponse(BaseModel):
    """백업 응답"""
    backup_id: str
    status: BackupStatus
    created_at: datetime
    description: Optional[str] = None
    size_mb: Optional[float] = None


class BackupListResponse(BaseModel):
    """백업 목록 응답"""
    backups: List[BackupResponse]
    total_backups: int
    total_size_mb: float


class BackupRestoreRequest(BaseModel):
    """백업 복원 요청"""
    restore_config: bool = True
    restore_database: bool = True
    restore_service_status: bool = False
    force: bool = False


class BackupRestoreResponse(BaseModel):
    """백업 복원 응답"""
    backup_id: str
    status: str  # success, failed
    restored_components: List[str]
    error_message: Optional[str] = None
    restored_at: datetime


class BackupSchedule(BaseModel):
    """백업 스케줄 설정"""
    enabled: bool = True
    schedule_type: str = "daily"  # daily, weekly, monthly
    time: str = "02:00"  # HH:MM
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None  # 1-31
    retention_days: int = 30
    backup_type: BackupType = BackupType.FULL
    description_template: str = "Scheduled backup - {date}"


# 기본 백업 스케줄 설정
DEFAULT_BACKUP_SCHEDULE = BackupSchedule(
    enabled=True,
    schedule_type="daily",
    time="02:00",
    retention_days=30,
    backup_type=BackupType.FULL,
    description_template="Daily scheduled backup - {date}"
) 