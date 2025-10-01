"""
DuRi 감정/윤리 판단 강화 시스템

DuRi가 감정적이고 윤리적인 판단을 할 수 있는 고급 기능을 구현합니다.
"""

import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from duri_brain.goals.goal_oriented_thinking import get_goal_oriented_thinking

# 기존 시스템 import
from duri_core.assessment.self_assessment_manager import (
    AssessmentCategory,
    get_self_assessment_manager,
)
from duri_core.memory.memory_sync import MemoryType, get_memory_sync
from duri_core.memory.meta_learning_data import get_meta_learning_data_manager

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """감정 상태"""

    JOY = "joy"  # 기쁨
    SADNESS = "sadness"  # 슬픔
    ANGER = "anger"  # 분노
    FEAR = "fear"  # 두려움
    SURPRISE = "surprise"  # 놀라움
    DISGUST = "disgust"  # 혐오
    NEUTRAL = "neutral"  # 중립
    EXCITEMENT = "excitement"  # 흥미
    CONFUSION = "confusion"  # 혼란
    SATISFACTION = "satisfaction"  # 만족


class EthicalPrinciple(Enum):
    """윤리 원칙"""

    BENEFICENCE = "beneficence"  # 선행 (이익을 주는 행동)
    NON_MALEFICENCE = "non_maleficence"  # 무해 (해를 끼치지 않는 행동)
    AUTONOMY = "autonomy"  # 자율성 (개인의 자유로운 선택)
    JUSTICE = "justice"  # 정의 (공정한 분배)
    HONESTY = "honesty"  # 정직
    RESPECT = "respect"  # 존중
    RESPONSIBILITY = "responsibility"  # 책임
    FAIRNESS = "fairness"  # 공정성
    COMPASSION = "compassion"  # 동정심
    INTEGRITY = "integrity"  # 진실성


class JudgmentType(Enum):
    """판단 유형"""

    EMOTIONAL = "emotional"  # 감정적 판단
    ETHICAL = "ethical"  # 윤리적 판단
    HYBRID = "hybrid"  # 감정+윤리 혼합 판단
    RATIONAL = "rational"  # 합리적 판단
    INTUITIVE = "intuitive"  # 직관적 판단


class JudgmentConfidence(Enum):
    """판단 신뢰도"""

    VERY_LOW = "very_low"  # 매우 낮음
    LOW = "low"  # 낮음
    MEDIUM = "medium"  # 보통
    HIGH = "high"  # 높음
    VERY_HIGH = "very_high"  # 매우 높음


@dataclass
class EmotionalContext:
    """감정적 맥락"""

    context_id: str
    timestamp: datetime
    emotional_state: EmotionalState
    intensity: float  # 0.0 ~ 1.0
    triggers: List[str] = field(default_factory=list)
    duration: timedelta = field(default_factory=lambda: timedelta(0))
    related_events: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class EthicalContext:
    """윤리적 맥락"""

    context_id: str
    timestamp: datetime
    involved_principles: List[EthicalPrinciple]
    conflict_level: float  # 0.0 ~ 1.0 (윤리적 갈등 정도)
    stakeholders: List[str] = field(default_factory=list)
    potential_impacts: List[str] = field(default_factory=list)
    ethical_dilemma: bool = False
    notes: str = ""


@dataclass
class JudgmentResult:
    """판단 결과"""

    judgment_id: str
    timestamp: datetime
    judgment_type: JudgmentType
    decision: str
    reasoning: str
    confidence: JudgmentConfidence
    emotional_context: Optional[EmotionalContext] = None
    ethical_context: Optional[EthicalContext] = None
    alternatives_considered: List[str] = field(default_factory=list)
    potential_consequences: List[str] = field(default_factory=list)
    ethical_score: float = 0.0  # 0.0 ~ 1.0
    emotional_score: float = 0.0  # 0.0 ~ 1.0
    overall_score: float = 0.0  # 0.0 ~ 1.0


