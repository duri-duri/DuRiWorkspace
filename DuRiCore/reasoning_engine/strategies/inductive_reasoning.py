#!/usr/bin/env python3
"""
DuRi 추론 엔진 - 귀납적 추론 전략
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

import logging
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..core.logical_processor import (
    InferenceType,
    LogicalProcessor,
    LogicalStep,
    PremiseType,
    SemanticPremise,
)

logger = logging.getLogger(__name__)


class InductivePattern(Enum):
    """귀납적 추론 패턴"""

    ENUMERATION = "enumeration"
    ANALOGY = "analogy"
    STATISTICAL = "statistical"
    CAUSAL = "causal"
    GENERALIZATION = "generalization"
    PREDICTION = "prediction"
    ABDUCTION = "abduction"


@dataclass
class InductivePremise:
    """귀납적 전제"""

    observations: List[str]
    pattern: InductivePattern
    conclusion: str
    confidence: float
    sample_size: int
    representativeness: float
    semantic_vectors: Dict[str, np.ndarray]


class InductiveReasoning:
    """귀납적 추론 전략 클래스"""

    def __init__(self, logical_processor: LogicalProcessor):
        """귀납적 추론 초기화"""
        self.logical_processor = logical_processor
        self.inductive_patterns = self._initialize_inductive_patterns()
        logger.info("귀납적 추론 전략 초기화 완료")

    def _initialize_inductive_patterns(self) -> Dict[InductivePattern, Dict[str, Any]]:
        """귀납적 추론 패턴 초기화"""
        return {
            InductivePattern.ENUMERATION: {
                "description": "개별 사례들의 관찰을 통해 일반적 결론 도출",
                "strength_multiplier": 0.8,
                "min_sample_size": 3,
            },
            InductivePattern.ANALOGY: {
                "description": "유사한 사례와의 비교를 통해 결론 도출",
                "strength_multiplier": 0.7,
                "similarity_threshold": 0.6,
            },
            InductivePattern.STATISTICAL: {
                "description": "통계적 분석을 통해 결론 도출",
                "strength_multiplier": 0.9,
                "confidence_level": 0.95,
            },
            InductivePattern.CAUSAL: {
                "description": "인과관계 분석을 통해 결론 도출",
                "strength_multiplier": 0.8,
                "causal_strength_threshold": 0.7,
            },
            InductivePattern.GENERALIZATION: {
                "description": "특정 사례에서 일반적 원리 도출",
                "strength_multiplier": 0.6,
                "generalization_breadth": 0.5,
            },
            InductivePattern.PREDICTION: {
                "description": "과거 패턴을 바탕으로 미래 예측",
                "strength_multiplier": 0.7,
                "prediction_horizon": 1.0,
            },
        }

    def construct_enumeration(self, observations: List[str]) -> InductivePremise:
        """열거적 귀납 구성"""
        logger.info(f"열거적 귀납 구성 시작: {len(observations)}개 관찰")

        if len(observations) < 3:
            logger.warning("관찰 수가 너무 적습니다 (최소 3개 필요)")
            return self._create_invalid_premise(
                observations, InductivePattern.ENUMERATION
            )

        # 관찰들의 의미 벡터 인코딩
        observation_vectors = []
        for observation in observations:
            vector = self.logical_processor.encode_semantics(observation)
            observation_vectors.append(vector)

        # 결론 도출
        conclusion = self._derive_enumeration_conclusion(observations)
        conclusion_vector = self.logical_processor.encode_semantics(conclusion)

        # 신뢰도 계산
        confidence = self._calculate_enumeration_confidence(
            observations, observation_vectors
        )

        # 표본 크기와 대표성 평가
        sample_size = len(observations)
        representativeness = self._evaluate_representativeness(observations)

        semantic_vectors = {
            "observations": observation_vectors,
            "conclusion": conclusion_vector,
        }

        return InductivePremise(
            observations=observations,
            pattern=InductivePattern.ENUMERATION,
            conclusion=conclusion,
            confidence=confidence,
            sample_size=sample_size,
            representativeness=representativeness,
            semantic_vectors=semantic_vectors,
        )

    def _derive_enumeration_conclusion(self, observations: List[str]) -> str:
        """열거적 귀납 결론 도출"""
        if not observations:
            return "관찰 데이터가 부족합니다."

        # 관찰들의 공통 패턴 찾기
        common_patterns = self._find_common_patterns(observations)

        if common_patterns:
            # 가장 빈번한 패턴을 기반으로 결론 도출
            most_common_pattern = max(common_patterns.items(), key=lambda x: x[1])
            return f"관찰된 패턴에 따르면 {most_common_pattern[0]}입니다."
        else:
            # 일반적인 결론 도출
            return "관찰된 사례들을 종합하면 일정한 패턴이 나타납니다."

    def _find_common_patterns(self, observations: List[str]) -> Dict[str, int]:
        """공통 패턴 찾기"""
        patterns = {}

        # 간단한 패턴 추출 (공통 단어나 구문)
        for observation in observations:
            words = observation.split()
            for word in words:
                if len(word) > 2:  # 2글자 이상의 단어만
                    patterns[word] = patterns.get(word, 0) + 1

        # 빈도가 2 이상인 패턴만 반환
        return {k: v for k, v in patterns.items() if v >= 2}

    def _calculate_enumeration_confidence(
        self, observations: List[str], observation_vectors: List[np.ndarray]
    ) -> float:
        """열거적 귀납 신뢰도 계산"""
        if len(observations) < 3:
            return 0.3

        # 기본 신뢰도 (표본 크기에 따른)
        base_confidence = min(0.8, len(observations) * 0.1)

        # 관찰들 간의 일관성 평가
        consistency_score = self._evaluate_observation_consistency(observation_vectors)

        # 최종 신뢰도 계산
        confidence = base_confidence * consistency_score

        return min(confidence, 1.0)

    def _evaluate_observation_consistency(
        self, observation_vectors: List[np.ndarray]
    ) -> float:
        """관찰 일관성 평가"""
        if len(observation_vectors) < 2:
            return 0.5

        # 관찰 벡터들 간의 평균 유사도 계산
        similarities = []
        for i in range(len(observation_vectors)):
            for j in range(i + 1, len(observation_vectors)):
                similarity = self.logical_processor.calculate_similarity(
                    observation_vectors[i], observation_vectors[j]
                )
                similarities.append(similarity)

        if similarities:
            return statistics.mean(similarities)
        else:
            return 0.5

    def _evaluate_representativeness(self, observations: List[str]) -> float:
        """대표성 평가"""
        # 간단한 대표성 평가 (관찰의 다양성과 균형성)
        if len(observations) < 3:
            return 0.3

        # 관찰들의 길이 분포 평가
        lengths = [len(obs) for obs in observations]
        length_variance = statistics.variance(lengths) if len(lengths) > 1 else 0

        # 분산이 작을수록 대표성이 높음
        representativeness = max(0.1, 1.0 - (length_variance / 100))

        return representativeness

    def construct_analogy(self, source_case: str, target_case: str) -> InductivePremise:
        """유추적 귀납 구성"""
        logger.info("유추적 귀납 구성 시작")

        # 소스와 타겟 케이스의 의미 벡터 인코딩
        source_vector = self.logical_processor.encode_semantics(source_case)
        target_vector = self.logical_processor.encode_semantics(target_case)

        # 유사도 계산
        similarity = self.logical_processor.calculate_similarity(
            source_vector, target_vector
        )

        # 결론 도출
        conclusion = self._derive_analogy_conclusion(
            source_case, target_case, similarity
        )
        conclusion_vector = self.logical_processor.encode_semantics(conclusion)

        # 신뢰도 계산
        confidence = self._calculate_analogy_confidence(similarity)

        semantic_vectors = {
            "source_case": source_vector,
            "target_case": target_vector,
            "conclusion": conclusion_vector,
        }

        return InductivePremise(
            observations=[source_case, target_case],
            pattern=InductivePattern.ANALOGY,
            conclusion=conclusion,
            confidence=confidence,
            sample_size=2,
            representativeness=similarity,
            semantic_vectors=semantic_vectors,
        )

    def _derive_analogy_conclusion(
        self, source_case: str, target_case: str, similarity: float
    ) -> str:
        """유추적 귀납 결론 도출"""
        if similarity > 0.7:
            return f"유사성이 높으므로 {target_case}에서도 {source_case}와 유사한 결과를 기대할 수 있습니다."
        elif similarity > 0.5:
            return f"일정한 유사성이 있으므로 {target_case}에서도 부분적으로 유사한 결과를 기대할 수 있습니다."
        else:
            return f"유사성이 낮으므로 {target_case}에서의 결과는 불확실합니다."

    def _calculate_analogy_confidence(self, similarity: float) -> float:
        """유추적 귀납 신뢰도 계산"""
        # 유사도에 기반한 신뢰도 계산
        confidence = similarity * 0.8  # 최대 0.8

        return min(confidence, 1.0)

    def construct_statistical(
        self, data_points: List[float], labels: List[str]
    ) -> InductivePremise:
        """통계적 귀납 구성"""
        logger.info(f"통계적 귀납 구성 시작: {len(data_points)}개 데이터 포인트")

        if len(data_points) < 5:
            logger.warning("데이터 포인트가 너무 적습니다 (최소 5개 필요)")
            return self._create_invalid_premise(
                [str(d) for d in data_points], InductivePattern.STATISTICAL
            )

        # 통계적 분석
        mean_value = statistics.mean(data_points)
        std_dev = statistics.stdev(data_points) if len(data_points) > 1 else 0

        # 결론 도출
        conclusion = self._derive_statistical_conclusion(
            data_points, mean_value, std_dev
        )
        conclusion_vector = self.logical_processor.encode_semantics(conclusion)

        # 신뢰도 계산
        confidence = self._calculate_statistical_confidence(data_points, std_dev)

        # 표본 크기와 대표성 평가
        sample_size = len(data_points)
        representativeness = self._evaluate_statistical_representativeness(data_points)

        observations = [
            f"{label}: {value}" for label, value in zip(labels, data_points)
        ]

        semantic_vectors = {
            "data_points": [
                self.logical_processor.encode_semantics(str(d)) for d in data_points
            ],
            "conclusion": conclusion_vector,
        }

        return InductivePremise(
            observations=observations,
            pattern=InductivePattern.STATISTICAL,
            conclusion=conclusion,
            confidence=confidence,
            sample_size=sample_size,
            representativeness=representativeness,
            semantic_vectors=semantic_vectors,
        )

    def _derive_statistical_conclusion(
        self, data_points: List[float], mean_value: float, std_dev: float
    ) -> str:
        """통계적 귀납 결론 도출"""
        if std_dev < 0.1 * mean_value:
            return (
                f"데이터가 일관적이며 평균값 {mean_value:.2f} 주변에 집중되어 있습니다."
            )
        elif std_dev < 0.3 * mean_value:
            return f"데이터가 비교적 일관적이며 평균값 {mean_value:.2f}를 중심으로 분포합니다."
        else:
            return f"데이터가 분산되어 있으며 평균값 {mean_value:.2f}이지만 변동성이 큽니다."

    def _calculate_statistical_confidence(
        self, data_points: List[float], std_dev: float
    ) -> float:
        """통계적 귀납 신뢰도 계산"""
        # 표본 크기에 따른 기본 신뢰도
        base_confidence = min(0.9, len(data_points) * 0.05)

        # 표준편차에 따른 조정
        if len(data_points) > 1:
            coefficient_of_variation = std_dev / statistics.mean(data_points)
            if coefficient_of_variation < 0.1:
                confidence_adjustment = 1.0
            elif coefficient_of_variation < 0.3:
                confidence_adjustment = 0.9
            else:
                confidence_adjustment = 0.7
        else:
            confidence_adjustment = 0.8

        return base_confidence * confidence_adjustment

    def _evaluate_statistical_representativeness(
        self, data_points: List[float]
    ) -> float:
        """통계적 대표성 평가"""
        if len(data_points) < 5:
            return 0.3

        # 데이터의 분포 평가
        sorted_data = sorted(data_points)
        q1 = sorted_data[len(sorted_data) // 4]
        q3 = sorted_data[3 * len(sorted_data) // 4]
        iqr = q3 - q1

        # IQR이 작을수록 대표성이 높음
        representativeness = max(0.1, 1.0 - (iqr / statistics.mean(data_points)))

        return representativeness

    def _create_invalid_premise(
        self, observations: List[str], pattern: InductivePattern
    ) -> InductivePremise:
        """유효하지 않은 전제 생성"""
        return InductivePremise(
            observations=observations,
            pattern=pattern,
            conclusion="데이터가 부족하여 결론을 도출할 수 없습니다.",
            confidence=0.1,
            sample_size=len(observations),
            representativeness=0.1,
            semantic_vectors={},
        )
