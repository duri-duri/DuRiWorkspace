#!/usr/bin/env python3
"""
DuRi 성능 모니터링 시스템 - Phase 1-3 Week 3 Day 8
실시간 성능 모니터링 및 분석을 제공하는 시스템

기능:
1. 실시간 성능 지표 수집
2. 성능 분석 및 트렌드 분석
3. 성능 알림 및 경고
4. 성능 최적화 제안
"""

import asyncio
import json
import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import statistics
import numpy as np
from collections import defaultdict, deque
import threading
import queue
import weakref

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 유형"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    ERROR = "error"
    CUSTOM = "custom"
    SYSTEM = "system"

class AlertLevel(Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class OptimizationType(Enum):
    """최적화 유형"""
    MEMORY = "memory"
    CPU = "cpu"
    NETWORK = "network"
    STORAGE = "storage"
    GENERAL = "general"

@dataclass
class PerformanceMetric:
    """성능 메트릭"""
    metric_id: str
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceAlert:
    """성능 알림"""
    alert_id: str
    alert_level: AlertLevel
    alert_message: str
    metric_name: str = ""
    threshold: float = 0.0
    current_value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimizationSuggestion:
    """최적화 제안"""
    suggestion_id: str
    optimization_type: OptimizationType
    suggestion_title: str
    suggestion_description: str
    expected_improvement: float = 0.0
    priority: str = "medium"
    timestamp: datetime = field(default_factory=datetime.now)
    implemented: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceReport:
    """성능 보고서"""
    report_id: str
    report_type: str
    start_time: datetime
    end_time: datetime
    metrics_summary: Dict[str, Any] = field(default_factory=dict)
    alerts_summary: Dict[str, Any] = field(default_factory=dict)
    suggestions_summary: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class PerformanceMonitoringSystem:
    """성능 모니터링 시스템"""
    
    def __init__(self):
        """초기화"""
        self.performance_metrics: Dict[str, PerformanceMetric] = {}
        self.performance_alerts: Dict[str, PerformanceAlert] = {}
        self.optimization_suggestions: Dict[str, OptimizationSuggestion] = {}
        self.performance_reports: Dict[str, PerformanceReport] = {}
        self.system_registry: Dict[str, Any] = {}
        
        # 모니터링 설정
        self.monitoring_config = {
            "collection_interval": 1.0,
            "retention_period": 86400,  # 24시간
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "response_time": 1000.0,
                "error_rate": 5.0
            },
            "optimization_thresholds": {
                "performance_degradation": 20.0,
                "resource_usage": 90.0,
                "error_increase": 10.0
            }
        }
        
        # 모니터링 데이터
        self.monitoring_metrics = {
            "total_metrics_collected": 0,
            "total_alerts_generated": 0,
            "total_suggestions_generated": 0,
            "average_performance_score": 0.0,
            "system_health_score": 0.0
        }
        
        # 메트릭 큐
        self.metric_queue = asyncio.Queue()
        self.alert_queue = asyncio.Queue()
        
        # 활성 모니터링
        self.active_monitoring: Set[str] = set()
        
        logger.info("성능 모니터링 시스템 초기화 완료")
    
    async def register_system(self, system_name: str, system_instance: Any) -> bool:
        """시스템 등록"""
        try:
            self.system_registry[system_name] = system_instance
            logger.info(f"시스템 등록 완료: {system_name}")
            return True
        except Exception as e:
            logger.error(f"시스템 등록 실패: {system_name} - {e}")
            return False
    
    async def collect_performance_metric(self, metric_type: MetricType, metric_name: str,
                                       value: float, unit: str = "", source: str = "") -> str:
        """성능 메트릭 수집"""
        metric_id = f"metric_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        performance_metric = PerformanceMetric(
            metric_id=metric_id,
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=unit,
            source=source
        )
        
        self.performance_metrics[metric_id] = performance_metric
        await self.metric_queue.put(performance_metric)
        
        # 메트릭 업데이트
        self.monitoring_metrics["total_metrics_collected"] += 1
        
        # 알림 확인
        await self._check_alert_thresholds(performance_metric)
        
        logger.info(f"성능 메트릭 수집: {metric_id} ({metric_name}: {value}{unit})")
        return metric_id
    
    async def generate_performance_alert(self, alert_level: AlertLevel, alert_message: str,
                                       metric_name: str = "", threshold: float = 0.0,
                                       current_value: float = 0.0) -> str:
        """성능 알림 생성"""
        alert_id = f"alert_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        performance_alert = PerformanceAlert(
            alert_id=alert_id,
            alert_level=alert_level,
            alert_message=alert_message,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value
        )
        
        self.performance_alerts[alert_id] = performance_alert
        await self.alert_queue.put(performance_alert)
        
        # 메트릭 업데이트
        self.monitoring_metrics["total_alerts_generated"] += 1
        
        logger.info(f"성능 알림 생성: {alert_id} ({alert_level.value})")
        return alert_id
    
    async def generate_optimization_suggestion(self, optimization_type: OptimizationType,
                                             suggestion_title: str, suggestion_description: str,
                                             expected_improvement: float = 0.0,
                                             priority: str = "medium") -> str:
        """최적화 제안 생성"""
        suggestion_id = f"suggestion_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # optimization_type이 문자열인 경우 enum으로 변환
        if isinstance(optimization_type, str):
            try:
                optimization_type = OptimizationType(optimization_type)
            except ValueError:
                optimization_type = OptimizationType.GENERAL
        
        optimization_suggestion = OptimizationSuggestion(
            suggestion_id=suggestion_id,
            optimization_type=optimization_type,
            suggestion_title=suggestion_title,
            suggestion_description=suggestion_description,
            expected_improvement=expected_improvement,
            priority=priority
        )
        
        self.optimization_suggestions[suggestion_id] = optimization_suggestion
        
        # 메트릭 업데이트
        self.monitoring_metrics["total_suggestions_generated"] += 1
        
        logger.info(f"최적화 제안 생성: {suggestion_id} ({optimization_type.value})")
        return suggestion_id
    
    async def analyze_performance_trends(self, metric_name: str, 
                                       time_range: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        end_time = datetime.now()
        start_time = end_time - time_range
        
        # 시간 범위 내 메트릭 필터링
        relevant_metrics = [
            metric for metric in self.performance_metrics.values()
            if metric.metric_name == metric_name and start_time <= metric.timestamp <= end_time
        ]
        
        if not relevant_metrics:
            return {"error": "분석할 메트릭이 없습니다."}
        
        # 트렌드 분석
        values = [metric.value for metric in relevant_metrics]
        timestamps = [metric.timestamp for metric in relevant_metrics]
        
        analysis = {
            "metric_name": metric_name,
            "time_range": str(time_range),
            "data_points": len(values),
            "min_value": min(values),
            "max_value": max(values),
            "average_value": statistics.mean(values),
            "median_value": statistics.median(values),
            "std_deviation": statistics.stdev(values) if len(values) > 1 else 0.0,
            "trend": self._calculate_trend(values),
            "timestamps": timestamps,
            "values": values
        }
        
        logger.info(f"성능 트렌드 분석 완료: {metric_name}")
        return analysis
    
    async def generate_performance_report(self, report_type: str = "comprehensive",
                                        time_range: timedelta = timedelta(hours=24)) -> str:
        """성능 보고서 생성"""
        report_id = f"report_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        end_time = datetime.now()
        start_time = end_time - time_range
        
        # 시간 범위 내 데이터 수집
        relevant_metrics = [
            metric for metric in self.performance_metrics.values()
            if start_time <= metric.timestamp <= end_time
        ]
        
        relevant_alerts = [
            alert for alert in self.performance_alerts.values()
            if start_time <= alert.timestamp <= end_time
        ]
        
        relevant_suggestions = [
            suggestion for suggestion in self.optimization_suggestions.values()
            if start_time <= suggestion.timestamp <= end_time
        ]
        
        # 메트릭 요약
        metrics_summary = self._generate_metrics_summary(relevant_metrics)
        
        # 알림 요약
        alerts_summary = self._generate_alerts_summary(relevant_alerts)
        
        # 제안 요약
        suggestions_summary = self._generate_suggestions_summary(relevant_suggestions)
        
        performance_report = PerformanceReport(
            report_id=report_id,
            report_type=report_type,
            start_time=start_time,
            end_time=end_time,
            metrics_summary=metrics_summary,
            alerts_summary=alerts_summary,
            suggestions_summary=suggestions_summary
        )
        
        self.performance_reports[report_id] = performance_report
        
        logger.info(f"성능 보고서 생성: {report_id} ({report_type})")
        return report_id
    
    async def get_system_health_score(self) -> float:
        """시스템 건강 점수 계산"""
        if not self.performance_metrics:
            return 0.0
        
        # 최근 메트릭 분석 (최근 1시간)
        recent_metrics = [
            metric for metric in self.performance_metrics.values()
            if metric.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_metrics:
            return 0.0
        
        # 건강 점수 계산
        health_scores = []
        
        for metric in recent_metrics:
            if metric.metric_name == "cpu_usage":
                health_scores.append(max(0, 100 - metric.value))
            elif metric.metric_name == "memory_usage":
                health_scores.append(max(0, 100 - metric.value))
            elif metric.metric_name == "response_time":
                health_scores.append(max(0, 100 - (metric.value / 1000 * 100)))
            elif metric.metric_name == "error_rate":
                health_scores.append(max(0, 100 - metric.value * 10))
            else:
                health_scores.append(80.0)  # 기본 점수
        
        health_score = statistics.mean(health_scores) if health_scores else 0.0
        self.monitoring_metrics["system_health_score"] = health_score
        
        return health_score
    
    async def get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """성능 권장사항 생성"""
        recommendations = []
        
        # 시스템 건강 점수 확인
        health_score = await self.get_system_health_score()
        
        if health_score < 70:
            recommendations.append({
                "type": "system_health",
                "priority": "high",
                "message": f"시스템 건강 점수가 낮습니다 ({health_score:.1f}%). 성능 최적화가 필요합니다.",
                "action": "optimize_system_performance"
            })
        
        # 메트릭 기반 권장사항
        metric_recommendations = await self._analyze_metric_recommendations()
        recommendations.extend(metric_recommendations)
        
        # 알림 기반 권장사항
        alert_recommendations = await self._analyze_alert_recommendations()
        recommendations.extend(alert_recommendations)
        
        return recommendations
    
    async def _check_alert_thresholds(self, metric: PerformanceMetric):
        """알림 임계값 확인"""
        thresholds = self.monitoring_config["alert_thresholds"]
        
        if metric.metric_name in thresholds:
            threshold = thresholds[metric.metric_name]
            
            if metric.value > threshold:
                alert_level = AlertLevel.WARNING if metric.value < threshold * 1.5 else AlertLevel.ERROR
                alert_message = f"{metric.metric_name}이 임계값({threshold})을 초과했습니다. 현재 값: {metric.value}"
                
                await self.generate_performance_alert(
                    alert_level,
                    alert_message,
                    metric.metric_name,
                    threshold,
                    metric.value
                )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return "stable"
        
        # 선형 회귀를 사용한 트렌드 계산
        x = list(range(len(values)))
        y = values
        
        # 기울기 계산
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return "stable"
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_metrics_summary(self, metrics: List[PerformanceMetric]) -> Dict[str, Any]:
        """메트릭 요약 생성"""
        if not metrics:
            return {}
        
        # 메트릭별 그룹화
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric.value)
        
        summary = {}
        for metric_name, values in metric_groups.items():
            summary[metric_name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "average": statistics.mean(values),
                "median": statistics.median(values)
            }
        
        return summary
    
    def _generate_alerts_summary(self, alerts: List[PerformanceAlert]) -> Dict[str, Any]:
        """알림 요약 생성"""
        if not alerts:
            return {}
        
        # 알림 레벨별 그룹화
        alert_groups = defaultdict(list)
        for alert in alerts:
            alert_groups[alert.alert_level.value].append(alert)
        
        summary = {}
        for level, level_alerts in alert_groups.items():
            summary[level] = {
                "count": len(level_alerts),
                "resolved": len([a for a in level_alerts if a.resolved]),
                "unresolved": len([a for a in level_alerts if not a.resolved])
            }
        
        return summary
    
    def _generate_suggestions_summary(self, suggestions: List[OptimizationSuggestion]) -> Dict[str, Any]:
        """제안 요약 생성"""
        if not suggestions:
            return {}
        
        # 최적화 유형별 그룹화
        suggestion_groups = defaultdict(list)
        for suggestion in suggestions:
            suggestion_groups[suggestion.optimization_type.value].append(suggestion)
        
        summary = {}
        for opt_type, type_suggestions in suggestion_groups.items():
            summary[opt_type] = {
                "count": len(type_suggestions),
                "implemented": len([s for s in type_suggestions if s.implemented]),
                "pending": len([s for s in type_suggestions if not s.implemented]),
                "average_improvement": statistics.mean([s.expected_improvement for s in type_suggestions])
            }
        
        return summary
    
    async def _analyze_metric_recommendations(self) -> List[Dict[str, Any]]:
        """메트릭 기반 권장사항 분석"""
        recommendations = []
        
        # 최근 메트릭 분석
        recent_metrics = [
            metric for metric in self.performance_metrics.values()
            if metric.timestamp >= datetime.now() - timedelta(hours=1)
        ]
        
        if not recent_metrics:
            return recommendations
        
        # 메트릭별 분석
        metric_groups = defaultdict(list)
        for metric in recent_metrics:
            metric_groups[metric.metric_name].append(metric.value)
        
        for metric_name, values in metric_groups.items():
            avg_value = statistics.mean(values)
            
            if metric_name == "cpu_usage" and avg_value > 80:
                recommendations.append({
                    "type": "cpu_optimization",
                    "priority": "high",
                    "message": f"CPU 사용률이 높습니다 ({avg_value:.1f}%). CPU 최적화가 필요합니다.",
                    "action": "optimize_cpu_usage"
                })
            elif metric_name == "memory_usage" and avg_value > 85:
                recommendations.append({
                    "type": "memory_optimization",
                    "priority": "high",
                    "message": f"메모리 사용률이 높습니다 ({avg_value:.1f}%). 메모리 최적화가 필요합니다.",
                    "action": "optimize_memory_usage"
                })
            elif metric_name == "response_time" and avg_value > 1000:
                recommendations.append({
                    "type": "response_time_optimization",
                    "priority": "medium",
                    "message": f"응답 시간이 느립니다 ({avg_value:.1f}ms). 성능 최적화가 필요합니다.",
                    "action": "optimize_response_time"
                })
        
        return recommendations
    
    async def _analyze_alert_recommendations(self) -> List[Dict[str, Any]]:
        """알림 기반 권장사항 분석"""
        recommendations = []
        
        # 최근 알림 분석
        recent_alerts = [
            alert for alert in self.performance_alerts.values()
            if alert.timestamp >= datetime.now() - timedelta(hours=1) and not alert.resolved
        ]
        
        if not recent_alerts:
            return recommendations
        
        # 알림 레벨별 분석
        critical_alerts = [alert for alert in recent_alerts if alert.alert_level == AlertLevel.CRITICAL]
        error_alerts = [alert for alert in recent_alerts if alert.alert_level == AlertLevel.ERROR]
        
        if critical_alerts:
            recommendations.append({
                "type": "critical_alert",
                "priority": "critical",
                "message": f"치명적 알림이 {len(critical_alerts)}개 있습니다. 즉시 조치가 필요합니다.",
                "action": "resolve_critical_alerts"
            })
        
        if error_alerts:
            recommendations.append({
                "type": "error_alert",
                "priority": "high",
                "message": f"오류 알림이 {len(error_alerts)}개 있습니다. 조치가 필요합니다.",
                "action": "resolve_error_alerts"
            })
        
        return recommendations
    
    def get_monitoring_metrics(self) -> Dict[str, Any]:
        """모니터링 메트릭 반환"""
        return self.monitoring_metrics.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "registered_systems": list(self.system_registry.keys()),
            "total_metrics": len(self.performance_metrics),
            "total_alerts": len(self.performance_alerts),
            "total_suggestions": len(self.optimization_suggestions),
            "total_reports": len(self.performance_reports),
            "active_monitoring": len(self.active_monitoring)
        }

