#!/usr/bin/env python3
"""
AdvancedSocialAdaptationSystem - Phase 15.1
고급 사회적 적응 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialContext(Enum):
    FAMILY = "family"
    WORK = "work"
    COMMUNITY = "community"
    EDUCATIONAL = "educational"
    EMERGENCY = "emergency"
    CELEBRATION = "celebration"
    CONFLICT = "conflict"


class AdaptationLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXCELLENT = "excellent"


class BehaviorType(Enum):
    COOPERATIVE = "cooperative"
    SUPPORTIVE = "supportive"
    LEADERSHIP = "leadership"
    MEDIATION = "mediation"
    LEARNING = "learning"
    EMOTIONAL_SUPPORT = "emotional_support"


class LearningOptimization(Enum):
    OBSERVATION = "observation"
    INTERACTION = "interaction"
    REFLECTION = "reflection"
    ADAPTATION = "adaptation"
    INTEGRATION = "integration"


@dataclass
class SocialSituation:
    id: str
    context: SocialContext
    participants: List[str]
    situation_description: str
    emotional_states: Dict[str, str]
    social_dynamics: List[str]
    adaptation_requirements: List[str]
    timestamp: datetime
    duration_minutes: int
    complexity_level: str


@dataclass
class AdaptiveResponse:
    id: str
    situation_id: str
    response_type: BehaviorType
    response_description: str
    adaptation_level: AdaptationLevel
    effectiveness_score: float
    family_impact: str
    learning_outcomes: List[str]
    timestamp: datetime
    confidence_level: float


@dataclass
class SocialLearning:
    id: str
    learning_type: LearningOptimization
    context: SocialContext
    learning_description: str
    insights_gained: List[str]
    behavioral_changes: List[str]
    family_benefits: List[str]
    timestamp: datetime
    learning_effectiveness: float


@dataclass
class AdaptationPattern:
    id: str
    pattern_type: str
    context_patterns: Dict[SocialContext, List[str]]
    response_patterns: Dict[BehaviorType, List[str]]
    effectiveness_patterns: Dict[str, float]
    family_impact_patterns: Dict[str, List[str]]
    timestamp: datetime
    pattern_reliability: float


class AdvancedSocialAdaptationSystem:
    def __init__(self):
        self.social_situations: List[SocialSituation] = []
        self.adaptive_responses: List[AdaptiveResponse] = []
        self.social_learnings: List[SocialLearning] = []
        self.adaptation_patterns: List[AdaptationPattern] = []
        self.family_members: List[str] = [
            "김신",
            "김제니",
            "김건",
            "김율",
            "김홍(셋째딸)",
        ]
        logger.info("AdvancedSocialAdaptationSystem 초기화 완료")

    def record_social_situation(
        self,
        context: SocialContext,
        participants: List[str],
        situation_description: str,
        emotional_states: Dict[str, str],
        social_dynamics: List[str],
        adaptation_requirements: List[str],
        duration_minutes: int,
        complexity_level: str,
    ) -> SocialSituation:
        """사회적 상황 기록"""
        situation_id = f"situation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        situation = SocialSituation(
            id=situation_id,
            context=context,
            participants=participants,
            situation_description=situation_description,
            emotional_states=emotional_states,
            social_dynamics=social_dynamics,
            adaptation_requirements=adaptation_requirements,
            timestamp=datetime.now(),
            duration_minutes=duration_minutes,
            complexity_level=complexity_level,
        )

        self.social_situations.append(situation)
        logger.info(f"사회적 상황 기록 완료: {context.value}")
        return situation

    def generate_adaptive_response(
        self,
        situation: SocialSituation,
        response_type: BehaviorType,
        response_description: str,
    ) -> AdaptiveResponse:
        """적응적 반응 생성"""
        response_id = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 적응 수준 평가
        adaptation_level = self._evaluate_adaptation_level(situation, response_type)
        effectiveness_score = self._calculate_effectiveness(situation, response_type)
        family_impact = self._assess_family_impact(situation, response_type)
        learning_outcomes = self._identify_learning_outcomes(situation, response_type)
        confidence_level = self._calculate_confidence(situation, response_type)

        response = AdaptiveResponse(
            id=response_id,
            situation_id=situation.id,
            response_type=response_type,
            response_description=response_description,
            adaptation_level=adaptation_level,
            effectiveness_score=effectiveness_score,
            family_impact=family_impact,
            learning_outcomes=learning_outcomes,
            timestamp=datetime.now(),
            confidence_level=confidence_level,
        )

        self.adaptive_responses.append(response)
        logger.info(f"적응적 반응 생성 완료: {response_type.value}")
        return response

    def _evaluate_adaptation_level(
        self, situation: SocialSituation, response_type: BehaviorType
    ) -> AdaptationLevel:
        """적응 수준 평가"""
        # 상황 복잡도와 반응 타입에 따른 적응 수준 결정
        complexity_scores = {"low": 0.3, "moderate": 0.5, "high": 0.7, "very_high": 0.9}

        behavior_scores = {
            BehaviorType.COOPERATIVE: 0.8,
            BehaviorType.SUPPORTIVE: 0.9,
            BehaviorType.LEADERSHIP: 0.7,
            BehaviorType.MEDIATION: 0.8,
            BehaviorType.LEARNING: 0.9,
            BehaviorType.EMOTIONAL_SUPPORT: 0.9,
        }

        complexity_score = complexity_scores.get(situation.complexity_level, 0.5)
        behavior_score = behavior_scores.get(response_type, 0.7)

        combined_score = (complexity_score + behavior_score) / 2

        if combined_score >= 0.9:
            return AdaptationLevel.EXCELLENT
        elif combined_score >= 0.7:
            return AdaptationLevel.HIGH
        elif combined_score >= 0.5:
            return AdaptationLevel.MODERATE
        else:
            return AdaptationLevel.LOW

    def _calculate_effectiveness(
        self, situation: SocialSituation, response_type: BehaviorType
    ) -> float:
        """효과성 점수 계산"""
        # 상황 맥락과 반응 타입의 적합성 평가
        context_effectiveness = {
            SocialContext.FAMILY: {
                BehaviorType.EMOTIONAL_SUPPORT: 0.95,
                BehaviorType.SUPPORTIVE: 0.90,
                BehaviorType.COOPERATIVE: 0.85,
            },
            SocialContext.CONFLICT: {
                BehaviorType.MEDIATION: 0.90,
                BehaviorType.LEADERSHIP: 0.85,
                BehaviorType.COOPERATIVE: 0.80,
            },
            SocialContext.CELEBRATION: {
                BehaviorType.SUPPORTIVE: 0.95,
                BehaviorType.EMOTIONAL_SUPPORT: 0.90,
                BehaviorType.COOPERATIVE: 0.85,
            },
        }

        base_effectiveness = context_effectiveness.get(situation.context, {}).get(
            response_type, 0.75
        )

        # 참여자 수와 감정 상태에 따른 조정
        participant_factor = min(len(situation.participants) / 5, 1.0)
        emotional_stability = self._assess_emotional_stability(
            situation.emotional_states
        )

        adjusted_effectiveness = (
            base_effectiveness * (0.8 + 0.2 * participant_factor) * emotional_stability
        )

        return min(adjusted_effectiveness, 1.0)

    def _assess_emotional_stability(self, emotional_states: Dict[str, str]) -> float:
        """감정적 안정성 평가"""
        positive_emotions = ["happy", "calm", "excited", "content", "grateful"]
        negative_emotions = ["angry", "sad", "anxious", "frustrated", "confused"]

        positive_count = sum(
            1 for emotion in emotional_states.values() if emotion in positive_emotions
        )
        negative_count = sum(
            1 for emotion in emotional_states.values() if emotion in negative_emotions
        )
        total_count = len(emotional_states)

        if total_count == 0:
            return 0.8  # 기본값

        stability_score = positive_count / total_count
        return max(stability_score, 0.3)  # 최소 0.3 보장

    def _assess_family_impact(
        self, situation: SocialSituation, response_type: BehaviorType
    ) -> str:
        """가족 영향 평가"""
        impact_assessments = {
            BehaviorType.EMOTIONAL_SUPPORT: "가족 구성원의 감정적 안정성 향상",
            BehaviorType.SUPPORTIVE: "가족 간 협력과 지지 강화",
            BehaviorType.COOPERATIVE: "가족 조화와 협력 증진",
            BehaviorType.MEDIATION: "가족 갈등 해소 및 이해 증진",
            BehaviorType.LEADERSHIP: "가족 발전 방향 제시",
            BehaviorType.LEARNING: "가족 구성원의 성장 촉진",
        }

        return impact_assessments.get(response_type, "가족 관계에 긍정적 영향")

    def _identify_learning_outcomes(
        self, situation: SocialSituation, response_type: BehaviorType
    ) -> List[str]:
        """학습 결과 식별"""
        learning_outcomes = {
            BehaviorType.EMOTIONAL_SUPPORT: [
                "감정 인식 능력 향상",
                "공감 능력 강화",
                "감정적 안정성 증진",
            ],
            BehaviorType.SUPPORTIVE: [
                "지지적 행동 패턴 학습",
                "협력적 문제 해결 능력 향상",
                "가족 중심 사고 강화",
            ],
            BehaviorType.COOPERATIVE: [
                "협력적 의사소통 능력 향상",
                "팀워크 이해 증진",
                "상호 존중 태도 강화",
            ],
            BehaviorType.MEDIATION: [
                "갈등 해결 능력 향상",
                "중재 기술 습득",
                "객관적 사고 능력 강화",
            ],
            BehaviorType.LEADERSHIP: [
                "리더십 능력 개발",
                "방향 제시 능력 향상",
                "책임감과 주도성 강화",
            ],
            BehaviorType.LEARNING: [
                "학습 능력 향상",
                "지식 통합 능력 강화",
                "성장 지향적 사고 강화",
            ],
        }

        return learning_outcomes.get(response_type, ["사회적 적응 능력 향상"])

    def _calculate_confidence(
        self, situation: SocialSituation, response_type: BehaviorType
    ) -> float:
        """신뢰도 계산"""
        # 상황 복잡도와 반응 타입의 적합성에 따른 신뢰도
        base_confidence = 0.8

        # 복잡도에 따른 조정
        complexity_adjustment = {
            "low": 0.1,
            "moderate": 0.0,
            "high": -0.1,
            "very_high": -0.2,
        }

        # 반응 타입에 따른 조정
        behavior_adjustment = {
            BehaviorType.EMOTIONAL_SUPPORT: 0.1,
            BehaviorType.SUPPORTIVE: 0.05,
            BehaviorType.COOPERATIVE: 0.0,
            BehaviorType.MEDIATION: -0.05,
            BehaviorType.LEADERSHIP: -0.1,
            BehaviorType.LEARNING: 0.05,
        }

        complexity_adj = complexity_adjustment.get(situation.complexity_level, 0.0)
        behavior_adj = behavior_adjustment.get(response_type, 0.0)

        confidence = base_confidence + complexity_adj + behavior_adj
        return max(min(confidence, 1.0), 0.5)  # 0.5 ~ 1.0 범위

    def record_social_learning(
        self,
        learning_type: LearningOptimization,
        context: SocialContext,
        learning_description: str,
        insights_gained: List[str],
        behavioral_changes: List[str],
        family_benefits: List[str],
    ) -> SocialLearning:
        """사회적 학습 기록"""
        learning_id = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        learning_effectiveness = self._calculate_learning_effectiveness(
            learning_type, context, insights_gained, behavioral_changes
        )

        learning = SocialLearning(
            id=learning_id,
            learning_type=learning_type,
            context=context,
            learning_description=learning_description,
            insights_gained=insights_gained,
            behavioral_changes=behavioral_changes,
            family_benefits=family_benefits,
            timestamp=datetime.now(),
            learning_effectiveness=learning_effectiveness,
        )

        self.social_learnings.append(learning)
        logger.info(f"사회적 학습 기록 완료: {learning_type.value}")
        return learning

    def _calculate_learning_effectiveness(
        self,
        learning_type: LearningOptimization,
        context: SocialContext,
        insights_gained: List[str],
        behavioral_changes: List[str],
    ) -> float:
        """학습 효과성 계산"""
        # 학습 타입별 기본 효과성
        type_effectiveness = {
            LearningOptimization.OBSERVATION: 0.7,
            LearningOptimization.INTERACTION: 0.8,
            LearningOptimization.REFLECTION: 0.9,
            LearningOptimization.ADAPTATION: 0.85,
            LearningOptimization.INTEGRATION: 0.9,
        }

        base_effectiveness = type_effectiveness.get(learning_type, 0.75)

        # 통찰과 행동 변화에 따른 조정
        insight_factor = min(len(insights_gained) / 3, 1.0)
        behavior_factor = min(len(behavioral_changes) / 2, 1.0)

        adjusted_effectiveness = (
            base_effectiveness
            * (0.7 + 0.3 * insight_factor)
            * (0.8 + 0.2 * behavior_factor)
        )

        return min(adjusted_effectiveness, 1.0)

    def analyze_adaptation_patterns(self) -> AdaptationPattern:
        """적응 패턴 분석"""
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 맥락별 패턴 분석
        context_patterns = {}
        for context in SocialContext:
            context_responses = [
                r
                for r in self.adaptive_responses
                if any(
                    s.context == context
                    for s in self.social_situations
                    if s.id == r.situation_id
                )
            ]
            if context_responses:
                context_patterns[context] = [
                    r.response_type.value for r in context_responses
                ]

        # 반응 타입별 패턴 분석
        response_patterns = {}
        for behavior_type in BehaviorType:
            type_responses = [
                r for r in self.adaptive_responses if r.response_type == behavior_type
            ]
            if type_responses:
                response_patterns[behavior_type] = [
                    r.adaptation_level.value for r in type_responses
                ]

        # 효과성 패턴 분석
        effectiveness_patterns = {}
        for response in self.adaptive_responses:
            response_type = response.response_type.value
            if response_type not in effectiveness_patterns:
                effectiveness_patterns[response_type] = []
            effectiveness_patterns[response_type].append(response.effectiveness_score)

        # 가족 영향 패턴 분석
        family_impact_patterns = {}
        for response in self.adaptive_responses:
            response_type = response.response_type.value
            if response_type not in family_impact_patterns:
                family_impact_patterns[response_type] = []
            family_impact_patterns[response_type].append(response.family_impact)

        # 패턴 신뢰도 계산
        pattern_reliability = self._calculate_pattern_reliability(
            context_patterns, response_patterns, effectiveness_patterns
        )

        pattern = AdaptationPattern(
            id=pattern_id,
            pattern_type="social_adaptation",
            context_patterns=context_patterns,
            response_patterns=response_patterns,
            effectiveness_patterns=effectiveness_patterns,
            family_impact_patterns=family_impact_patterns,
            timestamp=datetime.now(),
            pattern_reliability=pattern_reliability,
        )

        self.adaptation_patterns.append(pattern)
        logger.info("적응 패턴 분석 완료")
        return pattern

    def _calculate_pattern_reliability(
        self,
        context_patterns: Dict[SocialContext, List[str]],
        response_patterns: Dict[BehaviorType, List[str]],
        effectiveness_patterns: Dict[str, List[float]],
    ) -> float:
        """패턴 신뢰도 계산"""
        # 패턴의 일관성과 데이터 품질에 따른 신뢰도
        total_patterns = (
            len(context_patterns) + len(response_patterns) + len(effectiveness_patterns)
        )

        if total_patterns == 0:
            return 0.5

        # 각 패턴의 일관성 평가
        consistency_scores = []

        for patterns in [
            context_patterns.values(),
            response_patterns.values(),
            effectiveness_patterns.values(),
        ]:
            for pattern in patterns:
                if len(pattern) > 1:
                    # 패턴의 일관성 계산 (간단한 표준편차 기반)
                    if isinstance(pattern[0], float):
                        # 효과성 점수의 경우
                        mean_val = sum(pattern) / len(pattern)
                        variance = sum((x - mean_val) ** 2 for x in pattern) / len(
                            pattern
                        )
                        consistency = max(0, 1 - (variance**0.5))
                    else:
                        # 문자열 패턴의 경우
                        unique_count = len(set(pattern))
                        consistency = 1 - (unique_count / len(pattern))

                    consistency_scores.append(consistency)

        if not consistency_scores:
            return 0.5

        average_consistency = sum(consistency_scores) / len(consistency_scores)
        return min(average_consistency, 1.0)

    def get_social_adaptation_statistics(self) -> Dict[str, Any]:
        """사회적 적응 통계"""
        total_situations = len(self.social_situations)
        total_responses = len(self.adaptive_responses)
        total_learnings = len(self.social_learnings)
        total_patterns = len(self.adaptation_patterns)

        # 적응 수준 분포
        adaptation_distribution = {}
        for response in self.adaptive_responses:
            level = response.adaptation_level.value
            adaptation_distribution[level] = adaptation_distribution.get(level, 0) + 1

        # 평균 효과성
        avg_effectiveness = sum(
            r.effectiveness_score for r in self.adaptive_responses
        ) / max(total_responses, 1)

        # 평균 신뢰도
        avg_confidence = sum(r.confidence_level for r in self.adaptive_responses) / max(
            total_responses, 1
        )

        # 평균 학습 효과성
        avg_learning_effectiveness = sum(
            l.learning_effectiveness for l in self.social_learnings
        ) / max(total_learnings, 1)

        return {
            "total_situations": total_situations,
            "total_responses": total_responses,
            "total_learnings": total_learnings,
            "total_patterns": total_patterns,
            "adaptation_distribution": adaptation_distribution,
            "average_effectiveness": avg_effectiveness,
            "average_confidence": avg_confidence,
            "average_learning_effectiveness": avg_learning_effectiveness,
            "system_status": "active",
        }

    def export_social_adaptation_data(self) -> Dict[str, Any]:
        """사회적 적응 데이터 내보내기"""
        return {
            "social_situations": [
                asdict(situation) for situation in self.social_situations
            ],
            "adaptive_responses": [
                asdict(response) for response in self.adaptive_responses
            ],
            "social_learnings": [
                asdict(learning) for learning in self.social_learnings
            ],
            "adaptation_patterns": [
                asdict(pattern) for pattern in self.adaptation_patterns
            ],
            "statistics": self.get_social_adaptation_statistics(),
            "export_timestamp": datetime.now().isoformat(),
        }


def test_advanced_social_adaptation_system():
    """고급 사회적 적응 시스템 테스트"""
    print("🧠 AdvancedSocialAdaptationSystem 테스트 시작...")

    system = AdvancedSocialAdaptationSystem()

    # 1. 사회적 상황 기록
    situation = system.record_social_situation(
        context=SocialContext.FAMILY,
        participants=["김신", "김제니", "DuRi"],
        situation_description="가족 저녁 식사 중 감정적 대화",
        emotional_states={"김신": "calm", "김제니": "happy", "DuRi": "excited"},
        social_dynamics=["협력적 분위기", "상호 지지"],
        adaptation_requirements=["감정적 지원", "대화 참여"],
        duration_minutes=45,
        complexity_level="moderate",
    )
    print(f"✅ 사회적 상황 기록 완료: {situation.id}")

    # 2. 적응적 반응 생성
    response = system.generate_adaptive_response(
        situation=situation,
        response_type=BehaviorType.EMOTIONAL_SUPPORT,
        response_description="가족 구성원의 감정에 공감하며 적극적으로 대화에 참여",
    )
    print(f"✅ 적응적 반응 생성 완료: {response.adaptation_level.value}")

    # 3. 사회적 학습 기록
    learning = system.record_social_learning(
        learning_type=LearningOptimization.INTERACTION,
        context=SocialContext.FAMILY,
        learning_description="가족과의 감정적 상호작용을 통한 공감 능력 향상",
        insights_gained=["감정 인식의 중요성", "공감적 반응의 효과"],
        behavioral_changes=["적극적 듣기", "감정 표현 개선"],
        family_benefits=["가족 간 이해 증진", "감정적 안정성 향상"],
    )
    print(f"✅ 사회적 학습 기록 완료: {learning.learning_effectiveness:.2f}")

    # 4. 적응 패턴 분석
    pattern = system.analyze_adaptation_patterns()
    print(f"✅ 적응 패턴 분석 완료: {pattern.pattern_reliability:.2f}")

    # 5. 통계 확인
    stats = system.get_social_adaptation_statistics()
    print(
        f"📊 통계: 상황 {stats['total_situations']}개, 반응 {stats['total_responses']}개"
    )
    print(f"📈 평균 효과성: {stats['average_effectiveness']:.2f}")
    print(f"🎯 평균 신뢰도: {stats['average_confidence']:.2f}")

    print("✅ AdvancedSocialAdaptationSystem 테스트 완료!")


if __name__ == "__main__":
    test_advanced_social_adaptation_system()
