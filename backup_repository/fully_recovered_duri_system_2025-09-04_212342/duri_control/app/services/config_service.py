import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from ..models.config_model import (
    ServiceConfig, 
    ConfigUpdateRequest, 
    ConfigResponse, 
    ConfigListResponse,
    ConfigValidationResponse,
    DEFAULT_SERVICE_CONFIGS
)
from .config_backup_service import ConfigBackupService
from ..utils.validation import config_validator

logger = logging.getLogger(__name__)


class ConfigService:
    """설정 관리 서비스"""
    
    def __init__(self):
        self.db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        self._init_database()
        self.backup_service = ConfigBackupService(self.db_config)
    
    def _get_connection(self):
        """데이터베이스 연결 획득"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    def _init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 설정 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS service_configs (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) UNIQUE NOT NULL,
                    config_data JSONB NOT NULL,
                    version VARCHAR(20) DEFAULT '1.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_service_configs_name 
                ON service_configs(service_name)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("설정 데이터베이스 초기화 완료")
            
            # 기본 설정 데이터 삽입
            self._insert_default_configs()
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def _insert_default_configs(self):
        """기본 설정 데이터 삽입"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for service_name, config in DEFAULT_SERVICE_CONFIGS.items():
                # 기존 설정이 있는지 확인
                cursor.execute(
                    "SELECT id FROM service_configs WHERE service_name = %s",
                    (service_name,)
                )
                
                if not cursor.fetchone():
                    # 기본 설정 삽입
                    cursor.execute("""
                        INSERT INTO service_configs (service_name, config_data, version)
                        VALUES (%s, %s, %s)
                    """, (
                        service_name,
                        json.dumps(config.dict()),
                        "1.0"
                    ))
                    logger.info(f"기본 설정 삽입 완료: {service_name}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"기본 설정 삽입 실패: {e}")
            raise
    
    def get_service_config(self, service_name: str) -> Optional[ConfigResponse]:
        """서비스 설정 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT service_name, config_data, version, updated_at
                FROM service_configs 
                WHERE service_name = %s
            """, (service_name,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                config_data = result['config_data']
                config = ServiceConfig(**config_data)
                
                return ConfigResponse(
                    service_name=result['service_name'],
                    config=config,
                    last_updated=result['updated_at'],
                    version=result['version']
                )
            else:
                # 기본 설정 반환
                if service_name in DEFAULT_SERVICE_CONFIGS:
                    default_config = DEFAULT_SERVICE_CONFIGS[service_name]
                    return ConfigResponse(
                        service_name=service_name,
                        config=default_config,
                        last_updated=datetime.now(),
                        version="1.0"
                    )
                else:
                    logger.warning(f"알 수 없는 서비스: {service_name}")
                    return None
                    
        except Exception as e:
            logger.error(f"설정 조회 실패 ({service_name}): {e}")
            raise
    
    def update_service_config(self, service_name: str, update_data: ConfigUpdateRequest) -> Optional[ConfigResponse]:
        """서비스 설정 업데이트 (백업 및 검증 포함)"""
        backup_id = None
        
        try:
            # 1. 기존 설정 조회
            current_config = self.get_service_config(service_name)
            if not current_config:
                logger.error(f"설정을 찾을 수 없음: {service_name}")
                return None
            
            # 2. 백업 생성
            current_dict = current_config.config.dict()
            backup_id = self.backup_service.create_backup(
                service_name, 
                current_dict, 
                reason="설정 변경",
                created_by="system"
            )
            logger.info(f"백업 생성 완료: {service_name} (ID: {backup_id})")
            
            # 3. 업데이트할 데이터 준비
            update_dict = update_data.dict(exclude_unset=True)
            updated_dict = {**current_dict, **update_dict}
            
            # 커스텀 설정 병합
            if 'custom_config' in update_dict and 'custom_config' in current_dict:
                updated_dict['custom_config'] = {
                    **current_dict['custom_config'],
                    **update_dict['custom_config']
                }
            
            # 4. 강화된 검증 수행
            is_valid, errors, warnings = config_validator.validate_config(service_name, updated_dict)
            
            if not is_valid:
                logger.error(f"설정 검증 실패: {service_name} - {errors}")
                # 백업으로 롤백
                self.backup_service.rollback_to_backup(service_name, backup_id)
                raise ValueError(f"설정 검증 실패: {', '.join(errors)}")
            
            if warnings:
                logger.warning(f"설정 변경 경고: {service_name} - {warnings}")
            
            # 5. 새로운 설정 객체 생성
            new_config = ServiceConfig(**updated_dict)
            
            # 6. 데이터베이스 업데이트
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO service_configs (service_name, config_data, version, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_name) 
                DO UPDATE SET 
                    config_data = EXCLUDED.config_data,
                    version = EXCLUDED.version,
                    updated_at = EXCLUDED.updated_at
            """, (
                service_name,
                json.dumps(new_config.dict()),
                "1.1",
                datetime.now()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"설정 업데이트 완료: {service_name}")
            
            # 7. 업데이트된 설정 반환
            return self.get_service_config(service_name)
            
        except Exception as e:
            logger.error(f"설정 업데이트 실패 ({service_name}): {e}")
            
            # 실패 시 자동 롤백
            if backup_id:
                try:
                    self.backup_service.rollback_to_backup(service_name, backup_id)
                    logger.info(f"자동 롤백 완료: {service_name}")
                except Exception as rollback_error:
                    logger.error(f"롤백 실패: {service_name} - {rollback_error}")
            
            raise
    
    def update_service_config_without_backup(self, service_name: str, update_data: ConfigUpdateRequest) -> Optional[ConfigResponse]:
        """서비스 설정 업데이트 (백업 없이)"""
        try:
            current_config = self.get_service_config(service_name)
            if not current_config:
                logger.error(f"설정을 찾을 수 없음: {service_name}")
                return None
            
            current_dict = current_config.config.dict()
            update_dict = update_data.dict(exclude_unset=True)
            updated_dict = {**current_dict, **update_dict}
            
            if 'custom_config' in update_dict and 'custom_config' in current_dict:
                updated_dict['custom_config'] = {
                    **current_dict['custom_config'],
                    **update_dict['custom_config']
                }
            
            new_config = ServiceConfig(**updated_dict)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO service_configs (service_name, config_data, version, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_name) 
                DO UPDATE SET 
                    config_data = EXCLUDED.config_data,
                    version = EXCLUDED.version,
                    updated_at = EXCLUDED.updated_at
            """, (
                service_name,
                json.dumps(new_config.dict()),
                "1.1",
                datetime.now()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"설정 업데이트 완료 (백업 없이): {service_name}")
            return self.get_service_config(service_name)
            
        except Exception as e:
            logger.error(f"설정 업데이트 실패 ({service_name}): {e}")
            raise
    
    def get_all_services(self) -> ConfigListResponse:
        """모든 서비스 목록 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT service_name FROM service_configs ORDER BY service_name")
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            services = [row[0] for row in results]
            
            return ConfigListResponse(
                services=services,
                total_services=len(services)
            )
            
        except Exception as e:
            logger.error(f"서비스 목록 조회 실패: {e}")
            raise
    
    def validate_config(self, service_name: str, config_data: Dict[str, Any]) -> ConfigValidationResponse:
        """설정 유효성 검증 (강화된 검증기 사용)"""
        try:
            # 강화된 검증 수행
            is_valid, errors, warnings = config_validator.validate_config(service_name, config_data)
            
            return ConfigValidationResponse(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"설정 검증 중 오류 발생: {e}")
            return ConfigValidationResponse(
                is_valid=False,
                errors=[f"검증 중 오류 발생: {str(e)}"],
                warnings=[]
            )
            
            if config.retry_count > 10:
                warnings.append("재시도 횟수가 10을 초과합니다")
            
            # 포트 범위 검증
            if config.port and (config.port < 1024 or config.port > 65535):
                errors.append("포트 번호는 1024-65535 범위여야 합니다")
            
            # 로그 레벨 검증
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if config.log_level not in valid_log_levels:
                errors.append(f"유효하지 않은 로그 레벨: {config.log_level}")
            
            return ConfigValidationResponse(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            errors.append(f"설정 검증 실패: {str(e)}")
            return ConfigValidationResponse(
                is_valid=False,
                errors=errors,
                warnings=warnings
            )
    
    def reset_to_default(self, service_name: str) -> Optional[ConfigResponse]:
        """기본 설정으로 초기화"""
        try:
            if service_name not in DEFAULT_SERVICE_CONFIGS:
                logger.error(f"기본 설정이 없는 서비스: {service_name}")
                return None
            
            default_config = DEFAULT_SERVICE_CONFIGS[service_name]
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO service_configs (service_name, config_data, version, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (service_name) 
                DO UPDATE SET 
                    config_data = EXCLUDED.config_data,
                    version = EXCLUDED.version,
                    updated_at = EXCLUDED.updated_at
            """, (
                service_name,
                json.dumps(default_config.dict()),
                "1.0",
                datetime.now()
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"기본 설정으로 초기화 완료: {service_name}")
            
            return self.get_service_config(service_name)
            
        except Exception as e:
            logger.error(f"기본 설정 초기화 실패 ({service_name}): {e}")
            raise
    
    def delete_service_config(self, service_name: str) -> bool:
        """서비스 설정 삭제"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM service_configs WHERE service_name = %s", (service_name,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"설정 삭제 완료: {service_name}")
                return True
            else:
                logger.warning(f"삭제할 설정이 없음: {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"설정 삭제 실패 ({service_name}): {e}")
            raise


# 전역 인스턴스
config_service = ConfigService() 