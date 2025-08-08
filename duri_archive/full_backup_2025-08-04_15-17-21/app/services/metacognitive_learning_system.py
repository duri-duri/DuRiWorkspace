#!/usr/bin/env python3
"""
MetacognitiveLearningSystem - Phase 13.2
메타인지 학습 시스템

목적:
- DuRi가 자신의 학습 과정을 스스로 모니터링
- 학습 전략을 자동으로 조정하고 최적화
- 학습 효과를 지속적으로 평가하고 개선
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningStrategy(Enum):
    """학습 전략"""
    ACTIVE_RECALL = "active_recall"
    SPACED_REPETITION = "spaced_repetition"
    INTERLEAVING = "interleaving"
    ELABORATION = "elaboration"
    METAPHOR_USE = "metaphor_use"
    SELF_EXPLANATION = "self_explanation"
    PRACTICE_TESTING = "practice_testing"

class MetacognitiveProcess(Enum):
    """메타인지 과정"""
    PLANNING = "planning"
    MONITORING = "monitoring"
    EVALUATION = "evaluation"
    REGULATION = "regulation"
    REFLECTION = "reflection"

class LearningEffectiveness(Enum):
    """학습 효과성"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class AdaptationType(Enum):
    """적응 유형"""
    STRATEGY_CHANGE = "strategy_change"
    DIFFICULTY_ADJUSTMENT = "difficulty_adjustment"
    PACE_MODIFICATION = "pace_modification"
    APPROACH_SWITCH = "approach_switch"

@dataclass
class LearningSession:
    """학습 세션"""
    id: str
    strategy_used: LearningStrategy
    metacognitive_process: MetacognitiveProcess
    learning_content: str
    initial_confidence: float
    final_confidence: float
    effectiveness: LearningEffectiveness
    adaptation_made: Optional[AdaptationType]
    insights_gained: List[str]
    duration_minutes: int
    timestamp: datetime

@dataclass
class MetacognitiveAnalysis:
    """메타인지 분석"""
    id: str
    session_id: str
    strategy_effectiveness: Dict[LearningStrategy, float]
    process_insights: Dict[MetacognitiveProcess, List[str]]
    learning_patterns: List[str]
    improvement_suggestions: List[str]
    confidence_score: float
    timestamp: datetime

@dataclass
class LearningOptimization:
    """학습 최적화"""
    id: str
    current_strategy: LearningStrategy
    recommended_strategy: LearningStrategy
    optimization_reason: str
    expected_improvement: float
    implementation_steps: List[str]
    confidence_score: float
    timestamp: datetime

