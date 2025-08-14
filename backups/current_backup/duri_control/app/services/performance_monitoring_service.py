"""
DuRi Memory System - Performance Monitoring Service
기본 성능 모니터링 서비스
"""
import logging
import time
import json
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터 클래스"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_percent: float
    disk_free_gb: float
    network_io: Dict[str, float]
    timestamp: datetime

@dataclass
class ApplicationMetrics:
    """애플리케이션 메트릭 데이터 클래스"""
    total_memories: int
    avg_importance: float
    memory_compression_ratio: float
    analysis_queue_size: int
    active_connections: int
    response_time_ms: float
    timestamp: datetime

class PerformanceMonitoringService:
    """성능 모니터링 서비스"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.last_collection = datetime.now()
        self.collection_interval = 60  # 60초마다 수집
    
    def get_system_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 정보
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 디스크 정보
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                disk_percent=disk_percent,
                disk_free_gb=disk_free_gb,
                network_io=network_io,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0,
                disk_percent=0.0,
                disk_free_gb=0.0,
                network_io={},
                timestamp=datetime.now()
            )
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """애플리케이션 메트릭 수집"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            from .async_analysis_service import async_analysis_service
            
            memory_service = MemoryService(db)
            
            # 메모리 통계
            memory_stats = memory_service.get_memory_stats()
            total_memories = memory_stats.get("total_memories", 0)
            
            # 평균 중요도 계산
            memories = memory_service.query_memories(limit=1000)
            if memories:
                avg_importance = sum(m.importance_score for m in memories) / len(memories)
            else:
                avg_importance = 0.0
            
            # 압축률 (간단한 추정)
            memory_compression_ratio = 0.8  # 기본값
            
            # 분석 큐 크기
            analysis_queue_size = len(async_analysis_service.analysis_status)
            
            # 활성 연결 수 (간단한 추정)
            active_connections = 1  # 기본값
            
            # 응답 시간 (간단한 측정)
            start_time = time.time()
            memory_service.query_memories(limit=1)
            response_time_ms = (time.time() - start_time) * 1000
            
            return ApplicationMetrics(
                total_memories=total_memories,
                avg_importance=avg_importance,
                memory_compression_ratio=memory_compression_ratio,
                analysis_queue_size=analysis_queue_size,
                active_connections=active_connections,
                response_time_ms=response_time_ms,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"애플리케이션 메트릭 수집 실패: {e}")
            return ApplicationMetrics(
                total_memories=0,
                avg_importance=0.0,
                memory_compression_ratio=1.0,
                analysis_queue_size=0,
                active_connections=0,
                response_time_ms=0.0,
                timestamp=datetime.now()
            )
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """종합 메트릭 수집"""
        try:
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # 메트릭 저장
            metrics_data = {
                "system": {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "memory_available_mb": system_metrics.memory_available_mb,
                    "disk_percent": system_metrics.disk_percent,
                    "disk_free_gb": system_metrics.disk_free_gb,
                    "network_io": system_metrics.network_io
                },
                "application": {
                    "total_memories": app_metrics.total_memories,
                    "avg_importance": app_metrics.avg_importance,
                    "memory_compression_ratio": app_metrics.memory_compression_ratio,
                    "analysis_queue_size": app_metrics.analysis_queue_size,
                    "active_connections": app_metrics.active_connections,
                    "response_time_ms": app_metrics.response_time_ms
                },
                "timestamp": datetime.now().isoformat(),
                "collection_interval_seconds": self.collection_interval
            }
            
            # 메트릭 히스토리에 추가
            self.metrics_history.append(metrics_data)
            
            # 히스토리 크기 제한 (최근 100개)
            if len(self.metrics_history) > 100:
                self.metrics_history = self.metrics_history[-100:]
            
            # 분석 저장소에 저장
            from .analysis_repository_service import analysis_repository_service
            
            # 시스템 메트릭 저장
            analysis_repository_service.save_performance_metric(
                metric_type="system",
                metric_name="cpu_usage",
                metric_value=system_metrics.cpu_percent,
                metric_unit="percent"
            )
            
            analysis_repository_service.save_performance_metric(
                metric_type="system",
                metric_name="memory_usage",
                metric_value=system_metrics.memory_percent,
                metric_unit="percent"
            )
            
            analysis_repository_service.save_performance_metric(
                metric_type="application",
                metric_name="total_memories",
                metric_value=app_metrics.total_memories,
                metric_unit="count"
            )
            
            analysis_repository_service.save_performance_metric(
                metric_type="application",
                metric_name="avg_importance",
                metric_value=app_metrics.avg_importance,
                metric_unit="score"
            )
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"종합 메트릭 수집 실패: {e}")
            return {"error": str(e)}
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """메트릭 히스토리 조회"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # 메모리에서 필터링
            filtered_history = [
                metrics for metrics in self.metrics_history
                if datetime.fromisoformat(metrics["timestamp"]) > cutoff_time
            ]
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"메트릭 히스토리 조회 실패: {e}")
            return []
    
    def get_health_status(self) -> Dict[str, Any]:
        """시스템 건강도 상태"""
        try:
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # 건강도 점수 계산
            health_score = 100
            
            # CPU 사용률 체크
            if system_metrics.cpu_percent > 80:
                health_score -= 20
            elif system_metrics.cpu_percent > 60:
                health_score -= 10
            
            # 메모리 사용률 체크
            if system_metrics.memory_percent > 90:
                health_score -= 20
            elif system_metrics.memory_percent > 80:
                health_score -= 10
            
            # 디스크 사용률 체크
            if system_metrics.disk_percent > 90:
                health_score -= 15
            elif system_metrics.disk_percent > 80:
                health_score -= 5
            
            # 응답 시간 체크
            if app_metrics.response_time_ms > 1000:
                health_score -= 15
            elif app_metrics.response_time_ms > 500:
                health_score -= 5
            
            # 상태 결정
            if health_score >= 80:
                status = "healthy"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                "health_score": health_score,
                "status": status,
                "system_metrics": {
                    "cpu_percent": system_metrics.cpu_percent,
                    "memory_percent": system_metrics.memory_percent,
                    "disk_percent": system_metrics.disk_percent
                },
                "application_metrics": {
                    "total_memories": app_metrics.total_memories,
                    "response_time_ms": app_metrics.response_time_ms,
                    "analysis_queue_size": app_metrics.analysis_queue_size
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"건강도 상태 조회 실패: {e}")
            return {
                "health_score": 0,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        try:
            # 최근 메트릭들
            recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
            
            if not recent_metrics:
                return {"error": "No metrics available"}
            
            # 평균값 계산
            avg_cpu = sum(m["system"]["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m["system"]["memory_percent"] for m in recent_metrics) / len(recent_metrics)
            avg_response_time = sum(m["application"]["response_time_ms"] for m in recent_metrics) / len(recent_metrics)
            
            # 최대값 계산
            max_cpu = max(m["system"]["cpu_percent"] for m in recent_metrics)
            max_memory = max(m["system"]["memory_percent"] for m in recent_metrics)
            max_response_time = max(m["application"]["response_time_ms"] for m in recent_metrics)
            
            return {
                "summary": {
                    "avg_cpu_percent": round(avg_cpu, 2),
                    "avg_memory_percent": round(avg_memory, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "max_cpu_percent": round(max_cpu, 2),
                    "max_memory_percent": round(max_memory, 2),
                    "max_response_time_ms": round(max_response_time, 2)
                },
                "metrics_count": len(recent_metrics),
                "collection_period_hours": 24,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"성능 요약 조회 실패: {e}")
            return {"error": str(e)}

# 전역 인스턴스
performance_monitoring_service = PerformanceMonitoringService() 