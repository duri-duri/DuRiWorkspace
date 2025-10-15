#!/usr/bin/env python3
"""
DuRi SLO 모니터링 시스템
"""

import time
import psutil
import json
from typing import Dict, Any, List
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("slo_monitor")

class SLOMonitor:
    """SLO 모니터링 클래스"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_history = []
        self.alert_thresholds = {
            "response_time_ms": 100,      # 응답 시간 임계치
            "memory_usage_percent": 80,   # 메모리 사용률 임계치
            "cpu_usage_percent": 70,      # CPU 사용률 임계치
            "disk_usage_percent": 90,     # 디스크 사용률 임계치
            "error_rate_percent": 1.0,    # 오류율 임계치
            "failure_rate_percent": 5.0   # 실패율 임계치
        }
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": time.time(),
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory_percent,
                "disk_usage_percent": disk_percent,
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "uptime_seconds": time.time() - self.start_time
            }
            
            # 히스토리에 추가 (최근 100개만 유지)
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return {}
    
    def check_slo_compliance(self) -> Dict[str, Any]:
        """SLO 준수 여부 확인"""
        current_metrics = self.collect_system_metrics()
        
        if not current_metrics:
            return {"status": "error", "message": "메트릭 수집 실패"}
        
        violations = []
        alerts = []
        
        # 임계치 검사
        for metric, threshold in self.alert_thresholds.items():
            if metric in current_metrics:
                value = current_metrics[metric]
                if value > threshold:
                    violations.append({
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": "HIGH" if value > threshold * 1.5 else "MEDIUM"
                    })
                    
                    # 알람 생성
                    alerts.append({
                        "type": "SLO_VIOLATION",
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "timestamp": current_metrics["timestamp"],
                        "message": f"{metric} 임계치 초과: {value:.2f} > {threshold}"
                    })
        
        # 평균 응답 시간 계산 (최근 10개 샘플)
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        avg_response_time = sum(m.get("response_time_ms", 0) for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        # 오류율 계산 (최근 10개 샘플)
        recent_errors = sum(1 for m in recent_metrics if m.get("error_count", 0) > 0)
        error_rate = (recent_errors / len(recent_metrics)) * 100 if recent_metrics else 0
        
        result = {
            "status": "healthy" if not violations else "unhealthy",
            "timestamp": current_metrics["timestamp"],
            "uptime_seconds": current_metrics.get("uptime_seconds", 0),
            "current_metrics": current_metrics,
            "slo_violations": violations,
            "alerts": alerts,
            "summary": {
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": error_rate,
                "violation_count": len(violations),
                "alert_count": len(alerts)
            }
        }
        
        # 알람 로깅
        for alert in alerts:
            logger.warning(f"SLO 알람: {alert['message']}")
        
        return result
    
    def get_health_status(self) -> Dict[str, Any]:
        """헬스체크 상태 반환"""
        slo_status = self.check_slo_compliance()
        current_metrics = self.collect_system_metrics()
        
        # 개별 체크 상태
        checks = {}
        
        # CPU 체크
        cpu_usage = current_metrics.get("cpu_usage_percent", 0)
        checks["cpu"] = "ok" if cpu_usage < 70 else "warning" if cpu_usage < 90 else "critical"
        
        # 메모리 체크
        memory_usage = current_metrics.get("memory_usage_percent", 0)
        checks["memory"] = "ok" if memory_usage < 80 else "warning" if memory_usage < 95 else "critical"
        
        # 디스크 체크
        disk_usage = current_metrics.get("disk_usage_percent", 0)
        checks["disk"] = "ok" if disk_usage < 90 else "warning" if disk_usage < 95 else "critical"
        
        # 전체 상태 결정
        overall_status = "healthy"
        if any(status in ["critical"] for status in checks.values()):
            overall_status = "unhealthy"
        elif any(status in ["warning"] for status in checks.values()):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "version": "1.0.0",
            "git_sha": "abc1234",  # 실제로는 빌드 시 주입
            "uptime": current_metrics.get("uptime_seconds", 0),
            "checks": checks,
            "slo_compliance": slo_status["status"],
            "metrics": current_metrics
        }
    
    def record_response_time(self, response_time_ms: float):
        """응답 시간 기록"""
        if self.metrics_history:
            self.metrics_history[-1]["response_time_ms"] = response_time_ms
    
    def record_error(self, error_type: str, error_message: str):
        """오류 기록"""
        if self.metrics_history:
            current = self.metrics_history[-1]
            current["error_count"] = current.get("error_count", 0) + 1
            current["last_error"] = {
                "type": error_type,
                "message": error_message,
                "timestamp": time.time()
            }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """메트릭 요약 반환"""
        if not self.metrics_history:
            return {"message": "메트릭 데이터 없음"}
        
        recent_metrics = self.metrics_history[-20:]  # 최근 20개
        
        return {
            "sample_count": len(recent_metrics),
            "time_range_seconds": recent_metrics[-1]["timestamp"] - recent_metrics[0]["timestamp"] if len(recent_metrics) > 1 else 0,
            "averages": {
                "cpu_usage_percent": sum(m.get("cpu_usage_percent", 0) for m in recent_metrics) / len(recent_metrics),
                "memory_usage_percent": sum(m.get("memory_usage_percent", 0) for m in recent_metrics) / len(recent_metrics),
                "disk_usage_percent": sum(m.get("disk_usage_percent", 0) for m in recent_metrics) / len(recent_metrics)
            },
            "current_values": recent_metrics[-1] if recent_metrics else {},
            "slo_thresholds": self.alert_thresholds
        }

# 전역 인스턴스
slo_monitor = SLOMonitor()
