"""
Day 6: 메트릭 서비스
시스템 성능 모니터링을 위한 메트릭 수집 서비스
"""

import psutil
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import aiohttp
import json

from ..schemas.dashboard import (
    SystemMetrics, ApiMetrics, DatabaseMetrics, MemoryUsageMetrics
)

logger = logging.getLogger(__name__)

class MetricsService:
    """메트릭 수집 서비스"""
    
    def __init__(self):
        self.metrics_history = {
            "system": [],
            "api": [],
            "database": [],
            "memory": []
        }
        self.max_history_size = 100
        self.last_collection = datetime.now()
    
    async def get_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # 네트워크 통계
            net_io = psutil.net_io_counters()
            network_in = net_io.bytes_recv / 1024 / 1024  # MB
            network_out = net_io.bytes_sent / 1024 / 1024  # MB
            
            # 로드 평균
            load_avg = psutil.getloadavg()
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_in=network_in,
                network_out=network_out,
                load_average=list(load_avg)
            )
            
            # 히스토리에 저장
            self._add_to_history("system", {
                "timestamp": datetime.now(),
                "metrics": metrics.dict()
            })
            
            return metrics
            
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
    
    async def get_api_metrics(self) -> ApiMetrics:
        """API 메트릭 수집"""
        try:
            # 실제 구현에서는 API 호출 통계를 수집
            # 현재는 기본값 반환
            
            # 간단한 API 응답 시간 측정
            response_times = []
            endpoints = [
                "http://localhost:8080/health/",
                "http://localhost:8081/health/",
                "http://localhost:8082/health/",
                "http://localhost:8083/health/"
            ]
            
            for endpoint in endpoints:
                try:
                    start_time = time.time()
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        async with session.get(endpoint) as response:
                            response_time = (time.time() - start_time) * 1000
                            response_times.append(response_time)
                except Exception as e:
                    logger.warning(f"API 엔드포인트 {endpoint} 응답 시간 측정 실패: {e}")
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            requests_per_second = 10.5  # 실제로는 요청 수를 카운트해야 함
            error_rate = 0.1  # 실제로는 오류율을 계산해야 함
            active_connections = len([r for r in response_times if r < 1000])  # 응답 시간이 1초 미만인 연결
            total_requests = len(response_times)
            
            metrics = ApiMetrics(
                avg_response_time=avg_response_time,
                requests_per_second=requests_per_second,
                error_rate=error_rate,
                active_connections=active_connections,
                total_requests=total_requests
            )
            
            # 히스토리에 저장
            self._add_to_history("api", {
                "timestamp": datetime.now(),
                "metrics": metrics.dict()
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"API 메트릭 수집 실패: {e}")
            return ApiMetrics(
                avg_response_time=0.0,
                requests_per_second=0.0,
                error_rate=0.0,
                active_connections=0,
                total_requests=0
            )
    
    async def get_database_metrics(self) -> DatabaseMetrics:
        """데이터베이스 메트릭 수집"""
        try:
            # PostgreSQL 연결 수 확인
            connection_count = 0
            try:
                import psycopg2
                # 실제 구현에서는 PostgreSQL 통계를 조회
                connection_count = 3  # 기본값
            except ImportError:
                logger.warning("psycopg2가 설치되지 않음")
            
            # 기본 메트릭
            active_queries = 1
            avg_query_time = 25.0  # ms
            cache_hit_ratio = 85.0  # %
            table_size = {"memory": 1024, "analysis": 512}
            
            metrics = DatabaseMetrics(
                connection_count=connection_count,
                active_queries=active_queries,
                avg_query_time=avg_query_time,
                cache_hit_ratio=cache_hit_ratio,
                table_size=table_size
            )
            
            # 히스토리에 저장
            self._add_to_history("database", {
                "timestamp": datetime.now(),
                "metrics": metrics.dict()
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"데이터베이스 메트릭 수집 실패: {e}")
            return DatabaseMetrics(
                connection_count=0,
                active_queries=0,
                avg_query_time=0.0,
                cache_hit_ratio=0.0,
                table_size={}
            )
    
    async def get_memory_usage_metrics(self) -> MemoryUsageMetrics:
        """메모리 사용량 메트릭 수집"""
        try:
            from .memory_service import MemoryService
            
            memory_service = MemoryService()
            memory_stats = await memory_service.get_memory_stats()
            
            # 중요도별 분포 계산
            memories = await memory_service.query_memories(limit=1000)
            by_importance = {"high": 0, "medium": 0, "low": 0}
            
            for memory in memories:
                importance_score = memory.get("importance_score", 50)
                if importance_score >= 80:
                    by_importance["high"] += 1
                elif importance_score >= 50:
                    by_importance["medium"] += 1
                else:
                    by_importance["low"] += 1
            
            metrics = MemoryUsageMetrics(
                total_memories=memory_stats.get("total_memories", 0),
                recent_24h=memory_stats.get("recent_24h", 0),
                by_type=memory_stats.get("by_type", {}),
                by_source=memory_stats.get("by_source", {}),
                by_importance=by_importance
            )
            
            # 히스토리에 저장
            self._add_to_history("memory", {
                "timestamp": datetime.now(),
                "metrics": metrics.dict()
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"메모리 사용량 메트릭 수집 실패: {e}")
            return MemoryUsageMetrics(
                total_memories=0,
                recent_24h=0,
                by_type={},
                by_source={},
                by_importance={"high": 0, "medium": 0, "low": 0}
            )
    
    def _add_to_history(self, metric_type: str, data: Dict[str, Any]):
        """메트릭 히스토리에 데이터 추가"""
        if metric_type in self.metrics_history:
            self.metrics_history[metric_type].append(data)
            
            # 최대 크기 제한
            if len(self.metrics_history[metric_type]) > self.max_history_size:
                self.metrics_history[metric_type].pop(0)
    
    async def get_metrics_history(self, metric_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """메트릭 히스토리 조회"""
        try:
            if metric_type not in self.metrics_history:
                return []
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            history = self.metrics_history[metric_type]
            
            # 지정된 시간 범위의 데이터만 필터링
            filtered_history = [
                entry for entry in history
                if entry["timestamp"] >= cutoff_time
            ]
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"메트릭 히스토리 조회 실패: {e}")
            return []
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """메트릭 요약 조회"""
        try:
            summary = {
                "timestamp": datetime.now(),
                "system": await self.get_system_metrics(),
                "api": await self.get_api_metrics(),
                "database": await self.get_database_metrics(),
                "memory": await self.get_memory_usage_metrics()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"메트릭 요약 조회 실패: {e}")
            return {
                "timestamp": datetime.now(),
                "error": str(e)
            }
    
    async def clear_metrics_history(self, metric_type: Optional[str] = None):
        """메트릭 히스토리 정리"""
        try:
            if metric_type:
                if metric_type in self.metrics_history:
                    self.metrics_history[metric_type].clear()
            else:
                for key in self.metrics_history:
                    self.metrics_history[key].clear()
                    
            logger.info(f"메트릭 히스토리 정리 완료: {metric_type or 'all'}")
            
        except Exception as e:
            logger.error(f"메트릭 히스토리 정리 실패: {e}")
    
    async def export_metrics(self, metric_type: str, format: str = "json") -> str:
        """메트릭 데이터 내보내기"""
        try:
            history = await self.get_metrics_history(metric_type)
            
            if format.lower() == "json":
                return json.dumps(history, default=str, indent=2)
            elif format.lower() == "csv":
                # CSV 형식으로 변환
                if not history:
                    return ""
                
                headers = list(history[0]["metrics"].keys())
                csv_lines = [",".join(headers)]
                
                for entry in history:
                    row = [str(entry["metrics"].get(header, "")) for header in headers]
                    csv_lines.append(",".join(row))
                
                return "\n".join(csv_lines)
            else:
                raise ValueError(f"지원하지 않는 형식: {format}")
                
        except Exception as e:
            logger.error(f"메트릭 내보내기 실패: {e}")
            return "" 