"""
Day 6: 대시보드 서비스
실시간 대시보드를 위한 서비스 로직
"""

import asyncio
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import logging

from ..schemas.dashboard import (
    ServiceStatus, SystemMetrics, ApiMetrics, DatabaseMetrics,
    MemoryUsageMetrics, PerformanceMetrics, RealtimeData
)
from .memory_service import MemoryService

logger = logging.getLogger(__name__)

class DashboardService:
    """대시보드 서비스"""
    
    def __init__(self):
        self.memory_service = MemoryService()
        self.metrics_cache = {}
        self.last_update = datetime.now()
        self.service_endpoints = {
            "duri_core": "http://localhost:8080",
            "duri_brain": "http://localhost:8081", 
            "duri_evolution": "http://localhost:8082",
            "duri_control": "http://localhost:8083"
        }
    
    async def get_service_status(self) -> List[ServiceStatus]:
        """모든 서비스 상태 조회"""
        services = []
        
        for name, endpoint in self.service_endpoints.items():
            try:
                status = await self._check_service_health(name, endpoint)
                services.append(status)
            except Exception as e:
                logger.error(f"서비스 {name} 상태 확인 실패: {e}")
                services.append(ServiceStatus(
                    name=name,
                    status="error",
                    port=self._get_port_from_endpoint(endpoint),
                    last_check=datetime.now()
                ))
        
        return services
    
    async def get_all_service_status(self) -> List[ServiceStatus]:
        """모든 서비스 상태 조회 (별칭)"""
        return await self.get_service_status()
    
    async def _check_service_health(self, name: str, endpoint: str) -> ServiceStatus:
        """개별 서비스 상태 확인"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{endpoint}/health/") as response:
                    if response.status == 200:
                        data = await response.json()
                        response_time = (time.time() - start_time) * 1000
                        
                        return ServiceStatus(
                            name=name,
                            status="healthy",
                            port=self._get_port_from_endpoint(endpoint),
                            last_check=datetime.now()
                        )
                    else:
                        return ServiceStatus(
                            name=name,
                            status="error",
                            port=self._get_port_from_endpoint(endpoint),
                            last_check=datetime.now()
                        )
        except Exception as e:
            logger.error(f"서비스 {name} 연결 실패: {e}")
            return ServiceStatus(
                name=name,
                status="error",
                port=self._get_port_from_endpoint(endpoint),
                last_check=datetime.now()
            )
    
    def _get_port_from_endpoint(self, endpoint: str) -> int:
        """엔드포인트에서 포트 추출"""
        try:
            return int(endpoint.split(":")[-1].replace("/", ""))
        except:
            return 0
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """성능 지표 수집"""
        try:
            # 시스템 메트릭
            system_metrics = await self._get_system_metrics()
            
            # API 메트릭
            api_metrics = await self._get_api_metrics()
            
            # 데이터베이스 메트릭
            db_metrics = await self._get_database_metrics()
            
            # 메모리 사용량 메트릭
            memory_metrics = await self._get_memory_usage_metrics()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                system=system_metrics,
                api=api_metrics,
                database=db_metrics,
                memory=memory_metrics
            )
        except Exception as e:
            logger.error(f"성능 지표 수집 실패: {e}")
            # 기본값 반환
            return PerformanceMetrics(
                timestamp=datetime.now(),
                system=SystemMetrics(
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    disk_usage=0.0,
                    network_in=0.0,
                    network_out=0.0,
                    load_average=[0.0, 0.0, 0.0]
                ),
                api=ApiMetrics(
                    avg_response_time=0.0,
                    requests_per_second=0.0,
                    error_rate=0.0,
                    active_connections=0,
                    total_requests=0
                ),
                database=DatabaseMetrics(
                    connection_count=0,
                    active_queries=0,
                    avg_query_time=0.0,
                    cache_hit_ratio=0.0,
                    table_size={}
                ),
                memory=memory_metrics
            )
    
    async def _get_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 네트워크 통계
            net_io = psutil.net_io_counters()
            network_in = net_io.bytes_recv / 1024 / 1024  # MB
            network_out = net_io.bytes_sent / 1024 / 1024  # MB
            
            # 로드 평균
            load_avg = psutil.getloadavg()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_in=network_in,
                network_out=network_out,
                load_average=list(load_avg)
            )
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_in=0.0,
                network_out=0.0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    async def _get_api_metrics(self) -> ApiMetrics:
        """API 메트릭 수집"""
        # 실제 구현에서는 API 호출 통계를 수집
        # 현재는 기본값 반환
        return ApiMetrics(
            avg_response_time=150.0,  # ms
            requests_per_second=10.5,
            error_rate=0.1,  # %
            active_connections=5,
            total_requests=1000
        )
    
    async def _get_database_metrics(self) -> DatabaseMetrics:
        """데이터베이스 메트릭 수집"""
        # 실제 구현에서는 PostgreSQL 통계를 수집
        # 현재는 기본값 반환
        return DatabaseMetrics(
            connection_count=3,
            active_queries=1,
            avg_query_time=25.0,  # ms
            cache_hit_ratio=85.0,  # %
            table_size={"memory": 1024, "analysis": 512}
        )
    
    async def _get_memory_usage_metrics(self) -> MemoryUsageMetrics:
        """메모리 사용량 메트릭 수집"""
        try:
            # 메모리 통계 조회
            memory_stats = await self.memory_service.get_memory_stats()
            
            return MemoryUsageMetrics(
                total_memories=memory_stats.get("total_memories", 0),
                recent_24h=memory_stats.get("recent_24h", 0),
                by_type=memory_stats.get("by_type", {}),
                by_source=memory_stats.get("by_source", {}),
                by_importance={"high": 0, "medium": 0, "low": 0}
            )
        except Exception as e:
            logger.error(f"메모리 사용량 메트릭 수집 실패: {e}")
            return MemoryUsageMetrics(
                total_memories=0,
                recent_24h=0,
                by_type={},
                by_source={},
                by_importance={"high": 0, "medium": 0, "low": 0}
            )
    
    async def get_realtime_data(self) -> RealtimeData:
        """실시간 데이터 수집"""
        try:
            # 서비스 상태 확인
            services = await self.get_service_status()
            active_services = len([s for s in services if s.status == "healthy"])
            
            # 메모리 수 조회
            memory_stats = await self.memory_service.get_memory_stats()
            memory_count = memory_stats.get("total_memories", 0)
            
            # 최근 활동 (최근 10개 메모리)
            recent_memories = await self.memory_service.query_memories(
                limit=10,
                sort_by="created_at",
                sort_order="desc"
            )
            
            recent_activity = []
            for memory in recent_memories:
                recent_activity.append({
                    "type": memory.get("type", "unknown"),
                    "content": memory.get("content", "")[:50],
                    "timestamp": memory.get("created_at"),
                    "importance": memory.get("importance_score", 0)
                })
            
            # 시스템 상태 판단
            system_status = "healthy"
            if active_services < len(self.service_endpoints):
                system_status = "warning"
            if active_services == 0:
                system_status = "error"
            
            return RealtimeData(
                timestamp=datetime.now(),
                system_status=system_status,
                active_services=active_services,
                memory_count=memory_count,
                recent_activity=recent_activity
            )
        except Exception as e:
            logger.error(f"실시간 데이터 수집 실패: {e}")
            return RealtimeData(
                timestamp=datetime.now(),
                system_status="error",
                active_services=0,
                memory_count=0,
                recent_activity=[]
            )
    
    async def get_memory_by_type(self) -> Dict[str, int]:
        """메모리 타입별 분포"""
        try:
            memories = await self.memory_service.query_memories(limit=1000)
            by_type = {}
            
            for memory in memories:
                memory_type = memory.get("type", "unknown")
                by_type[memory_type] = by_type.get(memory_type, 0) + 1
            
            return by_type
        except Exception as e:
            logger.error(f"메모리 타입별 분포 조회 실패: {e}")
            return {}
    
    async def get_memory_by_source(self) -> Dict[str, int]:
        """메모리 소스별 분포"""
        try:
            memories = await self.memory_service.query_memories(limit=1000)
            by_source = {}
            
            for memory in memories:
                source = memory.get("source", "unknown")
                by_source[source] = by_source.get(source, 0) + 1
            
            return by_source
        except Exception as e:
            logger.error(f"메모리 소스별 분포 조회 실패: {e}")
            return {}
    
    async def get_memory_by_importance(self) -> Dict[str, int]:
        """메모리 중요도별 분포"""
        try:
            memories = await self.memory_service.query_memories(limit=1000)
            by_importance = {"high": 0, "medium": 0, "low": 0}
            
            for memory in memories:
                importance_score = memory.get("importance_score", 50)
                
                if importance_score >= 80:
                    by_importance["high"] += 1
                elif importance_score >= 50:
                    by_importance["medium"] += 1
                else:
                    by_importance["low"] += 1
            
            return by_importance
        except Exception as e:
            logger.error(f"메모리 중요도별 분포 조회 실패: {e}")
            return {"high": 0, "medium": 0, "low": 0}
    
    async def get_dashboard_config(self) -> Dict[str, Any]:
        """대시보드 설정 조회"""
        return {
            "auto_refresh_interval": 30,
            "chart_update_interval": 5,
            "max_data_points": 100,
            "enable_websocket": True,
            "enable_notifications": True
        }
    
    async def update_dashboard_config(self, config: Dict[str, Any]) -> bool:
        """대시보드 설정 업데이트"""
        try:
            # 설정 저장 로직 (실제로는 데이터베이스에 저장)
            logger.info(f"대시보드 설정 업데이트: {config}")
            return True
        except Exception as e:
            logger.error(f"대시보드 설정 업데이트 실패: {e}")
            return False 