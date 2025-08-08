from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..services.gateway_service import get_gateway_service
from ..models.gateway_model import GatewayHealthResponse, ProxyRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health", response_model=GatewayHealthResponse, tags=["gateway"])
async def gateway_health_check():
    """전체 서비스 헬스 체크 통합"""
    try:
        gateway_service = get_gateway_service()
        return gateway_service.get_overall_health()
    except Exception as e:
        logger.error(f"게이트웨이 헬스 체크 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Gateway health check failed: {str(e)}")

@router.get("/{service_name}/health", tags=["gateway"])
async def service_health_check(service_name: str):
    """개별 서비스 헬스 체크"""
    try:
        gateway_service = get_gateway_service()
        is_healthy, data, response_time = gateway_service.check_service_health(service_name)
        
        return {
            "service": service_name,
            "healthy": is_healthy,
            "response_time_ms": response_time,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"서비스 {service_name} 헬스 체크 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Service health check failed: {str(e)}")

@router.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], tags=["gateway"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    proxy_request_data: Optional[ProxyRequest] = None
):
    """서비스 프록시 요청"""
    try:
        gateway_service = get_gateway_service()
        
        # 요청 메서드 및 헤더 추출
        method = request.method
        headers = dict(request.headers)
        
        # 민감한 헤더 제거
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # 요청 본문 추출
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()
                if body:
                    body = body.decode()
        
        # 프록시 요청 실행
        proxy_response = gateway_service.proxy_request(
            service_name=service_name,
            path=path,
            method=method,
            headers=headers,
            body=body
        )
        
        # 응답 생성
        response = JSONResponse(
            content=proxy_response.body,
            status_code=proxy_response.status_code,
            headers=proxy_response.headers
        )
        
        # 게이트웨이 메타데이터 추가
        response.headers["X-Gateway-Service"] = service_name
        response.headers["X-Gateway-Path"] = path
        response.headers["X-Gateway-Response-Time"] = str(proxy_response.response_time_ms)
        
        return response
        
    except ValueError as e:
        # 서비스가 설정되지 않음
        logger.error(f"서비스 {service_name} 설정 오류: {e}")
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
    except Exception as e:
        # 서비스 오류 시 fallback 응답
        logger.error(f"서비스 {service_name} 프록시 실패: {e}")
        
        fallback_response = gateway_service.get_fallback_response(
            service_name=service_name,
            path=path,
            error=str(e)
        )
        
        return JSONResponse(
            content=fallback_response.body,
            status_code=fallback_response.status_code,
            headers=fallback_response.headers
        )

@router.get("/services", tags=["gateway"])
async def list_services():
    """사용 가능한 서비스 목록"""
    try:
        gateway_service = get_gateway_service()
        services = {}
        
        for service_name, service_config in gateway_service.config.services.items():
            services[service_name] = {
                "name": service_config.name,
                "host": service_config.host,
                "port": service_config.port,
                "enabled": service_config.enabled,
                "health_path": service_config.health_path,
                "timeout": service_config.timeout
            }
        
        return {
            "services": services,
            "total_services": len(services),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Service list failed: {str(e)}")

@router.get("/status", tags=["gateway"])
async def gateway_status():
    """게이트웨이 상태 정보"""
    try:
        gateway_service = get_gateway_service()
        
        # 각 서비스 상태 확인
        service_statuses = {}
        total_services = len(gateway_service.config.services)
        healthy_services = 0
        
        for service_name in gateway_service.config.services:
            is_healthy, _, response_time = gateway_service.check_service_health(service_name)
            if is_healthy:
                healthy_services += 1
            
            service_statuses[service_name] = {
                "healthy": is_healthy,
                "response_time_ms": response_time
            }
        
        return {
            "gateway_status": "running",
            "total_services": total_services,
            "healthy_services": healthy_services,
            "service_statuses": service_statuses,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"게이트웨이 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"Gateway status failed: {str(e)}") 