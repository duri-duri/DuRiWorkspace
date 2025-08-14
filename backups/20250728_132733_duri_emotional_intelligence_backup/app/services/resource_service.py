from datetime import datetime
from typing import List
from ..models.monitor import SystemResources, ContainerResourceInfo
from ..utils.resource_utils import ResourceUtils
from duri_common.logger import get_logger

logger = get_logger("duri_control.resource_service")

class ResourceService:
    """리소스 모니터링 서비스 클래스"""
    
    def __init__(self):
        self.resource_utils = ResourceUtils()
    
    def get_system_resources(self) -> SystemResources:
        """
        시스템 전체 리소스 정보 수집
        
        Returns:
            시스템 리소스 정보
        """
        logger.info("🔍 시스템 리소스 정보 수집 중...")
        
        try:
            # CPU 정보 수집
            cpu_info = self.resource_utils.get_cpu_info()
            logger.info(f"✅ CPU: {cpu_info.usage_percent:.1f}% 사용률 ({cpu_info.cores}코어)")
            
            # 메모리 정보 수집
            memory_info = self.resource_utils.get_memory_info()
            logger.info(f"✅ 메모리: {memory_info.usage_percent:.1f}% 사용률 ({memory_info.used_gb:.1f}GB/{memory_info.total_gb:.1f}GB)")
            
            # 디스크 정보 수집
            disks_info = self.resource_utils.get_disk_info()
            logger.info(f"✅ 디스크: {len(disks_info)}개 파티션")
            
            # 네트워크 정보 수집
            network_info = self.resource_utils.get_network_info()
            logger.info(f"✅ 네트워크: {network_info.interface} 인터페이스")
            
            return SystemResources(
                cpu=cpu_info,
                memory=memory_info,
                disks=disks_info,
                network=network_info,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ 시스템 리소스 수집 실패: {e}")
            # 기본값 반환
            return SystemResources(
                cpu=self.resource_utils.get_cpu_info(),
                memory=self.resource_utils.get_memory_info(),
                disks=[],
                network=self.resource_utils.get_network_info(),
                timestamp=datetime.now()
            )
    
    def get_container_resources(self) -> List[ContainerResourceInfo]:
        """
        컨테이너별 리소스 정보 수집
        
        Returns:
            컨테이너 리소스 정보 목록
        """
        logger.info("🔍 컨테이너 리소스 정보 수집 중...")
        
        try:
            containers = self.resource_utils.get_container_stats()
            logger.info(f"✅ {len(containers)}개 컨테이너 정보 수집 완료")
            
            # DuRi 관련 컨테이너만 필터링 (선택사항)
            duri_containers = [
                container for container in containers
                if any(name in container.container_name.lower() for name in ['duri', 'postgres', 'redis'])
            ]
            
            return duri_containers
            
        except Exception as e:
            logger.error(f"❌ 컨테이너 리소스 수집 실패: {e}")
            return []
    
    def get_resources_summary(self) -> dict:
        """
        리소스 요약 정보 생성
        
        Returns:
            리소스 요약 정보
        """
        try:
            system_resources = self.get_system_resources()
            containers = self.get_container_resources()
            
            # 전체 컨테이너 CPU/메모리 사용률 계산
            total_container_cpu = sum(c.cpu_percent for c in containers)
            total_container_memory = sum(c.memory_usage_mb for c in containers)
            
            return {
                "system": {
                    "cpu_usage": f"{system_resources.cpu.usage_percent:.1f}%",
                    "memory_usage": f"{system_resources.memory.usage_percent:.1f}%",
                    "disk_count": len(system_resources.disks)
                },
                "containers": {
                    "total_count": len(containers),
                    "total_cpu_usage": f"{total_container_cpu:.1f}%",
                    "total_memory_usage": f"{total_container_memory:.1f}MB"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 리소스 요약 생성 실패: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# 전역 인스턴스
resource_service = ResourceService() 