async def test_performance_monitoring_system():
    """성능 모니터링 시스템 테스트"""
    print("=== 성능 모니터링 시스템 테스트 시작 ===")
    
    # 성능 모니터링 시스템 초기화
    monitoring_system = PerformanceMonitoringSystem()
    
    # 가상 시스템 등록
    class MockSystem:
        def __init__(self, name: str):
            self.name = name
        
        def get_system_status(self):
            return {"system": self.name, "status": "active"}
    
    # 시스템 등록
    systems = ["lida_attention", "realtime_learning", "dynamic_reasoning"]
    for system_name in systems:
        mock_system = MockSystem(system_name)
        await monitoring_system.register_system(system_name, mock_system)
    
    print(f"등록된 시스템 수: {len(monitoring_system.system_registry)}")
    
    # 1. 성능 메트릭 수집 테스트
    print("\n1. 성능 메트릭 수집 테스트")
    metric_ids = []
    for i in range(5):
        metric_id = await monitoring_system.collect_performance_metric(
            MetricType.PERFORMANCE,
            "cpu_usage",
            np.random.uniform(20, 90),
            "%",
            "test_system"
        )
        metric_ids.append(metric_id)
    
    print(f"수집된 메트릭 수: {len(monitoring_system.performance_metrics)}")
    
    # 2. 성능 알림 생성 테스트
    print("\n2. 성능 알림 생성 테스트")
    alert_id = await monitoring_system.generate_performance_alert(
        AlertLevel.WARNING,
        "CPU 사용률이 높습니다.",
        "cpu_usage",
        80.0,
        85.0
    )
    print(f"생성된 알림: {alert_id}")
    
    # 3. 최적화 제안 생성 테스트
    print("\n3. 최적화 제안 생성 테스트")
    suggestion_id = await monitoring_system.generate_optimization_suggestion(
        OptimizationType.CPU,
        "CPU 최적화",
        "CPU 사용률을 줄이기 위해 불필요한 프로세스를 종료하세요.",
        15.0,
        "high"
    )
    print(f"생성된 제안: {suggestion_id}")
    
    # 4. 성능 트렌드 분석 테스트
    print("\n4. 성능 트렌드 분석 테스트")
    trend_analysis = await monitoring_system.analyze_performance_trends("cpu_usage")
    print(f"트렌드 분석 결과: {trend_analysis}")
    
    # 5. 성능 보고서 생성 테스트
    print("\n5. 성능 보고서 생성 테스트")
    report_id = await monitoring_system.generate_performance_report("comprehensive")
    print(f"생성된 보고서: {report_id}")
    
    # 6. 시스템 건강 점수 계산 테스트
    print("\n6. 시스템 건강 점수 계산 테스트")
    health_score = await monitoring_system.get_system_health_score()
    print(f"시스템 건강 점수: {health_score:.1f}%")
    
    # 7. 성능 권장사항 생성 테스트
    print("\n7. 성능 권장사항 생성 테스트")
    recommendations = await monitoring_system.get_performance_recommendations()
    print(f"권장사항 수: {len(recommendations)}")
    
    # 8. 메트릭 확인
    print("\n8. 메트릭 확인")
    monitoring_metrics = monitoring_system.get_monitoring_metrics()
    system_status = monitoring_system.get_system_status()
    
    print(f"모니터링 메트릭: {monitoring_metrics}")
    print(f"시스템 상태: {system_status}")
    
    print("\n=== 성능 모니터링 시스템 테스트 완료 ===")
    
    return {
        "monitoring_metrics": monitoring_metrics,
        "system_status": system_status,
        "health_score": health_score,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    asyncio.run(test_performance_monitoring_system()) 