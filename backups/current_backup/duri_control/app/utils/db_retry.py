import time
import logging
import psycopg2
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class DatabaseRetryManager:
    """데이터베이스 연결 재시도 관리자"""
    
    def __init__(self, max_retries: int = 30, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def wait_for_postgres(self, db_config: Dict[str, Any]) -> bool:
        """PostgreSQL 연결 가능할 때까지 대기"""
        logger.info("🔄 PostgreSQL 연결 대기 중...")
        
        for attempt in range(self.max_retries):
            try:
                conn = psycopg2.connect(**db_config)
                conn.close()
                logger.info("✅ PostgreSQL 연결 성공")
                return True
            except Exception as e:
                logger.warning(f"⏳ PostgreSQL 연결 시도 {attempt + 1}/{self.max_retries} 실패: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        logger.error(f"❌ PostgreSQL 연결 실패 (최대 {self.max_retries}회 시도)")
        return False
    
    def retry_on_db_error(self, max_retries: int = 3, retry_delay: float = 1.0):
        """데이터베이스 오류 시 재시도 데코레이터"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except psycopg2.OperationalError as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"DB 연결 오류, {retry_delay}초 후 재시도 ({attempt + 1}/{max_retries}): {e}")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"DB 연결 최종 실패: {e}")
                            raise
                    except Exception as e:
                        logger.error(f"예상치 못한 DB 오류: {e}")
                        raise
            return wrapper
        return decorator

# 전역 인스턴스
db_retry_manager = DatabaseRetryManager()

def wait_for_postgres(db_config: Dict[str, Any]) -> bool:
    """PostgreSQL 연결 대기 (편의 함수)"""
    return db_retry_manager.wait_for_postgres(db_config)

def retry_on_db_error(max_retries: int = 3, retry_delay: float = 1.0):
    """DB 오류 재시도 데코레이터 (편의 함수)"""
    return db_retry_manager.retry_on_db_error(max_retries, retry_delay) 