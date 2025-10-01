#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 동적 추론 엔진

상황에 따라 추론 방식을 자동으로 조정하는 엔진입니다.
- 컨텍스트별 추론 방식 매핑
- 입력 데이터 분석을 통한 적응
- 복잡성 계산 및 데이터 유형 분석
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from ..data_structures import ReasoningContext, ReasoningType

logger = logging.getLogger(__name__)


class DynamicReasoningEngine:
    """동적 추론 엔진"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_patterns = {}
        self.adaptation_history = []
        self.performance_metrics = {
            "total_sessions": 0,
            "average_confidence": 0.0,
            "average_adaptation": 0.0,
            "average_efficiency": 0.0,
        }
        self.logger.info("동적 추론 엔진 초기화 완료")

    async def adapt_reasoning_approach(
        self, context: ReasoningContext, input_data: Dict[str, Any]
    ) -> ReasoningType:
        """상황에 따라 추론 방식 자동 조정"""
        try:
            # 컨텍스트별 추론 방식 매핑
            context_mapping = {
                ReasoningContext.PROBLEM_SOLVING: [
                    ReasoningType.DEDUCTIVE,
                    ReasoningType.ANALOGICAL,
                ],
                ReasoningContext.DECISION_MAKING: [
                    ReasoningType.INDUCTIVE,
                    ReasoningType.EMOTIONAL,
                ],
                ReasoningContext.LEARNING: [
                    ReasoningType.ABDUCTIVE,
                    ReasoningType.INTEGRATED,
                ],
                ReasoningContext.CREATION: [
                    ReasoningType.CREATIVE,
                    ReasoningType.INTUITIVE,
                ],
                ReasoningContext.ANALYSIS: [
                    ReasoningType.DEDUCTIVE,
                    ReasoningType.ANALOGICAL,
                ],
                ReasoningContext.SYNTHESIS: [
                    ReasoningType.INDUCTIVE,
                    ReasoningType.INTEGRATED,
                ],
                ReasoningContext.EVALUATION: [
                    ReasoningType.DEDUCTIVE,
                    ReasoningType.EMOTIONAL,
                ],
                ReasoningContext.PREDICTION: [
                    ReasoningType.ABDUCTIVE,
                    ReasoningType.INTUITIVE,
                ],
            }

            # 기본 추론 방식 선택
            base_reasoning_types = context_mapping.get(
                context, [ReasoningType.INTEGRATED]
            )

            # 입력 데이터 분석을 통한 적응
            adapted_type = self._analyze_input_for_adaptation(
                input_data, base_reasoning_types
            )

            return adapted_type
        except Exception as e:
            self.logger.error(f"추론 방식 적응 중 오류 발생: {e}")
            return ReasoningType.INTEGRATED

    def _analyze_input_for_adaptation(
        self, input_data: Dict[str, Any], base_types: List[ReasoningType]
    ) -> ReasoningType:
        """입력 데이터 분석을 통한 적응"""
        try:
            # 데이터 복잡성 분석
            complexity_score = self._calculate_complexity(input_data)

            # 데이터 유형 분석
            data_type = self._analyze_data_type(input_data)

            # 적응 로직
            if complexity_score > 0.8:
                return ReasoningType.INTEGRATED
            elif data_type == "creative":
                return ReasoningType.CREATIVE
            elif data_type == "emotional":
                return ReasoningType.EMOTIONAL
            elif data_type == "logical":
                return ReasoningType.DEDUCTIVE
            else:
                return base_types[0] if base_types else ReasoningType.INTEGRATED
        except Exception as e:
            self.logger.error(f"입력 데이터 분석 중 오류: {e}")
            return ReasoningType.INTEGRATED

    def _calculate_complexity(self, input_data: Dict[str, Any]) -> float:
        """입력 데이터의 복잡성 계산"""
        try:
            complexity_factors = {
                "data_size": len(str(input_data)) / 1000,
                "nested_levels": self._count_nested_levels(input_data),
                "diversity": (
                    len(set(str(v) for v in input_data.values())) / len(input_data)
                    if input_data
                    else 0
                ),
            }

            return sum(complexity_factors.values()) / len(complexity_factors)
        except Exception as e:
            self.logger.error(f"복잡성 계산 중 오류: {e}")
            return 0.5

    def _count_nested_levels(self, data: Any, current_level: int = 0) -> int:
        """중첩 레벨 계산"""
        try:
            if isinstance(data, dict):
                return (
                    max(
                        self._count_nested_levels(v, current_level + 1)
                        for v in data.values()
                    )
                    if data
                    else current_level
                )
            elif isinstance(data, list):
                return (
                    max(
                        self._count_nested_levels(item, current_level + 1)
                        for item in data
                    )
                    if data
                    else current_level
                )
            else:
                return current_level
        except Exception as e:
            self.logger.error(f"중첩 레벨 계산 중 오류: {e}")
            return current_level

    def _analyze_data_type(self, input_data: Dict[str, Any]) -> str:
        """데이터 유형 분석"""
        try:
            # 감정적 키워드 검색
            emotional_keywords = [
                "feel",
                "emotion",
                "happy",
                "sad",
                "angry",
                "love",
                "hate",
            ]
            creative_keywords = [
                "create",
                "design",
                "imagine",
                "innovate",
                "art",
                "creative",
            ]
            logical_keywords = [
                "analyze",
                "logic",
                "reason",
                "proof",
                "evidence",
                "fact",
            ]

            data_str = str(input_data).lower()

            emotional_count = sum(
                1 for keyword in emotional_keywords if keyword in data_str
            )
            creative_count = sum(
                1 for keyword in creative_keywords if keyword in data_str
            )
            logical_count = sum(
                1 for keyword in logical_keywords if keyword in data_str
            )

            if emotional_count > max(creative_count, logical_count):
                return "emotional"
            elif creative_count > max(emotional_count, logical_count):
                return "creative"
            elif logical_count > max(emotional_count, creative_count):
                return "logical"
            else:
                return "mixed"
        except Exception as e:
            self.logger.error(f"데이터 유형 분석 중 오류: {e}")
            return "mixed"
