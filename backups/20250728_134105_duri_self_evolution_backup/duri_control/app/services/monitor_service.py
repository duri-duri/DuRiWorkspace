from datetime import datetime
from typing import Dict, List
from ..models.monitor import ServiceStatus, ServiceInfo, SystemSummary
from ..utils.system_utils import SystemUtils
from duri_common.logger import get_logger

logger = get_logger("duri_control.monitor_service")

class MonitorService:
    """모니터링 서비스 클래스"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        self.service_config = self.system_utils.get_service_config()
        self.container_names = self.system_utils.get_container_names()
    
    def check_all_services(self) -> Dict[str, ServiceInfo]:
        """
        모든 서비스의 헬스 상태 확인
        
        Returns:
            서비스별 상태 정보
        """
        services_info = {}
        
        for service_name, port in self.service_config.items():
            logger.info(f"🔍 {service_name} 서비스 상태 확인 중... (포트: {port})")
            
            # HTTP 헬스 체크
            is_healthy, response_time, error_message = self.system_utils.check_service_health(
                service_name, port
            )
            
            # Docker 컨테이너 상태 확인
            container_name = self.container_names.get(service_name)
            container_running = False
            if container_name:
                container_running = self.system_utils.check_docker_container_status(container_name)
            
            # 상태 결정
            if is_healthy:
                status = ServiceStatus.HEALTHY
            elif container_running:
                status = ServiceStatus.UNHEALTHY
            else:
                status = ServiceStatus.UNKNOWN
            
            services_info[service_name] = ServiceInfo(
                status=status,
                port=port,
                response_time=response_time,
                last_check=datetime.now(),
                error_message=error_message
            )
            
            logger.info(f"✅ {service_name}: {status.value} (응답시간: {response_time:.1f}ms)" if response_time else f"✅ {service_name}: {status.value}")
        
        return services_info
    
    def get_system_summary(self, services_info: Dict[str, ServiceInfo]) -> SystemSummary:
        """
        시스템 전체 요약 정보 생성
        
        Args:
            services_info: 서비스별 상태 정보
            
        Returns:
            시스템 요약 정보
        """
        total_services = len(services_info)
        healthy_services = sum(1 for info in services_info.values() if info.status == ServiceStatus.HEALTHY)
        unhealthy_services = sum(1 for info in services_info.values() if info.status == ServiceStatus.UNHEALTHY)
        unknown_services = sum(1 for info in services_info.values() if info.status == ServiceStatus.UNKNOWN)
        
        # 전체 상태 결정
        if healthy_services == total_services:
            overall_status = ServiceStatus.HEALTHY
        elif healthy_services > 0:
            overall_status = ServiceStatus.UNHEALTHY
        else:
            overall_status = ServiceStatus.UNKNOWN
        
        return SystemSummary(
            total_services=total_services,
            healthy_services=healthy_services,
            unhealthy_services=unhealthy_services,
            unknown_services=unknown_services,
            overall_status=overall_status,
            last_updated=datetime.now()
        )
    
    def get_services_status(self) -> Dict[str, ServiceInfo]:
        """
        서비스 상태 조회 (캐시된 결과 반환)
        
        Returns:
            서비스별 상태 정보
        """
        return self.check_all_services()
    
    def get_system_summary_status(self) -> SystemSummary:
        """
        시스템 요약 상태 조회
        
        Returns:
            시스템 요약 정보
        """
        services_info = self.check_all_services()
        return self.get_system_summary(services_info)


# 전역 인스턴스
monitor_service = MonitorService() 