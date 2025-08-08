"""
DuRi Meta Learning 데이터 구조

Meta Learning을 위한 데이터 구조와 관련 클래스들을 정의합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class MetaLearningType(Enum):
    """메타 학습 유형"""
    PERFORMANCE_ANALYSIS = "performance_analysis"    # 성능 분석
    ERROR_PATTERN_ANALYSIS = "error_pattern_analysis"  # 오류 패턴 분석
    LEARNING_STRATEGY_ANALYSIS = "learning_strategy_analysis"  # 학습 전략 분석
    SYSTEM_HEALTH_ANALYSIS = "system_health_analysis"  # 시스템 건강도 분석
    IMPROVEMENT_SUGGESTION = "improvement_suggestion"  # 개선 제안

class AnalysisConfidence(Enum):
    """분석 신뢰도"""
    HIGH = "high"        # 높음 (0.8-1.0)
    MEDIUM = "medium"    # 중간 (0.5-0.8)
    LOW = "low"          # 낮음 (0.0-0.5)

@dataclass
class PerformancePattern:
    """성능 패턴"""
    pattern_type: str
    description: str
    frequency: float
    impact_score: float
    trend_direction: str  # "improving", "declining", "stable"
    confidence: float
    detected_at: datetime

@dataclass
class ErrorPattern:
    """오류 패턴"""
    error_type: str
    error_message: str
    frequency: int
    affected_modules: List[str]
    recovery_time: Optional[float]
    impact_level: str  # "critical", "warning", "info"
    first_occurrence: datetime
    last_occurrence: datetime

@dataclass
class LearningStrategyUpdate:
    """학습 전략 업데이트"""
    strategy_name: str
    current_performance: float
    suggested_improvement: str
    expected_impact: float
    implementation_priority: str  # "high", "medium", "low"
    confidence: float

@dataclass
class ImprovementSuggestion:
    """개선 제안"""
    suggestion_id: str
    category: str
    description: str
    rationale: str
    expected_benefit: float
    implementation_cost: str  # "low", "medium", "high"
    priority: str  # "critical", "high", "medium", "low"
    confidence: float
    created_at: datetime

@dataclass
class MetaLearningData:
    """메타 학습 데이터"""
    analysis_id: str
    analysis_type: MetaLearningType
    analysis_timestamp: datetime
    analysis_period: timedelta
    
    # 분석 결과
    performance_patterns: List[PerformancePattern] = field(default_factory=list)
    error_patterns: List[ErrorPattern] = field(default_factory=list)
    learning_strategy_updates: List[LearningStrategyUpdate] = field(default_factory=list)
    improvement_suggestions: List[ImprovementSuggestion] = field(default_factory=list)
    
    # 메타 정보
    overall_confidence: float = 0.0
    data_quality_score: float = 0.0
    analysis_duration: float = 0.0
    
    # 시스템 상태
    system_health_score: float = 0.0
    performance_score: float = 0.0
    error_rate: float = 0.0
    
    # 추가 메타데이터
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetaLearningSummary:
    """메타 학습 요약"""
    summary_id: str
    period_start: datetime
    period_end: datetime
    
    # 통계
    total_analyses: int
    high_confidence_analyses: int
    critical_improvements: int
    implemented_suggestions: int
    
    # 성능 지표
    average_performance_score: float
    average_system_health: float
    average_error_rate: float
    
    # 개선 효과
    performance_improvement: float
    error_reduction: float
    learning_efficiency_gain: float
    
    # 메타 정보
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetaLearningDataManager:
    """메타 학습 데이터 관리자"""
    
    def __init__(self):
        """MetaLearningDataManager 초기화"""
        self.meta_learning_history: List[MetaLearningData] = []
        self.summaries: List[MetaLearningSummary] = []
        self.max_history_size = 1000
        
        logger.info("MetaLearningDataManager 초기화 완료")
    
    def store_meta_learning_data(self, data: MetaLearningData):
        """메타 학습 데이터를 저장합니다."""
        try:
            self.meta_learning_history.append(data)
            
            # 히스토리 크기 제한
            if len(self.meta_learning_history) > self.max_history_size:
                self.meta_learning_history = self.meta_learning_history[-self.max_history_size:]
            
            logger.debug(f"메타 학습 데이터 저장 완료: {data.analysis_id}")
            
        except Exception as e:
            logger.error(f"메타 학습 데이터 저장 실패: {e}")
    
    def get_recent_meta_learning_data(self, hours: int = 24) -> List[MetaLearningData]:
        """최근 메타 학습 데이터를 반환합니다."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_data = [
                data for data in self.meta_learning_history
                if data.analysis_timestamp >= cutoff_time
            ]
            
            return recent_data
            
        except Exception as e:
            logger.error(f"최근 메타 학습 데이터 조회 실패: {e}")
            return []
    
    def get_meta_learning_data_by_type(self, analysis_type: MetaLearningType, 
                                      hours: int = 24) -> List[MetaLearningData]:
        """특정 유형의 메타 학습 데이터를 반환합니다."""
        try:
            recent_data = self.get_recent_meta_learning_data(hours)
            
            filtered_data = [
                data for data in recent_data
                if data.analysis_type == analysis_type
            ]
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"메타 학습 데이터 필터링 실패: {e}")
            return []
    
    def create_summary(self, period_start: datetime, period_end: datetime) -> MetaLearningSummary:
        """메타 학습 요약을 생성합니다."""
        try:
            # 기간 내 데이터 필터링
            period_data = [
                data for data in self.meta_learning_history
                if period_start <= data.analysis_timestamp <= period_end
            ]
            
            if not period_data:
                return None
            
            # 통계 계산
            total_analyses = len(period_data)
            high_confidence_analyses = len([
                data for data in period_data
                if data.overall_confidence >= 0.8
            ])
            
            critical_improvements = len([
                suggestion for data in period_data
                for suggestion in data.improvement_suggestions
                if suggestion.priority == "critical"
            ])
            
            # 성능 지표 계산
            avg_performance = sum(data.performance_score for data in period_data) / len(period_data)
            avg_health = sum(data.system_health_score for data in period_data) / len(period_data)
            avg_error_rate = sum(data.error_rate for data in period_data) / len(period_data)
            
            # 개선 효과 계산 (간단한 추정)
            performance_improvement = self._calculate_performance_improvement(period_data)
            error_reduction = self._calculate_error_reduction(period_data)
            learning_efficiency_gain = self._calculate_learning_efficiency_gain(period_data)
            
            summary = MetaLearningSummary(
                summary_id=f"summary_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}",
                period_start=period_start,
                period_end=period_end,
                total_analyses=total_analyses,
                high_confidence_analyses=high_confidence_analyses,
                critical_improvements=critical_improvements,
                implemented_suggestions=0,  # 향후 구현
                average_performance_score=avg_performance,
                average_system_health=avg_health,
                average_error_rate=avg_error_rate,
                performance_improvement=performance_improvement,
                error_reduction=error_reduction,
                learning_efficiency_gain=learning_efficiency_gain,
                created_at=datetime.now()
            )
            
            self.summaries.append(summary)
            logger.info(f"메타 학습 요약 생성 완료: {summary.summary_id}")
            
            return summary
            
        except Exception as e:
            logger.error(f"메타 학습 요약 생성 실패: {e}")
            return None
    
    def _calculate_performance_improvement(self, period_data: List[MetaLearningData]) -> float:
        """성능 개선 효과를 계산합니다."""
        try:
            if len(period_data) < 2:
                return 0.0
            
            # 시간순 정렬
            sorted_data = sorted(period_data, key=lambda x: x.analysis_timestamp)
            
            # 첫 번째와 마지막 성능 점수 비교
            first_performance = sorted_data[0].performance_score
            last_performance = sorted_data[-1].performance_score
            
            improvement = (last_performance - first_performance) / first_performance if first_performance > 0 else 0.0
            
            return max(improvement, 0.0)  # 음수 개선은 0으로 처리
            
        except Exception as e:
            logger.error(f"성능 개선 효과 계산 실패: {e}")
            return 0.0
    
    def _calculate_error_reduction(self, period_data: List[MetaLearningData]) -> float:
        """오류 감소 효과를 계산합니다."""
        try:
            if len(period_data) < 2:
                return 0.0
            
            # 시간순 정렬
            sorted_data = sorted(period_data, key=lambda x: x.analysis_timestamp)
            
            # 첫 번째와 마지막 오류율 비교
            first_error_rate = sorted_data[0].error_rate
            last_error_rate = sorted_data[-1].error_rate
            
            reduction = (first_error_rate - last_error_rate) / first_error_rate if first_error_rate > 0 else 0.0
            
            return max(reduction, 0.0)  # 음수 감소는 0으로 처리
            
        except Exception as e:
            logger.error(f"오류 감소 효과 계산 실패: {e}")
            return 0.0
    
    def _calculate_learning_efficiency_gain(self, period_data: List[MetaLearningData]) -> float:
        """학습 효율성 향상을 계산합니다."""
        try:
            # 간단한 추정: 성능 향상과 오류 감소의 가중 평균
            performance_improvement = self._calculate_performance_improvement(period_data)
            error_reduction = self._calculate_error_reduction(period_data)
            
            # 가중 평균 (성능 70%, 오류 감소 30%)
            efficiency_gain = (performance_improvement * 0.7) + (error_reduction * 0.3)
            
            return efficiency_gain
            
        except Exception as e:
            logger.error(f"학습 효율성 향상 계산 실패: {e}")
            return 0.0
    
    def get_meta_learning_statistics(self) -> Dict[str, Any]:
        """메타 학습 통계를 반환합니다."""
        try:
            if not self.meta_learning_history:
                return {
                    "total_analyses": 0,
                    "average_confidence": 0.0,
                    "average_performance_score": 0.0,
                    "average_system_health": 0.0,
                    "average_error_rate": 0.0,
                    "recent_summaries": 0
                }
            
            total_analyses = len(self.meta_learning_history)
            avg_confidence = sum(data.overall_confidence for data in self.meta_learning_history) / total_analyses
            avg_performance = sum(data.performance_score for data in self.meta_learning_history) / total_analyses
            avg_health = sum(data.system_health_score for data in self.meta_learning_history) / total_analyses
            avg_error_rate = sum(data.error_rate for data in self.meta_learning_history) / total_analyses
            
            recent_summaries = len([s for s in self.summaries if s.created_at >= datetime.now() - timedelta(days=7)])
            
            return {
                "total_analyses": total_analyses,
                "average_confidence": avg_confidence,
                "average_performance_score": avg_performance,
                "average_system_health": avg_health,
                "average_error_rate": avg_error_rate,
                "recent_summaries": recent_summaries
            }
            
        except Exception as e:
            logger.error(f"메타 학습 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_meta_learning_data_manager = None

def get_meta_learning_data_manager() -> MetaLearningDataManager:
    """MetaLearningDataManager 싱글톤 인스턴스 반환"""
    global _meta_learning_data_manager
    if _meta_learning_data_manager is None:
        _meta_learning_data_manager = MetaLearningDataManager()
    return _meta_learning_data_manager 