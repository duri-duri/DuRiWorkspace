"""
DuRi 자기 평가 자동화 시스템

DuRi 스스로 자기 상태를 평가하고 성장 곡선을 관리합니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 기존 시스템 import
from duri_core.utils.performance_monitor import get_performance_monitor
from duri_core.utils.log_analyzer import get_log_analyzer
from duri_core.utils.performance_optimizer import get_performance_optimizer
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_core.memory.meta_learning_data import get_meta_learning_data_manager

logger = logging.getLogger(__name__)

class AssessmentCategory(Enum):
    """평가 카테고리"""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    LEARNING = "learning"
    CREATIVITY = "creativity"
    STABILITY = "stability"
    OVERALL = "overall"

class AssessmentLevel(Enum):
    """평가 수준"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    AVERAGE = "average"     # 50-69%
    POOR = "poor"          # 30-49%
    CRITICAL = "critical"   # 0-29%

@dataclass
class AssessmentMetric:
    """평가 메트릭"""
    metric_id: str
    category: AssessmentCategory
    name: str
    value: float
    max_value: float
    weight: float
    timestamp: datetime
    description: str = ""
    improvement_suggestions: List[str] = field(default_factory=list)

@dataclass
class SystemAssessment:
    """시스템 평가 결과"""
    assessment_id: str
    timestamp: datetime
    overall_score: float
    category_scores: Dict[AssessmentCategory, float]
    metrics: List[AssessmentMetric]
    growth_trend: str  # "improving", "stable", "declining"
    critical_issues: List[str]
    improvement_priorities: List[str]
    next_assessment_time: datetime

@dataclass
class GrowthCurve:
    """성장 곡선"""
    curve_id: str
    start_date: datetime
    end_date: datetime
    assessment_history: List[SystemAssessment]
    growth_rate: float
    target_score: float
    current_score: float
    milestones: List[Dict[str, Any]]