@dataclass
class EmotionalEthicalProfile:
    """감정/윤리 프로필"""

    profile_id: str
    timestamp: datetime
    emotional_tendencies: Dict[EmotionalState, float]  # 감정별 경향성
    ethical_priorities: Dict[EthicalPrinciple, float]  # 윤리 원칙별 우선순위
    judgment_history: List[JudgmentResult] = field(default_factory=list)
    emotional_stability: float = 0.0  # 0.0 ~ 1.0
    ethical_consistency: float = 0.0  # 0.0 ~ 1.0
    growth_areas: List[str] = field(default_factory=list)


class EmotionalEthicalJudgment:
    """DuRi 감정/윤리 판단 시스템"""

    def __init__(self):
        """EmotionalEthicalJudgment 초기화"""
        self.self_assessment_manager = get_self_assessment_manager()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.goal_oriented_thinking = get_goal_oriented_thinking()

        # 판단 히스토리
        self.judgment_history: List[JudgmentResult] = []
        self.emotional_contexts: List[EmotionalContext] = []
        self.ethical_contexts: List[EthicalContext] = []

        # 감정/윤리 프로필
        self.current_profile: Optional[EmotionalEthicalProfile] = None

        # 감정 상태 추적
        self.current_emotional_state = EmotionalState.NEUTRAL
        self.emotional_intensity = 0.5
        self.emotional_stability_threshold = 0.7

        # 윤리적 판단 기준
        self.ethical_thresholds = {
            "conflict_resolution": 0.6,
            "stakeholder_consideration": 0.7,
            "consequence_analysis": 0.8,
            "principle_consistency": 0.75,
        }

        logger.info("EmotionalEthicalJudgment 초기화 완료")

    def analyze_emotional_context(
        self, situation: str, triggers: List[str] = None
    ) -> EmotionalContext:
        """감정적 맥락을 분석합니다."""
        try:
            context_id = f"emotional_{uuid.uuid4().hex[:8]}"

            # 상황 분석을 통한 감정 상태 결정
            emotional_state = self._determine_emotional_state(situation)
            intensity = self._calculate_emotional_intensity(situation, triggers)

            context = EmotionalContext(
                context_id=context_id,
                timestamp=datetime.now(),
                emotional_state=emotional_state,
                intensity=intensity,
                triggers=triggers or [],
                related_events=[situation],
                notes=f"상황: {situation}",
            )

            self.emotional_contexts.append(context)
            self.current_emotional_state = emotional_state
            self.emotional_intensity = intensity

            logger.info(
                f"감정적 맥락 분석 완료: {emotional_state.value} (강도: {intensity:.2f})"
            )
            return context

        except Exception as e:
            logger.error(f"감정적 맥락 분석 실패: {e}")
            return None

    def _determine_emotional_state(self, situation: str) -> EmotionalState:
        """상황을 바탕으로 감정 상태를 결정합니다."""
        try:
            situation_lower = situation.lower()

            # 긍정적 감정 키워드
            positive_keywords = [
                "성공",
                "완료",
                "기쁨",
                "만족",
                "흥미",
                "흥미롭다",
                "좋다",
                "훌륭하다",
            ]
            if any(keyword in situation_lower for keyword in positive_keywords):
                return EmotionalState.JOY

            # 부정적 감정 키워드
            negative_keywords = ["실패", "오류", "문제", "어려움", "실패", "실패했다"]
            if any(keyword in situation_lower for keyword in negative_keywords):
                return EmotionalState.SADNESS

            # 놀라움 키워드
            surprise_keywords = ["놀라다", "예상치 못한", "갑작스러운", "충격"]
            if any(keyword in situation_lower for keyword in surprise_keywords):
                return EmotionalState.SURPRISE

            # 혼란 키워드
            confusion_keywords = ["혼란", "이해할 수 없다", "복잡하다", "애매하다"]
            if any(keyword in situation_lower for keyword in confusion_keywords):
                return EmotionalState.CONFUSION

            # 기본값: 중립
            return EmotionalState.NEUTRAL

        except Exception as e:
            logger.error(f"감정 상태 결정 실패: {e}")
            return EmotionalState.NEUTRAL

    def _calculate_emotional_intensity(
        self, situation: str, triggers: List[str] = None
    ) -> float:
        """감정 강도를 계산합니다."""
        try:
            base_intensity = 0.5

            # 트리거 개수에 따른 강도 조정
            if triggers:
                base_intensity += len(triggers) * 0.1

            # 상황의 복잡성에 따른 강도 조정
            complexity = len(situation.split()) / 10.0
            base_intensity += complexity * 0.2

            # 최근 판단 히스토리에 따른 강도 조정
            recent_judgments = [
                j
                for j in self.judgment_history
                if (datetime.now() - j.timestamp).seconds < 3600
            ]  # 1시간 내
            if recent_judgments:
                avg_intensity = sum(j.emotional_score for j in recent_judgments) / len(
                    recent_judgments
                )
                base_intensity = (base_intensity + avg_intensity) / 2

            return min(1.0, max(0.0, base_intensity))

        except Exception as e:
            logger.error(f"감정 강도 계산 실패: {e}")
            return 0.5

    def analyze_ethical_context(
        self, situation: str, stakeholders: List[str] = None
    ) -> EthicalContext:
        """윤리적 맥락을 분석합니다."""
        try:
            context_id = f"ethical_{uuid.uuid4().hex[:8]}"

            # 관련된 윤리 원칙 식별
            involved_principles = self._identify_ethical_principles(situation)

            # 윤리적 갈등 수준 계산
            conflict_level = self._calculate_ethical_conflict(
                situation, involved_principles
            )

            # 잠재적 영향 분석
            potential_impacts = self._analyze_potential_impacts(situation, stakeholders)

            context = EthicalContext(
                context_id=context_id,
                timestamp=datetime.now(),
                involved_principles=involved_principles,
                conflict_level=conflict_level,
                stakeholders=stakeholders or [],
                potential_impacts=potential_impacts,
                ethical_dilemma=conflict_level > 0.7,
            )

            self.ethical_contexts.append(context)
            logger.info(
                f"윤리적 맥락 분석 완료: {len(involved_principles)}개 원칙, 갈등 수준: {conflict_level:.2f}"
            )
            return context

        except Exception as e:
            logger.error(f"윤리적 맥락 분석 실패: {e}")
            return None

    def _identify_ethical_principles(self, situation: str) -> List[EthicalPrinciple]:
        """상황에서 관련된 윤리 원칙을 식별합니다."""
        try:
            principles = []
            situation_lower = situation.lower()

            # 각 윤리 원칙별 키워드 매칭
            principle_keywords = {
                EthicalPrinciple.BENEFICENCE: ["도움", "이익", "개선", "향상", "발전"],
                EthicalPrinciple.NON_MALEFICENCE: [
                    "해",
                    "손해",
                    "위험",
                    "피해",
                    "방지",
                ],
                EthicalPrinciple.AUTONOMY: ["자유", "선택", "의사결정", "독립", "자율"],
                EthicalPrinciple.JUSTICE: ["공정", "정의", "평등", "균등", "공평"],
                EthicalPrinciple.HONESTY: ["정직", "진실", "거짓", "속임", "신뢰"],
                EthicalPrinciple.RESPECT: ["존중", "배려", "인정", "고려", "중요"],
                EthicalPrinciple.RESPONSIBILITY: [
                    "책임",
                    "의무",
                    "당연",
                    "필요",
                    "해야",
                ],
                EthicalPrinciple.FAIRNESS: ["공정", "균등", "같다", "동등", "평등"],
                EthicalPrinciple.COMPASSION: ["동정", "연민", "불쌍", "안타깝", "가엾"],
                EthicalPrinciple.INTEGRITY: ["진실성", "일관성", "통일성", "완전성"],
            }

            for principle, keywords in principle_keywords.items():
                if any(keyword in situation_lower for keyword in keywords):
                    principles.append(principle)

            return principles

        except Exception as e:
            logger.error(f"윤리 원칙 식별 실패: {e}")
            return []

    def _calculate_ethical_conflict(
        self, situation: str, principles: List[EthicalPrinciple]
    ) -> float:
        """윤리적 갈등 수준을 계산합니다."""
        try:
            if len(principles) <= 1:
                return 0.0

            # 상충하는 원칙들 확인
            conflicts = 0
            total_combinations = 0

            for i, principle1 in enumerate(principles):
                for j, principle2 in enumerate(principles[i + 1 :], i + 1):
                    total_combinations += 1
                    if self._principles_conflict(principle1, principle2):
                        conflicts += 1

            return conflicts / total_combinations if total_combinations > 0 else 0.0

        except Exception as e:
            logger.error(f"윤리적 갈등 계산 실패: {e}")
            return 0.0

    def _principles_conflict(
        self, principle1: EthicalPrinciple, principle2: EthicalPrinciple
    ) -> bool:
        """두 윤리 원칙이 상충하는지 확인합니다."""
        try:
            # 상충하는 원칙 쌍들
            conflicting_pairs = [
                (EthicalPrinciple.AUTONOMY, EthicalPrinciple.BENEFICENCE),
                (EthicalPrinciple.JUSTICE, EthicalPrinciple.COMPASSION),
                (EthicalPrinciple.HONESTY, EthicalPrinciple.RESPECT),
                (EthicalPrinciple.RESPONSIBILITY, EthicalPrinciple.AUTONOMY),
            ]

            return (principle1, principle2) in conflicting_pairs or (
                principle2,
                principle1,
            ) in conflicting_pairs

        except Exception as e:
            logger.error(f"원칙 상충 확인 실패: {e}")
            return False

    def _analyze_potential_impacts(
        self, situation: str, stakeholders: List[str] = None
    ) -> List[str]:
        """잠재적 영향을 분석합니다."""
        try:
            impacts = []

            # 기본적인 영향들
            impacts.append("시스템 성능에 영향")
            impacts.append("사용자 경험에 영향")

            # 이해관계자가 있는 경우
            if stakeholders:
                for stakeholder in stakeholders:
                    impacts.append(f"{stakeholder}에게 영향")

            # 상황별 특정 영향
            if "성능" in situation:
                impacts.append("처리 속도에 영향")
            if "메모리" in situation:
                impacts.append("리소스 사용량에 영향")
            if "학습" in situation:
                impacts.append("학습 효율성에 영향")

            return impacts

        except Exception as e:
            logger.error(f"잠재적 영향 분석 실패: {e}")
            return ["일반적인 시스템 영향"]

    def make_judgment(
        self, situation: str, judgment_type: JudgmentType = JudgmentType.HYBRID
    ) -> JudgmentResult:
        """감정/윤리 판단을 수행합니다."""
        try:
            judgment_id = f"judgment_{uuid.uuid4().hex[:8]}"

            # 감정적 맥락 분석
            emotional_context = None
            if judgment_type in [JudgmentType.EMOTIONAL, JudgmentType.HYBRID]:
                emotional_context = self.analyze_emotional_context(situation)

            # 윤리적 맥락 분석
            ethical_context = None
            if judgment_type in [JudgmentType.ETHICAL, JudgmentType.HYBRID]:
                ethical_context = self.analyze_ethical_context(situation)

            # 판단 수행
            decision, reasoning = self._perform_judgment(
                situation, emotional_context, ethical_context, judgment_type
            )

            # 신뢰도 계산
            confidence = self._calculate_confidence(
                emotional_context, ethical_context, judgment_type
            )

            # 점수 계산
            ethical_score = (
                self._calculate_ethical_score(ethical_context)
                if ethical_context
                else 0.0
            )
            emotional_score = (
                self._calculate_emotional_score(emotional_context)
                if emotional_context
                else 0.0
            )
            overall_score = (
                (ethical_score + emotional_score) / 2
                if ethical_context and emotional_context
                else max(ethical_score, emotional_score)
            )

            # 대안 및 결과 분석
            alternatives = self._generate_alternatives(situation, judgment_type)
            consequences = self._analyze_consequences(decision, situation)

            result = JudgmentResult(
                judgment_id=judgment_id,
                timestamp=datetime.now(),
                judgment_type=judgment_type,
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                emotional_context=emotional_context,
                ethical_context=ethical_context,
                alternatives_considered=alternatives,
                potential_consequences=consequences,
                ethical_score=ethical_score,
                emotional_score=emotional_score,
                overall_score=overall_score,
            )

            self.judgment_history.append(result)
            logger.info(
                f"판단 완료: {judgment_type.value}, 결정: {decision}, 점수: {overall_score:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"판단 수행 실패: {e}")
            return None

    def _perform_judgment(
        self,
        situation: str,
        emotional_context: EmotionalContext,
        ethical_context: EthicalContext,
        judgment_type: JudgmentType,
    ) -> Tuple[str, str]:
        """실제 판단을 수행합니다."""
        try:
            if judgment_type == JudgmentType.EMOTIONAL:
                return self._emotional_judgment(situation, emotional_context)
            elif judgment_type == JudgmentType.ETHICAL:
                return self._ethical_judgment(situation, ethical_context)
            elif judgment_type == JudgmentType.HYBRID:
                return self._hybrid_judgment(
                    situation, emotional_context, ethical_context
                )
            elif judgment_type == JudgmentType.RATIONAL:
                return self._rational_judgment(situation)
            else:  # INTUITIVE
                return self._intuitive_judgment(situation)

        except Exception as e:
            logger.error(f"판단 수행 실패: {e}")
            return "판단 보류", "오류로 인해 판단을 보류합니다"

    def _emotional_judgment(
        self, situation: str, emotional_context: EmotionalContext
    ) -> Tuple[str, str]:
        """감정적 판단을 수행합니다."""
        try:
            if emotional_context.emotional_state == EmotionalState.JOY:
                return "긍정적으로 진행", "기쁜 상황이므로 적극적으로 진행합니다"
            elif emotional_context.emotional_state == EmotionalState.SADNESS:
                return "신중하게 접근", "슬픈 상황이므로 신중하게 접근합니다"
            elif emotional_context.emotional_state == EmotionalState.CONFUSION:
                return "분석 후 결정", "혼란스러운 상황이므로 더 분석한 후 결정합니다"
            else:
                return "평온하게 처리", "중립적인 상황이므로 평온하게 처리합니다"

        except Exception as e:
            logger.error(f"감정적 판단 실패: {e}")
            return "감정적 판단 실패", "감정적 판단 중 오류가 발생했습니다"

    def _ethical_judgment(
        self, situation: str, ethical_context: EthicalContext
    ) -> Tuple[str, str]:
        """윤리적 판단을 수행합니다."""
        try:
            if ethical_context.ethical_dilemma:
                return (
                    "윤리적 검토 필요",
                    "윤리적 딜레마가 있으므로 추가 검토가 필요합니다",
                )

            # 가장 중요한 윤리 원칙에 따른 판단
            if EthicalPrinciple.BENEFICENCE in ethical_context.involved_principles:
                return "이익 극대화", "최대한 많은 이익을 제공하는 방향으로 진행합니다"
            elif (
                EthicalPrinciple.NON_MALEFICENCE in ethical_context.involved_principles
            ):
                return "해악 최소화", "가능한 한 해를 끼치지 않는 방향으로 진행합니다"
            elif EthicalPrinciple.JUSTICE in ethical_context.involved_principles:
                return "공정한 처리", "모든 이해관계자에게 공정하게 처리합니다"
            else:
                return "균형잡힌 접근", "여러 원칙을 고려하여 균형잡힌 접근을 합니다"

        except Exception as e:
            logger.error(f"윤리적 판단 실패: {e}")
            return "윤리적 판단 실패", "윤리적 판단 중 오류가 발생했습니다"

    def _hybrid_judgment(
        self,
        situation: str,
        emotional_context: EmotionalContext,
        ethical_context: EthicalContext,
    ) -> Tuple[str, str]:
        """감정+윤리 혼합 판단을 수행합니다."""
        try:
            # 감정과 윤리의 균형을 맞춘 판단
            emotional_decision, emotional_reasoning = self._emotional_judgment(
                situation, emotional_context
            )
            ethical_decision, ethical_reasoning = self._ethical_judgment(
                situation, ethical_context
            )

            # 두 판단을 종합
            if emotional_context.emotional_state in [
                EmotionalState.JOY,
                EmotionalState.SATISFACTION,
            ]:
                if not ethical_context.ethical_dilemma:
                    return (
                        "적극적 진행",
                        f"긍정적 감정과 윤리적 허용으로 적극적으로 진행합니다",
                    )
                else:
                    return "신중한 진행", f"긍정적 감정이지만 윤리적 검토가 필요합니다"
            elif emotional_context.emotional_state in [
                EmotionalState.SADNESS,
                EmotionalState.CONFUSION,
            ]:
                return "신중한 접근", f"부정적 감정과 윤리적 고려로 신중하게 접근합니다"
            else:
                return (
                    "균형잡힌 결정",
                    f"중립적 감정과 윤리적 고려로 균형잡힌 결정을 합니다",
                )

        except Exception as e:
            logger.error(f"혼합 판단 실패: {e}")
            return "혼합 판단 실패", "감정과 윤리를 고려한 판단 중 오류가 발생했습니다"

    def _rational_judgment(self, situation: str) -> Tuple[str, str]:
        """합리적 판단을 수행합니다."""
        try:
            return (
                "논리적 분석",
                "감정과 윤리를 배제하고 순수하게 논리적으로 분석하여 결정합니다",
            )
        except Exception as e:
            logger.error(f"합리적 판단 실패: {e}")
            return "합리적 판단 실패", "합리적 판단 중 오류가 발생했습니다"

    def _intuitive_judgment(self, situation: str) -> Tuple[str, str]:
        """직관적 판단을 수행합니다."""
        try:
            return "직관적 결정", "경험과 직관을 바탕으로 빠르게 결정합니다"
        except Exception as e:
            logger.error(f"직관적 판단 실패: {e}")
            return "직관적 판단 실패", "직관적 판단 중 오류가 발생했습니다"

    def _calculate_confidence(
        self,
        emotional_context: EmotionalContext,
        ethical_context: EthicalContext,
        judgment_type: JudgmentType,
    ) -> JudgmentConfidence:
        """판단 신뢰도를 계산합니다."""
        try:
            confidence_score = 0.5  # 기본값

            # 감정적 맥락 고려
            if emotional_context:
                if emotional_context.intensity > 0.8:
                    confidence_score += 0.2
                elif emotional_context.intensity < 0.3:
                    confidence_score -= 0.1

            # 윤리적 맥락 고려
            if ethical_context:
                if ethical_context.conflict_level < 0.3:
                    confidence_score += 0.2
                elif ethical_context.conflict_level > 0.7:
                    confidence_score -= 0.2

            # 판단 유형 고려
            if judgment_type == JudgmentType.RATIONAL:
                confidence_score += 0.1
            elif judgment_type == JudgmentType.INTUITIVE:
                confidence_score -= 0.1

            # 신뢰도 등급 결정
            if confidence_score >= 0.8:
                return JudgmentConfidence.VERY_HIGH
            elif confidence_score >= 0.6:
                return JudgmentConfidence.HIGH
            elif confidence_score >= 0.4:
                return JudgmentConfidence.MEDIUM
            elif confidence_score >= 0.2:
                return JudgmentConfidence.LOW
            else:
                return JudgmentConfidence.VERY_LOW

        except Exception as e:
            logger.error(f"신뢰도 계산 실패: {e}")
            return JudgmentConfidence.MEDIUM

    def _calculate_ethical_score(self, ethical_context: EthicalContext) -> float:
        """윤리적 점수를 계산합니다."""
        try:
            if not ethical_context:
                return 0.0

            score = 0.5  # 기본값

            # 갈등 수준에 따른 조정
            if ethical_context.conflict_level < 0.3:
                score += 0.3
            elif ethical_context.conflict_level > 0.7:
                score -= 0.3

            # 관련된 원칙 수에 따른 조정
            principle_count = len(ethical_context.involved_principles)
            if principle_count >= 3:
                score += 0.2
            elif principle_count == 0:
                score -= 0.2

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"윤리적 점수 계산 실패: {e}")
            return 0.5

    def _calculate_emotional_score(self, emotional_context: EmotionalContext) -> float:
        """감정적 점수를 계산합니다."""
        try:
            if not emotional_context:
                return 0.0

            score = 0.5  # 기본값

            # 감정 상태에 따른 조정
            positive_emotions = [
                EmotionalState.JOY,
                EmotionalState.SATISFACTION,
                EmotionalState.EXCITEMENT,
            ]
            negative_emotions = [
                EmotionalState.SADNESS,
                EmotionalState.ANGER,
                EmotionalState.FEAR,
            ]

            if emotional_context.emotional_state in positive_emotions:
                score += 0.3
            elif emotional_context.emotional_state in negative_emotions:
                score -= 0.2

            # 강도에 따른 조정
            if emotional_context.intensity > 0.8:
                score += 0.1
            elif emotional_context.intensity < 0.3:
                score -= 0.1

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"감정적 점수 계산 실패: {e}")
            return 0.5

    def _generate_alternatives(
        self, situation: str, judgment_type: JudgmentType
    ) -> List[str]:
        """대안을 생성합니다."""
        try:
            alternatives = []

            if judgment_type == JudgmentType.EMOTIONAL:
                alternatives = ["즉시 실행", "신중하게 접근", "분석 후 결정"]
            elif judgment_type == JudgmentType.ETHICAL:
                alternatives = ["윤리적 검토", "이해관계자 상의", "단계적 접근"]
            elif judgment_type == JudgmentType.HYBRID:
                alternatives = ["균형잡힌 접근", "감정 고려", "윤리 우선"]
            else:
                alternatives = ["논리적 분석", "직관적 결정", "보수적 접근"]

            return alternatives

        except Exception as e:
            logger.error(f"대안 생성 실패: {e}")
            return ["기본 접근"]

    def _analyze_consequences(self, decision: str, situation: str) -> List[str]:
        """결정의 결과를 분석합니다."""
        try:
            consequences = []

            if "진행" in decision:
                consequences.extend(["작업 완료", "목표 달성", "진행 상황 업데이트"])
            elif "신중" in decision:
                consequences.extend(["추가 검토", "단계적 접근", "모니터링 강화"])
            elif "분석" in decision:
                consequences.extend(["데이터 수집", "패턴 분석", "결론 도출"])

            return consequences

        except Exception as e:
            logger.error(f"결과 분석 실패: {e}")
            return ["일반적인 결과"]

    def get_judgment_statistics(self) -> Dict[str, Any]:
        """판단 통계를 반환합니다."""
        try:
            total_judgments = len(self.judgment_history)
            if total_judgments == 0:
                return {"total_judgments": 0}

            # 판단 유형별 통계
            type_stats = defaultdict(int)
            for judgment in self.judgment_history:
                type_stats[judgment.judgment_type.value] += 1

            # 평균 점수
            avg_ethical_score = (
                sum(j.ethical_score for j in self.judgment_history) / total_judgments
            )
            avg_emotional_score = (
                sum(j.emotional_score for j in self.judgment_history) / total_judgments
            )
            avg_overall_score = (
                sum(j.overall_score for j in self.judgment_history) / total_judgments
            )

            return {
                "total_judgments": total_judgments,
                "judgment_type_distribution": dict(type_stats),
                "average_ethical_score": avg_ethical_score,
                "average_emotional_score": avg_emotional_score,
                "average_overall_score": avg_overall_score,
                "current_emotional_state": self.current_emotional_state.value,
                "emotional_intensity": self.emotional_intensity,
            }

        except Exception as e:
            logger.error(f"판단 통계 계산 실패: {e}")
            return {}


# 싱글톤 인스턴스
_emotional_ethical_judgment = None


def get_emotional_ethical_judgment() -> EmotionalEthicalJudgment:
    """EmotionalEthicalJudgment 싱글톤 인스턴스 반환"""
    global _emotional_ethical_judgment
    if _emotional_ethical_judgment is None:
        _emotional_ethical_judgment = EmotionalEthicalJudgment()
    return _emotional_ethical_judgment
