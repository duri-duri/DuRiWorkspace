#!/usr/bin/env python3
"""
DuRi All-in-One Health Monitor
통합 모드에서 모든 서비스의 상태를 모니터링
"""
import time
import requests
import logging
import json
from datetime import datetime
from typing import Dict, List, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DuRiHealthMonitor:
    """DuRi 서비스 헬스 모니터"""
    
    def __init__(self):
        self.services = {
            "duri_core": {
                "url": "http://localhost:8080/health",
                "name": "DuRi Core",
                "port": 8080
            },
            "duri_brain": {
                "url": "http://localhost:8081/health",
                "name": "DuRi Brain",
                "port": 8081
            },
            "duri_evolution": {
                "url": "http://localhost:8082/health",
                "name": "DuRi Evolution",
                "port": 8082
            },
            "duri_control": {
                "url": "http://localhost:8083/health",
                "name": "DuRi Control",
                "port": 8083
            }
        }
        
        self.health_status = {}
        self.start_time = datetime.now()
    
    def check_service_health(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """개별 서비스 헬스 체크"""
        try:
            response = requests.get(service_config["url"], timeout=5)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "last_check": datetime.now().isoformat(),
                    "uptime": (datetime.now() - self.start_time).total_seconds()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "last_check": datetime.now().isoformat()
                }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def check_all_services(self) -> Dict[str, Any]:
        """모든 서비스 헬스 체크"""
        logger.info("🔍 모든 DuRi 서비스 헬스 체크 시작")
        
        overall_status = "healthy"
        service_statuses = {}
        
        for service_name, service_config in self.services.items():
            status = self.check_service_health(service_name, service_config)
            service_statuses[service_name] = status
            
            if status["status"] != "healthy":
                overall_status = "unhealthy"
                logger.warning(f"⚠️ {service_config['name']} 서비스 비정상: {status.get('error', 'Unknown error')}")
            else:
                logger.info(f"✅ {service_config['name']} 서비스 정상 (응답시간: {status['response_time']:.3f}s)")
        
        self.health_status = {
            "overall_status": overall_status,
            "services": service_statuses,
            "timestamp": datetime.now().isoformat(),
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
        
        return self.health_status
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        try:
            # 메모리 사용량 (간단한 추정)
            import psutil
            memory = psutil.virtual_memory()
            
            return {
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        except ImportError:
            return {
                "memory_usage_percent": 0,
                "memory_available_mb": 0,
                "cpu_percent": 0,
                "disk_usage_percent": 0,
                "note": "psutil not available"
            }
    
    def generate_health_report(self) -> Dict[str, Any]:
        """헬스 리포트 생성"""
        health_status = self.check_all_services()
        system_metrics = self.get_system_metrics()
        
        report = {
            "health_status": health_status,
            "system_metrics": system_metrics,
            "report_generated": datetime.now().isoformat()
        }
        
        # 로그 파일에 저장
        try:
            with open("/var/log/supervisor/health_report.json", "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"헬스 리포트 저장 실패: {e}")
        
        return report
    
    def run_monitoring_loop(self, interval: int = 60):
        """모니터링 루프 실행"""
        logger.info(f"🔄 DuRi 헬스 모니터링 시작 (간격: {interval}초)")
        
        while True:
            try:
                report = self.generate_health_report()
                
                # 전체 상태가 비정상이면 경고
                if report["health_status"]["overall_status"] != "healthy":
                    logger.error("🚨 일부 DuRi 서비스가 비정상 상태입니다!")
                
                # 시스템 메트릭이 높으면 경고
                if report["system_metrics"]["memory_usage_percent"] > 80:
                    logger.warning("⚠️ 메모리 사용량이 높습니다!")
                
                if report["system_metrics"]["cpu_percent"] > 80:
                    logger.warning("⚠️ CPU 사용량이 높습니다!")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 헬스 모니터링 중단")
                break
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(interval)

def main():
    """메인 함수"""
    monitor = DuRiHealthMonitor()
    
    # 초기 헬스 체크
    logger.info("🚀 DuRi All-in-One 헬스 모니터 시작")
    initial_report = monitor.generate_health_report()
    
    print("=" * 60)
    print("DuRi All-in-One 헬스 모니터")
    print("=" * 60)
    print(f"시작 시간: {monitor.start_time}")
    print(f"전체 상태: {initial_report['health_status']['overall_status']}")
    print()
    
    for service_name, status in initial_report['health_status']['services'].items():
        print(f"{service_name}: {status['status']}")
        if status['status'] == 'healthy':
            print(f"  응답시간: {status['response_time']:.3f}s")
        else:
            print(f"  오류: {status.get('error', 'Unknown')}")
        print()
    
    # 모니터링 루프 시작
    monitor.run_monitoring_loop()

if __name__ == "__main__":
    main() 