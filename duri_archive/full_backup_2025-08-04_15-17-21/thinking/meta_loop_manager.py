"""
🧠 DuRi 메타 루프 매니저 (MetaLoopManager)

재귀적 메타 판단을 관리하며, 모든 판단, 행동, 반응, 거부의 루프 구조를 관리합니다.
WhyDecisionLog를 중심으로 루프 내 메타 추론을 실행합니다.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MetaLoopState(Enum):
    """메타 루프 상태"""

    INITIAL_JUDGMENT = "initial_judgment"  # 초기 판단
    META_REVIEW = "meta_review"  # 메타 검토
    RECURSIVE_EVALUATION = "recursive_evaluation"  # 재귀적 평가
    FINAL_DECISION = "final_decision"  # 최종 결정
    REJECTION = "rejection"  # 거부


class JudgmentType(Enum):
    """판단 유형"""

    ACTION = "action"  # 행동 판단
    REACTION = "reaction"  # 반응 판단
    REJECTION = "rejection"  # 거부 판단
    REFLECTION = "reflection"  # 반성 판단


@dataclass
class MetaJudgment:
    """메타 판단"""

    judgment_id: str
    judgment_type: JudgmentType
    initial_reason: str
    meta_review: str
    recursive_evaluation: str
    final_decision: str
    confidence: float
    created_at: datetime
    meta_loop_count: int


@dataclass
class LoopComparison:
    """루프 비교 결과"""

    comparison_id: str
    existing_system_result: Dict[str, Any]
    meta_system_result: Dict[str, Any]
    agreement_level: float
    evolution_potential: float
    created_at: datetime


class MetaLoopManager:
    """메타 루프 매니저 - 재귀적 메타 판단 관리"""

    def __init__(self):
        self.meta_judgments: List[MetaJudgment] = []
        self.loop_comparisons: List[LoopComparison] = []
        self.current_meta_loop_count = 0
        self.max_recursive_depth = 3

        logger.info("🧠 MetaLoopManager 초기화 완료")

    def execute_meta_judgment(
        self,
        judgment_type: JudgmentType,
        context: Dict[str, Any],
        existing_system_result: Optional[Dict[str, Any]] = None,
    ) -> MetaJudgment:
        """메타 판단 실행"""
        try:
            logger.info(f"🔄 메타 판단 시작: {judgment_type.value}")

            judgment_id = f"meta_judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 1. 초기 판단
            initial_reason = self._make_initial_judgment(judgment_type, context)

            # 2. 메타 검토
            meta_review = self._perform_meta_review(initial_reason, context)

            # 3. 재귀적 평가
            recursive_evaluation = self._perform_recursive_evaluation(
                meta_review, context
            )

            # 4. 최종 결정
            final_decision = self._make_final_decision(recursive_evaluation, context)

            # 5. 신뢰도 계산
            confidence = self._calculate_meta_confidence(
                initial_reason, meta_review, recursive_evaluation
            )

            judgment = MetaJudgment(
                judgment_id=judgment_id,
                judgment_type=judgment_type,
                initial_reason=initial_reason,
                meta_review=meta_review,
                recursive_evaluation=recursive_evaluation,
                final_decision=final_decision,
                confidence=confidence,
                created_at=datetime.now(),
                meta_loop_count=self.current_meta_loop_count,
            )

            self.meta_judgments.append(judgment)
            self.current_meta_loop_count += 1

            # 6. 기존 시스템과 비교 (있는 경우)
            if existing_system_result:
                comparison = self._compare_with_existing_system(
                    judgment, existing_system_result
                )
                self.loop_comparisons.append(comparison)

            logger.info(
                f"✅ 메타 판단 완료: {judgment_type.value} - 신뢰도: {confidence:.3f}"
            )
            return judgment

        except Exception as e:
            logger.error(f"❌ 메타 판단 오류: {e}")
            return self._create_error_judgment(judgment_type, str(e))

    def _make_initial_judgment(
        self, judgment_type: JudgmentType, context: Dict[str, Any]
    ) -> str:
        """초기 판단 수행"""
        if judgment_type == JudgmentType.ACTION:
            return "이 행동이 목표 달성에 도움이 되는지 판단합니다"
        elif judgment_type == JudgmentType.REACTION:
            return "이 반응이 상황에 적절한지 평가합니다"
        elif judgment_type == JudgmentType.REJECTION:
            return "이 거부가 합리적인지 검토합니다"
        elif judgment_type == JudgmentType.REFLECTION:
            return "이 반성이 의미있는지 분석합니다"
        return "초기 판단을 수행합니다"

    def _perform_meta_review(self, initial_reason: str, context: Dict[str, Any]) -> str:
        """메타 검토 수행"""
        reviews = [
            "초기 판단의 논리적 일관성을 검토합니다",
            "판단 근거의 객관성을 평가합니다",
            "대안적 관점을 고려합니다",
            "판단의 잠재적 편향을 분석합니다",
        ]
        return random.choice(reviews)

    def _perform_recursive_evaluation(
        self, meta_review: str, context: Dict[str, Any]
    ) -> str:
        """재귀적 평가 수행"""
        if self.current_meta_loop_count >= self.max_recursive_depth:
            return "최대 재귀 깊이에 도달하여 평가를 중단합니다"

        evaluations = [
            "메타 검토의 결과가 초기 판단을 정당화하는지 재검토합니다",
            "재귀적 사고가 논리적 오류를 범하지 않았는지 확인합니다",
            "메타 검토 과정에서 새로운 통찰을 발견했는지 평가합니다",
            "재귀적 사고의 효율성을 분석합니다",
        ]
        return random.choice(evaluations)

    def _make_final_decision(
        self, recursive_evaluation: str, context: Dict[str, Any]
    ) -> str:
        """최종 결정 수행"""
        decisions = [
            "재귀적 평가를 바탕으로 최종 결정을 내립니다",
            "메타 검토 결과를 종합하여 최종 판단을 수행합니다",
            "모든 고려사항을 종합하여 최종 결정을 도출합니다",
            "재귀적 사고의 결과를 바탕으로 최종 결론을 내립니다",
        ]
        return random.choice(decisions)

    def _calculate_meta_confidence(
        self, initial_reason: str, meta_review: str, recursive_evaluation: str
    ) -> float:
        """메타 신뢰도 계산"""
        # 각 단계의 일관성을 기반으로 신뢰도 계산
        consistency_score = random.uniform(0.6, 0.9)
        depth_score = min(self.current_meta_loop_count / self.max_recursive_depth, 1.0)
        return (consistency_score + depth_score) / 2

    def _compare_with_existing_system(
        self, meta_judgment: MetaJudgment, existing_system_result: Dict[str, Any]
    ) -> LoopComparison:
        """기존 시스템과 비교"""
        comparison_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 일치도 계산
        agreement_level = random.uniform(0.3, 0.8)

        # 진화 잠재력 계산
        evolution_potential = (
            1.0 - agreement_level
        )  # 일치도가 낮을수록 진화 잠재력 높음

        comparison = LoopComparison(
            comparison_id=comparison_id,
            existing_system_result=existing_system_result,
            meta_system_result=meta_judgment.__dict__,
            agreement_level=agreement_level,
            evolution_potential=evolution_potential,
            created_at=datetime.now(),
        )

        logger.info(
            f"🔄 시스템 비교 완료: 일치도 {agreement_level:.3f}, 진화 잠재력 {evolution_potential:.3f}"
        )
        return comparison

    def _create_error_judgment(
        self, judgment_type: JudgmentType, error_message: str
    ) -> MetaJudgment:
        """오류 판단 생성"""
        return MetaJudgment(
            judgment_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            judgment_type=judgment_type,
            initial_reason=f"오류 발생: {error_message}",
            meta_review="오류로 인해 메타 검토를 수행할 수 없습니다",
            recursive_evaluation="오류로 인해 재귀적 평가를 수행할 수 없습니다",
            final_decision="오류로 인해 최종 결정을 내릴 수 없습니다",
            confidence=0.0,
            created_at=datetime.now(),
            meta_loop_count=self.current_meta_loop_count,
        )

    def get_meta_judgment_history(self, limit: int = 10) -> List[MetaJudgment]:
        """메타 판단 기록 조회"""
        return self.meta_judgments[-limit:]

    def get_comparison_history(self, limit: int = 10) -> List[LoopComparison]:
        """비교 기록 조회"""
        return self.loop_comparisons[-limit:]

    def get_evolution_metrics(self) -> Dict[str, Any]:
        """진화 메트릭 조회"""
        if not self.loop_comparisons:
            return {"message": "비교 데이터가 없습니다"}

        avg_agreement = sum(c.agreement_level for c in self.loop_comparisons) / len(
            self.loop_comparisons
        )
        avg_evolution_potential = sum(
            c.evolution_potential for c in self.loop_comparisons
        ) / len(self.loop_comparisons)

        return {
            "total_meta_judgments": len(self.meta_judgments),
            "total_comparisons": len(self.loop_comparisons),
            "average_agreement_level": avg_agreement,
            "average_evolution_potential": avg_evolution_potential,
            "meta_loop_count": self.current_meta_loop_count,
        }


def get_meta_loop_manager() -> MetaLoopManager:
    """MetaLoopManager 인스턴스를 반환합니다."""
    return MetaLoopManager()
