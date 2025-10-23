#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 의사결정 모듈

의사결정 및 판단을 담당하는 모듈입니다.
- 의사결정 프레임워크
- 판단 기준 분석
- 의사결정 결과 평가
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """의사결정 유형"""

    RATIONAL = "rational"  # 합리적 의사결정
    INTUITIVE = "intuitive"  # 직관적 의사결정
    EMOTIONAL = "emotional"  # 감정적 의사결정
    COLLABORATIVE = "collaborative"  # 협력적 의사결정
    ADAPTIVE = "adaptive"  # 적응적 의사결정
    STRATEGIC = "strategic"  # 전략적 의사결정


@dataclass
class DecisionCriteria:
    """의사결정 기준"""

    criteria_id: str
    name: str
    weight: float
    description: str
    evaluation_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionOption:
    """의사결정 옵션"""

    option_id: str
    name: str
    description: str
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    """의사결정 결과"""

    selected_option: DecisionOption
    decision_type: DecisionType
    confidence: float
    reasoning: List[str]
    alternatives: List[DecisionOption] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionContext:
    """의사결정 컨텍스트"""

    context_id: str
    description: str
    criteria: List[DecisionCriteria]
    options: List[DecisionOption]
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DecisionMaker:
    """의사결정 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.decision_history = []
        self.performance_metrics = {
            "total_decisions": 0,
            "successful_decisions": 0,
            "average_confidence": 0.0,
            "average_processing_time": 0.0,
        }
        self.logger.info("의사결정기 초기화 완료")

    async def make_decision(
        self,
        context: DecisionContext,
        decision_type: DecisionType = DecisionType.RATIONAL,
    ) -> DecisionResult:
        """의사결정 수행"""
        try:
            start_time = datetime.now()
            self.logger.info(f"의사결정 시작: {decision_type.value}")

            # 의사결정 방식에 따른 처리
            if decision_type == DecisionType.RATIONAL:
                result = await self._rational_decision(context)
            elif decision_type == DecisionType.INTUITIVE:
                result = await self._intuitive_decision(context)
            elif decision_type == DecisionType.EMOTIONAL:
                result = await self._emotional_decision(context)
            elif decision_type == DecisionType.COLLABORATIVE:
                result = await self._collaborative_decision(context)
            elif decision_type == DecisionType.ADAPTIVE:
                result = await self._adaptive_decision(context)
            elif decision_type == DecisionType.STRATEGIC:
                result = await self._strategic_decision(context)
            else:
                result = await self._rational_decision(context)

            # 성능 메트릭 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(result, processing_time)

            # 의사결정 히스토리에 추가
            self.decision_history.append(
                {
                    "context": context,
                    "result": result,
                    "decision_type": decision_type,
                    "processing_time": processing_time,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(
                f"의사결정 완료: {decision_type.value}, 신뢰도: {result.confidence:.2f}"
            )
            return result

        except Exception as e:
            self.logger.error(f"의사결정 중 오류 발생: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=decision_type,
                confidence=0.0,
                reasoning=[f"오류 발생: {str(e)}"],
            )

    async def _rational_decision(self, context: DecisionContext) -> DecisionResult:
        """합리적 의사결정"""
        try:
            # 기준별 점수 계산
            scored_options = []
            for option in context.options:
                option_scores = {}
                total_score = 0.0

                for criteria in context.criteria:
                    score = self._evaluate_criteria(option, criteria)
                    option_scores[criteria.criteria_id] = score
                    total_score += score * criteria.weight

                option.criteria_scores = option_scores
                option.overall_score = total_score
                scored_options.append(option)

            # 최적 옵션 선택
            best_option = max(scored_options, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_confidence(scored_options, best_option)

            # 추론 과정
            reasoning = [
                f"합리적 의사결정: {len(context.criteria)}개 기준으로 평가",
                f"최적 옵션: {best_option.name} (점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(scored_options)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.RATIONAL,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=scored_options,
            )

        except Exception as e:
            self.logger.error(f"합리적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.RATIONAL,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    async def _intuitive_decision(self, context: DecisionContext) -> DecisionResult:
        """직관적 의사결정"""
        try:
            # 직관적 패턴 분석
            intuitive_scores = []
            for option in context.options:
                # 직관적 점수 계산 (간단한 휴리스틱)
                intuitive_score = self._calculate_intuitive_score(option, context)
                option.overall_score = intuitive_score
                intuitive_scores.append(option)

            # 직관적으로 최적 옵션 선택
            best_option = max(intuitive_scores, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_intuitive_confidence(
                intuitive_scores, best_option
            )

            # 추론 과정
            reasoning = [
                f"직관적 의사결정: 패턴 기반 평가",
                f"선택된 옵션: {best_option.name} (직관적 점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(intuitive_scores)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.INTUITIVE,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=intuitive_scores,
            )

        except Exception as e:
            self.logger.error(f"직관적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.INTUITIVE,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    async def _emotional_decision(self, context: DecisionContext) -> DecisionResult:
        """감정적 의사결정"""
        try:
            # 감정적 요소 분석
            emotional_scores = []
            for option in context.options:
                # 감정적 점수 계산
                emotional_score = self._calculate_emotional_score(option, context)
                option.overall_score = emotional_score
                emotional_scores.append(option)

            # 감정적으로 최적 옵션 선택
            best_option = max(emotional_scores, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_emotional_confidence(
                emotional_scores, best_option
            )

            # 추론 과정
            reasoning = [
                f"감정적 의사결정: 감정적 요소 기반 평가",
                f"선택된 옵션: {best_option.name} (감정적 점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(emotional_scores)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.EMOTIONAL,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=emotional_scores,
            )

        except Exception as e:
            self.logger.error(f"감정적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.EMOTIONAL,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    async def _collaborative_decision(self, context: DecisionContext) -> DecisionResult:
        """협력적 의사결정"""
        try:
            # 다중 관점 분석
            collaborative_scores = []
            for option in context.options:
                # 협력적 점수 계산 (다양한 관점 고려)
                collaborative_score = self._calculate_collaborative_score(
                    option, context
                )
                option.overall_score = collaborative_score
                collaborative_scores.append(option)

            # 협력적으로 최적 옵션 선택
            best_option = max(collaborative_scores, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_collaborative_confidence(
                collaborative_scores, best_option
            )

            # 추론 과정
            reasoning = [
                f"협력적 의사결정: 다중 관점 기반 평가",
                f"선택된 옵션: {best_option.name} (협력적 점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(collaborative_scores)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.COLLABORATIVE,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=collaborative_scores,
            )

        except Exception as e:
            self.logger.error(f"협력적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.COLLABORATIVE,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    async def _adaptive_decision(self, context: DecisionContext) -> DecisionResult:
        """적응적 의사결정"""
        try:
            # 상황에 따른 적응적 평가
            adaptive_scores = []
            for option in context.options:
                # 적응적 점수 계산 (상황 변화 고려)
                adaptive_score = self._calculate_adaptive_score(option, context)
                option.overall_score = adaptive_score
                adaptive_scores.append(option)

            # 적응적으로 최적 옵션 선택
            best_option = max(adaptive_scores, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_adaptive_confidence(
                adaptive_scores, best_option
            )

            # 추론 과정
            reasoning = [
                f"적응적 의사결정: 상황 변화 고려 평가",
                f"선택된 옵션: {best_option.name} (적응적 점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(adaptive_scores)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.ADAPTIVE,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=adaptive_scores,
            )

        except Exception as e:
            self.logger.error(f"적응적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.ADAPTIVE,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    async def _strategic_decision(self, context: DecisionContext) -> DecisionResult:
        """전략적 의사결정"""
        try:
            # 전략적 가치 분석
            strategic_scores = []
            for option in context.options:
                # 전략적 점수 계산 (장기적 가치 고려)
                strategic_score = self._calculate_strategic_score(option, context)
                option.overall_score = strategic_score
                strategic_scores.append(option)

            # 전략적으로 최적 옵션 선택
            best_option = max(strategic_scores, key=lambda x: x.overall_score)

            # 신뢰도 계산
            confidence = self._calculate_strategic_confidence(
                strategic_scores, best_option
            )

            # 추론 과정
            reasoning = [
                f"전략적 의사결정: 장기적 가치 기반 평가",
                f"선택된 옵션: {best_option.name} (전략적 점수: {best_option.overall_score:.2f})",
                f"평가된 옵션 수: {len(strategic_scores)}개",
            ]

            return DecisionResult(
                selected_option=best_option,
                decision_type=DecisionType.STRATEGIC,
                confidence=confidence,
                reasoning=reasoning,
                alternatives=strategic_scores,
            )

        except Exception as e:
            self.logger.error(f"전략적 의사결정 중 오류: {e}")
            return DecisionResult(
                selected_option=DecisionOption(
                    option_id="error", name="오류", description=str(e)
                ),
                decision_type=DecisionType.STRATEGIC,
                confidence=0.0,
                reasoning=[f"오류: {str(e)}"],
            )

    def _evaluate_criteria(
        self, option: DecisionOption, criteria: DecisionCriteria
    ) -> float:
        """기준별 평가"""
        try:
            # 간단한 평가 로직 (실제로는 더 복잡한 로직이 필요)
            if criteria.evaluation_method == "binary":
                return (
                    1.0 if option.name.lower() in criteria.description.lower() else 0.0
                )
            elif criteria.evaluation_method == "scale":
                # 0-1 스케일로 평가
                return min(1.0, len(option.description) / 100.0)
            else:
                return 0.5  # 기본값
        except Exception as e:
            self.logger.error(f"기준 평가 중 오류: {e}")
            return 0.0

    def _calculate_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 선택된 옵션의 점수와 다른 옵션들의 점수 차이를 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            max_score = max(scores)
            selected_score = selected_option.overall_score

            if max_score == 0:
                return 0.0

            # 점수 차이에 따른 신뢰도
            score_ratio = selected_score / max_score
            confidence = min(1.0, score_ratio * 1.2)

            return confidence

        except Exception as e:
            self.logger.error(f"신뢰도 계산 중 오류: {e}")
            return 0.5

    def _calculate_intuitive_score(
        self, option: DecisionOption, context: DecisionContext
    ) -> float:
        """직관적 점수 계산"""
        try:
            # 간단한 직관적 점수 계산 (실제로는 더 복잡한 패턴 인식이 필요)
            score = 0.0

            # 옵션 이름의 길이와 복잡성
            name_length = len(option.name)
            score += min(0.3, name_length / 50.0)

            # 설명의 상세함
            description_length = len(option.description)
            score += min(0.3, description_length / 200.0)

            # 메타데이터의 풍부함
            metadata_count = len(option.metadata)
            score += min(0.4, metadata_count / 10.0)

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"직관적 점수 계산 중 오류: {e}")
            return 0.5

    def _calculate_intuitive_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """직관적 신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 직관적 점수의 분산을 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            variance = sum(
                (score - sum(scores) / len(scores)) ** 2 for score in scores
            ) / len(scores)

            # 분산이 작을수록 신뢰도가 높음
            confidence = max(0.3, 1.0 - variance)
            return confidence

        except Exception as e:
            self.logger.error(f"직관적 신뢰도 계산 중 오류: {e}")
            return 0.5

    def _calculate_emotional_score(
        self, option: DecisionOption, context: DecisionContext
    ) -> float:
        """감정적 점수 계산"""
        try:
            # 간단한 감정적 점수 계산
            score = 0.0

            # 긍정적 키워드 확인
            positive_keywords = ["good", "positive", "happy", "success", "benefit"]
            for keyword in positive_keywords:
                if keyword in option.description.lower():
                    score += 0.2

            # 부정적 키워드 확인
            negative_keywords = ["bad", "negative", "sad", "failure", "harm"]
            for keyword in negative_keywords:
                if keyword in option.description.lower():
                    score -= 0.1

            return max(0.0, min(1.0, score + 0.5))

        except Exception as e:
            self.logger.error(f"감정적 점수 계산 중 오류: {e}")
            return 0.5

    def _calculate_emotional_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """감정적 신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 감정적 점수의 일관성을 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            average_score = sum(scores) / len(scores)

            # 평균에 가까울수록 신뢰도가 높음
            selected_score = selected_option.overall_score
            confidence = max(0.3, 1.0 - abs(selected_score - average_score))

            return confidence

        except Exception as e:
            self.logger.error(f"감정적 신뢰도 계산 중 오류: {e}")
            return 0.5

    def _calculate_collaborative_score(
        self, option: DecisionOption, context: DecisionContext
    ) -> float:
        """협력적 점수 계산"""
        try:
            # 다중 관점을 고려한 점수 계산
            score = 0.0

            # 기준 수에 따른 점수
            criteria_count = len(context.criteria)
            score += min(0.4, criteria_count / 10.0)

            # 옵션의 복잡성
            complexity = len(option.description) + len(option.metadata)
            score += min(0.3, complexity / 100.0)

            # 메타데이터의 다양성
            metadata_diversity = len(set(option.metadata.values()))
            score += min(0.3, metadata_diversity / 5.0)

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"협력적 점수 계산 중 오류: {e}")
            return 0.5

    def _calculate_collaborative_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """협력적 신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 협력적 점수의 다양성을 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            unique_scores = len(set(scores))

            # 다양성이 높을수록 신뢰도가 높음
            confidence = min(1.0, unique_scores / len(scores) * 1.5)

            return confidence

        except Exception as e:
            self.logger.error(f"협력적 신뢰도 계산 중 오류: {e}")
            return 0.5

    def _calculate_adaptive_score(
        self, option: DecisionOption, context: DecisionContext
    ) -> float:
        """적응적 점수 계산"""
        try:
            # 상황 변화에 대한 적응성을 고려한 점수 계산
            score = 0.0

            # 옵션의 유연성
            flexibility_keywords = ["flexible", "adaptive", "dynamic", "changeable"]
            for keyword in flexibility_keywords:
                if keyword in option.description.lower():
                    score += 0.25

            # 메타데이터의 적응성
            if "adaptability" in option.metadata:
                score += min(0.3, option.metadata["adaptability"])

            # 기본 점수
            score += 0.3

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"적응적 점수 계산 중 오류: {e}")
            return 0.5

    def _calculate_adaptive_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """적응적 신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 적응적 점수의 안정성을 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            score_range = max(scores) - min(scores)

            # 점수 범위가 작을수록 신뢰도가 높음
            confidence = max(0.3, 1.0 - score_range)

            return confidence

        except Exception as e:
            self.logger.error(f"적응적 신뢰도 계산 중 오류: {e}")
            return 0.5

    def _calculate_strategic_score(
        self, option: DecisionOption, context: DecisionContext
    ) -> float:
        """전략적 점수 계산"""
        try:
            # 장기적 가치를 고려한 점수 계산
            score = 0.0

            # 전략적 키워드 확인
            strategic_keywords = ["strategic", "long-term", "future", "vision", "goal"]
            for keyword in strategic_keywords:
                if keyword in option.description.lower():
                    score += 0.2

            # 메타데이터의 전략적 가치
            if "strategic_value" in option.metadata:
                score += min(0.4, option.metadata["strategic_value"])

            # 기본 점수
            score += 0.3

            return min(1.0, score)

        except Exception as e:
            self.logger.error(f"전략적 점수 계산 중 오류: {e}")
            return 0.5

    def _calculate_strategic_confidence(
        self, options: List[DecisionOption], selected_option: DecisionOption
    ) -> float:
        """전략적 신뢰도 계산"""
        try:
            if not options:
                return 0.0

            # 전략적 점수의 일관성을 기반으로 신뢰도 계산
            scores = [option.overall_score for option in options]
            median_score = sorted(scores)[len(scores) // 2]

            # 중앙값에 가까울수록 신뢰도가 높음
            selected_score = selected_option.overall_score
            confidence = max(0.3, 1.0 - abs(selected_score - median_score))

            return confidence

        except Exception as e:
            self.logger.error(f"전략적 신뢰도 계산 중 오류: {e}")
            return 0.5

    def _update_performance_metrics(
        self, result: DecisionResult, processing_time: float
    ):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_decisions"] += 1
        if result.confidence > 0.5:
            self.performance_metrics["successful_decisions"] += 1

        # 평균 신뢰도 업데이트
        total_confidence = self.performance_metrics["average_confidence"] * (
            self.performance_metrics["total_decisions"] - 1
        )
        self.performance_metrics["average_confidence"] = (
            total_confidence + result.confidence
        ) / self.performance_metrics["total_decisions"]

        # 평균 처리 시간 업데이트
        total_time = self.performance_metrics["average_processing_time"] * (
            self.performance_metrics["total_decisions"] - 1
        )
        self.performance_metrics["average_processing_time"] = (
            total_time + processing_time
        ) / self.performance_metrics["total_decisions"]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """의사결정 히스토리 조회"""
        return self.decision_history.copy()
