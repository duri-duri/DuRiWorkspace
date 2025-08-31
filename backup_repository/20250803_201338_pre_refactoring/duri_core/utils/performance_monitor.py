"""
DuRi 성능 모니터링 시스템

시스템 성능을 실시간으로 모니터링하고 통계를 수집합니다.
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    system_load: float
    process_count: int

@dataclass
class SystemHealth:
    """시스템 건강도"""
    overall_health: float  # 0.0 ~ 1.0
    cpu_health: float
    memory_health: float
    disk_health: float
    network_health: float
    alerts: List[str]

class PerformanceMonitor:
    """DuRi 성능 모니터링 시스템"""
    
    def __init__(self, monitoring_interval: int = 60):
        """PerformanceMonitor 초기화"""
        self.monitoring_interval = monitoring_interval
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.performance_history: List[PerformanceMetrics] = []
        self.health_history: List[SystemHealth] = []
        self.alert_thresholds = {
            'cpu_critical': 90.0,
            'cpu_warning': 80.0,
            'memory_critical': 95.0,
            'memory_warning': 85.0,
            'disk_critical': 95.0,
            'disk_warning': 85.0
        }
        self.max_history_size = 1000
        
        # Moving Average 설정
        self.moving_average_window = 5  # 5초간 평균
        self.moving_average_data = {
            'cpu_usage': [],
            'memory_usage': [],
            'system_load': []
        }
        
        logger.info("PerformanceMonitor 초기화 완료")
    
    def start_monitoring(self, context: Optional[Dict[str, Any]] = None):
        """성능 모니터링을 시작합니다."""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("성능 모니터링 시작")
        
        # context가 제공된 경우 로깅
        if context:
            logger.info(f"모니터링 컨텍스트: {context}")
    
    def stop_monitoring(self):
        """성능 모니터링을 중지합니다."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("성능 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 성능 메트릭 수집
                metrics = self._collect_performance_metrics()
                self.performance_history.append(metrics)
                
                # Moving Average 업데이트
                self._update_moving_averages(metrics)
                
                # 시스템 건강도 계산
                health = self._calculate_system_health(metrics)
                self.health_history.append(health)
                
                # 히스토리 크기 제한
                self._cleanup_history()
                
                # 알림 체크
                self._check_alerts(health)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기
    
    def _update_moving_averages(self, metrics: PerformanceMetrics):
        """Moving Average를 업데이트합니다."""
        try:
            # CPU 사용률 Moving Average
            self.moving_average_data['cpu_usage'].append(metrics.cpu_usage)
            if len(self.moving_average_data['cpu_usage']) > self.moving_average_window:
                self.moving_average_data['cpu_usage'].pop(0)
            
            # 메모리 사용률 Moving Average
            self.moving_average_data['memory_usage'].append(metrics.memory_usage)
            if len(self.moving_average_data['memory_usage']) > self.moving_average_window:
                self.moving_average_data['memory_usage'].pop(0)
            
            # 시스템 로드 Moving Average
            self.moving_average_data['system_load'].append(metrics.system_load)
            if len(self.moving_average_data['system_load']) > self.moving_average_window:
                self.moving_average_data['system_load'].pop(0)
                
        except Exception as e:
            logger.error(f"Moving Average 업데이트 실패: {e}")
    
    def get_moving_averages(self) -> Dict[str, float]:
        """현재 Moving Average 값을 반환합니다."""
        try:
            return {
                'cpu_usage': sum(self.moving_average_data['cpu_usage']) / len(self.moving_average_data['cpu_usage']) if self.moving_average_data['cpu_usage'] else 0.0,
                'memory_usage': sum(self.moving_average_data['memory_usage']) / len(self.moving_average_data['memory_usage']) if self.moving_average_data['memory_usage'] else 0.0,
                'system_load': sum(self.moving_average_data['system_load']) / len(self.moving_average_data['system_load']) if self.moving_average_data['system_load'] else 0.0
            }
        except Exception as e:
            logger.error(f"Moving Average 조회 실패: {e}")
            return {'cpu_usage': 0.0, 'memory_usage': 0.0, 'system_load': 0.0}
    
    def _collect_performance_metrics(self) -> PerformanceMetrics:
        """성능 메트릭을 수집합니다."""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # 시스템 로드
            system_load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0.0
            
            # 프로세스 수
            process_count = len(psutil.pids())
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                system_load=system_load,
                process_count=process_count
            )
            
        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                system_load=0.0,
                process_count=0
            )
    
    def _calculate_system_health(self, metrics: PerformanceMetrics) -> SystemHealth:
        """시스템 건강도를 계산합니다."""
        alerts = []
        
        # CPU 건강도
        cpu_health = max(0.0, 1.0 - (metrics.cpu_usage / 100.0))
        if metrics.cpu_usage >= self.alert_thresholds['cpu_critical']:
            alerts.append(f"CPU 사용률이 임계값을 초과했습니다: {metrics.cpu_usage:.1f}%")
        elif metrics.cpu_usage >= self.alert_thresholds['cpu_warning']:
            alerts.append(f"CPU 사용률이 높습니다: {metrics.cpu_usage:.1f}%")
        
        # 메모리 건강도
        memory_health = max(0.0, 1.0 - (metrics.memory_usage / 100.0))
        if metrics.memory_usage >= self.alert_thresholds['memory_critical']:
            alerts.append(f"메모리 사용률이 임계값을 초과했습니다: {metrics.memory_usage:.1f}%")
        elif metrics.memory_usage >= self.alert_thresholds['memory_warning']:
            alerts.append(f"메모리 사용률이 높습니다: {metrics.memory_usage:.1f}%")
        
        # 디스크 건강도
        disk_health = max(0.0, 1.0 - (metrics.disk_usage / 100.0))
        if metrics.disk_usage >= self.alert_thresholds['disk_critical']:
            alerts.append(f"디스크 사용률이 임계값을 초과했습니다: {metrics.disk_usage:.1f}%")
        elif metrics.disk_usage >= self.alert_thresholds['disk_warning']:
            alerts.append(f"디스크 사용률이 높습니다: {metrics.disk_usage:.1f}%")
        
        # 네트워크 건강도 (기본값)
        network_health = 1.0
        
        # 전체 건강도
        overall_health = (cpu_health * 0.3 + memory_health * 0.3 + 
                         disk_health * 0.2 + network_health * 0.2)
        
        return SystemHealth(
            overall_health=overall_health,
            cpu_health=cpu_health,
            memory_health=memory_health,
            disk_health=disk_health,
            network_health=network_health,
            alerts=alerts
        )
    
    def _cleanup_history(self):
        """히스토리 크기를 제한합니다."""
        if len(self.performance_history) > self.max_history_size:
            self.performance_history = self.performance_history[-self.max_history_size:]
        
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
    
    def _check_alerts(self, health: SystemHealth):
        """알림을 체크합니다."""
        if health.alerts:
            for alert in health.alerts:
                logger.warning(f"시스템 알림: {alert}")
        
        if health.overall_health < 0.5:
            logger.error(f"시스템 건강도가 낮습니다: {health.overall_health:.2f}")
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """현재 성능 메트릭을 반환합니다."""
        if self.performance_history:
            return self.performance_history[-1]
        return None
    
    def get_current_health(self) -> Optional[SystemHealth]:
        """현재 시스템 건강도를 반환합니다."""
        if self.health_history:
            return self.health_history[-1]
        return None
    
    def get_performance_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """성능 통계를 반환합니다."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.performance_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {
                "error": "최근 데이터가 없습니다.",
                "optimization_suggestions": ["성능 데이터가 부족합니다. 모니터링을 활성화하세요."]
            }
        
        # 평균 계산
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)
        
        # 최대값 계산
        max_cpu = max(m.cpu_usage for m in recent_metrics)
        max_memory = max(m.memory_usage for m in recent_metrics)
        max_disk = max(m.disk_usage for m in recent_metrics)
        
        # 성능 최적화 제안 생성
        optimization_suggestions = self._generate_optimization_suggestions(
            avg_cpu, avg_memory, avg_disk, max_cpu, max_memory, max_disk
        )
        
        return {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "average_metrics": {
                "cpu_usage": avg_cpu,
                "memory_usage": avg_memory,
                "disk_usage": avg_disk
            },
            "maximum_metrics": {
                "cpu_usage": max_cpu,
                "memory_usage": max_memory,
                "disk_usage": max_disk
            },
            "current_health": self.get_current_health().overall_health if self.get_current_health() else 0.0,
            "optimization_suggestions": optimization_suggestions
        }
    
    def _generate_optimization_suggestions(self, avg_cpu: float, avg_memory: float, 
                                         avg_disk: float, max_cpu: float, 
                                         max_memory: float, max_disk: float) -> List[str]:
        """성능 최적화 제안을 생성합니다."""
        suggestions = []
        
        # CPU 최적화 제안
        if avg_cpu > 70.0:
            suggestions.append("CPU 사용률이 높습니다. 불필요한 프로세스를 종료하거나 작업 부하를 분산하세요.")
        elif avg_cpu < 20.0:
            suggestions.append("CPU 사용률이 낮습니다. 시스템 리소스를 더 효율적으로 활용할 수 있습니다.")
        
        if max_cpu > 90.0:
            suggestions.append("CPU 사용률이 임계값을 초과했습니다. 즉시 조치가 필요합니다.")
        
        # 메모리 최적화 제안
        if avg_memory > 80.0:
            suggestions.append("메모리 사용률이 높습니다. 메모리 누수 확인 및 정리가 필요합니다.")
        elif avg_memory < 30.0:
            suggestions.append("메모리 사용률이 낮습니다. 캐싱을 통해 성능을 향상시킬 수 있습니다.")
        
        if max_memory > 95.0:
            suggestions.append("메모리 사용률이 임계값을 초과했습니다. 즉시 조치가 필요합니다.")
        
        # 디스크 최적화 제안
        if avg_disk > 85.0:
            suggestions.append("디스크 사용률이 높습니다. 불필요한 파일 정리 및 압축이 필요합니다.")
        
        if max_disk > 95.0:
            suggestions.append("디스크 사용률이 임계값을 초과했습니다. 즉시 조치가 필요합니다.")
        
        # 성능 향상 제안
        if avg_cpu < 50.0 and avg_memory < 60.0:
            suggestions.append("시스템 리소스가 여유롭습니다. 더 많은 작업을 병렬로 처리할 수 있습니다.")
        
        return suggestions
    
    def update_alert_thresholds(self, new_thresholds: Dict[str, float]):
        """알림 임계값을 업데이트합니다."""
        self.alert_thresholds.update(new_thresholds)
        logger.info("알림 임계값 업데이트 완료")

# 싱글톤 인스턴스
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """PerformanceMonitor 싱글톤 인스턴스 반환"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor 