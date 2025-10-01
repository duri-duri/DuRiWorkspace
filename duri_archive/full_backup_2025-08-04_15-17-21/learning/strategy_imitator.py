"""
DuRi의 전략 모방 시스템

1단계 학습: 모르면 모방
기존 전략을 복사하여 모방 실행하는 클래스입니다.
"""

import copy
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ImitationType(Enum):
    """모방 유형"""

    EXACT_COPY = "exact_copy"  # 정확한 복사
    ADAPTIVE_COPY = "adaptive_copy"  # 상황에 맞게 조정
    PARTIAL_COPY = "partial_copy"  # 일부만 복사
    CREATIVE_COPY = "creative_copy"  # 창의적 변형


@dataclass
class ImitationResult:
    """모방 결과"""

    original_strategy: Dict[str, Any]
    imitated_strategy: Dict[str, Any]
    imitation_type: ImitationType
    confidence: float
    adaptation_notes: List[str]
    timestamp: datetime
    success: bool


class StrategyImitator:
    """
    DuRi의 전략 모방 시스템

    1단계 학습: 모르면 모방
    기존 전략을 복사하여 모방 실행하는 클래스입니다.
    """

    def __init__(self):
        """StrategyImitator 초기화"""
        self.imitation_history: List[ImitationResult] = []
        self.successful_patterns: Dict[str, float] = {}
        self.adaptation_rules: Dict[str, Any] = {}

        logger.info("StrategyImitator 초기화 완료")

    def imitate(
        self,
        reference_strategy: Dict[str, Any],
        imitation_type: ImitationType = ImitationType.EXACT_COPY,
        context: Optional[Dict[str, Any]] = None,
    ) -> ImitationResult:
        """
        전략을 모방합니다.

        Args:
            reference_strategy: 참조할 전략
            imitation_type: 모방 유형
            context: 현재 상황 정보

        Returns:
            ImitationResult: 모방 결과
        """
        try:
            if imitation_type == ImitationType.EXACT_COPY:
                imitated_strategy = self._exact_copy(reference_strategy)
            elif imitation_type == ImitationType.ADAPTIVE_COPY:
                imitated_strategy = self._adaptive_copy(reference_strategy, context)
            elif imitation_type == ImitationType.PARTIAL_COPY:
                imitated_strategy = self._partial_copy(reference_strategy)
            elif imitation_type == ImitationType.CREATIVE_COPY:
                imitated_strategy = self._creative_copy(reference_strategy, context)
            else:
                raise ValueError(f"알 수 없는 모방 유형: {imitation_type}")

            # 모방 결과 생성
            result = ImitationResult(
                original_strategy=reference_strategy,
                imitated_strategy=imitated_strategy,
                imitation_type=imitation_type,
                confidence=self._calculate_confidence(imitation_type, context),
                adaptation_notes=self._generate_adaptation_notes(
                    imitation_type, context
                ),
                timestamp=datetime.now(),
                success=True,
            )

            self.imitation_history.append(result)
            self._update_successful_patterns(result)

            logger.info(
                f"전략 모방 완료: {imitation_type.value}, 신뢰도: {result.confidence:.2f}"
            )
            return result

        except Exception as e:
            logger.error(f"전략 모방 실패: {e}")
            return ImitationResult(
                original_strategy=reference_strategy,
                imitated_strategy={},
                imitation_type=imitation_type,
                confidence=0.0,
                adaptation_notes=[f"모방 실패: {str(e)}"],
                timestamp=datetime.now(),
                success=False,
            )

    def _exact_copy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """정확한 복사"""
        return copy.deepcopy(strategy)

    def _adaptive_copy(
        self, strategy: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """상황에 맞게 조정된 복사"""
        copied_strategy = copy.deepcopy(strategy)

        if context:
            # 상황에 맞게 전략 조정
            for key, value in context.items():
                if key in copied_strategy:
                    copied_strategy[key] = value

        return copied_strategy

    def _partial_copy(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """일부만 복사"""
        copied_strategy = {}

        # 핵심 요소들만 복사
        core_keys = ["name", "type", "priority", "execution_method"]
        for key in core_keys:
            if key in strategy:
                copied_strategy[key] = strategy[key]

        return copied_strategy

    def _creative_copy(
        self, strategy: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """창의적 변형"""
        copied_strategy = copy.deepcopy(strategy)

        # 창의적 변형 적용
        if "parameters" in copied_strategy:
            # 파라미터에 약간의 변형 추가
            for param, value in copied_strategy["parameters"].items():
                if isinstance(value, (int, float)):
                    # 10% 범위 내에서 변형
                    variation = value * 0.1
                    copied_strategy["parameters"][param] = value + variation

        return copied_strategy

    def _calculate_confidence(
        self, imitation_type: ImitationType, context: Optional[Dict[str, Any]]
    ) -> float:
        """모방 신뢰도 계산"""
        base_confidence = {
            ImitationType.EXACT_COPY: 0.95,
            ImitationType.ADAPTIVE_COPY: 0.85,
            ImitationType.PARTIAL_COPY: 0.75,
            ImitationType.CREATIVE_COPY: 0.65,
        }

        confidence = base_confidence.get(imitation_type, 0.5)

        # 컨텍스트에 따른 조정
        if context and "complexity" in context:
            if context["complexity"] == "high":
                confidence *= 0.9
            elif context["complexity"] == "low":
                confidence *= 1.1

        return min(confidence, 1.0)

    def _generate_adaptation_notes(
        self, imitation_type: ImitationType, context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """적응 노트 생성"""
        notes = []

        if imitation_type == ImitationType.EXACT_COPY:
            notes.append("정확한 복사 수행")
        elif imitation_type == ImitationType.ADAPTIVE_COPY:
            notes.append("상황에 맞게 조정된 복사")
            if context:
                notes.append(f"컨텍스트 적용: {list(context.keys())}")
        elif imitation_type == ImitationType.PARTIAL_COPY:
            notes.append("핵심 요소만 복사")
        elif imitation_type == ImitationType.CREATIVE_COPY:
            notes.append("창의적 변형 적용")
            notes.append("파라미터 변형 추가")

        return notes

    def _update_successful_patterns(self, result: ImitationResult):
        """성공적인 패턴 업데이트"""
        if result.success:
            pattern_key = (
                f"{result.imitation_type.value}_{len(result.original_strategy)}"
            )
            current_success = self.successful_patterns.get(pattern_key, 0)
            self.successful_patterns[pattern_key] = current_success + 1

    def get_imitation_statistics(self) -> Dict[str, Any]:
        """모방 통계 반환"""
        total_imitations = len(self.imitation_history)
        successful_imitations = len([r for r in self.imitation_history if r.success])

        type_counts = {}
        for result in self.imitation_history:
            type_name = result.imitation_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        avg_confidence = (
            sum(r.confidence for r in self.imitation_history) / total_imitations
            if total_imitations > 0
            else 0
        )

        return {
            "total_imitations": total_imitations,
            "successful_imitations": successful_imitations,
            "success_rate": (
                successful_imitations / total_imitations if total_imitations > 0 else 0
            ),
            "type_distribution": type_counts,
            "average_confidence": avg_confidence,
            "successful_patterns": self.successful_patterns,
        }

    def recommend_imitation_type(
        self, strategy_complexity: str = "medium"
    ) -> ImitationType:
        """모방 유형 추천"""
        if strategy_complexity == "high":
            return ImitationType.EXACT_COPY
        elif strategy_complexity == "medium":
            return ImitationType.ADAPTIVE_COPY
        elif strategy_complexity == "low":
            return ImitationType.CREATIVE_COPY
        else:
            return ImitationType.PARTIAL_COPY


# 싱글톤 인스턴스
_strategy_imitator = None


def get_strategy_imitator() -> StrategyImitator:
    """StrategyImitator 싱글톤 인스턴스 반환"""
    global _strategy_imitator
    if _strategy_imitator is None:
        _strategy_imitator = StrategyImitator()
    return _strategy_imitator
