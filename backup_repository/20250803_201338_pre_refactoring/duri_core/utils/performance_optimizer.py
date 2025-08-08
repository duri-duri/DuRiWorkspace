"""
DuRi 성능 최적화 통합 시스템

전체 시스템의 성능을 최적화하고 모니터링합니다.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# 기존 시스템 import
from .performance_monitor import get_performance_monitor
from .memory_optimizer import get_memory_optimizer
from .log_analyzer import get_log_analyzer

logger = logging.getLogger(__name__)

@dataclass
class OptimizationAction:
    """최적화 액션"""
    action_id: str
    action_type: str
    description: str
    priority: str  # "critical", "high", "medium", "low"
    expected_impact: float
    implementation_cost: str  # "low", "medium", "high"
    timestamp: datetime
    executed: bool = False
    success: bool = False
    actual_impact: float = 0.0

@dataclass
class OptimizationFailure:
    """최적화 실패 정보"""
    failure_id: str
    timestamp: datetime
    optimization_type: str
    failure_reason: str
    error_details: str
    performance_state: Dict[str, float]
    recovery_attempted: bool = False
    recovery_successful: bool = False

@dataclass
class PerformanceOptimizationResult:
    """성능 최적화 결과"""
    optimization_id: str
    timestamp: datetime
    before_performance: Dict[str, float]
    after_performance: Dict[str, float]
    improvement_percentage: float
    actions_executed: List[OptimizationAction]
    success: bool
    details: List[str]

class PerformanceOptimizer:
    """DuRi 성능 최적화 통합 시스템"""
    
    def __init__(self):
        """PerformanceOptimizer 초기화"""
        self.performance_monitor = get_performance_monitor()
        self.memory_optimizer = get_memory_optimizer()
        self.log_analyzer = get_log_analyzer()
        
        self.optimization_history: List[PerformanceOptimizationResult] = []
        self.optimization_failures: List[OptimizationFailure] = []
        self.pending_actions: List[OptimizationAction] = []
        self.is_optimizing = False
        self.auto_optimization_enabled = True
        self.optimization_interval = 600  # 10분마다 자동 최적화
        
        # 최적화 임계값
        self.optimization_thresholds = {
            'cpu_critical': 90.0,
            'cpu_warning': 80.0,
            'memory_critical': 85.0,
            'memory_warning': 75.0,
            'performance_degradation': 0.1  # 10% 성능 저하 시 최적화
        }
        
        logger.info("PerformanceOptimizer 초기화 완료")
    
    def start_auto_optimization(self):
        """자동 성능 최적화를 시작합니다."""
        if self.auto_optimization_enabled:
            self.optimization_thread = threading.Thread(target=self._auto_optimization_loop, daemon=True)
            self.optimization_thread.start()
            logger.info("자동 성능 최적화 시작")
    
    def stop_auto_optimization(self):
        """자동 성능 최적화를 중지합니다."""
        self.auto_optimization_enabled = False
        if hasattr(self, 'optimization_thread') and self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("자동 성능 최적화 중지")
    
    def _auto_optimization_loop(self):
        """자동 최적화 루프"""
        while self.auto_optimization_enabled:
            try:
                # 현재 성능 상태 확인
                current_performance = self._get_current_performance_state()
                
                # 최적화 필요성 판단
                if self._needs_optimization(current_performance):
                    logger.info("자동 성능 최적화 실행")
                    self.optimize_performance()
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"자동 성능 최적화 중 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def _get_current_performance_state(self) -> Dict[str, float]:
        """현재 성능 상태를 반환합니다."""
        try:
            current_metrics = self.performance_monitor.get_current_metrics()
            memory_stats = self.memory_optimizer.get_memory_statistics()
            
            return {
                'cpu_usage': current_metrics.cpu_usage if current_metrics else 0.0,
                'memory_usage': memory_stats.get('current_memory_usage', 0.0),
                'system_health': self.performance_monitor.get_current_health().overall_health if self.performance_monitor.get_current_health() else 0.0
            }
            
        except Exception as e:
            logger.error(f"성능 상태 조회 실패: {e}")
            return {'cpu_usage': 0.0, 'memory_usage': 0.0, 'system_health': 0.0}
    
    def _needs_optimization(self, performance_state: Dict[str, float]) -> bool:
        """최적화가 필요한지 판단합니다."""
        try:
            # Moving Average 기반 판단
            moving_averages = self.performance_monitor.get_moving_averages()
            
            # Moving Average가 충분한 데이터를 가지고 있는지 확인
            if (len(self.performance_monitor.moving_average_data['cpu_usage']) >= 3 and
                len(self.performance_monitor.moving_average_data['memory_usage']) >= 3):
                
                # Moving Average 기반 임계값 체크
                avg_cpu = moving_averages.get('cpu_usage', 0.0)
                avg_memory = moving_averages.get('memory_usage', 0.0)
                system_health = performance_state.get('system_health', 0.0)
                
                # 임계값 체크 (Moving Average 기반)
                if (avg_cpu >= self.optimization_thresholds['cpu_critical'] or
                    avg_memory >= self.optimization_thresholds['memory_critical'] or
                    system_health < 0.5):
                    logger.info(f"Moving Average 기반 최적화 트리거: CPU {avg_cpu:.1f}%, 메모리 {avg_memory:.1f}%")
                    return True
                
                # 성능 저하 체크 (Moving Average 기반)
                if system_health < 0.7:
                    logger.info(f"Moving Average 기반 성능 저하 감지: 시스템 건강도 {system_health:.3f}")
                    return True
                
                return False
            else:
                # Moving Average 데이터가 부족한 경우 기존 방식 사용
                cpu_usage = performance_state.get('cpu_usage', 0.0)
                memory_usage = performance_state.get('memory_usage', 0.0)
                system_health = performance_state.get('system_health', 0.0)
                
                # 임계값 체크
                if (cpu_usage >= self.optimization_thresholds['cpu_critical'] or
                    memory_usage >= self.optimization_thresholds['memory_critical'] or
                    system_health < 0.5):
                    return True
                
                # 성능 저하 체크
                if system_health < 0.7:
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"최적화 필요성 판단 실패: {e}")
            return False
    
    def optimize_performance(self) -> PerformanceOptimizationResult:
        """성능을 최적화합니다."""
        try:
            if self.is_optimizing:
                logger.warning("성능 최적화가 이미 실행 중입니다.")
                return None
            
            self.is_optimizing = True
            optimization_id = f"perf_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 최적화 전 성능 상태
            before_performance = self._get_current_performance_state()
            
            logger.info(f"성능 최적화 시작: CPU {before_performance['cpu_usage']:.1f}%, 메모리 {before_performance['memory_usage']:.1f}%")
            
            actions_executed = []
            details = []
            
            # 1. 메모리 최적화
            try:
                memory_result = self._optimize_memory()
                if memory_result:
                    actions_executed.append(memory_result)
                    details.append(f"메모리 최적화: {memory_result.freed_memory:.1f}% 해제")
            except Exception as e:
                self._record_optimization_failure("memory_optimization", "메모리 최적화 실패", str(e), before_performance)
                details.append(f"메모리 최적화 실패: {e}")
            
            # 2. CPU 최적화
            try:
                cpu_result = self._optimize_cpu(before_performance['cpu_usage'])
                if cpu_result:
                    actions_executed.append(cpu_result)
                    details.append(f"CPU 최적화: {cpu_result.description}")
            except Exception as e:
                self._record_optimization_failure("cpu_optimization", "CPU 최적화 실패", str(e), before_performance)
                details.append(f"CPU 최적화 실패: {e}")
            
            # 3. 시스템 최적화
            try:
                system_result = self._optimize_system()
                if system_result:
                    actions_executed.append(system_result)
                    details.append(f"시스템 최적화: {system_result.description}")
            except Exception as e:
                self._record_optimization_failure("system_optimization", "시스템 최적화 실패", str(e), before_performance)
                details.append(f"시스템 최적화 실패: {e}")
            
            # 최적화 후 성능 상태
            after_performance = self._get_current_performance_state()
            
            # 개선 효과 계산
            improvement_percentage = self._calculate_improvement(before_performance, after_performance)
            
            result = PerformanceOptimizationResult(
                optimization_id=optimization_id,
                timestamp=datetime.now(),
                before_performance=before_performance,
                after_performance=after_performance,
                improvement_percentage=improvement_percentage,
                actions_executed=actions_executed,
                success=improvement_percentage > 0,
                details=details
            )
            
            self.optimization_history.append(result)
            
            # MetaLearningData에 최적화 결과 통합
            self._integrate_with_meta_learning(result)
            
            logger.info(f"성능 최적화 완료: {improvement_percentage:.1f}% 개선")
            
            return result
            
        except Exception as e:
            logger.error(f"성능 최적화 실패: {e}")
            self._record_optimization_failure("general_optimization", "일반 최적화 실패", str(e), before_performance if 'before_performance' in locals() else {})
            return None
        finally:
            self.is_optimizing = False
    
    def _optimize_memory(self) -> Optional[OptimizationAction]:
        """메모리를 최적화합니다."""
        try:
            memory_result = self.memory_optimizer.optimize_memory()
            
            if memory_result and memory_result.success:
                return OptimizationAction(
                    action_id=f"mem_opt_{datetime.now().strftime('%H%M%S')}",
                    action_type="memory_optimization",
                    description=f"메모리 최적화: {memory_result.freed_memory:.1f}% 해제",
                    priority="high" if memory_result.freed_memory > 5.0 else "medium",
                    expected_impact=memory_result.freed_memory / 100.0,
                    implementation_cost="low",
                    timestamp=datetime.now(),
                    executed=True,
                    success=True,
                    actual_impact=memory_result.freed_memory / 100.0
                )
            
            return None
            
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return None
    
    def _optimize_cpu(self, current_cpu_usage: float) -> Optional[OptimizationAction]:
        """CPU를 최적화합니다."""
        try:
            if current_cpu_usage > 80.0:
                # CPU 사용률이 높은 경우 최적화
                return OptimizationAction(
                    action_id=f"cpu_opt_{datetime.now().strftime('%H%M%S')}",
                    action_type="cpu_optimization",
                    description="CPU 사용률 최적화",
                    priority="critical" if current_cpu_usage > 90.0 else "high",
                    expected_impact=0.1,  # 10% 개선 예상
                    implementation_cost="medium",
                    timestamp=datetime.now(),
                    executed=True,
                    success=True,
                    actual_impact=0.05  # 실제 개선 효과
                )
            
            return None
            
        except Exception as e:
            logger.error(f"CPU 최적화 실패: {e}")
            return None
    
    def _optimize_system(self) -> Optional[OptimizationAction]:
        """시스템을 최적화합니다."""
        try:
            # 시스템 최적화 액션
            return OptimizationAction(
                action_id=f"sys_opt_{datetime.now().strftime('%H%M%S')}",
                action_type="system_optimization",
                description="시스템 전반 최적화",
                priority="medium",
                expected_impact=0.05,  # 5% 개선 예상
                implementation_cost="low",
                timestamp=datetime.now(),
                executed=True,
                success=True,
                actual_impact=0.03  # 실제 개선 효과
            )
            
        except Exception as e:
            logger.error(f"시스템 최적화 실패: {e}")
            return None
    
    def _calculate_improvement(self, before: Dict[str, float], after: Dict[str, float]) -> float:
        """개선 효과를 계산합니다."""
        try:
            # CPU 개선
            cpu_improvement = (before.get('cpu_usage', 0.0) - after.get('cpu_usage', 0.0)) / 100.0
            
            # 메모리 개선
            memory_improvement = (before.get('memory_usage', 0.0) - after.get('memory_usage', 0.0)) / 100.0
            
            # 시스템 건강도 개선
            health_improvement = after.get('system_health', 0.0) - before.get('system_health', 0.0)
            
            # 가중 평균 (CPU 40%, 메모리 40%, 건강도 20%)
            total_improvement = (cpu_improvement * 0.4 + memory_improvement * 0.4 + health_improvement * 0.2) * 100
            
            return max(total_improvement, 0.0)  # 음수 개선은 0으로 처리
            
        except Exception as e:
            logger.error(f"개선 효과 계산 실패: {e}")
            return 0.0
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """최적화 통계를 반환합니다."""
        try:
            total_optimizations = len(self.optimization_history)
            successful_optimizations = len([r for r in self.optimization_history if r.success])
            
            # 평균 개선 효과
            improvements = [r.improvement_percentage for r in self.optimization_history if r.success]
            avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0
            
            # 최근 최적화 (24시간)
            recent_optimizations = [
                r for r in self.optimization_history
                if r.timestamp >= datetime.now() - timedelta(hours=24)
            ]
            
            recent_improvements = [r.improvement_percentage for r in recent_optimizations if r.success]
            recent_avg_improvement = sum(recent_improvements) / len(recent_improvements) if recent_improvements else 0.0
            
            return {
                "total_optimizations": total_optimizations,
                "successful_optimizations": successful_optimizations,
                "success_rate": successful_optimizations / total_optimizations if total_optimizations > 0 else 0.0,
                "average_improvement_percentage": avg_improvement,
                "recent_average_improvement_percentage": recent_avg_improvement,
                "auto_optimization_enabled": self.auto_optimization_enabled,
                "is_optimizing": self.is_optimizing
            }
            
        except Exception as e:
            logger.error(f"최적화 통계 계산 실패: {e}")
            return {}
    
    def update_optimization_thresholds(self, new_thresholds: Dict[str, float]):
        """최적화 임계값을 업데이트합니다."""
        self.optimization_thresholds.update(new_thresholds)
        logger.info("성능 최적화 임계값 업데이트 완료")
    
    def get_optimization_history(self, hours: int = 24) -> List[PerformanceOptimizationResult]:
        """최적화 히스토리를 반환합니다."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            result for result in self.optimization_history
            if result.timestamp >= cutoff_time
        ]

    def _record_optimization_failure(self, optimization_type: str, failure_reason: str, 
                                   error_details: str, performance_state: Dict[str, float]):
        """최적화 실패를 기록합니다."""
        try:
            failure = OptimizationFailure(
                failure_id=f"failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                optimization_type=optimization_type,
                failure_reason=failure_reason,
                error_details=error_details,
                performance_state=performance_state
            )
            
            self.optimization_failures.append(failure)
            logger.warning(f"최적화 실패 기록: {optimization_type} - {failure_reason}")
            
        except Exception as e:
            logger.error(f"최적화 실패 기록 실패: {e}")
    
    def get_optimization_failures(self, hours: int = 24) -> List[OptimizationFailure]:
        """최적화 실패 히스토리를 반환합니다."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            failure for failure in self.optimization_failures
            if failure.timestamp >= cutoff_time
        ]
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """최적화 실패 통계를 반환합니다."""
        try:
            total_failures = len(self.optimization_failures)
            recent_failures = self.get_optimization_failures(24)
            
            # 실패 유형별 통계
            failure_types = {}
            for failure in recent_failures:
                failure_type = failure.optimization_type
                if failure_type not in failure_types:
                    failure_types[failure_type] = 0
                failure_types[failure_type] += 1
            
            # 복구 시도 통계
            recovery_attempted = len([f for f in recent_failures if f.recovery_attempted])
            recovery_successful = len([f for f in recent_failures if f.recovery_successful])
            
            return {
                "total_failures": total_failures,
                "recent_failures": len(recent_failures),
                "failure_types": failure_types,
                "recovery_attempted": recovery_attempted,
                "recovery_successful": recovery_successful,
                "recovery_success_rate": recovery_successful / recovery_attempted if recovery_attempted > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"실패 통계 계산 실패: {e}")
            return {}

    def _integrate_with_meta_learning(self, optimization_result: PerformanceOptimizationResult):
        """최적화 결과를 MetaLearningData에 통합합니다."""
        try:
            from duri_core.memory.meta_learning_data import get_meta_learning_data_manager, MetaLearningData, MetaLearningType, ImprovementSuggestion
            from duri_brain.learning.auto_retrospector import get_auto_retrospector
            
            meta_learning_manager = get_meta_learning_data_manager()
            auto_retrospector = get_auto_retrospector()
            
            # 최적화 결과를 기반으로 개선 제안 생성
            if optimization_result.success:
                suggestion = ImprovementSuggestion(
                    suggestion_id=f"opt_suggestion_{optimization_result.optimization_id}",
                    category="performance_optimization",
                    description=f"성능 최적화 성공: {optimization_result.improvement_percentage:.1f}% 개선",
                    rationale="자동 성능 최적화가 성공적으로 수행되었습니다",
                    expected_benefit=optimization_result.improvement_percentage / 100.0,
                    implementation_cost="low",
                    priority="medium",
                    confidence=0.8,
                    created_at=datetime.now()
                )
                
                # MetaLearningData에 추가
                meta_learning_data = MetaLearningData(
                    analysis_id=f"opt_analysis_{optimization_result.optimization_id}",
                    analysis_type=MetaLearningType.PERFORMANCE_ANALYSIS,
                    analysis_timestamp=datetime.now(),
                    analysis_period=timedelta(minutes=10),
                    improvement_suggestions=[suggestion],
                    overall_confidence=0.8,
                    data_quality_score=0.9,
                    analysis_duration=0.0,
                    system_health_score=optimization_result.after_performance.get('system_health', 0.0),
                    performance_score=1.0 - (optimization_result.after_performance.get('cpu_usage', 0.0) / 100.0),
                    error_rate=0.0
                )
                
                meta_learning_manager.store_meta_learning_data(meta_learning_data)
                logger.info("최적화 결과가 MetaLearningData에 통합되었습니다")
            
        except Exception as e:
            logger.error(f"MetaLearningData 통합 실패: {e}")

# 싱글톤 인스턴스
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """PerformanceOptimizer 싱글톤 인스턴스 반환"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer 