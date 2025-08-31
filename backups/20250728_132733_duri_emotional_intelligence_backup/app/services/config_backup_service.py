import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

logger = logging.getLogger(__name__)


class ConfigBackupService:
    """설정 백업 및 롤백 서비스"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self._init_backup_table()
    
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
            
            # 백업 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_backups (
                    id SERIAL PRIMARY KEY,
                    service_name VARCHAR(100) NOT NULL,
                    backup_data JSONB NOT NULL,
                    backup_reason VARCHAR(255),
                    created_by VARCHAR(100) DEFAULT 'system',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_config_backups_service 
                ON config_backups(service_name, created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_config_backups_active 
                ON config_backups(service_name, is_active)
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("백업 테이블 초기화 완료")
            
        except Exception as e:
            logger.error(f"백업 테이블 초기화 실패: {e}")
            raise
    
    def create_backup(self, service_name: str, config_data: Dict[str, Any], 
                     reason: str = "설정 변경", created_by: str = "system") -> int:
        """설정 백업 생성"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 이전 백업들을 비활성화
            cursor.execute("""
                UPDATE config_backups 
                SET is_active = FALSE 
                WHERE service_name = %s
            """, (service_name,))
            
            # 새 백업 생성
            cursor.execute("""
                INSERT INTO config_backups 
                (service_name, backup_data, backup_reason, created_by)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                service_name,
                json.dumps(config_data),
                reason,
                created_by
            ))
            
            backup_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"백업 생성 완료: {service_name} (ID: {backup_id})")
            return backup_id
            
        except Exception as e:
            logger.error(f"백업 생성 실패: {e}")
            raise
    
    def get_latest_backup(self, service_name: str) -> Optional[Dict[str, Any]]:
        """최신 백업 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM config_backups 
                WHERE service_name = %s AND is_active = TRUE
                ORDER BY created_at DESC 
                LIMIT 1
            """, (service_name,))
            
            backup = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if backup:
                backup_dict = dict(backup)
                # backup_data가 이미 딕셔너리인지 확인
                if isinstance(backup_dict['backup_data'], str):
                    backup_dict['backup_data'] = json.loads(backup_dict['backup_data'])
                return backup_dict
            
            return None
            
        except Exception as e:
            logger.error(f"백업 조회 실패: {e}")
            raise
    
    def get_backup_history(self, service_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """백업 히스토리 조회"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM config_backups 
                WHERE service_name = %s
                ORDER BY created_at DESC 
                LIMIT %s
            """, (service_name, limit))
            
            backups = cursor.fetchall()
            cursor.close()
            conn.close()
            
            result = []
            for backup in backups:
                backup_dict = dict(backup)
                # backup_data가 이미 딕셔너리인지 확인
                if isinstance(backup_dict['backup_data'], str):
                    backup_dict['backup_data'] = json.loads(backup_dict['backup_data'])
                result.append(backup_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"백업 히스토리 조회 실패: {e}")
            raise
    
    def rollback_to_backup(self, service_name: str, backup_id: Optional[int] = None) -> bool:
        """백업으로 롤백"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 롤백할 백업 조회
            if backup_id:
                cursor.execute("""
                    SELECT backup_data FROM config_backups 
                    WHERE id = %s AND service_name = %s
                """, (backup_id, service_name))
            else:
                # 최신 백업 사용
                cursor.execute("""
                    SELECT backup_data FROM config_backups 
                    WHERE service_name = %s AND is_active = TRUE
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (service_name,))
            
            backup_result = cursor.fetchone()
            if not backup_result:
                logger.error(f"롤백할 백업을 찾을 수 없음: {service_name}")
                return False
            
            # backup_data가 이미 딕셔너리인지 확인
            if isinstance(backup_result[0], str):
                backup_data = json.loads(backup_result[0])
            else:
                backup_data = backup_result[0]
            
            # 현재 설정을 백업으로 업데이트
            cursor.execute("""
                UPDATE service_configs 
                SET config_data = %s, 
                    updated_at = CURRENT_TIMESTAMP,
                    version = '1.1'
                WHERE service_name = %s
            """, (json.dumps(backup_data), service_name))
            
            if cursor.rowcount == 0:
                logger.error(f"설정 업데이트 실패: {service_name}")
                return False
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"롤백 완료: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"롤백 실패: {e}")
            raise
    
    def cleanup_old_backups(self, service_name: str, keep_count: int = 5) -> int:
        """오래된 백업 정리"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 유지할 백업 수를 제외한 나머지 삭제
            cursor.execute("""
                DELETE FROM config_backups 
                WHERE service_name = %s 
                AND id NOT IN (
                    SELECT id FROM config_backups 
                    WHERE service_name = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                )
            """, (service_name, service_name, keep_count))
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"백업 정리 완료: {service_name} ({deleted_count}개 삭제)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"백업 정리 실패: {e}")
            raise 