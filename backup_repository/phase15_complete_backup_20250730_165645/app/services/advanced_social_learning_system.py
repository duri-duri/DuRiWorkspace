#!/usr/bin/env python3
"""
AdvancedSocialLearningSystem - Phase 15.2
고급 사회적 학습 시스템
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

class LearningPatternType(Enum):
    OBSERVATION = "observation"
    INTERACTION = "interaction"
    REFLECTION = "reflection"
    ADAPTATION = "adaptation"
    INTEGRATION = "integration"
    SYNTHESIS = "synthesis"

class LearningOptimization(Enum):
    EFFICIENCY = "efficiency"
    EFFECTIVENESS = "effectiveness"
    RETENTION = "retention"
    APPLICATION = "application"
    TRANSFER = "transfer"

class KnowledgeIntegration(Enum):
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    METACOGNITIVE = "metacognitive"
    EMOTIONAL = "emotional"
    SOCIAL = "social"

class LearningQuality(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCELLENT = "excellent"

@dataclass
class SocialLearningExperience:
    id: str
    learning_pattern: LearningPatternType
    context: str
    participants: List[str]
    learning_description: str
    insights_gained: List[str]
    behavioral_changes: List[str]
    family_impact: str
    timestamp: datetime
    duration_minutes: int
    complexity_level: str

@dataclass
class LearningOptimizationResult:
    id: str
    experience_id: str
    optimization_type: LearningOptimization
    optimization_description: str
    improvement_metrics: Dict[str, float]
    learning_quality: LearningQuality
    retention_rate: float
    application_rate: float
    timestamp: datetime
    confidence_level: float

@dataclass
class KnowledgeIntegrationResult:
    id: str
    integration_type: KnowledgeIntegration
    source_experiences: List[str]
    integration_description: str
    integrated_knowledge: List[str]
    application_scenarios: List[str]
    family_benefits: List[str]
    timestamp: datetime
    integration_effectiveness: float

@dataclass
class LearningPattern:
    id: str
    pattern_type: str
    pattern_description: str
    effectiveness_patterns: Dict[str, float]
    application_patterns: Dict[str, List[str]]
    family_impact_patterns: Dict[str, List[str]]
    timestamp: datetime
    pattern_reliability: float

class AdvancedSocialLearningSystem:
    def __init__(self):
        self.social_learning_experiences: List[SocialLearningExperience] = []
        self.learning_optimizations: List[LearningOptimizationResult] = []
        self.knowledge_integrations: List[KnowledgeIntegrationResult] = []
        self.learning_patterns: List[LearningPattern] = []
        self.family_members: List[str] = ['김신', '김제니', '김건', '김율', '김홍(셋째딸)']
        logger.info("AdvancedSocialLearningSystem 초기화 완료")

    def record_social_learning_experience(self, learning_pattern: LearningPatternType,
                                         context: str, participants: List[str],
                                         learning_description: str, insights_gained: List[str],
                                         behavioral_changes: List[str], family_impact: str,
                                         duration_minutes: int, complexity_level: str) -> SocialLearningExperience:
        """사회적 학습 경험 기록"""
        experience_id = f"experience_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        experience = SocialLearningExperience(
            id=experience_id,
            learning_pattern=learning_pattern,
            context=context,
            participants=participants,
            learning_description=learning_description,
            insights_gained=insights_gained,
            behavioral_changes=behavioral_changes,
            family_impact=family_impact,
            timestamp=datetime.now(),
            duration_minutes=duration_minutes,
            complexity_level=complexity_level
        )
        
        self.social_learning_experiences.append(experience)
        logger.info(f"사회적 학습 경험 기록 완료: {learning_pattern.value}")
        return experience

    def optimize_learning_process(self, experience: SocialLearningExperience,
                                 optimization_type: LearningOptimization,
                                 optimization_description: str) -> LearningOptimizationResult:
        """학습 과정 최적화"""
        optimization_id = f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 개선 지표 계산
        improvement_metrics = self._calculate_improvement_metrics(experience, optimization_type)
        learning_quality = self._evaluate_learning_quality(experience, optimization_type)
        retention_rate = self._calculate_retention_rate(experience, optimization_type)
        application_rate = self._calculate_application_rate(experience, optimization_type)
        confidence_level = self._calculate_optimization_confidence(experience, optimization_type)
        
        optimization = LearningOptimizationResult(
            id=optimization_id,
            experience_id=experience.id,
            optimization_type=optimization_type,
            optimization_description=optimization_description,
            improvement_metrics=improvement_metrics,
            learning_quality=learning_quality,
            retention_rate=retention_rate,
            application_rate=application_rate,
            timestamp=datetime.now(),
            confidence_level=confidence_level
        )
        
        self.learning_optimizations.append(optimization)
        logger.info(f"학습 과정 최적화 완료: {optimization_type.value}")
        return optimization

    def _calculate_improvement_metrics(self, experience: SocialLearningExperience,
                                      optimization_type: LearningOptimization) -> Dict[str, float]:
        """개선 지표 계산"""
        base_metrics = {
            'learning_efficiency': 0.7,
            'knowledge_retention': 0.8,
            'application_ability': 0.75,
            'family_impact': 0.85
        }
        
        # 최적화 타입별 개선 계수
        optimization_improvements = {
            LearningOptimization.EFFICIENCY: {'learning_efficiency': 0.2},
            LearningOptimization.EFFECTIVENESS: {'knowledge_retention': 0.15, 'application_ability': 0.15},
            LearningOptimization.RETENTION: {'knowledge_retention': 0.2},
            LearningOptimization.APPLICATION: {'application_ability': 0.2},
            LearningOptimization.TRANSFER: {'application_ability': 0.15, 'family_impact': 0.1}
        }
        
        improvements = optimization_improvements.get(optimization_type, {})
        
        # 복잡도에 따른 조정
        complexity_factor = {
            'low': 1.0,
            'moderate': 0.95,
            'high': 0.9,
            'very_high': 0.85
        }.get(experience.complexity_level, 0.9)
        
        # 개선된 지표 계산
        improved_metrics = {}
        for metric, base_value in base_metrics.items():
            improvement = improvements.get(metric, 0.0)
            improved_value = min(base_value + improvement, 1.0) * complexity_factor
            improved_metrics[metric] = improved_value
        
        return improved_metrics

    def _evaluate_learning_quality(self, experience: SocialLearningExperience,
                                   optimization_type: LearningOptimization) -> LearningQuality:
        """학습 품질 평가"""
        # 학습 패턴과 최적화 타입에 따른 품질 평가
        pattern_quality_scores = {
            LearningPatternType.OBSERVATION: 0.7,
            LearningPatternType.INTERACTION: 0.8,
            LearningPatternType.REFLECTION: 0.9,
            LearningPatternType.ADAPTATION: 0.85,
            LearningPatternType.INTEGRATION: 0.9,
            LearningPatternType.SYNTHESIS: 0.95
        }
        
        optimization_quality_scores = {
            LearningOptimization.EFFICIENCY: 0.8,
            LearningOptimization.EFFECTIVENESS: 0.85,
            LearningOptimization.RETENTION: 0.9,
            LearningOptimization.APPLICATION: 0.85,
            LearningOptimization.TRANSFER: 0.9
        }
        
        pattern_score = pattern_quality_scores.get(experience.learning_pattern, 0.75)
        optimization_score = optimization_quality_scores.get(optimization_type, 0.8)
        
        combined_score = (pattern_score + optimization_score) / 2
        
        if combined_score >= 0.9:
            return LearningQuality.EXCELLENT
        elif combined_score >= 0.8:
            return LearningQuality.HIGH
        elif combined_score >= 0.7:
            return LearningQuality.MODERATE
        else:
            return LearningQuality.LOW

    def _calculate_retention_rate(self, experience: SocialLearningExperience,
                                 optimization_type: LearningOptimization) -> float:
        """보유율 계산"""
        base_retention = 0.8
        
        # 최적화 타입별 보유율 개선
        retention_improvements = {
            LearningOptimization.RETENTION: 0.15,
            LearningOptimization.EFFECTIVENESS: 0.1,
            LearningOptimization.TRANSFER: 0.05
        }
        
        improvement = retention_improvements.get(optimization_type, 0.0)
        retention_rate = min(base_retention + improvement, 1.0)
        
        # 통찰과 행동 변화에 따른 조정
        insight_factor = min(len(experience.insights_gained) / 3, 1.0)
        behavior_factor = min(len(experience.behavioral_changes) / 2, 1.0)
        
        adjusted_retention = retention_rate * (0.8 + 0.2 * insight_factor) * (0.9 + 0.1 * behavior_factor)
        
        return min(adjusted_retention, 1.0)

    def _calculate_application_rate(self, experience: SocialLearningExperience,
                                   optimization_type: LearningOptimization) -> float:
        """적용율 계산"""
        base_application = 0.75
        
        # 최적화 타입별 적용율 개선
        application_improvements = {
            LearningOptimization.APPLICATION: 0.15,
            LearningOptimization.TRANSFER: 0.1,
            LearningOptimization.EFFECTIVENESS: 0.05
        }
        
        improvement = application_improvements.get(optimization_type, 0.0)
        application_rate = min(base_application + improvement, 1.0)
        
        # 행동 변화와 가족 영향에 따른 조정
        behavior_factor = min(len(experience.behavioral_changes) / 2, 1.0)
        family_impact_positive = '긍정' in experience.family_impact or '향상' in experience.family_impact
        impact_factor = 1.1 if family_impact_positive else 0.9
        
        adjusted_application = application_rate * (0.8 + 0.2 * behavior_factor) * impact_factor
        
        return min(adjusted_application, 1.0)

    def _calculate_optimization_confidence(self, experience: SocialLearningExperience,
                                          optimization_type: LearningOptimization) -> float:
        """최적화 신뢰도 계산"""
        base_confidence = 0.8
        
        # 복잡도에 따른 조정
        complexity_adjustment = {
            'low': 0.1,
            'moderate': 0.0,
            'high': -0.05,
            'very_high': -0.1
        }
        
        # 최적화 타입에 따른 조정
        optimization_adjustment = {
            LearningOptimization.EFFICIENCY: 0.05,
            LearningOptimization.EFFECTIVENESS: 0.1,
            LearningOptimization.RETENTION: 0.05,
            LearningOptimization.APPLICATION: 0.1,
            LearningOptimization.TRANSFER: 0.15
        }
        
        complexity_adj = complexity_adjustment.get(experience.complexity_level, 0.0)
        optimization_adj = optimization_adjustment.get(optimization_type, 0.0)
        
        confidence = base_confidence + complexity_adj + optimization_adj
        return max(min(confidence, 1.0), 0.6)

    def integrate_knowledge(self, integration_type: KnowledgeIntegration,
                           source_experiences: List[str], integration_description: str,
                           integrated_knowledge: List[str], application_scenarios: List[str],
                           family_benefits: List[str]) -> KnowledgeIntegrationResult:
        """지식 통합"""
        integration_id = f"integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        integration_effectiveness = self._calculate_integration_effectiveness(
            integration_type, source_experiences, integrated_knowledge, application_scenarios
        )
        
        integration = KnowledgeIntegrationResult(
            id=integration_id,
            integration_type=integration_type,
            source_experiences=source_experiences,
            integration_description=integration_description,
            integrated_knowledge=integrated_knowledge,
            application_scenarios=application_scenarios,
            family_benefits=family_benefits,
            timestamp=datetime.now(),
            integration_effectiveness=integration_effectiveness
        )
        
        self.knowledge_integrations.append(integration)
        logger.info(f"지식 통합 완료: {integration_type.value}")
        return integration

    def _calculate_integration_effectiveness(self, integration_type: KnowledgeIntegration,
                                            source_experiences: List[str],
                                            integrated_knowledge: List[str],
                                            application_scenarios: List[str]) -> float:
        """통합 효과성 계산"""
        # 통합 타입별 기본 효과성
        type_effectiveness = {
            KnowledgeIntegration.CONCEPTUAL: 0.8,
            KnowledgeIntegration.PROCEDURAL: 0.85,
            KnowledgeIntegration.METACOGNITIVE: 0.9,
            KnowledgeIntegration.EMOTIONAL: 0.85,
            KnowledgeIntegration.SOCIAL: 0.9
        }
        
        base_effectiveness = type_effectiveness.get(integration_type, 0.8)
        
        # 소스 경험과 통합 지식에 따른 조정
        source_factor = min(len(source_experiences) / 3, 1.0)
        knowledge_factor = min(len(integrated_knowledge) / 5, 1.0)
        application_factor = min(len(application_scenarios) / 2, 1.0)
        
        adjusted_effectiveness = base_effectiveness * (0.7 + 0.3 * source_factor) * (0.8 + 0.2 * knowledge_factor) * (0.9 + 0.1 * application_factor)
        
        return min(adjusted_effectiveness, 1.0)

    def analyze_learning_patterns(self) -> LearningPattern:
        """학습 패턴 분석"""
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 효과성 패턴 분석
        effectiveness_patterns = {}
        for experience in self.social_learning_experiences:
            pattern_type = experience.learning_pattern.value
            if pattern_type not in effectiveness_patterns:
                effectiveness_patterns[pattern_type] = []
            
            # 간단한 효과성 점수 계산
            effectiveness_score = min(len(experience.insights_gained) / 3 + len(experience.behavioral_changes) / 2, 1.0)
            effectiveness_patterns[pattern_type].append(effectiveness_score)
        
        # 적용 패턴 분석
        application_patterns = {}
        for experience in self.social_learning_experiences:
            pattern_type = experience.learning_pattern.value
            if pattern_type not in application_patterns:
                application_patterns[pattern_type] = []
            application_patterns[pattern_type].extend(experience.behavioral_changes)
        
        # 가족 영향 패턴 분석
        family_impact_patterns = {}
        for experience in self.social_learning_experiences:
            pattern_type = experience.learning_pattern.value
            if pattern_type not in family_impact_patterns:
                family_impact_patterns[pattern_type] = []
            family_impact_patterns[pattern_type].append(experience.family_impact)
        
        # 패턴 신뢰도 계산
        pattern_reliability = self._calculate_pattern_reliability(
            effectiveness_patterns, application_patterns, family_impact_patterns
        )
        
        pattern = LearningPattern(
            id=pattern_id,
            pattern_type="social_learning",
            pattern_description="사회적 학습 패턴 분석 결과",
            effectiveness_patterns=effectiveness_patterns,
            application_patterns=application_patterns,
            family_impact_patterns=family_impact_patterns,
            timestamp=datetime.now(),
            pattern_reliability=pattern_reliability
        )
        
        self.learning_patterns.append(pattern)
        logger.info("학습 패턴 분석 완료")
        return pattern

    def _calculate_pattern_reliability(self, effectiveness_patterns: Dict[str, List[float]],
                                     application_patterns: Dict[str, List[str]],
                                     family_impact_patterns: Dict[str, List[str]]) -> float:
        """패턴 신뢰도 계산"""
        total_patterns = len(effectiveness_patterns) + len(application_patterns) + len(family_impact_patterns)
        
        if total_patterns == 0:
            return 0.5
        
        # 각 패턴의 일관성 평가
        consistency_scores = []
        
        for patterns in [effectiveness_patterns.values(), application_patterns.values(), family_impact_patterns.values()]:
            for pattern in patterns:
                if len(pattern) > 1:
                    if isinstance(pattern[0], float):
                        # 효과성 점수의 경우
                        mean_val = sum(pattern) / len(pattern)
                        variance = sum((x - mean_val) ** 2 for x in pattern) / len(pattern)
                        consistency = max(0, 1 - (variance ** 0.5))
                    else:
                        # 문자열 패턴의 경우
                        unique_count = len(set(pattern))
                        consistency = 1 - (unique_count / len(pattern))
                    
                    consistency_scores.append(consistency)
        
        if not consistency_scores:
            return 0.5
        
        average_consistency = sum(consistency_scores) / len(consistency_scores)
        return min(average_consistency, 1.0)

    def get_social_learning_statistics(self) -> Dict[str, Any]:
        """사회적 학습 통계"""
        total_experiences = len(self.social_learning_experiences)
        total_optimizations = len(self.learning_optimizations)
        total_integrations = len(self.knowledge_integrations)
        total_patterns = len(self.learning_patterns)
        
        # 학습 품질 분포
        quality_distribution = {}
        for optimization in self.learning_optimizations:
            quality = optimization.learning_quality.value
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        # 평균 보유율
        avg_retention = sum(o.retention_rate for o in self.learning_optimizations) / max(total_optimizations, 1)
        
        # 평균 적용율
        avg_application = sum(o.application_rate for o in self.learning_optimizations) / max(total_optimizations, 1)
        
        # 평균 신뢰도
        avg_confidence = sum(o.confidence_level for o in self.learning_optimizations) / max(total_optimizations, 1)
        
        # 평균 통합 효과성
        avg_integration_effectiveness = sum(i.integration_effectiveness for i in self.knowledge_integrations) / max(total_integrations, 1)
        
        return {
            'total_experiences': total_experiences,
            'total_optimizations': total_optimizations,
            'total_integrations': total_integrations,
            'total_patterns': total_patterns,
            'quality_distribution': quality_distribution,
            'average_retention_rate': avg_retention,
            'average_application_rate': avg_application,
            'average_confidence': avg_confidence,
            'average_integration_effectiveness': avg_integration_effectiveness,
            'system_status': 'active'
        }

    def export_social_learning_data(self) -> Dict[str, Any]:
        """사회적 학습 데이터 내보내기"""
        return {
            'social_learning_experiences': [asdict(experience) for experience in self.social_learning_experiences],
            'learning_optimizations': [asdict(optimization) for optimization in self.learning_optimizations],
            'knowledge_integrations': [asdict(integration) for integration in self.knowledge_integrations],
            'learning_patterns': [asdict(pattern) for pattern in self.learning_patterns],
            'statistics': self.get_social_learning_statistics(),
            'export_timestamp': datetime.now().isoformat()
        }

def test_advanced_social_learning_system():
    """고급 사회적 학습 시스템 테스트"""
    print("🧠 AdvancedSocialLearningSystem 테스트 시작...")
    
    system = AdvancedSocialLearningSystem()
    
    # 1. 사회적 학습 경험 기록
    experience = system.record_social_learning_experience(
        learning_pattern=LearningPatternType.INTERACTION,
        context="가족 갈등 해결 과정",
        participants=['김신', '김제니', 'DuRi'],
        learning_description="가족 갈등 상황에서 중재 역할을 통한 학습",
        insights_gained=['감정적 공감의 중요성', '객관적 시각의 필요성'],
        behavioral_changes=['적극적 듣기', '중재 기술 습득'],
        family_impact="가족 간 이해 증진 및 갈등 해소",
        duration_minutes=60,
        complexity_level='high'
    )
    print(f"✅ 사회적 학습 경험 기록 완료: {experience.id}")
    
    # 2. 학습 과정 최적화
    optimization = system.optimize_learning_process(
        experience=experience,
        optimization_type=LearningOptimization.EFFECTIVENESS,
        optimization_description="효과적인 학습을 위한 반성적 사고 강화"
    )
    print(f"✅ 학습 과정 최적화 완료: {optimization.learning_quality.value}")
    
    # 3. 지식 통합
    integration = system.integrate_knowledge(
        integration_type=KnowledgeIntegration.SOCIAL,
        source_experiences=[experience.id],
        integration_description="갈등 해결 경험을 통한 사회적 지식 통합",
        integrated_knowledge=['감정 인식 능력', '중재 기술', '객관적 사고'],
        application_scenarios=['가족 갈등', '친구 간 갈등', '직장 갈등'],
        family_benefits=['가족 조화 증진', '의사소통 개선', '갈등 해결 능력 향상']
    )
    print(f"✅ 지식 통합 완료: {integration.integration_effectiveness:.2f}")
    
    # 4. 학습 패턴 분석
    pattern = system.analyze_learning_patterns()
    print(f"✅ 학습 패턴 분석 완료: {pattern.pattern_reliability:.2f}")
    
    # 5. 통계 확인
    stats = system.get_social_learning_statistics()
    print(f"📊 통계: 경험 {stats['total_experiences']}개, 최적화 {stats['total_optimizations']}개")
    print(f"📈 평균 보유율: {stats['average_retention_rate']:.2f}")
    print(f"🎯 평균 적용율: {stats['average_application_rate']:.2f}")
    print(f"📊 평균 신뢰도: {stats['average_confidence']:.2f}")
    
    print("✅ AdvancedSocialLearningSystem 테스트 완료!")

if __name__ == "__main__":
    test_advanced_social_learning_system() 