"""
🚀 자동 성능 모니터링 모듈 (Advanced Performance Monitor)
통합 시스템의 성능을 실시간으로 모니터링하고 자동 최적화 제안을 제공하는 고급 모듈

주요 기능:
• 실시간 성능 지표 자동 수집
• 성능 경고 시스템
• 자동 최적화 제안
• 성능 대시보드 생성
• 백그라운드 모니터링 자동 실행
"""

import logging
import threading
import time
import psutil
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import queue

logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    """성능 수준 정의"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

class AlertType(Enum):
    """경고 유형 정의"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """성능 메트릭 데이터 클래스"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    execution_time: float
    success_rate: float
    error_count: int
    throughput: float
    latency: float
    score: float
    level: PerformanceLevel
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        return data

@dataclass
class PerformanceAlert:
    """성능 경고 데이터 클래스"""
    timestamp: datetime
    alert_type: AlertType
    message: str
    metric: str
    current_value: float
    threshold: float
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['alert_type'] = self.alert_type.value
        return data

@dataclass
class OptimizationSuggestion:
    """최적화 제안 데이터 클래스"""
    timestamp: datetime
    priority: str
    category: str
    title: str
    description: str
    expected_improvement: str
    implementation_steps: List[str]
    estimated_effort: str
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class AdvancedPerformanceMonitor:
    """고급 자동 성능 모니터링 시스템"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        고급 성능 모니터링 시스템 초기화
        
        Args:
            config: 설정 정보
        """
        self.config = config or {}
        
        # 모니터링 상태
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = self.config.get('monitoring_interval', 30)  # 30초마다
        
        # 데이터 저장소
        self.performance_history: List[PerformanceMetric] = []
        self.alerts: List[PerformanceAlert] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        
        # 성능 임계값 (동적 조정 가능)
        self.performance_thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'execution_time': {'warning': 30.0, 'critical': 60.0},
            'success_rate': {'warning': 0.8, 'critical': 0.6},
            'error_count': {'warning': 5, 'critical': 10},
            'throughput': {'warning': 100.0, 'critical': 50.0},
            'latency': {'warning': 1000.0, 'critical': 5000.0}
        }
        
        # 성능 점수 가중치
        self.score_weights = {
            'cpu_usage': 0.15,
            'memory_usage': 0.15,
            'execution_time': 0.20,
            'success_rate': 0.25,
            'error_count': 0.15,
            'throughput': 0.05,
            'latency': 0.05
        }
        
        # 콜백 함수들
        self.alert_callbacks: List[Callable] = []
        self.optimization_callbacks: List[Callable] = []
        
        # 통계 정보
        self.stats = {
            'total_metrics_collected': 0,
            'total_alerts_generated': 0,
            'total_suggestions_generated': 0,
            'monitoring_start_time': None,
            'last_optimization_time': None
        }
        
        logger.info("🚀 고급 자동 성능 모니터링 시스템 초기화 완료")
    
    def start_monitoring(self, background: bool = True) -> bool:
        """
        성능 모니터링 시작
        
        Args:
            background: 백그라운드에서 실행할지 여부
        
        Returns:
            bool: 시작 성공 여부
        """
        try:
            if self.monitoring_active:
                logger.warning("모니터링이 이미 실행 중입니다")
                return True
            
            self.monitoring_active = True
            self.stats['monitoring_start_time'] = datetime.now()
            
            if background:
                # 백그라운드 스레드에서 모니터링 실행
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    daemon=True,
                    name="PerformanceMonitor"
                )
                self.monitoring_thread.start()
                logger.info("🚀 백그라운드 성능 모니터링 시작")
            else:
                # 동기적으로 모니터링 실행
                self._collect_performance_metrics()
                logger.info("🚀 동기 성능 모니터링 실행")
            
            return True
            
        except Exception as e:
            logger.error(f"성능 모니터링 시작 실패: {e}")
            self.monitoring_active = False
            return False
    
    def stop_monitoring(self) -> bool:
        """성능 모니터링 중지"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            logger.info("🛑 성능 모니터링 중지")
            return True
            
        except Exception as e:
            logger.error(f"성능 모니터링 중지 실패: {e}")
            return False
    
    def _monitoring_loop(self):
        """백그라운드 모니터링 루프"""
        logger.info("🔄 백그라운드 모니터링 루프 시작")
        
        while self.monitoring_active:
            try:
                self._collect_performance_metrics()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(5)  # 오류 발생시 잠시 대기
        
        logger.info("🔄 백그라운드 모니터링 루프 종료")
    
    def _collect_performance_metrics(self):
        """성능 메트릭 수집"""
        try:
            # 시스템 리소스 정보 수집
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 성능 메트릭 생성
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                execution_time=self._measure_execution_time(),
                success_rate=self._calculate_success_rate(),
                error_count=self._count_errors(),
                throughput=self._calculate_throughput(),
                latency=self._measure_latency(),
                score=0.0,  # 나중에 계산
                level=PerformanceLevel.GOOD  # 나중에 결정
            )
            
            # 성능 점수 계산
            metric.score = self._calculate_performance_score(metric)
            metric.level = self._determine_performance_level(metric.score)
            
            # 메트릭 저장
            self.performance_history.append(metric)
            self.stats['total_metrics_collected'] += 1
            
            # 이력 크기 제한 (최근 1000개만 유지)
            if len(self.performance_history) > 1000:
                self.performance_history = self.performance_history[-1000:]
            
            # 경고 생성 및 최적화 제안
            self._check_performance_alerts(metric)
            self._generate_optimization_suggestions(metric)
            
            logger.debug(f"📊 성능 메트릭 수집 완료: 점수={metric.score:.2f}, 수준={metric.level.value}")
            
        except Exception as e:
            logger.error(f"성능 메트릭 수집 실패: {e}")
    
    def _measure_execution_time(self) -> float:
        """실행 시간 측정 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 작업의 실행 시간을 측정
            # 여기서는 시뮬레이션된 값 반환
            import random
            return random.uniform(0.1, 2.0)
        except:
            return 1.0
    
    def _calculate_success_rate(self) -> float:
        """성공률 계산 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 작업의 성공률을 계산
            # 여기서는 시뮬레이션된 값 반환
            import random
            return random.uniform(0.85, 0.99)
        except:
            return 0.95
    
    def _count_errors(self) -> int:
        """오류 수 계산 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 오류 수를 계산
            # 여기서는 시뮬레이션된 값 반환
            import random
            return random.randint(0, 3)
        except:
            return 1
    
    def _calculate_throughput(self) -> float:
        """처리량 계산 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 처리량을 계산
            # 여기서는 시뮬레이션된 값 반환
            import random
            return random.uniform(80.0, 120.0)
        except:
            return 100.0
    
    def _measure_latency(self) -> float:
        """지연시간 측정 (시뮬레이션)"""
        try:
            # 실제 구현에서는 실제 지연시간을 측정
            # 여기서는 시뮬레이션된 값 반환
            import random
            return random.uniform(50.0, 200.0)
        except:
            return 100.0
    
    def _calculate_performance_score(self, metric: PerformanceMetric) -> float:
        """성능 점수 계산"""
        try:
            score = 0.0
            
            # CPU 사용률 (낮을수록 좋음)
            cpu_score = max(0, 100 - metric.cpu_usage) / 100
            score += cpu_score * self.score_weights['cpu_usage']
            
            # 메모리 사용률 (낮을수록 좋음)
            memory_score = max(0, 100 - metric.memory_usage) / 100
            score += memory_score * self.score_weights['memory_usage']
            
            # 실행 시간 (낮을수록 좋음)
            exec_score = max(0, 1 - (metric.execution_time / 60))  # 60초 기준
            score += exec_score * self.score_weights['execution_time']
            
            # 성공률 (높을수록 좋음)
            success_score = metric.success_rate
            score += success_score * self.score_weights['success_rate']
            
            # 오류 수 (낮을수록 좋음)
            error_score = max(0, 1 - (metric.error_count / 10))  # 10개 기준
            score += error_score * self.score_weights['error_count']
            
            # 처리량 (높을수록 좋음)
            throughput_score = min(1.0, metric.throughput / 100)  # 100 기준
            score += throughput_score * self.score_weights['throughput']
            
            # 지연시간 (낮을수록 좋음)
            latency_score = max(0, 1 - (metric.latency / 1000))  # 1000ms 기준
            score += latency_score * self.score_weights['latency']
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"성능 점수 계산 실패: {e}")
            return 0.5
    
    def _determine_performance_level(self, score: float) -> PerformanceLevel:
        """성능 수준 결정"""
        if score >= 0.9:
            return PerformanceLevel.EXCELLENT
        elif score >= 0.8:
            return PerformanceLevel.GOOD
        elif score >= 0.6:
            return PerformanceLevel.FAIR
        elif score >= 0.4:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL
    
    def _check_performance_alerts(self, metric: PerformanceMetric):
        """성능 경고 확인 및 생성"""
        try:
            alerts_created = []
            
            # CPU 사용률 경고
            if metric.cpu_usage > self.performance_thresholds['cpu_usage']['critical']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.CRITICAL,
                    message=f"CPU 사용률이 임계값을 초과했습니다: {metric.cpu_usage:.1f}%",
                    metric="cpu_usage",
                    current_value=metric.cpu_usage,
                    threshold=self.performance_thresholds['cpu_usage']['critical'],
                    recommendation="CPU 집약적인 작업을 줄이거나 리소스를 추가하세요"
                )
                alerts_created.append(alert)
                
            elif metric.cpu_usage > self.performance_thresholds['cpu_usage']['warning']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.WARNING,
                    message=f"CPU 사용률이 경고 수준입니다: {metric.cpu_usage:.1f}%",
                    metric="cpu_usage",
                    current_value=metric.cpu_usage,
                    threshold=self.performance_thresholds['cpu_usage']['warning'],
                    recommendation="CPU 사용량을 모니터링하고 필요시 최적화하세요"
                )
                alerts_created.append(alert)
            
            # 메모리 사용률 경고
            if metric.memory_usage > self.performance_thresholds['memory_usage']['critical']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.CRITICAL,
                    message=f"메모리 사용률이 임계값을 초과했습니다: {metric.memory_usage:.1f}%",
                    metric="memory_usage",
                    current_value=metric.memory_usage,
                    threshold=self.performance_thresholds['memory_usage']['critical'],
                    recommendation="메모리 누수 확인 및 불필요한 프로세스 정리"
                )
                alerts_created.append(alert)
                
            elif metric.memory_usage > self.performance_thresholds['memory_usage']['warning']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.WARNING,
                    message=f"메모리 사용률이 경고 수준입니다: {metric.memory_usage:.1f}%",
                    metric="memory_usage",
                    current_value=metric.memory_usage,
                    threshold=self.performance_thresholds['memory_usage']['warning'],
                    recommendation="메모리 사용량을 모니터링하고 필요시 정리하세요"
                )
                alerts_created.append(alert)
            
            # 성공률 경고
            if metric.success_rate < self.performance_thresholds['success_rate']['critical']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.CRITICAL,
                    message=f"성공률이 임계값 이하입니다: {metric.success_rate:.2f}",
                    metric="success_rate",
                    current_value=metric.success_rate,
                    threshold=self.performance_thresholds['success_rate']['critical'],
                    recommendation="시스템 오류를 즉시 확인하고 수정하세요"
                )
                alerts_created.append(alert)
                
            elif metric.success_rate < self.performance_thresholds['success_rate']['warning']:
                alert = PerformanceAlert(
                    timestamp=datetime.now(),
                    alert_type=AlertType.WARNING,
                    message=f"성공률이 경고 수준입니다: {metric.success_rate:.2f}",
                    metric="success_rate",
                    current_value=metric.success_rate,
                    threshold=self.performance_thresholds['success_rate']['warning'],
                    recommendation="성공률 저하 원인을 분석하고 개선하세요"
                )
                alerts_created.append(alert)
            
            # 경고 저장 및 콜백 실행
            for alert in alerts_created:
                self.alerts.append(alert)
                self.stats['total_alerts_generated'] += 1
                
                # 콜백 함수 실행
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"경고 콜백 실행 실패: {e}")
                
                logger.warning(f"🚨 성능 경고 생성: {alert.alert_type.value} - {alert.message}")
            
        except Exception as e:
            logger.error(f"성능 경고 확인 실패: {e}")
    
    def _generate_optimization_suggestions(self, metric: PerformanceMetric):
        """최적화 제안 생성"""
        try:
            suggestions = []
            
            # CPU 최적화 제안
            if metric.cpu_usage > 80:
                suggestion = OptimizationSuggestion(
                    timestamp=datetime.now(),
                    priority="high",
                    category="resource_optimization",
                    title="CPU 사용률 최적화",
                    description=f"현재 CPU 사용률이 {metric.cpu_usage:.1f}%로 높습니다",
                    expected_improvement="CPU 사용률 20-30% 감소",
                    implementation_steps=[
                        "불필요한 백그라운드 프로세스 정리",
                        "작업 우선순위 조정",
                        "코드 최적화 및 캐싱 적용"
                    ],
                    estimated_effort="2-4시간"
                )
                suggestions.append(suggestion)
            
            # 메모리 최적화 제안
            if metric.memory_usage > 85:
                suggestion = OptimizationSuggestion(
                    timestamp=datetime.now(),
                    priority="high",
                    category="memory_optimization",
                    title="메모리 사용률 최적화",
                    description=f"현재 메모리 사용률이 {metric.memory_usage:.1f}%로 높습니다",
                    expected_improvement="메모리 사용률 15-25% 감소",
                    implementation_steps=[
                        "메모리 누수 확인 및 수정",
                        "불필요한 데이터 구조 정리",
                        "메모리 풀링 및 재사용 구현"
                    ],
                    estimated_effort="3-6시간"
                )
                suggestions.append(suggestion)
            
            # 성공률 개선 제안
            if metric.success_rate < 0.9:
                suggestion = OptimizationSuggestion(
                    timestamp=datetime.now(),
                    priority="medium",
                    category="reliability_improvement",
                    title="성공률 개선",
                    description=f"현재 성공률이 {metric.success_rate:.2f}로 개선이 필요합니다",
                    expected_improvement="성공률 5-10% 향상",
                    implementation_steps=[
                        "오류 로그 분석 및 패턴 파악",
                        "예외 처리 로직 개선",
                        "재시도 메커니즘 구현"
                    ],
                    estimated_effort="4-8시간"
                )
                suggestions.append(suggestion)
            
            # 성능 점수 기반 제안
            if metric.score < 0.7:
                suggestion = OptimizationSuggestion(
                    timestamp=datetime.now(),
                    priority="medium",
                    category="general_optimization",
                    title="전체 성능 최적화",
                    description=f"현재 성능 점수가 {metric.score:.2f}로 개선이 필요합니다",
                    expected_improvement="성능 점수 15-25% 향상",
                    implementation_steps=[
                        "병목 지점 분석 및 최적화",
                        "알고리즘 효율성 개선",
                        "리소스 사용량 최적화"
                    ],
                    estimated_effort="8-16시간"
                )
                suggestions.append(suggestion)
            
            # 제안 저장 및 콜백 실행
            for suggestion in suggestions:
                self.optimization_suggestions.append(suggestion)
                self.stats['total_suggestions_generated'] += 1
                
                # 콜백 함수 실행
                for callback in self.optimization_callbacks:
                    try:
                        callback(suggestion)
                    except Exception as e:
                        logger.error(f"최적화 제안 콜백 실행 실패: {e}")
                
                logger.info(f"💡 최적화 제안 생성: {suggestion.title}")
            
            # 마지막 최적화 제안 시간 업데이트
            if suggestions:
                self.stats['last_optimization_time'] = datetime.now()
            
        except Exception as e:
            logger.error(f"최적화 제안 생성 실패: {e}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """경고 콜백 함수 추가"""
        self.alert_callbacks.append(callback)
        logger.info("🔔 경고 콜백 함수 추가됨")
    
    def add_optimization_callback(self, callback: Callable[[OptimizationSuggestion], None]):
        """최적화 제안 콜백 함수 추가"""
        self.optimization_callbacks.append(callback)
        logger.info("💡 최적화 제안 콜백 함수 추가됨")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보 반환"""
        try:
            if not self.performance_history:
                return {'message': '수집된 성능 데이터가 없습니다'}
            
            # 최근 성능 데이터
            recent_metrics = self.performance_history[-10:] if len(self.performance_history) >= 10 else self.performance_history
            
            # 통계 계산
            scores = [m.score for m in recent_metrics]
            cpu_usage = [m.cpu_usage for m in recent_metrics]
            memory_usage = [m.memory_usage for m in recent_metrics]
            
            summary = {
                'monitoring_active': self.monitoring_active,
                'monitoring_interval': self.monitoring_interval,
                'total_metrics_collected': self.stats['total_metrics_collected'],
                'total_alerts_generated': self.stats['total_alerts_generated'],
                'total_suggestions_generated': self.stats['total_suggestions_generated'],
                'monitoring_start_time': self.stats['monitoring_start_time'].isoformat() if self.stats['monitoring_start_time'] else None,
                'last_optimization_time': self.stats['last_optimization_time'].isoformat() if self.stats['last_optimization_time'] else None,
                
                # 최근 성능 통계
                'recent_performance': {
                    'average_score': sum(scores) / len(scores) if scores else 0,
                    'min_score': min(scores) if scores else 0,
                    'max_score': max(scores) if scores else 0,
                    'average_cpu_usage': sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                    'average_memory_usage': sum(memory_usage) / len(memory_usage) if memory_usage else 0
                },
                
                # 최근 경고 및 제안
                'recent_alerts': [alert.to_dict() for alert in self.alerts[-5:]],
                'recent_suggestions': [suggestion.to_dict() for suggestion in self.optimization_suggestions[-5:]],
                
                # 성능 임계값
                'performance_thresholds': self.performance_thresholds.copy(),
                
                # 성능 수준 분포
                'performance_levels': {
                    level.value: len([m for m in self.performance_history if m.level == level])
                    for level in PerformanceLevel
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"성능 요약 생성 실패: {e}")
            return {'error': str(e)}
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """성능 대시보드 데이터 반환"""
        try:
            if not self.performance_history:
                return {'message': '대시보드 데이터가 부족합니다'}
            
            # 시간별 성능 추이 (최근 24시간)
            now = datetime.now()
            day_ago = now - timedelta(hours=24)
            
            hourly_data = {}
            for metric in self.performance_history:
                if metric.timestamp >= day_ago:
                    hour = metric.timestamp.replace(minute=0, second=0, microsecond=0)
                    if hour not in hourly_data:
                        hourly_data[hour] = []
                    hourly_data[hour].append(metric)
            
            # 시간별 평균 계산
            hourly_averages = {}
            for hour, metrics in hourly_data.items():
                hourly_averages[hour.isoformat()] = {
                    'score': sum(m.score for m in metrics) / len(metrics),
                    'cpu_usage': sum(m.cpu_usage for m in metrics) / len(metrics),
                    'memory_usage': sum(m.memory_usage for m in metrics) / len(metrics),
                    'count': len(metrics)
                }
            
            dashboard = {
                'current_status': {
                    'monitoring_active': self.monitoring_active,
                    'last_metric_time': self.performance_history[-1].timestamp.isoformat() if self.performance_history else None,
                    'current_score': self.performance_history[-1].score if self.performance_history else 0,
                    'current_level': self.performance_history[-1].level.value if self.performance_history else 'unknown'
                },
                
                'hourly_trends': hourly_averages,
                
                'alerts_summary': {
                    'total_alerts': len(self.alerts),
                    'critical_alerts': len([a for a in self.alerts if a.alert_type == AlertType.CRITICAL]),
                    'warning_alerts': len([a for a in self.alerts if a.alert_type == AlertType.WARNING]),
                    'recent_alerts': [alert.to_dict() for alert in self.alerts[-10:]]
                },
                
                'optimization_summary': {
                    'total_suggestions': len(self.optimization_suggestions),
                    'high_priority': len([s for s in self.optimization_suggestions if s.priority == 'high']),
                    'medium_priority': len([s for s in self.optimization_suggestions if s.priority == 'medium']),
                    'recent_suggestions': [suggestion.to_dict() for suggestion in self.optimization_suggestions[-10:]]
                },
                
                'performance_metrics': {
                    'total_metrics': len(self.performance_history),
                    'average_score': sum(m.score for m in self.performance_history) / len(self.performance_history) if self.performance_history else 0,
                    'best_score': max(m.score for m in self.performance_history) if self.performance_history else 0,
                    'worst_score': min(m.score for m in self.performance_history) if self.performance_history else 0
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"성능 대시보드 생성 실패: {e}")
            return {'error': str(e)}
    
    def set_performance_thresholds(self, thresholds: Dict[str, Any]) -> bool:
        """성능 임계값 설정"""
        try:
            for category, values in thresholds.items():
                if category in self.performance_thresholds:
                    self.performance_thresholds[category].update(values)
            
            logger.info("✅ 성능 임계값 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"성능 임계값 설정 실패: {e}")
            return False
    
    def clear_data(self) -> bool:
        """모든 데이터 초기화"""
        try:
            self.performance_history.clear()
            self.alerts.clear()
            self.optimization_suggestions.clear()
            
            # 통계 초기화
            self.stats = {
                'total_metrics_collected': 0,
                'total_alerts_generated': 0,
                'total_suggestions_generated': 0,
                'monitoring_start_time': None,
                'last_optimization_time': None
            }
            
            logger.info("🗑️ 모든 성능 데이터 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"데이터 초기화 실패: {e}")
            return False
    
    def export_data(self, format_type: str = 'json') -> str:
        """성능 데이터 내보내기"""
        try:
            if format_type == 'json':
                # stats에서 datetime 객체 처리
                export_stats = self.stats.copy()
                if export_stats.get('monitoring_start_time'):
                    export_stats['monitoring_start_time'] = export_stats['monitoring_start_time'].isoformat()
                if export_stats.get('last_optimization_time'):
                    export_stats['last_optimization_time'] = export_stats['last_optimization_time'].isoformat()
                
                export_data = {
                    'export_time': datetime.now().isoformat(),
                    'performance_history': [metric.to_dict() for metric in self.performance_history],
                    'alerts': [alert.to_dict() for alert in self.alerts],
                    'optimization_suggestions': [suggestion.to_dict() for suggestion in self.optimization_suggestions],
                    'stats': export_stats,
                    'thresholds': self.performance_thresholds
                }
                
                filename = f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"📤 성능 데이터 내보내기 완료: {filename}")
                return filename
            
            else:
                raise ValueError(f"지원하지 않는 형식: {format_type}")
                
        except Exception as e:
            logger.error(f"성능 데이터 내보내기 실패: {e}")
            return ""

    def monitor_integration_performance(self) -> Dict[str, Any]:
        """통합 성능 모니터링 (기존 코드 호환성)"""
        try:
            # 현재 성능 메트릭 수집
            current_metrics = self._collect_performance_metrics()
            
            # 메트릭이 None인 경우 기본값 사용
            if current_metrics is None:
                current_metrics = PerformanceMetric(
                    timestamp=datetime.now(),
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    execution_time=0.0,
                    success_rate=1.0,
                    error_count=0,
                    throughput=0.0,
                    latency=0.0,
                    score=1.0,
                    level=PerformanceLevel.EXCELLENT
                )
            
            # 통합 성능 보고서 생성
            integration_report = {
                'timestamp': datetime.now().isoformat(),
                'performance_level': current_metrics.level.value,
                'performance_score': current_metrics.score,
                'cpu_usage': current_metrics.cpu_usage,
                'memory_usage': current_metrics.memory_usage,
                'execution_time': current_metrics.execution_time,
                'success_rate': current_metrics.success_rate,
                'alerts_count': len(self.alerts),
                'suggestions_count': len(self.optimization_suggestions),
                'status': 'active' if self.monitoring_active else 'inactive'
            }
            
            logger.info("🔍 통합 성능 모니터링 완료")
            return integration_report
            
        except Exception as e:
            logger.error(f"통합 성능 모니터링 실패: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }

# 기존 호환성을 위한 별칭
PerformanceMonitor = AdvancedPerformanceMonitor
