import logging
from typing import Dict, Any, List, Callable
from ..utils.db_retry import wait_for_postgres

logger = logging.getLogger(__name__)

class ServiceManager:
    """서비스 초기화 관리자"""
    
    def __init__(self):
        self.db_config = {
            'host': 'duri-postgres',
            'port': 5432,
            'database': 'duri',
            'user': 'duri',
            'password': 'duri'
        }
        self.initialized_services: List[str] = []
        self.service_initializers: Dict[str, Callable] = {}
    
    def register_service(self, service_name: str, initializer: Callable):
        """서비스 초기화 함수 등록"""
        self.service_initializers[service_name] = initializer
        logger.info(f"📝 서비스 등록: {service_name}")
    
    def initialize_all_services(self) -> bool:
        """모든 서비스 초기화 (DB 연결 대기 후)"""
        try:
            # 1. PostgreSQL 연결 대기
            logger.info("🚀 서비스 초기화 시작...")
            if not wait_for_postgres(self.db_config):
                logger.error("❌ PostgreSQL 연결 실패로 서비스 초기화 중단")
                return False
            
            # 2. 서비스들 순차 초기화
            for service_name, initializer in self.service_initializers.items():
                try:
                    logger.info(f"🔧 {service_name} 초기화 중...")
                    initializer()
                    self.initialized_services.append(service_name)
                    logger.info(f"✅ {service_name} 초기화 완료")
                except Exception as e:
                    logger.error(f"❌ {service_name} 초기화 실패: {e}")
                    return False
            
            logger.info(f"🎉 모든 서비스 초기화 완료: {', '.join(self.initialized_services)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 서비스 초기화 중 오류 발생: {e}")
            return False
    
    def get_initialization_status(self) -> Dict[str, Any]:
        """초기화 상태 반환"""
        return {
            "total_services": len(self.service_initializers),
            "initialized_services": self.initialized_services,
            "pending_services": [
                name for name in self.service_initializers.keys() 
                if name not in self.initialized_services
            ]
        }

# 전역 서비스 매니저 인스턴스
service_manager = ServiceManager()

def get_service_manager() -> ServiceManager:
    """서비스 매니저 인스턴스 반환"""
    return service_manager 