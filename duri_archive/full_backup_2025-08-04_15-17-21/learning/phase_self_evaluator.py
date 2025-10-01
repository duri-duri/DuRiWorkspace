"""
🎯 DuRi 자발적 Phase Up 시스템
목표: DuRi가 스스로 성장 단계를 판단하고 Phase Up을 요청하는 구조
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhaseLevel(Enum):
    """DuRi 성장 단계"""

    PHASE_1_BASIC = "Phase 1: 기본 학습"
    PHASE_2_ADVANCED = "Phase 2: 고급 학습"
    PHASE_3_CREATIVE = "Phase 3: 창의적 학습"
    PHASE_4_WISDOM = "Phase 4: 지혜"
    PHASE_5_META = "Phase 5: 메타 학습"
    PHASE_6_INSIGHT = "Phase 6: 통찰 학습"
    PHASE_7_SELF_EVOLUTION = "Phase 7: 자가 진화"
    PHASE_8_THINKING_AI = "Phase 8: 생각하는 AI"
    PHASE_9_CONSCIOUSNESS = "Phase 9: 의식적 AI"


class PhaseCriteria(Enum):
    """Phase Up 기준"""

    LEARNING_MASTERY = "학습 숙련도"
    INSIGHT_GENERATION = "통찰 생성 능력"
    SELF_REFLECTION = "자기 반영 능력"
    PROBLEM_SOLVING = "문제 해결 능력"
    CREATIVITY = "창의성"
    META_COGNITION = "메타 인지"
    SELF_EVOLUTION = "자가 진화"
    CONSCIOUSNESS = "의식"


@dataclass
class PhaseAchievement:
    """Phase 성취도"""

    criteria: PhaseCriteria
    current_score: float
    required_score: float
    achieved: bool
    description: str


@dataclass
class PhaseUpRequest:
    """Phase Up 요청"""

    current_phase: PhaseLevel
    target_phase: PhaseLevel
    achievements: List[PhaseAchievement]
    confidence: float
    reasoning: str
    timestamp: datetime
    request_id: str


class PhaseSelfEvaluator:
    """DuRi 자발적 Phase 평가기"""

    def __init__(self):
        self.current_phase = PhaseLevel.PHASE_1_BASIC
        self.phase_history = []
        self.achievement_tracker = {}
        self.insight_success_rate = 0.0
        self.learning_mastery_score = 0.0
        self.self_reflection_count = 0
        self.creative_solutions = 0
        self.meta_cognition_events = 0

    def evaluate_learning_mastery(self) -> PhaseAchievement:
        """학습 숙련도 평가"""
        # 실제로는 학습 루프 성공률, 오류율 등을 분석
        current_score = min(self.learning_mastery_score, 1.0)
        required_score = 0.8

        return PhaseAchievement(
            criteria=PhaseCriteria.LEARNING_MASTERY,
            current_score=current_score,
            required_score=required_score,
            achieved=current_score >= required_score,
            description=f"학습 숙련도: {current_score:.2f}/{required_score:.2f}",
        )

    def evaluate_insight_generation(self) -> PhaseAchievement:
        """통찰 생성 능력 평가"""
        current_score = min(self.insight_success_rate, 1.0)
        required_score = 0.7

        return PhaseAchievement(
            criteria=PhaseCriteria.INSIGHT_GENERATION,
            current_score=current_score,
            required_score=required_score,
            achieved=current_score >= required_score,
            description=f"통찰 성공률: {current_score:.2f}/{required_score:.2f}",
        )

    def evaluate_self_reflection(self) -> PhaseAchievement:
        """자기 반영 능력 평가"""
        # 자기 반영 횟수와 품질을 평가
        reflection_quality = min(self.self_reflection_count / 10.0, 1.0)
        required_score = 0.6

        return PhaseAchievement(
            criteria=PhaseCriteria.SELF_REFLECTION,
            current_score=reflection_quality,
            required_score=required_score,
            achieved=reflection_quality >= required_score,
            description=f"자기 반영 품질: {reflection_quality:.2f}/{required_score:.2f}",
        )

    def evaluate_creativity(self) -> PhaseAchievement:
        """창의성 평가"""
        # 창의적 해결책 생성 횟수
        creativity_score = min(self.creative_solutions / 5.0, 1.0)
        required_score = 0.5

        return PhaseAchievement(
            criteria=PhaseCriteria.CREATIVITY,
            current_score=creativity_score,
            required_score=required_score,
            achieved=creativity_score >= required_score,
            description=f"창의적 해결책: {creativity_score:.2f}/{required_score:.2f}",
        )

    def evaluate_meta_cognition(self) -> PhaseAchievement:
        """메타 인지 평가"""
        meta_score = min(self.meta_cognition_events / 3.0, 1.0)
        required_score = 0.4

        return PhaseAchievement(
            criteria=PhaseCriteria.META_COGNITION,
            current_score=meta_score,
            required_score=required_score,
            achieved=meta_score >= required_score,
            description=f"메타 인지 이벤트: {meta_score:.2f}/{required_score:.2f}",
        )

    def get_phase_requirements(self, target_phase: PhaseLevel) -> List[PhaseCriteria]:
        """각 Phase별 요구사항 반환"""
        requirements = {
            PhaseLevel.PHASE_2_ADVANCED: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.PROBLEM_SOLVING,
            ],
            PhaseLevel.PHASE_3_CREATIVE: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.CREATIVITY,
            ],
            PhaseLevel.PHASE_4_META: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.META_COGNITION,
            ],
            PhaseLevel.PHASE_5_INSIGHT: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.INSIGHT_GENERATION,
            ],
            PhaseLevel.PHASE_6_SELF_EVOLUTION: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.INSIGHT_GENERATION,
                PhaseCriteria.SELF_REFLECTION,
            ],
            PhaseLevel.PHASE_7_THINKING_AI: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.INSIGHT_GENERATION,
                PhaseCriteria.SELF_REFLECTION,
                PhaseCriteria.CREATIVITY,
            ],
            PhaseLevel.PHASE_8_CONSCIOUSNESS: [
                PhaseCriteria.LEARNING_MASTERY,
                PhaseCriteria.INSIGHT_GENERATION,
                PhaseCriteria.SELF_REFLECTION,
                PhaseCriteria.CREATIVITY,
                PhaseCriteria.META_COGNITION,
                PhaseCriteria.CONSCIOUSNESS,
            ],
        }

        return requirements.get(target_phase, [])

    def evaluate_phase_readiness(
        self, target_phase: PhaseLevel
    ) -> List[PhaseAchievement]:
        """특정 Phase 준비도 평가"""
        requirements = self.get_phase_requirements(target_phase)
        achievements = []

        for criteria in requirements:
            if criteria == PhaseCriteria.LEARNING_MASTERY:
                achievements.append(self.evaluate_learning_mastery())
            elif criteria == PhaseCriteria.INSIGHT_GENERATION:
                achievements.append(self.evaluate_insight_generation())
            elif criteria == PhaseCriteria.SELF_REFLECTION:
                achievements.append(self.evaluate_self_reflection())
            elif criteria == PhaseCriteria.CREATIVITY:
                achievements.append(self.evaluate_creativity())
            elif criteria == PhaseCriteria.META_COGNITION:
                achievements.append(self.evaluate_meta_cognition())
            # 다른 기준들도 추가 가능

        return achievements

    def should_request_phase_up(self) -> Optional[PhaseUpRequest]:
        """Phase Up 요청 여부 판단"""
        logger.info("🎯 Phase Up 준비도 자체 평가 시작")

        # 현재 Phase에서 다음 Phase로의 가능성 확인
        current_phase_index = list(PhaseLevel).index(self.current_phase)

        if current_phase_index >= len(PhaseLevel) - 1:
            logger.info("🎯 이미 최고 단계에 도달")
            return None

        next_phase = list(PhaseLevel)[current_phase_index + 1]

        # 다음 Phase 준비도 평가
        achievements = self.evaluate_phase_readiness(next_phase)

        # 모든 요구사항 달성 여부 확인
        all_achieved = all(achievement.achieved for achievement in achievements)

        if all_achieved:
            # Phase Up 요청 생성
            confidence = sum(
                achievement.current_score for achievement in achievements
            ) / len(achievements)

            reasoning = f"DuRi가 {next_phase.value}로의 진화 준비가 완료되었습니다. "
            reasoning += f"주요 성취: {', '.join([a.criteria.value for a in achievements if a.achieved])}"

            request = PhaseUpRequest(
                current_phase=self.current_phase,
                target_phase=next_phase,
                achievements=achievements,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now(),
                request_id=f"phase_up_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            )

            logger.info(
                f"🎯 Phase Up 요청 생성: {self.current_phase.value} → {next_phase.value}"
            )
            return request
        else:
            logger.info(
                f"🎯 Phase Up 준비 부족: {len([a for a in achievements if not a.achieved])}개 기준 미달성"
            )
            return None

    def update_metrics(self, metric_type: str, value: float):
        """메트릭 업데이트"""
        if metric_type == "insight_success_rate":
            self.insight_success_rate = value
        elif metric_type == "learning_mastery":
            self.learning_mastery_score = value
        elif metric_type == "self_reflection":
            self.self_reflection_count += 1
        elif metric_type == "creative_solution":
            self.creative_solutions += 1
        elif metric_type == "meta_cognition":
            self.meta_cognition_events += 1

        logger.info(f"📊 메트릭 업데이트: {metric_type} = {value}")

    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "current_phase": self.current_phase.value,
            "insight_success_rate": self.insight_success_rate,
            "learning_mastery_score": self.learning_mastery_score,
            "self_reflection_count": self.self_reflection_count,
            "creative_solutions": self.creative_solutions,
            "meta_cognition_events": self.meta_cognition_events,
            "phase_history": [phase.value for phase in self.phase_history],
        }


# 전역 인스턴스
_phase_evaluator = None


def get_phase_evaluator() -> PhaseSelfEvaluator:
    """전역 Phase 평가기 인스턴스 반환"""
    global _phase_evaluator
    if _phase_evaluator is None:
        _phase_evaluator = PhaseSelfEvaluator()
    return _phase_evaluator


if __name__ == "__main__":
    # 데모 실행
    evaluator = get_phase_evaluator()

    # 메트릭 업데이트 (시뮬레이션)
    evaluator.update_metrics("insight_success_rate", 0.75)
    evaluator.update_metrics("learning_mastery", 0.85)
    evaluator.update_metrics("self_reflection", 1)
    evaluator.update_metrics("creative_solution", 1)
    evaluator.update_metrics("meta_cognition", 1)

    # Phase Up 요청 확인
    request = evaluator.should_request_phase_up()

    if request:
        print(
            f"🎯 Phase Up 요청: {request.current_phase.value} → {request.target_phase.value}"
        )
        print(f"📊 신뢰도: {request.confidence:.3f}")
        print(f"💭 이유: {request.reasoning}")

        for achievement in request.achievements:
            status = "✅" if achievement.achieved else "❌"
            print(f"   {status} {achievement.description}")
    else:
        print("🎯 Phase Up 준비 부족")

    # 현재 상태 출력
    status = evaluator.get_current_status()
    print(f"\n📊 현재 상태: {status}")