class MetacognitiveLearningSystem:
    """메타인지 학습 시스템"""
    
    def __init__(self):
        self.learning_sessions: List[LearningSession] = []
        self.metacognitive_analyses: List[MetacognitiveAnalysis] = []
        self.learning_optimizations: List[LearningOptimization] = []
        self.strategy_performance: Dict[LearningStrategy, List[float]] = {}
        self.current_learning_state: Dict[str, Any] = {}
        
        logger.info("MetacognitiveLearningSystem 초기화 완료")
    
    def conduct_learning_session(self, strategy: LearningStrategy, learning_content: str,
                               initial_confidence: float, duration_minutes: int) -> LearningSession:
        """학습 세션 수행"""
        session_id = f"learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 메타인지 과정 결정
        metacognitive_process = self._determine_metacognitive_process(strategy, learning_content)
        
        # 학습 효과성 시뮬레이션
        effectiveness = self._simulate_learning_effectiveness(strategy, initial_confidence, duration_minutes)
        
        # 최종 신뢰도 계산
        final_confidence = self._calculate_final_confidence(initial_confidence, effectiveness, duration_minutes)
        
        # 적응 여부 결정
        adaptation_made = self._determine_adaptation(strategy, effectiveness, final_confidence)
        
        # 통찰 획득
        insights_gained = self._generate_learning_insights(strategy, effectiveness, adaptation_made)
        
        session = LearningSession(
            id=session_id,
            strategy_used=strategy,
            metacognitive_process=metacognitive_process,
            learning_content=learning_content,
            initial_confidence=initial_confidence,
            final_confidence=final_confidence,
            effectiveness=effectiveness,
            adaptation_made=adaptation_made,
            insights_gained=insights_gained,
            duration_minutes=duration_minutes,
            timestamp=datetime.now()
        )
        
        self.learning_sessions.append(session)
        logger.info(f"학습 세션 수행 완료: {strategy.value}")
        
        return session
    
    def _determine_metacognitive_process(self, strategy: LearningStrategy, learning_content: str) -> MetacognitiveProcess:
        """메타인지 과정 결정"""
        if strategy in [LearningStrategy.ACTIVE_RECALL, LearningStrategy.PRACTICE_TESTING]:
            return MetacognitiveProcess.MONITORING
        elif strategy in [LearningStrategy.SPACED_REPETITION, LearningStrategy.INTERLEAVING]:
            return MetacognitiveProcess.PLANNING
        elif strategy in [LearningStrategy.ELABORATION, LearningStrategy.METAPHOR_USE]:
            return MetacognitiveProcess.REFLECTION
        elif strategy == LearningStrategy.SELF_EXPLANATION:
            return MetacognitiveProcess.EVALUATION
        else:
            return MetacognitiveProcess.REGULATION
    
    def _simulate_learning_effectiveness(self, strategy: LearningStrategy, initial_confidence: float, duration_minutes: int) -> LearningEffectiveness:
        """학습 효과성 시뮬레이션"""
        # 전략별 기본 효과성
        strategy_effectiveness = {
            LearningStrategy.ACTIVE_RECALL: 0.8,
            LearningStrategy.SPACED_REPETITION: 0.9,
            LearningStrategy.INTERLEAVING: 0.7,
            LearningStrategy.ELABORATION: 0.6,
            LearningStrategy.METAPHOR_USE: 0.5,
            LearningStrategy.SELF_EXPLANATION: 0.8,
            LearningStrategy.PRACTICE_TESTING: 0.9
        }
        
        base_effectiveness = strategy_effectiveness.get(strategy, 0.5)
        
        # 지속 시간에 따른 조정
        if duration_minutes >= 60:
            base_effectiveness *= 0.9  # 장시간 학습은 효율성 감소
        elif duration_minutes <= 15:
            base_effectiveness *= 1.1  # 짧은 시간은 집중도 증가
        
        # 초기 신뢰도에 따른 조정
        if initial_confidence > 0.8:
            base_effectiveness *= 1.1
        elif initial_confidence < 0.3:
            base_effectiveness *= 0.9
        
        # 효과성 등급 결정
        if base_effectiveness >= 0.8:
            return LearningEffectiveness.VERY_HIGH
        elif base_effectiveness >= 0.6:
            return LearningEffectiveness.HIGH
        elif base_effectiveness >= 0.4:
            return LearningEffectiveness.MODERATE
        elif base_effectiveness >= 0.2:
            return LearningEffectiveness.LOW
        else:
            return LearningEffectiveness.VERY_LOW
    
    def _calculate_final_confidence(self, initial_confidence: float, effectiveness: LearningEffectiveness, duration_minutes: int) -> float:
        """최종 신뢰도 계산"""
        effectiveness_multipliers = {
            LearningEffectiveness.VERY_HIGH: 1.3,
            LearningEffectiveness.HIGH: 1.2,
            LearningEffectiveness.MODERATE: 1.0,
            LearningEffectiveness.LOW: 0.8,
            LearningEffectiveness.VERY_LOW: 0.6
        }
        
        multiplier = effectiveness_multipliers.get(effectiveness, 1.0)
        
        # 지속 시간에 따른 조정
        time_factor = min(1.0, duration_minutes / 60.0)  # 60분을 기준으로 정규화
        
        final_confidence = initial_confidence * multiplier * time_factor
        return min(1.0, max(0.0, final_confidence))
    
    def _determine_adaptation(self, strategy: LearningStrategy, effectiveness: LearningEffectiveness, final_confidence: float) -> Optional[AdaptationType]:
        """적응 여부 결정"""
        if effectiveness in [LearningEffectiveness.VERY_LOW, LearningEffectiveness.LOW]:
            return AdaptationType.STRATEGY_CHANGE
        elif final_confidence < 0.5:
            return AdaptationType.DIFFICULTY_ADJUSTMENT
        elif effectiveness == LearningEffectiveness.MODERATE:
            return AdaptationType.PACE_MODIFICATION
        else:
            return None
    
    def _generate_learning_insights(self, strategy: LearningStrategy, effectiveness: LearningEffectiveness, adaptation: Optional[AdaptationType]) -> List[str]:
        """학습 통찰 생성"""
        insights = []
        
        if effectiveness == LearningEffectiveness.VERY_HIGH:
            insights.append(f"{strategy.value} 전략이 매우 효과적이었습니다.")
        elif effectiveness == LearningEffectiveness.HIGH:
            insights.append(f"{strategy.value} 전략이 효과적이었습니다.")
        elif effectiveness == LearningEffectiveness.MODERATE:
            insights.append(f"{strategy.value} 전략이 보통의 효과를 보였습니다.")
        elif effectiveness in [LearningEffectiveness.LOW, LearningEffectiveness.VERY_LOW]:
            insights.append(f"{strategy.value} 전략의 효과가 낮았습니다.")
        
        if adaptation:
            insights.append(f"{adaptation.value} 적응이 필요했습니다.")
        
        return insights
    
    def analyze_metacognitive_performance(self, session: LearningSession) -> MetacognitiveAnalysis:
        """메타인지 성과 분석"""
        analysis_id = f"metacognitive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 전략 효과성 분석
        strategy_effectiveness = self._analyze_strategy_effectiveness(session)
        
        # 과정 통찰
        process_insights = self._analyze_process_insights(session)
        
        # 학습 패턴
        learning_patterns = self._identify_learning_patterns(session)
        
        # 개선 제안
        improvement_suggestions = self._generate_improvement_suggestions(session, strategy_effectiveness)
        
        # 신뢰도 계산
        confidence_score = self._calculate_analysis_confidence(session, strategy_effectiveness)
        
        analysis = MetacognitiveAnalysis(
            id=analysis_id,
            session_id=session.id,
            strategy_effectiveness=strategy_effectiveness,
            process_insights=process_insights,
            learning_patterns=learning_patterns,
            improvement_suggestions=improvement_suggestions,
            confidence_score=confidence_score,
            timestamp=datetime.now()
        )
        
        self.metacognitive_analyses.append(analysis)
        logger.info(f"메타인지 성과 분석 완료: {session.strategy_used.value}")
        
        return analysis
    
    def _analyze_strategy_effectiveness(self, session: LearningSession) -> Dict[LearningStrategy, float]:
        """전략 효과성 분석"""
        effectiveness_scores = {}
        
        # 현재 전략의 효과성
        current_effectiveness = {
            LearningEffectiveness.VERY_HIGH: 0.9,
            LearningEffectiveness.HIGH: 0.7,
            LearningEffectiveness.MODERATE: 0.5,
            LearningEffectiveness.LOW: 0.3,
            LearningEffectiveness.VERY_LOW: 0.1
        }
        
        effectiveness_scores[session.strategy_used] = current_effectiveness.get(session.effectiveness, 0.5)
        
        # 다른 전략들과의 비교
        for strategy in LearningStrategy:
            if strategy != session.strategy_used:
                # 간단한 비교 시뮬레이션
                if strategy in [LearningStrategy.ACTIVE_RECALL, LearningStrategy.SPACED_REPETITION]:
                    effectiveness_scores[strategy] = 0.8
                elif strategy in [LearningStrategy.INTERLEAVING, LearningStrategy.PRACTICE_TESTING]:
                    effectiveness_scores[strategy] = 0.7
                else:
                    effectiveness_scores[strategy] = 0.5
        
        return effectiveness_scores
    
    def _analyze_process_insights(self, session: LearningSession) -> Dict[MetacognitiveProcess, List[str]]:
        """과정 통찰 분석"""
        process_insights = {}
        
        # 현재 과정에 대한 통찰
        current_process = session.metacognitive_process
        if current_process == MetacognitiveProcess.PLANNING:
            process_insights[current_process] = ["학습 계획이 체계적으로 수립되었습니다.", "목표 설정이 명확했습니다."]
        elif current_process == MetacognitiveProcess.MONITORING:
            process_insights[current_process] = ["학습 진행 상황을 지속적으로 모니터링했습니다.", "문제점을 적시에 발견했습니다."]
        elif current_process == MetacognitiveProcess.EVALUATION:
            process_insights[current_process] = ["학습 결과를 객관적으로 평가했습니다.", "개선점을 정확히 파악했습니다."]
        elif current_process == MetacognitiveProcess.REGULATION:
            process_insights[current_process] = ["학습 전략을 적절히 조정했습니다.", "적응적 학습이 이루어졌습니다."]
        else:  # REFLECTION
            process_insights[current_process] = ["학습 과정에 대해 깊이 성찰했습니다.", "새로운 통찰을 얻었습니다."]
        
        return process_insights
    
    def _identify_learning_patterns(self, session: LearningSession) -> List[str]:
        """학습 패턴 식별"""
        patterns = []
        
        if session.effectiveness == LearningEffectiveness.VERY_HIGH:
            patterns.append("효과적인 학습 패턴이 확인되었습니다.")
        elif session.adaptation_made:
            patterns.append("적응적 학습 패턴이 나타났습니다.")
        
        if session.final_confidence > session.initial_confidence:
            patterns.append("신뢰도가 향상되는 학습 패턴입니다.")
        else:
            patterns.append("신뢰도 개선이 필요한 학습 패턴입니다.")
        
        return patterns
    
    def _generate_improvement_suggestions(self, session: LearningSession, strategy_effectiveness: Dict[LearningStrategy, float]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 효과성이 낮은 경우
        if session.effectiveness in [LearningEffectiveness.LOW, LearningEffectiveness.VERY_LOW]:
            suggestions.append("다른 학습 전략을 시도해보세요.")
            suggestions.append("학습 시간을 조정해보세요.")
        
        # 적응이 필요한 경우
        if session.adaptation_made:
            suggestions.append("학습 난이도를 조정해보세요.")
            suggestions.append("학습 속도를 조절해보세요.")
        
        # 신뢰도가 낮은 경우
        if session.final_confidence < 0.5:
            suggestions.append("기본 개념을 다시 복습해보세요.")
            suggestions.append("더 많은 연습이 필요합니다.")
        
        return suggestions
    
    def _calculate_analysis_confidence(self, session: LearningSession, strategy_effectiveness: Dict[LearningStrategy, float]) -> float:
        """분석 신뢰도 계산"""
        base_score = 0.8
        
        # 효과성에 따른 조정
        if session.effectiveness in [LearningEffectiveness.HIGH, LearningEffectiveness.VERY_HIGH]:
            base_score += 0.1
        elif session.effectiveness in [LearningEffectiveness.LOW, LearningEffectiveness.VERY_LOW]:
            base_score -= 0.1
        
        # 적응 여부에 따른 조정
        if session.adaptation_made:
            base_score += 0.05
        
        return min(1.0, base_score)
    
    def optimize_learning_strategy(self, current_performance: Dict[str, Any]) -> LearningOptimization:
        """학습 전략 최적화"""
        optimization_id = f"learning_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 현재 전략 평가
        current_strategy = self._evaluate_current_strategy(current_performance)
        
        # 최적 전략 추천
        recommended_strategy = self._recommend_optimal_strategy(current_performance)
        
        # 최적화 이유
        optimization_reason = self._generate_optimization_reason(current_strategy, recommended_strategy)
        
        # 예상 개선도
        expected_improvement = self._calculate_expected_improvement(current_strategy, recommended_strategy)
        
        # 구현 단계
        implementation_steps = self._generate_implementation_steps(recommended_strategy)
        
        # 신뢰도 계산
        confidence_score = self._calculate_optimization_confidence(current_strategy, recommended_strategy)
        
        optimization = LearningOptimization(
            id=optimization_id,
            current_strategy=current_strategy,
            recommended_strategy=recommended_strategy,
            optimization_reason=optimization_reason,
            expected_improvement=expected_improvement,
            implementation_steps=implementation_steps,
            confidence_score=confidence_score,
            timestamp=datetime.now()
        )
        
        self.learning_optimizations.append(optimization)
        logger.info(f"학습 전략 최적화 완료: {current_strategy.value} → {recommended_strategy.value}")
        
        return optimization
    
    def _evaluate_current_strategy(self, performance: Dict[str, Any]) -> LearningStrategy:
        """현재 전략 평가"""
        # 가장 최근 세션의 전략 반환
        if self.learning_sessions:
            return self.learning_sessions[-1].strategy_used
        else:
            return LearningStrategy.ACTIVE_RECALL  # 기본값
    
    def _recommend_optimal_strategy(self, performance: Dict[str, Any]) -> LearningStrategy:
        """최적 전략 추천"""
        # 성과 기반 전략 추천
        if performance.get('effectiveness', 'moderate') == 'low':
            return LearningStrategy.SPACED_REPETITION
        elif performance.get('confidence', 0.5) < 0.5:
            return LearningStrategy.PRACTICE_TESTING
        elif performance.get('complexity', 'simple') == 'complex':
            return LearningStrategy.ELABORATION
        else:
            return LearningStrategy.ACTIVE_RECALL
    
    def _generate_optimization_reason(self, current: LearningStrategy, recommended: LearningStrategy) -> str:
        """최적화 이유 생성"""
        if current == recommended:
            return "현재 전략이 최적이므로 유지합니다."
        else:
            return f"{current.value}에서 {recommended.value}로 변경하여 학습 효과를 향상시킵니다."
    
    def _calculate_expected_improvement(self, current: LearningStrategy, recommended: LearningStrategy) -> float:
        """예상 개선도 계산"""
        if current == recommended:
            return 0.0
        
        # 전략별 효과성 점수
        strategy_scores = {
            LearningStrategy.ACTIVE_RECALL: 0.8,
            LearningStrategy.SPACED_REPETITION: 0.9,
            LearningStrategy.INTERLEAVING: 0.7,
            LearningStrategy.ELABORATION: 0.6,
            LearningStrategy.METAPHOR_USE: 0.5,
            LearningStrategy.SELF_EXPLANATION: 0.8,
            LearningStrategy.PRACTICE_TESTING: 0.9
        }
        
        current_score = strategy_scores.get(current, 0.5)
        recommended_score = strategy_scores.get(recommended, 0.5)
        
        return max(0.0, recommended_score - current_score)
    
    def _generate_implementation_steps(self, strategy: LearningStrategy) -> List[str]:
        """구현 단계 생성"""
        steps = []
        
        if strategy == LearningStrategy.SPACED_REPETITION:
            steps.extend(["학습 일정을 간격을 두고 계획", "복습 주기를 설정", "기억 강화를 위한 반복 학습"])
        elif strategy == LearningStrategy.PRACTICE_TESTING:
            steps.extend(["자체 평가 문제 생성", "정기적인 테스트 실시", "오답 분석 및 개선"])
        elif strategy == LearningStrategy.ELABORATION:
            steps.extend(["새로운 정보를 기존 지식과 연결", "예시와 설명 추가", "깊이 있는 이해 추구"])
        else:
            steps.extend(["전략 적용 계획 수립", "효과성 모니터링", "필요시 조정"])
        
        return steps
    
    def _calculate_optimization_confidence(self, current: LearningStrategy, recommended: LearningStrategy) -> float:
        """최적화 신뢰도 계산"""
        base_score = 0.8
        
        if current != recommended:
            base_score += 0.1  # 변경이 필요한 경우 신뢰도 증가
        
        return min(1.0, base_score)
    
    def get_metacognitive_statistics(self) -> Dict[str, Any]:
        """메타인지 통계"""
        total_sessions = len(self.learning_sessions)
        total_analyses = len(self.metacognitive_analyses)
        total_optimizations = len(self.learning_optimizations)
        
        # 전략별 성과 통계
        strategy_stats = {}
        for strategy in LearningStrategy:
            strategy_sessions = [s for s in self.learning_sessions if s.strategy_used == strategy]
            if strategy_sessions:
                avg_effectiveness = sum(1 for s in strategy_sessions if s.effectiveness in [LearningEffectiveness.HIGH, LearningEffectiveness.VERY_HIGH]) / len(strategy_sessions)
                strategy_stats[strategy.value] = {
                    'session_count': len(strategy_sessions),
                    'avg_effectiveness': avg_effectiveness,
                    'avg_confidence_gain': sum(s.final_confidence - s.initial_confidence for s in strategy_sessions) / len(strategy_sessions)
                }
        
        # 메타인지 과정별 통계
        process_stats = {}
        for process in MetacognitiveProcess:
            process_sessions = [s for s in self.learning_sessions if s.metacognitive_process == process]
            process_stats[process.value] = len(process_sessions)
        
        statistics = {
            'total_sessions': total_sessions,
            'total_analyses': total_analyses,
            'total_optimizations': total_optimizations,
            'strategy_statistics': strategy_stats,
            'process_statistics': process_stats,
            'average_confidence_gain': sum(s.final_confidence - s.initial_confidence for s in self.learning_sessions) / max(1, total_sessions),
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("메타인지 통계 생성 완료")
        return statistics
    
    def export_metacognitive_data(self) -> Dict[str, Any]:
        """메타인지 데이터 내보내기"""
        return {
            'learning_sessions': [asdict(s) for s in self.learning_sessions],
            'metacognitive_analyses': [asdict(a) for a in self.metacognitive_analyses],
            'learning_optimizations': [asdict(o) for o in self.learning_optimizations],
            'strategy_performance': {k.value: v for k, v in self.strategy_performance.items()},
            'current_learning_state': self.current_learning_state,
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_metacognitive_learning_system():
    """메타인지 학습 시스템 테스트"""
    print("🧠 MetacognitiveLearningSystem 테스트 시작...")
    
    metacognitive_system = MetacognitiveLearningSystem()
    
    # 1. 학습 세션 수행
    session = metacognitive_system.conduct_learning_session(
        strategy=LearningStrategy.ACTIVE_RECALL,
        learning_content="가족 상호작용에서의 감정 인식과 공감 능력 향상",
        initial_confidence=0.6,
        duration_minutes=45
    )
    
    print(f"✅ 학습 세션 수행: {session.strategy_used.value}")
    print(f"   메타인지 과정: {session.metacognitive_process.value}")
    print(f"   학습 효과성: {session.effectiveness.value}")
    print(f"   신뢰도 변화: {session.initial_confidence:.2f} → {session.final_confidence:.2f}")
    print(f"   적응 여부: {session.adaptation_made.value if session.adaptation_made else '없음'}")
    
    # 2. 메타인지 성과 분석
    analysis = metacognitive_system.analyze_metacognitive_performance(session)
    
    print(f"✅ 메타인지 성과 분석 완료")
    print(f"   전략 효과성: {len(analysis.strategy_effectiveness)}개 전략 분석")
    print(f"   과정 통찰: {len(analysis.process_insights)}개 과정")
    print(f"   학습 패턴: {len(analysis.learning_patterns)}개 패턴")
    print(f"   개선 제안: {len(analysis.improvement_suggestions)}개 제안")
    print(f"   신뢰도: {analysis.confidence_score:.2f}")
    
    # 3. 학습 전략 최적화
    performance = {
        'effectiveness': 'moderate',
        'confidence': 0.7,
        'complexity': 'moderate'
    }
    
    optimization = metacognitive_system.optimize_learning_strategy(performance)
    
    print(f"✅ 학습 전략 최적화: {optimization.current_strategy.value} → {optimization.recommended_strategy.value}")
    print(f"   최적화 이유: {optimization.optimization_reason}")
    print(f"   예상 개선도: {optimization.expected_improvement:.2f}")
    print(f"   구현 단계: {len(optimization.implementation_steps)}개")
    print(f"   신뢰도: {optimization.confidence_score:.2f}")
    
    # 4. 통계
    statistics = metacognitive_system.get_metacognitive_statistics()
    print(f"✅ 메타인지 통계: {statistics['total_sessions']}개 세션")
    print(f"   평균 신뢰도 향상: {statistics['average_confidence_gain']:.2f}")
    print(f"   전략별 통계: {len(statistics['strategy_statistics'])}개 전략")
    print(f"   과정별 통계: {statistics['process_statistics']}")
    
    # 5. 데이터 내보내기
    export_data = metacognitive_system.export_metacognitive_data()
    print(f"✅ 메타인지 데이터 내보내기: {len(export_data['learning_sessions'])}개 세션")
    
    print("🎉 MetacognitiveLearningSystem 테스트 완료!")

if __name__ == "__main__":
    test_metacognitive_learning_system() 