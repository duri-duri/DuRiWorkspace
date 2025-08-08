import requests
import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse
import json

from ..models.gateway_model import (
    ServiceConfig, GatewayConfig, ServiceStatus, 
    GatewayHealthResponse, ProxyResponse, DEFAULT_SERVICES
)

logger = logging.getLogger(__name__)

class GatewayService:
    """API 게이트웨이 서비스"""
    
    def __init__(self, config: Optional[GatewayConfig] = None):
        """게이트웨이 서비스 초기화"""
        self.config = config or GatewayConfig(
            services=DEFAULT_SERVICES,
            default_timeout=30,
            default_retries=3,
            enable_caching=True,
            cache_ttl=300
        )
        self.session = requests.Session()
        
        # 기본 헤더 설정
        self.session.headers.update({
            'User-Agent': 'DuRi-Gateway/1.0.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """서비스 설정 조회"""
        return self.config.services.get(service_name)
    
    def check_service_health(self, service_name: str) -> Tuple[bool, Dict[str, Any], float]:
        """
        개별 서비스 헬스 체크
        
        Returns:
            (is_healthy, response_data, response_time_ms)
        """
        service_config = self.get_service_config(service_name)
        if not service_config or not service_config.enabled:
            return False, {"error": "Service not configured or disabled"}, 0.0
        
        url = f"http://{service_config.host}:{service_config.port}{service_config.health_path}"
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=service_config.timeout)
            response_time = (time.time() - start_time) * 1000  # ms로 변환
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, response_time
                except json.JSONDecodeError:
                    return True, {"raw_response": response.text}, response_time
            else:
                return False, {"error": f"HTTP {response.status_code}"}, response_time
                
        except requests.exceptions.Timeout:
            logger.warning(f"서비스 {service_name} 헬스 체크 타임아웃")
            return False, {"error": "Timeout"}, 0.0
        except requests.exceptions.ConnectionError:
            logger.warning(f"서비스 {service_name} 연결 실패")
            return False, {"error": "Connection refused"}, 0.0
        except Exception as e:
            logger.error(f"서비스 {service_name} 헬스 체크 실패: {e}")
            return False, {"error": str(e)}, 0.0
    
    def get_overall_health(self) -> GatewayHealthResponse:
        """전체 서비스 헬스 체크 통합"""
        services_status = {}
        healthy_count = 0
        total_count = len(self.config.services)
        
        for service_name, service_config in self.config.services.items():
            if not service_config.enabled:
                services_status[service_name] = {
                    "status": ServiceStatus.UNKNOWN,
                    "enabled": False,
                    "error": "Service disabled"
                }
                continue
            
            is_healthy, data, response_time = self.check_service_health(service_name)
            
            if is_healthy:
                status = ServiceStatus.HEALTHY
                healthy_count += 1
            else:
                status = ServiceStatus.UNHEALTHY
            
            services_status[service_name] = {
                "status": status,
                "enabled": True,
                "response_time_ms": response_time,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        
        # 전체 상태 결정
        if healthy_count == total_count:
            overall_status = ServiceStatus.HEALTHY
        elif healthy_count > 0:
            overall_status = ServiceStatus.UNHEALTHY
        else:
            overall_status = ServiceStatus.UNHEALTHY
        
        return GatewayHealthResponse(
            overall_status=overall_status,
            services=services_status,
            timestamp=datetime.now()
        )
    
    def proxy_request(
        self, 
        service_name: str, 
        path: str, 
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> ProxyResponse:
        """
        서비스로 요청 프록시
        
        Args:
            service_name: 서비스 이름 (core, brain, evolution, control)
            path: 요청 경로
            method: HTTP 메서드
            headers: 요청 헤더
            body: 요청 본문
            timeout: 타임아웃 (초)
            
        Returns:
            ProxyResponse
        """
        service_config = self.get_service_config(service_name)
        if not service_config or not service_config.enabled:
            raise ValueError(f"Service {service_name} not configured or disabled")
        
        # URL 구성
        base_url = f"http://{service_config.host}:{service_config.port}"
        full_url = urljoin(base_url, path.lstrip('/'))
        
        # 타임아웃 설정
        request_timeout = timeout or service_config.timeout
        
        # 요청 헤더 준비
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # 요청 본문 준비
        request_body = None
        if body and method in ["POST", "PUT", "PATCH"]:
            request_body = json.dumps(body)
            if "Content-Type" not in request_headers:
                request_headers["Content-Type"] = "application/json"
        
        try:
            start_time = time.time()
            
            # 요청 실행
            response = self.session.request(
                method=method,
                url=full_url,
                headers=request_headers,
                data=request_body,
                timeout=request_timeout
            )
            
            response_time = (time.time() - start_time) * 1000  # ms로 변환
            
            # 응답 본문 파싱
            try:
                response_body = response.json()
            except json.JSONDecodeError:
                response_body = response.text
            
            return ProxyResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response_body,
                response_time_ms=response_time,
                service_name=service_name,
                original_path=path
            )
            
        except requests.exceptions.Timeout:
            logger.error(f"서비스 {service_name} 프록시 타임아웃: {path}")
            raise Exception(f"Service {service_name} timeout")
        except requests.exceptions.ConnectionError:
            logger.error(f"서비스 {service_name} 연결 실패: {path}")
            raise Exception(f"Service {service_name} connection failed")
        except Exception as e:
            logger.error(f"서비스 {service_name} 프록시 실패: {e}")
            raise Exception(f"Service {service_name} proxy failed: {str(e)}")
    
    def get_fallback_response(self, service_name: str, path: str, error: str) -> ProxyResponse:
        """서비스 실패 시 fallback 응답"""
        return ProxyResponse(
            status_code=503,
            headers={"Content-Type": "application/json"},
            body={
                "error": "Service unavailable",
                "service": service_name,
                "path": path,
                "reason": error,
                "timestamp": datetime.now().isoformat(),
                "fallback": True
            },
            response_time_ms=0.0,
            service_name=service_name,
            original_path=path
        )

# 전역 게이트웨이 서비스 인스턴스
gateway_service = None

def get_gateway_service() -> 'GatewayService':
    """게이트웨이 서비스 인스턴스 반환"""
    global gateway_service
    if gateway_service is None:
        gateway_service = GatewayService()
    return gateway_service

def init_gateway_service(config: Optional[GatewayConfig] = None):
    """게이트웨이 서비스 초기화"""
    global gateway_service
    gateway_service = GatewayService(config)
    return gateway_service 