import requests
import time
from typing import Dict, Optional, Tuple
from datetime import datetime
import subprocess
import json

class SystemUtils:
    """시스템 유틸리티 클래스"""
    
    @staticmethod
    def check_service_health(service_name: str, port: int, timeout: int = 5) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        서비스 헬스 체크
        
        Args:
            service_name: 서비스 이름
            port: 포트 번호
            timeout: 타임아웃 (초)
            
        Returns:
            (is_healthy, response_time, error_message)
        """
        # docker-compose 서비스 이름으로 접근
        service_hosts = {
            "duri_core": "duri_core",
            "duri_brain": "duri_brain", 
            "duri_evolution": "duri_evolution",
            "duri_control": "duri_control"
        }
        
        host = service_hosts.get(service_name, "localhost")
        url = f"http://{host}:{port}/health"
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # ms로 변환
            
            if response.status_code == 200:
                return True, response_time, None
            else:
                return False, None, f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, None, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection refused"
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def check_docker_container_status(container_name: str) -> bool:
        """
        Docker 컨테이너 상태 확인
        
        Args:
            container_name: 컨테이너 이름
            
        Returns:
            컨테이너가 실행 중이면 True
        """
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return container_name in result.stdout
        except Exception:
            return False
    
    @staticmethod
    def get_service_config() -> Dict[str, int]:
        """
        서비스별 포트 설정 반환
        
        Returns:
            서비스명과 포트 매핑
        """
        return {
            "duri_core": 8080,
            "duri_brain": 8081,
            "duri_evolution": 8082,
            "duri_control": 8083
        }
    
    @staticmethod
    def get_container_names() -> Dict[str, str]:
        """
        서비스별 Docker 컨테이너 이름 반환
        
        Returns:
            서비스명과 컨테이너명 매핑
        """
        return {
            "duri_core": "duri_core_container",
            "duri_brain": "duri_brain_container", 
            "duri_evolution": "duri_evolution_container",
            "duri_control": "duri_control_container"
        } 