class SelfAssessmentManager:
    """DuRi 자기 평가 자동화 시스템"""
    
    def __init__(self):
        """SelfAssessmentManager 초기화"""
        self.performance_monitor = get_performance_monitor()
        self.log_analyzer = get_log_analyzer()
        self.performance_optimizer = get_performance_optimizer()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.learning_loop_manager = None # 순환 참조 문제로 인해 초기화 지연
        
        # 평가 설정
        self.assessment_interval = 3600  # 1시간마다 평가
        self.last_assessment_time = None
        self.assessment_history: List[SystemAssessment] = []
        self.growth_curves: List[GrowthCurve] = []
        
        # 평가 가중치 설정
        self.category_weights = {
            AssessmentCategory.PERFORMANCE: 0.25,
            AssessmentCategory.MEMORY: 0.20,
            AssessmentCategory.LEARNING: 0.25,
            AssessmentCategory.CREATIVITY: 0.15,
            AssessmentCategory.STABILITY: 0.15
        }
        
        # 성장 목표 설정
        self.growth_targets = {
            AssessmentCategory.PERFORMANCE: 0.85,
            AssessmentCategory.MEMORY: 0.80,
            AssessmentCategory.LEARNING: 0.90,
            AssessmentCategory.CREATIVITY: 0.75,
            AssessmentCategory.STABILITY: 0.90
        }
        
        logger.info("SelfAssessmentManager 초기화 완료")
    
    def should_run_assessment(self) -> bool:
        """평가를 실행해야 하는지 확인합니다."""
        if self.last_assessment_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_assessment_time
        return time_since_last.total_seconds() >= self.assessment_interval
    
    def run_comprehensive_assessment(self) -> SystemAssessment:
        """종합 평가를 실행합니다."""
        try:
            assessment_id = f"assessment_{uuid.uuid4().hex[:8]}"
            start_time = time.time()
            
            logger.info(f"자기 평가 시작: {assessment_id}")
            
            # 1. 성능 평가
            performance_metrics = self._assess_performance()
            
            # 2. 메모리 평가
            memory_metrics = self._assess_memory()
            
            # 3. 학습 평가
            learning_metrics = self._assess_learning()
            
            # 4. 창의성 평가
            creativity_metrics = self._assess_creativity()
            
            # 5. 안정성 평가
            stability_metrics = self._assess_stability()
            
            # 6. 종합 점수 계산
            overall_score, category_scores = self._calculate_overall_score([
                performance_metrics, memory_metrics, learning_metrics, 
                creativity_metrics, stability_metrics
            ])
            
            # 7. 성장 트렌드 분석
            growth_trend = self._analyze_growth_trend()
            
            # 8. 중요 이슈 및 개선 우선순위 식별
            critical_issues, improvement_priorities = self._identify_issues_and_priorities(
                [performance_metrics, memory_metrics, learning_metrics, 
                 creativity_metrics, stability_metrics]
            )
            
            # 9. 평가 결과 생성
            assessment = SystemAssessment(
                assessment_id=assessment_id,
                timestamp=datetime.now(),
                overall_score=overall_score,
                category_scores=category_scores,
                metrics=performance_metrics + memory_metrics + learning_metrics + 
                       creativity_metrics + stability_metrics,
                growth_trend=growth_trend,
                critical_issues=critical_issues,
                improvement_priorities=improvement_priorities,
                next_assessment_time=datetime.now() + timedelta(seconds=self.assessment_interval)
            )
            
            # 10. 평가 히스토리에 저장
            self.assessment_history.append(assessment)
            
            # 11. 성장 곡선 업데이트
            self._update_growth_curves(assessment)
            
            self.last_assessment_time = datetime.now()
            
            logger.info(f"자기 평가 완료: {assessment_id} - 전체 점수: {overall_score:.2f}")
            return assessment
            
        except Exception as e:
            logger.error(f"자기 평가 실패: {e}")
            return self._create_error_assessment()
    
    def _assess_performance(self) -> List[AssessmentMetric]:
        """성능을 평가합니다."""
        try:
            metrics = []
            
            # CPU 사용률 평가
            current_metrics = self.performance_monitor.get_current_metrics()
            if current_metrics:
                cpu_score = max(0.0, 1.0 - (current_metrics.cpu_usage / 100.0))
                metrics.append(AssessmentMetric(
                    metric_id=f"cpu_usage_{uuid.uuid4().hex[:8]}",
                    category=AssessmentCategory.PERFORMANCE,
                    name="CPU 사용률",
                    value=cpu_score,
                    max_value=1.0,
                    weight=0.4,
                    timestamp=datetime.now(),
                    description=f"CPU 사용률: {current_metrics.cpu_usage:.1f}%",
                    improvement_suggestions=["CPU 사용률이 높습니다. 작업 부하를 분산하세요."] if current_metrics.cpu_usage > 80.0 else []
                ))
            
            # 메모리 사용률 평가
            memory_stats = self.performance_optimizer.memory_optimizer.get_memory_statistics()
            memory_usage = memory_stats.get('current_memory_usage', 0.0)
            memory_score = max(0.0, 1.0 - (memory_usage / 100.0))
            metrics.append(AssessmentMetric(
                metric_id=f"memory_usage_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.PERFORMANCE,
                name="메모리 사용률",
                value=memory_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"메모리 사용률: {memory_usage:.1f}%",
                improvement_suggestions=["메모리 사용률이 높습니다. 최적화가 필요합니다."] if memory_usage > 80.0 else []
            ))
            
            # 시스템 건강도 평가
            current_health = self.performance_monitor.get_current_health()
            if current_health:
                health_score = current_health.overall_health
                metrics.append(AssessmentMetric(
                    metric_id=f"system_health_{uuid.uuid4().hex[:8]}",
                    category=AssessmentCategory.PERFORMANCE,
                    name="시스템 건강도",
                    value=health_score,
                    max_value=1.0,
                    weight=0.3,
                    timestamp=datetime.now(),
                    description=f"시스템 건강도: {health_score:.3f}",
                    improvement_suggestions=["시스템 건강도가 낮습니다. 점검이 필요합니다."] if health_score < 0.7 else []
                ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"성능 평가 실패: {e}")
            return []
    
    def _assess_memory(self) -> List[AssessmentMetric]:
        """메모리를 평가합니다."""
        try:
            metrics = []
            
            # 메모리 최적화 성공률
            memory_stats = self.performance_optimizer.memory_optimizer.get_memory_statistics()
            success_rate = memory_stats.get('success_rate', 0.0)
            metrics.append(AssessmentMetric(
                metric_id=f"memory_optimization_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.MEMORY,
                name="메모리 최적화 성공률",
                value=success_rate,
                max_value=1.0,
                weight=0.4,
                timestamp=datetime.now(),
                description=f"메모리 최적화 성공률: {success_rate:.1%}",
                improvement_suggestions=["메모리 최적화 성공률이 낮습니다."] if success_rate < 0.8 else []
            ))
            
            # 메모리 해제량
            recent_freed = memory_stats.get('recent_freed_memory_percent', 0.0)
            freed_score = min(1.0, recent_freed / 10.0)  # 10% 해제를 최고 점수로
            metrics.append(AssessmentMetric(
                metric_id=f"memory_freed_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.MEMORY,
                name="메모리 해제량",
                value=freed_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"최근 메모리 해제량: {recent_freed:.1f}%",
                improvement_suggestions=["메모리 해제량이 부족합니다."] if freed_score < 0.3 else []
            ))
            
            # 메모리 상태
            memory_status = memory_stats.get('memory_status', 'normal')
            status_score = 1.0 if memory_status == 'normal' else 0.5 if memory_status == 'warning' else 0.0
            metrics.append(AssessmentMetric(
                metric_id=f"memory_status_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.MEMORY,
                name="메모리 상태",
                value=status_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"메모리 상태: {memory_status}",
                improvement_suggestions=["메모리 상태가 좋지 않습니다."] if status_score < 0.5 else []
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"메모리 평가 실패: {e}")
            return []
    
    def _assess_learning(self) -> List[AssessmentMetric]:
        """학습을 평가합니다."""
        try:
            metrics = []
            
            # 학습 루프 상태
            # 학습 루프 매니저가 초기화되지 않아 간접적으로 평가
            is_running = self._get_learning_loop_manager().get_current_status().get('is_running', False) if self._get_learning_loop_manager() else False
            learning_score = 1.0 if is_running else 0.0
            metrics.append(AssessmentMetric(
                metric_id=f"learning_status_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.LEARNING,
                name="학습 루프 상태",
                value=learning_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"학습 루프 상태: {'실행 중' if is_running else '중지됨'}",
                improvement_suggestions=["학습 루프가 중지되었습니다."] if not is_running else []
            ))
            
            # 메타 학습 활성화
            # 학습 루프 매니저가 초기화되지 않아 간접적으로 평가
            meta_learning_enabled = self._get_learning_loop_manager().get_current_status().get('meta_learning_enabled', False) if self._get_learning_loop_manager() else False
            meta_score = 1.0 if meta_learning_enabled else 0.0
            metrics.append(AssessmentMetric(
                metric_id=f"meta_learning_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.LEARNING,
                name="메타 학습 활성화",
                value=meta_score,
                max_value=1.0,
                weight=0.4,
                timestamp=datetime.now(),
                description=f"메타 학습: {'활성화' if meta_learning_enabled else '비활성화'}",
                improvement_suggestions=["메타 학습이 비활성화되었습니다."] if not meta_learning_enabled else []
            ))
            
            # 학습 경험 수집
            # 학습 루프 매니저가 초기화되지 않아 간접적으로 평가
            learning_experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.LEARNING_EXPERIENCE, limit=10
            ) if self._get_learning_loop_manager() else []
            experience_score = min(1.0, len(learning_experiences) / 10.0)
            metrics.append(AssessmentMetric(
                metric_id=f"learning_experiences_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.LEARNING,
                name="학습 경험 수집",
                value=experience_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"학습 경험 수: {len(learning_experiences)}개",
                improvement_suggestions=["학습 경험이 부족합니다."] if experience_score < 0.5 else []
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"학습 평가 실패: {e}")
            return []
    
    def _assess_creativity(self) -> List[AssessmentMetric]:
        """창의성을 평가합니다."""
        try:
            metrics = []
            
            # Dream Engine 상태 (간접 평가)
            dream_score = 0.8  # 기본값, 향후 실제 Dream Engine 연동
            metrics.append(AssessmentMetric(
                metric_id=f"dream_engine_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.CREATIVITY,
                name="Dream Engine 상태",
                value=dream_score,
                max_value=1.0,
                weight=0.5,
                timestamp=datetime.now(),
                description="Dream Engine 창의성 평가",
                improvement_suggestions=["Dream Engine 성능을 개선해야 합니다."] if dream_score < 0.7 else []
            ))
            
            # 창의적 전략 수집 (안전한 방법으로)
            try:
                creative_strategies = self.memory_sync.retrieve_experiences(
                    memory_type=MemoryType.LEARNING_EXPERIENCE, limit=5  # CREATIVE_EXPERIENCE 대신 LEARNING_EXPERIENCE 사용
                )
                strategy_score = min(1.0, len(creative_strategies) / 5.0)
            except Exception:
                creative_strategies = []
                strategy_score = 0.0
            
            metrics.append(AssessmentMetric(
                metric_id=f"creative_strategies_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.CREATIVITY,
                name="창의적 전략 수집",
                value=strategy_score,
                max_value=1.0,
                weight=0.5,
                timestamp=datetime.now(),
                description=f"창의적 전략 수: {len(creative_strategies)}개",
                improvement_suggestions=["창의적 전략이 부족합니다."] if strategy_score < 0.6 else []
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"창의성 평가 실패: {e}")
            return []
    
    def _assess_stability(self) -> List[AssessmentMetric]:
        """안정성을 평가합니다."""
        try:
            metrics = []
            
            # 로그 오류율
            log_stats = self.log_analyzer.analyze_logs()
            total_entries = log_stats.total_entries if log_stats.total_entries > 0 else 1
            error_rate = log_stats.error_count / total_entries
            stability_score = max(0.0, 1.0 - error_rate)
            metrics.append(AssessmentMetric(
                metric_id=f"error_rate_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.STABILITY,
                name="오류율",
                value=stability_score,
                max_value=1.0,
                weight=0.4,
                timestamp=datetime.now(),
                description=f"오류율: {error_rate:.1%}",
                improvement_suggestions=["오류율이 높습니다. 안정성을 개선해야 합니다."] if error_rate > 0.1 else []
            ))
            
            # 성능 최적화 성공률
            optimization_stats = self.performance_optimizer.get_optimization_statistics()
            opt_success_rate = optimization_stats.get('success_rate', 0.0)
            metrics.append(AssessmentMetric(
                metric_id=f"optimization_success_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.STABILITY,
                name="최적화 성공률",
                value=opt_success_rate,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description=f"최적화 성공률: {opt_success_rate:.1%}",
                improvement_suggestions=["최적화 성공률이 낮습니다."] if opt_success_rate < 0.8 else []
            ))
            
            # 시스템 가동 시간 (간접 평가)
            uptime_score = 0.9  # 기본값, 향후 실제 가동 시간 측정
            metrics.append(AssessmentMetric(
                metric_id=f"uptime_{uuid.uuid4().hex[:8]}",
                category=AssessmentCategory.STABILITY,
                name="시스템 가동률",
                value=uptime_score,
                max_value=1.0,
                weight=0.3,
                timestamp=datetime.now(),
                description="시스템 가동률 평가",
                improvement_suggestions=["시스템 가동률이 낮습니다."] if uptime_score < 0.8 else []
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"안정성 평가 실패: {e}")
            return []
    
    def _calculate_overall_score(self, all_metrics: List[List[AssessmentMetric]]) -> Tuple[float, Dict[AssessmentCategory, float]]:
        """전체 점수를 계산합니다."""
        try:
            category_scores = {}
            overall_score = 0.0
            total_weight = 0.0
            
            for metrics in all_metrics:
                for metric in metrics:
                    category = metric.category
                    if category not in category_scores:
                        category_scores[category] = 0.0
                        category_weight = 0.0
                    
                    category_scores[category] += metric.value * metric.weight
                    category_weight += metric.weight
            
            # 카테고리별 평균 점수 계산
            for category in category_scores:
                if category in self.category_weights:
                    # 해당 카테고리의 메트릭들 찾기
                    category_metrics = []
                    for metrics in all_metrics:
                        category_metrics.extend([m for m in metrics if m.category == category])
                    
                    if category_metrics:
                        total_category_weight = sum(m.weight for m in category_metrics)
                        if total_category_weight > 0:
                            category_scores[category] /= total_category_weight
                        else:
                            category_scores[category] = 0.0
                    
                    overall_score += category_scores[category] * self.category_weights[category]
                    total_weight += self.category_weights[category]
            
            if total_weight > 0:
                overall_score /= total_weight
            else:
                overall_score = 0.0
            
            return overall_score, category_scores
            
        except Exception as e:
            logger.error(f"전체 점수 계산 실패: {e}")
            return 0.0, {}
    
    def _analyze_growth_trend(self) -> str:
        """성장 트렌드를 분석합니다."""
        try:
            if len(self.assessment_history) < 2:
                return "stable"
            
            recent_assessments = self.assessment_history[-3:]  # 최근 3개 평가
            scores = [assessment.overall_score for assessment in recent_assessments]
            
            if len(scores) >= 2:
                trend = scores[-1] - scores[0]
                if trend > 0.05:
                    return "improving"
                elif trend < -0.05:
                    return "declining"
                else:
                    return "stable"
            
            return "stable"
            
        except Exception as e:
            logger.error(f"성장 트렌드 분석 실패: {e}")
            return "stable"
    
    def _identify_issues_and_priorities(self, all_metrics: List[List[AssessmentMetric]]) -> Tuple[List[str], List[str]]:
        """중요 이슈와 개선 우선순위를 식별합니다."""
        try:
            critical_issues = []
            improvement_priorities = []
            
            for metrics in all_metrics:
                for metric in metrics:
                    if metric.value < 0.5:  # 50% 미만은 중요 이슈
                        critical_issues.append(f"{metric.name}: {metric.description}")
                    
                    if metric.value < 0.7:  # 70% 미만은 개선 필요
                        improvement_priorities.append(f"{metric.name} 개선 필요")
            
            return critical_issues, improvement_priorities
            
        except Exception as e:
            logger.error(f"이슈 및 우선순위 식별 실패: {e}")
            return [], []
    
    def _update_growth_curves(self, assessment: SystemAssessment):
        """성장 곡선을 업데이트합니다."""
        try:
            # 현재 활성 성장 곡선 찾기
            active_curve = None
            for curve in self.growth_curves:
                if curve.end_date > datetime.now():
                    active_curve = curve
                    break
            
            if active_curve:
                active_curve.assessment_history.append(assessment)
                active_curve.current_score = assessment.overall_score
                
                # 성장률 계산
                if len(active_curve.assessment_history) >= 2:
                    first_score = active_curve.assessment_history[0].overall_score
                    current_score = active_curve.assessment_history[-1].overall_score
                    time_diff = (active_curve.end_date - active_curve.start_date).days
                    if time_diff > 0:
                        active_curve.growth_rate = (current_score - first_score) / time_diff
            else:
                # 새로운 성장 곡선 생성
                new_curve = GrowthCurve(
                    curve_id=f"curve_{uuid.uuid4().hex[:8]}",
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30),
                    assessment_history=[assessment],
                    growth_rate=0.0,
                    target_score=0.9,
                    current_score=assessment.overall_score,
                    milestones=[]
                )
                self.growth_curves.append(new_curve)
            
        except Exception as e:
            logger.error(f"성장 곡선 업데이트 실패: {e}")
    
    def _create_error_assessment(self) -> SystemAssessment:
        """오류 시 기본 평가를 생성합니다."""
        return SystemAssessment(
            assessment_id=f"error_assessment_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            overall_score=0.0,
            category_scores={},
            metrics=[],
            growth_trend="stable",
            critical_issues=["평가 시스템 오류"],
            improvement_priorities=["시스템 안정성 개선"],
            next_assessment_time=datetime.now() + timedelta(seconds=self.assessment_interval)
        )
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """평가 통계를 반환합니다."""
        try:
            if not self.assessment_history:
                return {
                    "total_assessments": 0,
                    "average_score": 0.0,
                    "growth_trend": "stable",
                    "critical_issues_count": 0,
                    "improvement_priorities_count": 0
                }
            
            total_assessments = len(self.assessment_history)
            average_score = sum(a.overall_score for a in self.assessment_history) / total_assessments
            latest_assessment = self.assessment_history[-1]
            
            return {
                "total_assessments": total_assessments,
                "average_score": average_score,
                "latest_score": latest_assessment.overall_score,
                "growth_trend": latest_assessment.growth_trend,
                "critical_issues_count": len(latest_assessment.critical_issues),
                "improvement_priorities_count": len(latest_assessment.improvement_priorities),
                "last_assessment_time": latest_assessment.timestamp.isoformat(),
                "next_assessment_time": latest_assessment.next_assessment_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"평가 통계 계산 실패: {e}")
            return {}
    
    def get_growth_curves(self) -> List[GrowthCurve]:
        """성장 곡선을 반환합니다."""
        return self.growth_curves

    def _get_learning_loop_manager(self):
        """LearningLoopManager를 지연 초기화합니다."""
        if self.learning_loop_manager is None:
            try:
                from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
                self.learning_loop_manager = get_learning_loop_manager()
            except Exception as e:
                logger.warning(f"LearningLoopManager 초기화 실패: {e}")
                return None
        return self.learning_loop_manager

# 싱글톤 인스턴스
_self_assessment_manager = None

def get_self_assessment_manager() -> SelfAssessmentManager:
    """SelfAssessmentManager 싱글톤 인스턴스 반환"""
    global _self_assessment_manager
    if _self_assessment_manager is None:
        _self_assessment_manager = SelfAssessmentManager()
    return _self_assessment_manager 