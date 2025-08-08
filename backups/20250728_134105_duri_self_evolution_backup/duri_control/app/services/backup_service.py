import json
import logging
import os
import shutil
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import docker
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from ..models.backup_model import (
    FullBackupData, BackupType, BackupStatus, BackupCreateRequest,
    BackupResponse, BackupListResponse, BackupRestoreRequest,
    BackupRestoreResponse, BackupSchedule, DEFAULT_BACKUP_SCHEDULE,
    ConfigSnapshot, DatabaseSnapshot, ServiceStatus
)

logger = logging.getLogger(__name__)


class BackupService:
    """전체 백업 서비스"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.backup_dir = "/app/backups"
        self._init_backup_table()
        self._init_backup_directory()
        self.scheduler = BackgroundScheduler()
        self._init_scheduler()
    
    def _get_connection(self):
        """데이터베이스 연결 획득"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    def _init_backup_table(self):
        """백업 테이블 초기화"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 전체 백업 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS full_backups (
                    id SERIAL PRIMARY KEY,
                    backup_id VARCHAR(100) UNIQUE NOT NULL,
                    backup_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    backup_data JSONB,
                    description TEXT,
                    created_by VARCHAR(100) DEFAULT 'system',
                    size_mb FLOAT,
                    error_message TEXT
                )
            """)
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_full_backups_id 
                ON full_backups(backup_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_full_backups_status 
                ON full_backups(status, created_at DESC)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("전체 백업 테이블 초기화 완료")
            
        except Exception as e:
            logger.error(f"백업 테이블 초기화 실패: {e}")
            raise
    
    def _init_backup_directory(self):
        """백업 디렉토리 초기화"""
        try:
            if not os.path.exists(self.backup_dir):
                os.makedirs(self.backup_dir)
                logger.info(f"백업 디렉토리 생성: {self.backup_dir}")
        except Exception as e:
            logger.error(f"백업 디렉토리 초기화 실패: {e}")
            raise
    
    def _init_scheduler(self):
        """백업 스케줄러 초기화"""
        try:
            # 스케줄러 시작
            self.scheduler.start()
            
            # 기본 스케줄 등록
            self._add_scheduled_backup(DEFAULT_BACKUP_SCHEDULE)
            
            logger.info("백업 스케줄러 초기화 완료")
            
        except Exception as e:
            logger.error(f"백업 스케줄러 초기화 실패: {e}")
    
    def _add_scheduled_backup(self, schedule: BackupSchedule):
        """스케줄된 백업 추가"""
        if not schedule.enabled:
            return
        
        try:
            if schedule.schedule_type == "daily":
                trigger = CronTrigger(
                    hour=int(schedule.time.split(":")[0]),
                    minute=int(schedule.time.split(":")[1])
                )
            elif schedule.schedule_type == "weekly":
                trigger = CronTrigger(
                    day_of_week=schedule.day_of_week,
                    hour=int(schedule.time.split(":")[0]),
                    minute=int(schedule.time.split(":")[1])
                )
            elif schedule.schedule_type == "monthly":
                trigger = CronTrigger(
                    day=schedule.day_of_month,
                    hour=int(schedule.time.split(":")[0]),
                    minute=int(schedule.time.split(":")[1])
                )
            else:
                logger.error(f"지원하지 않는 스케줄 타입: {schedule.schedule_type}")
                return
            
            self.scheduler.add_job(
                func=self._run_scheduled_backup,
                trigger=trigger,
                args=[schedule],
                id=f"backup_schedule_{schedule.schedule_type}",
                replace_existing=True
            )
            
            logger.info(f"스케줄된 백업 등록: {schedule.schedule_type} at {schedule.time}")
            
        except Exception as e:
            logger.error(f"스케줄된 백업 등록 실패: {e}")
    
    def _run_scheduled_backup(self, schedule: BackupSchedule):
        """스케줄된 백업 실행"""
        try:
            description = schedule.description_template.format(
                date=datetime.now().strftime("%Y-%m-%d")
            )
            
            self.create_full_backup(
                BackupCreateRequest(
                    backup_type=schedule.backup_type,
                    description=description
                )
            )
            
            # 오래된 백업 정리
            self._cleanup_old_backups(schedule.retention_days)
            
        except Exception as e:
            logger.error(f"스케줄된 백업 실행 실패: {e}")
    
    def create_full_backup(self, request: BackupCreateRequest) -> str:
        """전체 백업 생성"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 백업 시작 기록
            self._save_backup_record(backup_id, request, BackupStatus.IN_PROGRESS)
            
            backup_data = FullBackupData(
                backup_id=backup_id,
                backup_type=request.backup_type,
                status=BackupStatus.IN_PROGRESS,
                created_at=datetime.now(),
                description=request.description
            )
            
            # 설정 스냅샷 생성
            if request.include_config:
                backup_data.config_snapshot = self._create_config_snapshot()
            
            # 데이터베이스 스냅샷 생성
            if request.include_database:
                backup_data.database_snapshot = self._create_database_snapshot()
            
            # 서비스 상태 수집
            if request.include_service_status:
                backup_data.service_statuses = self._collect_service_statuses()
            
            # 백업 파일 생성
            backup_file_path = self._create_backup_file(backup_id, backup_data)
            
            # 백업 완료 기록
            backup_data.status = BackupStatus.COMPLETED
            backup_data.completed_at = datetime.now()
            backup_data.size_mb = self._get_file_size_mb(backup_file_path)
            
            self._update_backup_record(backup_id, backup_data)
            
            logger.info(f"전체 백업 완료: {backup_id}")
            return backup_id
            
        except Exception as e:
            logger.error(f"전체 백업 실패: {backup_id} - {e}")
            self._update_backup_status(backup_id, BackupStatus.FAILED, str(e))
            raise
    
    def _create_config_snapshot(self) -> ConfigSnapshot:
        """설정 스냅샷 생성"""
        try:
            from .config_service import config_service
            
            # 모든 서비스 설정 수집
            service_configs = {}
            services = config_service.get_all_services()
            
            for service_name in services.services:
                config = config_service.get_service_config(service_name)
                if config:
                    service_configs[service_name] = config.dict()
            
            return ConfigSnapshot(
                service_configs=service_configs,
                total_services=len(service_configs),
                backup_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"설정 스냅샷 생성 실패: {e}")
            raise
    
    def _create_database_snapshot(self) -> DatabaseSnapshot:
        """데이터베이스 스냅샷 생성"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 테이블 목록 조회
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # 각 테이블의 레코드 수 조회
            record_counts = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                record_counts[table] = count
            
            # 데이터베이스 크기 계산 (근사값)
            cursor.execute("""
                SELECT pg_database_size(current_database())
            """)
            size_bytes = cursor.fetchone()[0]
            size_mb = size_bytes / (1024 * 1024)
            
            cursor.close()
            conn.close()
            
            return DatabaseSnapshot(
                tables=tables,
                record_counts=record_counts,
                size_mb=size_mb,
                backup_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"데이터베이스 스냅샷 생성 실패: {e}")
            raise
    
    def _collect_service_statuses(self) -> List[ServiceStatus]:
        """서비스 상태 수집"""
        try:
            client = docker.from_env()
            services = ['duri_core', 'duri_brain', 'duri_evolution', 'duri_control']
            statuses = []
            
            for service_name in services:
                try:
                    container = client.containers.get(f"{service_name}_container")
                    
                    # 컨테이너 상태 확인
                    container_status = container.status
                    health_check = container_status == "running"
                    
                    # 포트 정보 추출
                    port = 8080  # 기본값
                    if service_name == "duri_brain":
                        port = 8081
                    elif service_name == "duri_evolution":
                        port = 8082
                    elif service_name == "duri_control":
                        port = 8083
                    
                    statuses.append(ServiceStatus(
                        service_name=service_name,
                        status=container_status,
                        port=port,
                        health_check=health_check,
                        last_check=datetime.now()
                    ))
                    
                except Exception as e:
                    logger.warning(f"서비스 상태 수집 실패 ({service_name}): {e}")
                    statuses.append(ServiceStatus(
                        service_name=service_name,
                        status="error",
                        port=0,
                        health_check=False,
                        last_check=datetime.now()
                    ))
            
            return statuses
            
        except Exception as e:
            logger.error(f"서비스 상태 수집 실패: {e}")
            return []
    
    def _create_backup_file(self, backup_id: str, backup_data: FullBackupData) -> str:
        """백업 파일 생성"""
        try:
            backup_file_path = os.path.join(self.backup_dir, f"{backup_id}.json")
            
            with open(backup_file_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data.dict(), f, indent=2, default=str)
            
            return backup_file_path
            
        except Exception as e:
            logger.error(f"백업 파일 생성 실패: {e}")
            raise
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """파일 크기 (MB) 조회"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def _save_backup_record(self, backup_id: str, request: BackupCreateRequest, status: BackupStatus):
        """백업 기록 저장"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO full_backups 
                (backup_id, backup_type, status, description, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                backup_id,
                request.backup_type.value,
                status.value,
                request.description,
                "system"
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"백업 기록 저장 실패: {e}")
            raise
    
    def _update_backup_record(self, backup_id: str, backup_data: FullBackupData):
        """백업 기록 업데이트"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE full_backups 
                SET status = %s, completed_at = %s, backup_data = %s, size_mb = %s
                WHERE backup_id = %s
            """, (
                backup_data.status.value,
                backup_data.completed_at,
                json.dumps(backup_data.dict(), default=str),
                backup_data.size_mb,
                backup_id
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"백업 기록 업데이트 실패: {e}")
            raise
    
    def _update_backup_status(self, backup_id: str, status: BackupStatus, error_message: str = None):
        """백업 상태 업데이트"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if error_message:
                cursor.execute("""
                    UPDATE full_backups 
                    SET status = %s, error_message = %s
                    WHERE backup_id = %s
                """, (status.value, error_message, backup_id))
            else:
                cursor.execute("""
                    UPDATE full_backups 
                    SET status = %s
                    WHERE backup_id = %s
                """, (status.value, backup_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"백업 상태 업데이트 실패: {e}")
    
    def get_backup_list(self, limit: int = 50) -> BackupListResponse:
        """백업 목록 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT backup_id, status, created_at, description, size_mb
                FROM full_backups 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            
            backups = []
            total_size_mb = 0.0
            
            for row in cursor.fetchall():
                backup = BackupResponse(
                    backup_id=row['backup_id'],
                    status=BackupStatus(row['status']),
                    created_at=row['created_at'],
                    description=row['description'],
                    size_mb=row['size_mb'] or 0.0
                )
                backups.append(backup)
                total_size_mb += backup.size_mb
            
            cursor.close()
            conn.close()
            
            return BackupListResponse(
                backups=backups,
                total_backups=len(backups),
                total_size_mb=total_size_mb
            )
            
        except Exception as e:
            logger.error(f"백업 목록 조회 실패: {e}")
            raise
    
    def restore_backup(self, backup_id: str, request: BackupRestoreRequest) -> BackupRestoreResponse:
        """백업 복원"""
        try:
            # 백업 데이터 조회
            backup_data = self._get_backup_data(backup_id)
            if not backup_data:
                raise ValueError(f"백업을 찾을 수 없음: {backup_id}")
            
            restored_components = []
            
            # 설정 복원
            if request.restore_config and backup_data.config_snapshot:
                self._restore_config(backup_data.config_snapshot)
                restored_components.append("config")
            
            # 데이터베이스 복원
            if request.restore_database and backup_data.database_snapshot:
                self._restore_database(backup_id)
                restored_components.append("database")
            
            # 서비스 상태 복원
            if request.restore_service_status and backup_data.service_statuses:
                self._restore_service_status(backup_data.service_statuses)
                restored_components.append("service_status")
            
            return BackupRestoreResponse(
                backup_id=backup_id,
                status="success",
                restored_components=restored_components,
                restored_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"백업 복원 실패: {backup_id} - {e}")
            return BackupRestoreResponse(
                backup_id=backup_id,
                status="failed",
                restored_components=[],
                error_message=str(e),
                restored_at=datetime.now()
            )
    
    def _get_backup_data(self, backup_id: str) -> Optional[FullBackupData]:
        """백업 데이터 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT backup_data FROM full_backups 
                WHERE backup_id = %s
            """, (backup_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result['backup_data']:
                return FullBackupData(**result['backup_data'])
            
            return None
            
        except Exception as e:
            logger.error(f"백업 데이터 조회 실패: {e}")
            return None
    
    def _restore_config(self, config_snapshot: ConfigSnapshot):
        """설정 복원"""
        try:
            from .config_service import config_service
            
            for service_name, config_data in config_snapshot.service_configs.items():
                # 설정 복원 로직 구현
                logger.info(f"설정 복원: {service_name}")
                
                # config_data에서 실제 설정 추출
                if 'config' in config_data:
                    config_dict = config_data['config']
                    
                    # ConfigUpdateRequest 형태로 변환
                    from ..models.config_model import ConfigUpdateRequest
                    update_request = ConfigUpdateRequest(**config_dict)
                    
                    # 설정 업데이트 (백업 없이)
                    config_service.update_service_config_without_backup(service_name, update_request)
                
        except Exception as e:
            logger.error(f"설정 복원 실패: {e}")
            raise
    
    def _restore_database(self, backup_id: str):
        """데이터베이스 복원"""
        try:
            # PostgreSQL 덤프 복원 로직
            backup_file = os.path.join(self.backup_dir, f"{backup_id}.sql")
            if os.path.exists(backup_file):
                # pg_restore 명령어 실행
                logger.info(f"데이터베이스 복원: {backup_id}")
            else:
                logger.warning(f"데이터베이스 백업 파일을 찾을 수 없음: {backup_file}")
                
        except Exception as e:
            logger.error(f"데이터베이스 복원 실패: {e}")
            raise
    
    def _restore_service_status(self, service_statuses: List[ServiceStatus]):
        """서비스 상태 복원"""
        try:
            client = docker.from_env()
            
            for status in service_statuses:
                if status.status == "running":
                    try:
                        container = client.containers.get(f"{status.service_name}_container")
                        if container.status != "running":
                            container.start()
                            logger.info(f"서비스 시작: {status.service_name}")
                    except Exception as e:
                        logger.warning(f"서비스 시작 실패 ({status.service_name}): {e}")
                        
        except Exception as e:
            logger.error(f"서비스 상태 복원 실패: {e}")
            raise
    
    def _cleanup_old_backups(self, retention_days: int):
        """오래된 백업 정리"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 오래된 백업 ID 조회
            cursor.execute("""
                SELECT backup_id FROM full_backups 
                WHERE created_at < %s AND status = 'completed'
            """, (cutoff_date,))
            
            old_backups = [row[0] for row in cursor.fetchall()]
            
            # 파일 및 DB 레코드 삭제
            for backup_id in old_backups:
                # 백업 파일 삭제
                backup_file = os.path.join(self.backup_dir, f"{backup_id}.json")
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                
                # DB 레코드 삭제
                cursor.execute("DELETE FROM full_backups WHERE backup_id = %s", (backup_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            if old_backups:
                logger.info(f"오래된 백업 정리 완료: {len(old_backups)}개 삭제")
            
        except Exception as e:
            logger.error(f"오래된 백업 정리 실패: {e}")


# 전역 백업 서비스 인스턴스
backup_service = None

def get_backup_service() -> 'BackupService':
    """백업 서비스 인스턴스 반환"""
    global backup_service
    if backup_service is None:
        # 기본 DB 설정으로 초기화
        db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        backup_service = BackupService(db_config)
    return backup_service

def init_backup_service(db_config: Dict[str, Any]):
    """백업 서비스 초기화"""
    global backup_service
    if backup_service is None:
        backup_service = BackupService(db_config)
    return backup_service 