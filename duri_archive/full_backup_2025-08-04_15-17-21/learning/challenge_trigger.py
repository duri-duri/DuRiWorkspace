"""
DuRi의 도전 트리거 시스템

4단계 학습: 도전 시점 판단
DuRi가 도전을 시작할 타이밍을 판단하는 클래스입니다.
"""

import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    """도전 유형"""

    EXPLORATION = "exploration"  # 탐색적 도전
    INNOVATION = "innovation"  # 혁신적 도전
    OPTIMIZATION = "optimization"  # 최적화 도전
    RISK_TAKING = "risk_taking"  # 위험 감수 도전


@dataclass
class ChallengeCondition:
    """도전 조건"""

    condition_type: str
    threshold: float
    current_value: float
    met: bool
    weight: float


@dataclass
class ChallengeDecision:
    """도전 결정"""

    should_challenge: bool
    challenge_type: Optional[ChallengeType]
    confidence: float
    reasoning: List[str]
    conditions_met: List[ChallengeCondition]
    recommended_strategy: Optional[Dict[str, Any]]
    risk_level: float


class ChallengeTrigger:
    """
    DuRi의 도전 트리거 시스템

    4단계 학습: 도전 시점 판단
    DuRi가 도전을 시작할 타이밍을 판단하는 클래스입니다.
    """

    def __init__(self):
        """ChallengeTrigger 초기화"""
        self.challenge_history: List[ChallengeDecision] = []
        self.strategy_performance: Dict[str, List[float]] = {}
        self.challenge_patterns: Dict[str, float] = {}
        self.last_challenge_time: Optional[datetime] = None
        self.min_challenge_interval = timedelta(hours=1)  # 최소 도전 간격

        logger.info("ChallengeTrigger 초기화 완료")

    def should_explore(
        self,
        strategy_history: Dict[str, Any],
        current_context: Optional[Dict[str, Any]] = None,
    ) -> ChallengeDecision:
        """
        도전 여부를 판단합니다.

        Args:
            strategy_history: 전략 성과 히스토리
            current_context: 현재 상황 정보

        Returns:
            ChallengeDecision: 도전 결정
        """
        try:
            # 도전 조건들 평가
            conditions = self._evaluate_challenge_conditions(
                strategy_history, current_context
            )

            # 도전 점수 계산
            challenge_score = self._calculate_challenge_score(conditions)

            # 도전 여부 결정
            should_challenge = challenge_score > 0.7

            # 도전 유형 결정
            challenge_type = (
                self._determine_challenge_type(conditions, current_context)
                if should_challenge
                else None
            )

            # 신뢰도 계산
            confidence = self._calculate_confidence(conditions, challenge_score)

            # 추론 과정
            reasoning = self._generate_reasoning(
                conditions, challenge_score, should_challenge
            )

            # 추천 전략
            recommended_strategy = (
                self._generate_recommended_strategy(challenge_type, current_context)
                if should_challenge
                else None
            )

            # 위험도 계산
            risk_level = self._calculate_risk_level(challenge_type, current_context)

            decision = ChallengeDecision(
                should_challenge=should_challenge,
                challenge_type=challenge_type,
                confidence=confidence,
                reasoning=reasoning,
                conditions_met=[c for c in conditions if c.met],
                recommended_strategy=recommended_strategy,
                risk_level=risk_level,
            )

            self.challenge_history.append(decision)

            if should_challenge:
                self.last_challenge_time = datetime.now()
                logger.info(
                    f"도전 결정: {challenge_type.value if challenge_type else 'None'}, 신뢰도: {confidence:.2f}, 위험도: {risk_level:.2f}"
                )
            else:
                logger.info(
                    f"도전 보류: 점수 {challenge_score:.2f}, 신뢰도: {confidence:.2f}"
                )

            return decision

        except Exception as e:
            logger.error(f"도전 판단 실패: {e}")
            return ChallengeDecision(
                should_challenge=False,
                challenge_type=None,
                confidence=0.0,
                reasoning=[f"도전 판단 실패: {str(e)}"],
                conditions_met=[],
                recommended_strategy=None,
                risk_level=1.0,
            )

    def _evaluate_challenge_conditions(
        self,
        strategy_history: Dict[str, Any],
        current_context: Optional[Dict[str, Any]],
    ) -> List[ChallengeCondition]:
        """도전 조건들을 평가합니다."""
        conditions = []

        # 1. 성공 스트릭 조건
        success_streak = strategy_history.get("success_streak", 0)
        success_threshold = 20
        conditions.append(
            ChallengeCondition(
                condition_type="success_streak",
                threshold=success_threshold,
                current_value=success_streak,
                met=success_streak >= success_threshold,
                weight=0.3,
            )
        )

        # 2. 성능 안정성 조건
        performance_stability = strategy_history.get("performance_stability", 0.0)
        stability_threshold = 0.8
        conditions.append(
            ChallengeCondition(
                condition_type="performance_stability",
                threshold=stability_threshold,
                current_value=performance_stability,
                met=performance_stability >= stability_threshold,
                weight=0.25,
            )
        )

        # 3. 새로운 피드백 부족 조건
        new_feedback_detected = strategy_history.get("new_feedback_detected", True)
        conditions.append(
            ChallengeCondition(
                condition_type="no_new_feedback",
                threshold=0.0,
                current_value=0.0 if new_feedback_detected else 1.0,
                met=not new_feedback_detected,
                weight=0.2,
            )
        )

        # 4. 시간 간격 조건
        time_since_last_challenge = self._get_time_since_last_challenge()
        min_interval_hours = 1.0
        conditions.append(
            ChallengeCondition(
                condition_type="time_interval",
                threshold=min_interval_hours,
                current_value=time_since_last_challenge,
                met=time_since_last_challenge >= min_interval_hours,
                weight=0.15,
            )
        )

        # 5. 컨텍스트 기반 조건
        if current_context:
            context_complexity = current_context.get("complexity", "medium")
            if context_complexity == "low":
                # 낮은 복잡도에서는 더 쉽게 도전
                conditions.append(
                    ChallengeCondition(
                        condition_type="low_complexity",
                        threshold=0.0,
                        current_value=1.0,
                        met=True,
                        weight=0.1,
                    )
                )

        return conditions

    def _calculate_challenge_score(self, conditions: List[ChallengeCondition]) -> float:
        """도전 점수를 계산합니다."""
        if not conditions:
            return 0.0

        total_weight = sum(c.weight for c in conditions)
        if total_weight == 0:
            return 0.0

        weighted_score = sum(c.weight for c in conditions if c.met)
        return weighted_score / total_weight

    def _determine_challenge_type(
        self,
        conditions: List[ChallengeCondition],
        current_context: Optional[Dict[str, Any]],
    ) -> ChallengeType:
        """도전 유형을 결정합니다."""
        # 조건에 따른 도전 유형 결정
        met_conditions = [c for c in conditions if c.met]

        if any(c.condition_type == "success_streak" for c in met_conditions):
            if any(c.condition_type == "performance_stability" for c in met_conditions):
                return ChallengeType.INNOVATION  # 안정적 성공 → 혁신
            else:
                return ChallengeType.RISK_TAKING  # 성공하지만 불안정 → 위험 감수
        elif any(c.condition_type == "no_new_feedback" for c in met_conditions):
            return ChallengeType.EXPLORATION  # 새로운 피드백 없음 → 탐색
        else:
            return ChallengeType.OPTIMIZATION  # 기타 → 최적화

    def _calculate_confidence(
        self, conditions: List[ChallengeCondition], challenge_score: float
    ) -> float:
        """신뢰도를 계산합니다."""
        # 조건 충족률 기반 신뢰도
        met_conditions = len([c for c in conditions if c.met])
        total_conditions = len(conditions)

        condition_confidence = (
            met_conditions / total_conditions if total_conditions > 0 else 0
        )

        # 점수 기반 신뢰도
        score_confidence = challenge_score

        # 평균 신뢰도
        return (condition_confidence + score_confidence) / 2

    def _generate_reasoning(
        self,
        conditions: List[ChallengeCondition],
        challenge_score: float,
        should_challenge: bool,
    ) -> List[str]:
        """추론 과정을 생성합니다."""
        reasoning = []

        if should_challenge:
            reasoning.append(f"도전 점수 {challenge_score:.2f}로 도전을 권장합니다.")

            met_conditions = [c for c in conditions if c.met]
            reasoning.append(f"충족된 조건: {len(met_conditions)}개")

            for condition in met_conditions:
                reasoning.append(
                    f"- {condition.condition_type}: {condition.current_value:.1f} >= {condition.threshold:.1f}"
                )
        else:
            reasoning.append(f"도전 점수 {challenge_score:.2f}로 도전을 보류합니다.")

            unmet_conditions = [c for c in conditions if not c.met]
            reasoning.append(f"미충족 조건: {len(unmet_conditions)}개")

            for condition in unmet_conditions:
                reasoning.append(
                    f"- {condition.condition_type}: {condition.current_value:.1f} < {condition.threshold:.1f}"
                )

        return reasoning

    def _generate_recommended_strategy(
        self, challenge_type: ChallengeType, current_context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """추천 전략을 생성합니다."""
        if not challenge_type:
            return None

        base_strategy = {
            "id": f"challenge_{challenge_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": challenge_type.value,
            "priority": "high",
            "execution_method": "challenge",
            "parameters": {},
        }

        if challenge_type == ChallengeType.EXPLORATION:
            base_strategy["parameters"] = {
                "exploration_rate": 0.3,
                "random_factor": 0.2,
                "max_iterations": 50,
            }
        elif challenge_type == ChallengeType.INNOVATION:
            base_strategy["parameters"] = {
                "innovation_rate": 0.4,
                "creativity_factor": 0.3,
                "risk_tolerance": 0.6,
            }
        elif challenge_type == ChallengeType.OPTIMIZATION:
            base_strategy["parameters"] = {
                "optimization_rate": 0.25,
                "precision_factor": 0.4,
                "convergence_threshold": 0.01,
            }
        elif challenge_type == ChallengeType.RISK_TAKING:
            base_strategy["parameters"] = {
                "risk_factor": 0.5,
                "aggressive_rate": 0.4,
                "fallback_strategy": "safe_mode",
            }

        return base_strategy

    def _calculate_risk_level(
        self, challenge_type: ChallengeType, current_context: Optional[Dict[str, Any]]
    ) -> float:
        """위험도를 계산합니다."""
        base_risk = {
            ChallengeType.EXPLORATION: 0.3,
            ChallengeType.INNOVATION: 0.5,
            ChallengeType.OPTIMIZATION: 0.2,
            ChallengeType.RISK_TAKING: 0.8,
        }

        risk = base_risk.get(challenge_type, 0.5)

        # 컨텍스트에 따른 위험도 조정
        if current_context:
            complexity = current_context.get("complexity", "medium")
            if complexity == "high":
                risk *= 1.3
            elif complexity == "low":
                risk *= 0.8

        return min(risk, 1.0)

    def _get_time_since_last_challenge(self) -> float:
        """마지막 도전으로부터 경과 시간을 반환합니다 (시간 단위)."""
        if not self.last_challenge_time:
            return float("inf")  # 첫 도전

        elapsed = datetime.now() - self.last_challenge_time
        return elapsed.total_seconds() / 3600  # 시간 단위로 변환

    def get_challenge_statistics(self) -> Dict[str, Any]:
        """도전 통계를 반환합니다."""
        total_decisions = len(self.challenge_history)
        challenge_decisions = len(
            [d for d in self.challenge_history if d.should_challenge]
        )

        type_counts = {}
        for decision in self.challenge_history:
            if decision.challenge_type:
                type_name = decision.challenge_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

        avg_confidence = (
            sum(d.confidence for d in self.challenge_history) / total_decisions
            if total_decisions > 0
            else 0
        )
        avg_risk = (
            sum(d.risk_level for d in self.challenge_history) / total_decisions
            if total_decisions > 0
            else 0
        )

        return {
            "total_decisions": total_decisions,
            "challenge_decisions": challenge_decisions,
            "challenge_rate": (
                challenge_decisions / total_decisions if total_decisions > 0 else 0
            ),
            "type_distribution": type_counts,
            "average_confidence": avg_confidence,
            "average_risk_level": avg_risk,
        }

    def update_strategy_performance(self, strategy_id: str, performance: float):
        """전략 성능을 업데이트합니다."""
        if strategy_id not in self.strategy_performance:
            self.strategy_performance[strategy_id] = []

        self.strategy_performance[strategy_id].append(performance)


# 싱글톤 인스턴스
_challenge_trigger = None


def get_challenge_trigger() -> ChallengeTrigger:
    """ChallengeTrigger 싱글톤 인스턴스 반환"""
    global _challenge_trigger
    if _challenge_trigger is None:
        _challenge_trigger = ChallengeTrigger()
    return _challenge_trigger
