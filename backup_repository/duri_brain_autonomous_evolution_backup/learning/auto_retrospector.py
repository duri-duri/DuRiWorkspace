"""
DuRi AutoRetrospector (자동 회고 시스템)

DuRi의 자동 회고 및 메타 학습 분석 시스템입니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# 기존 시스템 import
from duri_core.utils.performance_monitor import get_performance_monitor
from duri_core.utils.log_analyzer import get_log_analyzer
from duri_core.utils.fallback_handler import get_fallback_handler
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_core.memory.meta_learning_data import (
    get_meta_learning_data_manager, MetaLearningData, MetaLearningType,
    PerformancePattern, ErrorPattern, LearningStrategyUpdate, ImprovementSuggestion
)

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """분석 결과"""
    analysis_id: str
    analysis_type: str
    confidence: float
    findings: List[str]
    recommendations: List[str]
    performance_impact: float
    analysis_duration: float

class AutoRetrospector:
    """DuRi의 자동 회고 및 메타 학습 분석 시스템"""
    
    def __init__(self):
        """AutoRetrospector 초기화"""
        self.performance_monitor = get_performance_monitor()
        self.log_analyzer = get_log_analyzer()
        self.fallback_handler = get_fallback_handler()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        
        # 분석 설정
        self.analysis_interval = 3600  # 1시간마다 분석
        self.last_analysis_time = None
        self.analysis_history: List[AnalysisResult] = []
        
        logger.info("AutoRetrospector 초기화 완료")
    
    def should_run_analysis(self) -> bool:
        """분석을 실행해야 하는지 확인합니다."""
        if self.last_analysis_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= self.analysis_interval
    
    def run_comprehensive_analysis(self) -> MetaLearningData:
        """종합 분석을 실행합니다."""
        try:
            start_time = time.time()
            analysis_id = f"analysis_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"AutoRetrospector 종합 분석 시작: {analysis_id}")
            
            # 1. 성능 분석
            performance_analysis = self._analyze_performance_patterns()
            
            # 2. 오류 패턴 분석
            error_analysis = self._analyze_error_patterns()
            
            # 3. 학습 전략 분석
            learning_strategy_analysis = self._analyze_learning_strategies()
            
            # 4. 시스템 건강도 분석
            system_health_analysis = self._analyze_system_health()
            
            # 5. 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions(
                performance_analysis, error_analysis, learning_strategy_analysis, system_health_analysis
            )
            
            # 6. 메타 학습 데이터 생성
            meta_learning_data = MetaLearningData(
                analysis_id=analysis_id,
                analysis_type=MetaLearningType.PERFORMANCE_ANALYSIS,
                analysis_timestamp=datetime.now(),
                analysis_period=timedelta(hours=24),
                performance_patterns=performance_analysis.get('patterns', []),
                error_patterns=error_analysis.get('patterns', []),
                learning_strategy_updates=learning_strategy_analysis.get('updates', []),
                improvement_suggestions=improvement_suggestions,
                overall_confidence=self._calculate_overall_confidence(
                    performance_analysis, error_analysis, learning_strategy_analysis, system_health_analysis
                ),
                data_quality_score=self._calculate_data_quality_score(),
                analysis_duration=time.time() - start_time,
                system_health_score=system_health_analysis.get('health_score', 0.0),
                performance_score=performance_analysis.get('overall_score', 0.0),
                error_rate=error_analysis.get('error_rate', 0.0)
            )
            
            # 7. 메타 학습 데이터 저장
            self.meta_learning_manager.store_meta_learning_data(meta_learning_data)
            
            self.last_analysis_time = datetime.now()
            
            logger.info(f"AutoRetrospector 종합 분석 완료: {analysis_id}")
            return meta_learning_data
            
        except Exception as e:
            logger.error(f"AutoRetrospector 종합 분석 실패: {e}")
            return self._create_error_meta_learning_data()
    
    def _analyze_performance_patterns(self) -> Dict[str, Any]:
        """성능 패턴을 분석합니다."""
        try:
            # 성능 모니터링 데이터 수집
            performance_stats = self.performance_monitor.get_performance_statistics(hours=24)
            current_metrics = self.performance_monitor.get_current_metrics()
            
            patterns = []
            overall_score = 0.0
            
            if performance_stats and current_metrics:
                # CPU 사용률 패턴 분석
                cpu_usage = current_metrics.get('cpu_usage', 0.0)
                if cpu_usage > 80.0:
                    patterns.append(PerformancePattern(
                        pattern_type="high_cpu_usage",
                        description="CPU 사용률이 높습니다",
                        frequency=0.8,
                        impact_score=0.7,
                        trend_direction="declining",
                        confidence=0.9,
                        detected_at=datetime.now()
                    ))
                elif cpu_usage < 20.0:
                    patterns.append(PerformancePattern(
                        pattern_type="low_cpu_usage",
                        description="CPU 사용률이 낮습니다",
                        frequency=0.6,
                        impact_score=0.3,
                        trend_direction="stable",
                        confidence=0.8,
                        detected_at=datetime.now()
                    ))
                
                # 메모리 사용률 패턴 분석
                memory_usage = current_metrics.get('memory_usage', 0.0)
                if memory_usage > 85.0:
                    patterns.append(PerformancePattern(
                        pattern_type="high_memory_usage",
                        description="메모리 사용률이 높습니다",
                        frequency=0.7,
                        impact_score=0.8,
                        trend_direction="declining",
                        confidence=0.9,
                        detected_at=datetime.now()
                    ))
                
                # 전체 성능 점수 계산
                overall_score = self._calculate_performance_score(cpu_usage, memory_usage)
            
            return {
                'patterns': patterns,
                'overall_score': overall_score,
                'cpu_usage': current_metrics.get('cpu_usage', 0.0) if current_metrics else 0.0,
                'memory_usage': current_metrics.get('memory_usage', 0.0) if current_metrics else 0.0
            }
            
        except Exception as e:
            logger.error(f"성능 패턴 분석 실패: {e}")
            return {'patterns': [], 'overall_score': 0.0}
    
    def _analyze_error_patterns(self) -> Dict[str, Any]:
        """오류 패턴을 분석합니다."""
        try:
            # 로그 분석을 통한 오류 패턴 수집
            log_stats = self.log_analyzer.analyze_logs()
            fallback_stats = self.fallback_handler.get_fallback_statistics()
            
            patterns = []
            error_rate = 0.0
            
            # 로그 기반 오류 패턴 분석
            if log_stats.error_patterns:
                for error_type, count in log_stats.error_patterns.items():
                    if count > 1:  # 반복 오류만 분석
                        patterns.append(ErrorPattern(
                            error_type=error_type,
                            error_message=f"반복 오류: {error_type}",
                            frequency=count,
                            affected_modules=self._identify_affected_modules(error_type),
                            recovery_time=None,  # 향후 구현
                            impact_level="warning" if count < 5 else "critical",
                            first_occurrence=datetime.now() - timedelta(hours=1),  # 추정
                            last_occurrence=datetime.now()
                        ))
            
            # Fallback 기반 오류 패턴 분석
            if fallback_stats.get('total_fallbacks', 0) > 0:
                patterns.append(ErrorPattern(
                    error_type="fallback_activation",
                    error_message="Fallback 모드 활성화",
                    frequency=fallback_stats.get('total_fallbacks', 0),
                    affected_modules=fallback_stats.get('affected_modules', []),
                    recovery_time=None,
                    impact_level="warning",
                    first_occurrence=datetime.now() - timedelta(hours=1),
                    last_occurrence=datetime.now()
                ))
            
            # 오류율 계산
            total_entries = log_stats.total_entries if log_stats.total_entries > 0 else 1
            error_rate = (log_stats.error_count / total_entries) * 100
            
            return {
                'patterns': patterns,
                'error_rate': error_rate,
                'total_errors': log_stats.error_count,
                'fallback_count': fallback_stats.get('total_fallbacks', 0)
            }
            
        except Exception as e:
            logger.error(f"오류 패턴 분석 실패: {e}")
            return {'patterns': [], 'error_rate': 0.0}
    
    def _analyze_learning_strategies(self) -> Dict[str, Any]:
        """학습 전략을 분석합니다."""
        try:
            # 메모리에서 학습 관련 데이터 수집
            learning_memories = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.LEARNING_EXPERIENCE, limit=50
            )
            
            updates = []
            
            # 학습 성과 분석
            if learning_memories:
                # 학습 성공률 계산
                successful_learning = len([m for m in learning_memories if m.get('success', False)])
                total_learning = len(learning_memories)
                success_rate = successful_learning / total_learning if total_learning > 0 else 0.0
                
                if success_rate < 0.5:
                    updates.append(LearningStrategyUpdate(
                        strategy_name="learning_efficiency",
                        current_performance=success_rate,
                        suggested_improvement="학습 성공률이 낮습니다. 학습 전략을 개선해야 합니다.",
                        expected_impact=0.3,
                        implementation_priority="high",
                        confidence=0.8
                    ))
                
                # 학습 속도 분석
                recent_memories = [m for m in learning_memories if m.get('timestamp')]
                if len(recent_memories) >= 2:
                    # 간단한 학습 속도 추정
                    learning_speed = len(recent_memories) / 24  # 시간당 학습 횟수
                    
                    if learning_speed < 1.0:
                        updates.append(LearningStrategyUpdate(
                            strategy_name="learning_speed",
                            current_performance=learning_speed,
                            suggested_improvement="학습 속도가 느립니다. 학습 주기를 단축해야 합니다.",
                            expected_impact=0.4,
                            implementation_priority="medium",
                            confidence=0.7
                        ))
            
            return {
                'updates': updates,
                'total_learning_sessions': len(learning_memories),
                'success_rate': success_rate if 'success_rate' in locals() else 0.0
            }
            
        except Exception as e:
            logger.error(f"학습 전략 분석 실패: {e}")
            return {'updates': [], 'total_learning_sessions': 0, 'success_rate': 0.0}
    
    def _analyze_system_health(self) -> Dict[str, Any]:
        """시스템 건강도를 분석합니다."""
        try:
            # 성능 모니터링 데이터 수집
            current_health = self.performance_monitor.get_current_health()
            current_metrics = self.performance_monitor.get_current_metrics()
            
            health_score = 0.0
            
            if current_health and current_metrics:
                health_score = current_health.get('overall_health', 0.0)
                
                # 건강도 기반 분석
                if health_score < 0.5:
                    logger.warning("시스템 건강도가 낮습니다")
                elif health_score > 0.8:
                    logger.info("시스템 건강도가 양호합니다")
            
            return {
                'health_score': health_score,
                'cpu_health': current_health.get('cpu_health', 0.0) if current_health else 0.0,
                'memory_health': current_health.get('memory_health', 0.0) if current_health else 0.0,
                'disk_health': current_health.get('disk_health', 0.0) if current_health else 0.0
            }
            
        except Exception as e:
            logger.error(f"시스템 건강도 분석 실패: {e}")
            return {'health_score': 0.0}
    
    def _generate_improvement_suggestions(self, performance_analysis: Dict[str, Any],
                                        error_analysis: Dict[str, Any],
                                        learning_analysis: Dict[str, Any],
                                        health_analysis: Dict[str, Any]) -> List[ImprovementSuggestion]:
        """개선 제안을 생성합니다."""
        try:
            suggestions = []
            
            # 성능 기반 제안
            if performance_analysis.get('overall_score', 0.0) < 0.6:
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    category="performance",
                    description="시스템 성능 최적화 필요",
                    rationale="전체 성능 점수가 낮습니다",
                    expected_benefit=0.3,
                    implementation_cost="medium",
                    priority="high",
                    confidence=0.8,
                    created_at=datetime.now()
                ))
            
            # 오류 기반 제안
            if error_analysis.get('error_rate', 0.0) > 5.0:
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    category="error_handling",
                    description="오류 처리 개선 필요",
                    rationale="오류율이 높습니다",
                    expected_benefit=0.4,
                    implementation_cost="high",
                    priority="critical",
                    confidence=0.9,
                    created_at=datetime.now()
                ))
            
            # 학습 기반 제안
            if learning_analysis.get('success_rate', 0.0) < 0.5:
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    category="learning",
                    description="학습 전략 개선 필요",
                    rationale="학습 성공률이 낮습니다",
                    expected_benefit=0.5,
                    implementation_cost="medium",
                    priority="high",
                    confidence=0.8,
                    created_at=datetime.now()
                ))
            
            # 시스템 건강도 기반 제안
            if health_analysis.get('health_score', 0.0) < 0.6:
                suggestions.append(ImprovementSuggestion(
                    suggestion_id=f"suggestion_{uuid.uuid4().hex[:8]}",
                    category="system_health",
                    description="시스템 건강도 개선 필요",
                    rationale="시스템 건강도가 낮습니다",
                    expected_benefit=0.4,
                    implementation_cost="low",
                    priority="medium",
                    confidence=0.7,
                    created_at=datetime.now()
                ))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"개선 제안 생성 실패: {e}")
            return []
    
    def _calculate_overall_confidence(self, performance_analysis: Dict[str, Any],
                                    error_analysis: Dict[str, Any],
                                    learning_analysis: Dict[str, Any],
                                    health_analysis: Dict[str, Any]) -> float:
        """전체 신뢰도를 계산합니다."""
        try:
            # 각 분석의 신뢰도 가중 평균
            confidences = []
            weights = []
            
            # 성능 분석 신뢰도
            if performance_analysis.get('patterns'):
                confidences.append(0.8)
                weights.append(0.3)
            
            # 오류 분석 신뢰도
            if error_analysis.get('patterns'):
                confidences.append(0.9)
                weights.append(0.3)
            
            # 학습 분석 신뢰도
            if learning_analysis.get('updates'):
                confidences.append(0.7)
                weights.append(0.2)
            
            # 건강도 분석 신뢰도
            if health_analysis.get('health_score', 0.0) > 0:
                confidences.append(0.8)
                weights.append(0.2)
            
            if not confidences:
                return 0.5  # 기본값
            
            # 가중 평균 계산
            total_weight = sum(weights)
            if total_weight > 0:
                weighted_confidence = sum(c * w for c, w in zip(confidences, weights)) / total_weight
                return min(weighted_confidence, 1.0)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"전체 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _calculate_data_quality_score(self) -> float:
        """데이터 품질 점수를 계산합니다."""
        try:
            # 간단한 데이터 품질 평가
            quality_score = 0.8  # 기본값
            
            # 로그 데이터 품질 확인
            log_stats = self.log_analyzer.analyze_logs()
            if log_stats.total_entries > 0:
                quality_score += 0.1
            
            # 성능 데이터 품질 확인
            current_metrics = self.performance_monitor.get_current_metrics()
            if current_metrics:
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.error(f"데이터 품질 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_performance_score(self, cpu_usage: float, memory_usage: float) -> float:
        """성능 점수를 계산합니다."""
        try:
            # CPU와 메모리 사용률을 기반으로 성능 점수 계산
            cpu_score = 1.0 - (cpu_usage / 100.0)  # 낮을수록 좋음
            memory_score = 1.0 - (memory_usage / 100.0)  # 낮을수록 좋음
            
            # 가중 평균 (CPU 60%, 메모리 40%)
            performance_score = (cpu_score * 0.6) + (memory_score * 0.4)
            
            return max(performance_score, 0.0)
            
        except Exception as e:
            logger.error(f"성능 점수 계산 실패: {e}")
            return 0.5
    
    def _identify_affected_modules(self, error_type: str) -> List[str]:
        """오류 유형에 따른 영향받는 모듈을 식별합니다."""
        try:
            # 오류 유형에 따른 모듈 매핑
            module_mapping = {
                "ModuleNotFoundError": ["duri_brain", "duri_core"],
                "AttributeError": ["duri_brain", "duri_core"],
                "TypeError": ["duri_brain", "duri_core"],
                "fallback_activation": ["duri_brain.eval.core_eval", "duri_core.utils.fallback_handler"]
            }
            
            return module_mapping.get(error_type, ["unknown"])
            
        except Exception as e:
            logger.error(f"영향받는 모듈 식별 실패: {e}")
            return ["unknown"]
    
    def _create_error_meta_learning_data(self) -> MetaLearningData:
        """오류 시 기본 메타 학습 데이터를 생성합니다."""
        return MetaLearningData(
            analysis_id=f"error_analysis_{uuid.uuid4().hex[:8]}",
            analysis_type=MetaLearningType.PERFORMANCE_ANALYSIS,
            analysis_timestamp=datetime.now(),
            analysis_period=timedelta(hours=1),
            overall_confidence=0.0,
            data_quality_score=0.0,
            analysis_duration=0.0,
            system_health_score=0.0,
            performance_score=0.0,
            error_rate=1.0
        )
    
    def get_analysis_history(self, limit: int = 10) -> List[AnalysisResult]:
        """분석 히스토리를 반환합니다."""
        return self.analysis_history[-limit:] if self.analysis_history else []
    
    def get_auto_retrospector(self) -> 'AutoRetrospector':
        """AutoRetrospector 인스턴스를 반환합니다."""
        return self

# 싱글톤 인스턴스
_auto_retrospector = None

def get_auto_retrospector() -> AutoRetrospector:
    """AutoRetrospector 싱글톤 인스턴스 반환"""
    global _auto_retrospector
    if _auto_retrospector is None:
        _auto_retrospector = AutoRetrospector()
    return _auto_retrospector 