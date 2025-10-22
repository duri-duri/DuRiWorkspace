#!/usr/bin/env python3
"""
DuRi 추론 엔진 - 가설적 추론 전략
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

import itertools
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..core.logical_processor import (InferenceType, LogicalProcessor,
                                      LogicalStep, PremiseType,
                                      SemanticPremise)

logger = logging.getLogger(__name__)


class AbductivePattern(Enum):
    """가설적 추론 패턴"""

    BEST_EXPLANATION = "best_explanation"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    CAUSAL_INFERENCE = "causal_inference"
    DIAGNOSTIC_REASONING = "diagnostic_reasoning"
    CREATIVE_EXPLANATION = "creative_explanation"
    SCIENTIFIC_DISCOVERY = "scientific_discovery"


@dataclass
class AbductivePremise:
    """가설적 전제"""

    observations: List[str]
    hypotheses: List[str]
    best_hypothesis: str
    pattern: AbductivePattern
    confidence: float
    explanatory_power: float
    simplicity: float
    semantic_vectors: Dict[str, np.ndarray]


class AbductiveReasoning:
    """가설적 추론 전략 클래스"""

    def __init__(self, logical_processor: LogicalProcessor):
        """가설적 추론 초기화"""
        self.logical_processor = logical_processor
        self.abductive_patterns = self._initialize_abductive_patterns()
        logger.info("가설적 추론 전략 초기화 완료")

    def _initialize_abductive_patterns(self) -> Dict[AbductivePattern, Dict[str, Any]]:
        """가설적 추론 패턴 초기화"""
        return {
            AbductivePattern.BEST_EXPLANATION: {
                "description": "관찰된 현상을 가장 잘 설명하는 가설 선택",
                "strength_multiplier": 0.8,
                "explanatory_threshold": 0.6,
            },
            AbductivePattern.HYPOTHESIS_GENERATION: {
                "description": "관찰된 현상을 설명할 수 있는 가설들 생성",
                "strength_multiplier": 0.7,
                "creativity_factor": 0.5,
            },
            AbductivePattern.CAUSAL_INFERENCE: {
                "description": "인과관계를 추론하여 원인 가설 도출",
                "strength_multiplier": 0.8,
                "causal_strength_threshold": 0.7,
            },
            AbductivePattern.DIAGNOSTIC_REASONING: {
                "description": "증상을 바탕으로 진단 가설 도출",
                "strength_multiplier": 0.9,
                "diagnostic_accuracy": 0.8,
            },
            AbductivePattern.CREATIVE_EXPLANATION: {
                "description": "창의적인 설명 가설 생성",
                "strength_multiplier": 0.6,
                "novelty_factor": 0.7,
            },
            AbductivePattern.SCIENTIFIC_DISCOVERY: {
                "description": "과학적 발견을 위한 가설 생성",
                "strength_multiplier": 0.8,
                "falsifiability": 0.9,
            },
        }

    def construct_best_explanation(self, observations: List[str]) -> AbductivePremise:
        """최선의 설명 구성"""
        logger.info(f"최선의 설명 구성 시작: {len(observations)}개 관찰")

        if not observations:
            logger.warning("관찰 데이터가 없습니다")
            return self._create_invalid_premise(observations, AbductivePattern.BEST_EXPLANATION)

        # 관찰들의 의미 벡터 인코딩
        observation_vectors = []
        for observation in observations:
            vector = self.logical_processor.encode_semantics(observation)
            observation_vectors.append(vector)

        # 가설들 생성
        hypotheses = self._generate_hypotheses(observations)

        if not hypotheses:
            logger.warning("가설을 생성할 수 없습니다")
            return self._create_invalid_premise(observations, AbductivePattern.BEST_EXPLANATION)

        # 최선의 가설 선택
        best_hypothesis = self._select_best_hypothesis(observations, hypotheses)
        best_hypothesis_vector = self.logical_processor.encode_semantics(best_hypothesis)

        # 신뢰도 계산
        confidence = self._calculate_abductive_confidence(observations, hypotheses, best_hypothesis)

        # 설명력과 단순성 평가
        explanatory_power = self._evaluate_explanatory_power(observations, best_hypothesis)
        simplicity = self._evaluate_simplicity(best_hypothesis)

        semantic_vectors = {
            "observations": observation_vectors,
            "hypotheses": [self.logical_processor.encode_semantics(h) for h in hypotheses],
            "best_hypothesis": best_hypothesis_vector,
        }

        return AbductivePremise(
            observations=observations,
            hypotheses=hypotheses,
            best_hypothesis=best_hypothesis,
            pattern=AbductivePattern.BEST_EXPLANATION,
            confidence=confidence,
            explanatory_power=explanatory_power,
            simplicity=simplicity,
            semantic_vectors=semantic_vectors,
        )

    def _generate_hypotheses(self, observations: List[str]) -> List[str]:
        """가설들 생성"""
        hypotheses = []

        # 관찰들의 공통 패턴 분석
        common_patterns = self._analyze_common_patterns(observations)

        # 패턴 기반 가설 생성
        for pattern in common_patterns:
            hypothesis = self._create_pattern_based_hypothesis(pattern, observations)
            if hypothesis:
                hypotheses.append(hypothesis)

        # 인과관계 기반 가설 생성
        causal_hypotheses = self._create_causal_hypotheses(observations)
        hypotheses.extend(causal_hypotheses)

        # 일반적 가설 생성
        general_hypotheses = self._create_general_hypotheses(observations)
        hypotheses.extend(general_hypotheses)

        return list(set(hypotheses))  # 중복 제거

    def _analyze_common_patterns(self, observations: List[str]) -> List[Dict[str, Any]]:
        """공통 패턴 분석"""
        patterns = []

        # 단어 빈도 분석
        word_frequencies = {}
        for observation in observations:
            words = observation.split()
            for word in words:
                if len(word) > 2:
                    word_frequencies[word] = word_frequencies.get(word, 0) + 1

        # 빈도가 높은 단어들로 패턴 구성
        frequent_words = [word for word, freq in word_frequencies.items() if freq >= 2]

        for word in frequent_words:
            patterns.append(
                {
                    "type": "word_frequency",
                    "content": word,
                    "frequency": word_frequencies[word],
                }
            )

        return patterns

    def _create_pattern_based_hypothesis(
        self, pattern: Dict[str, Any], observations: List[str]
    ) -> Optional[str]:
        """패턴 기반 가설 생성"""
        if pattern["type"] == "word_frequency":
            word = pattern["content"]
            frequency = pattern["frequency"]

            if frequency >= len(observations) * 0.5:  # 50% 이상에서 나타나는 단어
                return f"{word}와 관련된 요인이 주요 원인일 수 있습니다."

        return None

    def _create_causal_hypotheses(self, observations: List[str]) -> List[str]:
        """인과관계 기반 가설 생성"""
        causal_hypotheses = []

        # 간단한 인과관계 가설 생성
        for observation in observations:
            # 시간적 순서나 조건적 관계를 찾아 가설 생성
            if "때문에" in observation or "로 인해" in observation:
                parts = (
                    observation.split("때문에")
                    if "때문에" in observation
                    else observation.split("로 인해")
                )
                if len(parts) > 1:
                    cause = parts[0].strip()
                    effect = parts[1].strip()
                    hypothesis = f"{cause}가 {effect}의 원인일 수 있습니다."
                    causal_hypotheses.append(hypothesis)

        return causal_hypotheses

    def _create_general_hypotheses(self, observations: List[str]) -> List[str]:
        """일반적 가설 생성"""
        general_hypotheses = []

        # 관찰의 특성에 따른 일반적 가설
        if len(observations) > 3:
            general_hypotheses.append("관찰된 현상들이 일정한 패턴을 따르고 있습니다.")

        # 관찰의 다양성에 따른 가설
        observation_lengths = [len(obs) for obs in observations]
        if max(observation_lengths) - min(observation_lengths) > 20:
            general_hypotheses.append("관찰된 현상들이 다양한 복잡성을 보이고 있습니다.")

        return general_hypotheses

    def _select_best_hypothesis(self, observations: List[str], hypotheses: List[str]) -> str:
        """최선의 가설 선택"""
        if not hypotheses:
            return "가설을 생성할 수 없습니다."

        # 각 가설의 점수 계산
        hypothesis_scores = []
        for hypothesis in hypotheses:
            score = self._calculate_hypothesis_score(observations, hypothesis)
            hypothesis_scores.append((hypothesis, score))

        # 점수가 가장 높은 가설 선택
        best_hypothesis = max(hypothesis_scores, key=lambda x: x[1])

        return best_hypothesis[0]

    def _calculate_hypothesis_score(self, observations: List[str], hypothesis: str) -> float:
        """가설 점수 계산"""
        score = 0.0

        # 1. 설명력 점수
        explanatory_score = self._evaluate_explanatory_power(observations, hypothesis)
        score += explanatory_score * 0.4

        # 2. 단순성 점수
        simplicity_score = self._evaluate_simplicity(hypothesis)
        score += simplicity_score * 0.3

        # 3. 일관성 점수
        consistency_score = self._evaluate_consistency(observations, hypothesis)
        score += consistency_score * 0.3

        return score

    def _evaluate_explanatory_power(self, observations: List[str], hypothesis: str) -> float:
        """설명력 평가"""
        if not observations or not hypothesis:
            return 0.0

        # 가설과 관찰들 간의 의미적 유사도 계산
        hypothesis_vector = self.logical_processor.encode_semantics(hypothesis)

        similarities = []
        for observation in observations:
            observation_vector = self.logical_processor.encode_semantics(observation)
            similarity = self.logical_processor.calculate_similarity(
                hypothesis_vector, observation_vector
            )
            similarities.append(similarity)

        # 평균 유사도를 설명력으로 사용
        explanatory_power = sum(similarities) / len(similarities) if similarities else 0.0

        return explanatory_power

    def _evaluate_simplicity(self, hypothesis: str) -> float:
        """단순성 평가"""
        if not hypothesis:
            return 0.0

        # 가설의 길이와 복잡성에 따른 단순성 평가
        length = len(hypothesis)

        # 길이가 짧을수록 단순성 높음
        if length < 20:
            simplicity = 1.0
        elif length < 50:
            simplicity = 0.8
        elif length < 100:
            simplicity = 0.6
        else:
            simplicity = 0.4

        # 복잡한 구문이나 조건이 많을수록 단순성 감소
        complex_indicators = ["만약", "그러나", "하지만", "또한", "또는", "그리고"]
        for indicator in complex_indicators:
            if indicator in hypothesis:
                simplicity *= 0.9

        return simplicity

    def _evaluate_consistency(self, observations: List[str], hypothesis: str) -> float:
        """일관성 평가"""
        if not observations or not hypothesis:
            return 0.0

        # 가설이 모든 관찰과 일관되는지 평가
        hypothesis_vector = self.logical_processor.encode_semantics(hypothesis)

        consistencies = []
        for observation in observations:
            observation_vector = self.logical_processor.encode_semantics(observation)
            similarity = self.logical_processor.calculate_similarity(
                hypothesis_vector, observation_vector
            )

            # 유사도가 높을수록 일관성 높음
            consistency = similarity
            consistencies.append(consistency)

        # 평균 일관성 반환
        return sum(consistencies) / len(consistencies) if consistencies else 0.0

    def _calculate_abductive_confidence(
        self, observations: List[str], hypotheses: List[str], best_hypothesis: str
    ) -> float:
        """가설적 추론 신뢰도 계산"""
        if not observations or not hypotheses:
            return 0.1

        # 기본 신뢰도
        base_confidence = 0.5

        # 관찰 수에 따른 조정
        observation_factor = min(1.0, len(observations) * 0.1)

        # 가설 수에 따른 조정
        hypothesis_factor = min(1.0, len(hypotheses) * 0.05)

        # 최선의 가설의 품질에 따른 조정
        best_hypothesis_score = self._calculate_hypothesis_score(observations, best_hypothesis)
        quality_factor = best_hypothesis_score

        # 최종 신뢰도 계산
        confidence = base_confidence * observation_factor * hypothesis_factor * quality_factor

        return min(confidence, 1.0)

    def construct_diagnostic_reasoning(self, symptoms: List[str]) -> AbductivePremise:
        """진단적 추론 구성"""
        logger.info(f"진단적 추론 구성 시작: {len(symptoms)}개 증상")

        # 증상들의 의미 벡터 인코딩
        symptom_vectors = []
        for symptom in symptoms:
            vector = self.logical_processor.encode_semantics(symptom)
            symptom_vectors.append(vector)

        # 가능한 진단들 생성
        diagnoses = self._generate_diagnoses(symptoms)

        if not diagnoses:
            logger.warning("진단을 생성할 수 없습니다")
            return self._create_invalid_premise(symptoms, AbductivePattern.DIAGNOSTIC_REASONING)

        # 최선의 진단 선택
        best_diagnosis = self._select_best_diagnosis(symptoms, diagnoses)
        best_diagnosis_vector = self.logical_processor.encode_semantics(best_diagnosis)

        # 신뢰도 계산
        confidence = self._calculate_diagnostic_confidence(symptoms, diagnoses, best_diagnosis)

        # 설명력과 단순성 평가
        explanatory_power = self._evaluate_explanatory_power(symptoms, best_diagnosis)
        simplicity = self._evaluate_simplicity(best_diagnosis)

        semantic_vectors = {
            "symptoms": symptom_vectors,
            "diagnoses": [self.logical_processor.encode_semantics(d) for d in diagnoses],
            "best_diagnosis": best_diagnosis_vector,
        }

        return AbductivePremise(
            observations=symptoms,
            hypotheses=diagnoses,
            best_hypothesis=best_diagnosis,
            pattern=AbductivePattern.DIAGNOSTIC_REASONING,
            confidence=confidence,
            explanatory_power=explanatory_power,
            simplicity=simplicity,
            semantic_vectors=semantic_vectors,
        )

    def _generate_diagnoses(self, symptoms: List[str]) -> List[str]:
        """진단들 생성"""
        diagnoses = []

        # 증상 패턴 분석
        symptom_patterns = self._analyze_symptom_patterns(symptoms)

        # 패턴 기반 진단 생성
        for pattern in symptom_patterns:
            diagnosis = self._create_pattern_based_diagnosis(pattern, symptoms)
            if diagnosis:
                diagnoses.append(diagnosis)

        # 일반적 진단 생성
        general_diagnoses = self._create_general_diagnoses(symptoms)
        diagnoses.extend(general_diagnoses)

        return list(set(diagnoses))

    def _analyze_symptom_patterns(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """증상 패턴 분석"""
        patterns = []

        # 증상의 특성 분석
        for symptom in symptoms:
            if "통증" in symptom or "아프다" in symptom:
                patterns.append({"type": "pain", "content": symptom})
            elif "열" in symptom or "발열" in symptom:
                patterns.append({"type": "fever", "content": symptom})
            elif "피로" in symptom or "무력" in symptom:
                patterns.append({"type": "fatigue", "content": symptom})

        return patterns

    def _create_pattern_based_diagnosis(
        self, pattern: Dict[str, Any], symptoms: List[str]
    ) -> Optional[str]:
        """패턴 기반 진단 생성"""
        if pattern["type"] == "pain":
            return "통증 관련 질환이 의심됩니다."
        elif pattern["type"] == "fever":
            return "발열 관련 질환이 의심됩니다."
        elif pattern["type"] == "fatigue":
            return "피로 관련 질환이 의심됩니다."

        return None

    def _create_general_diagnoses(self, symptoms: List[str]) -> List[str]:
        """일반적 진단 생성"""
        general_diagnoses = []

        if len(symptoms) > 2:
            general_diagnoses.append("복합 증상이 나타나고 있어 종합적인 진단이 필요합니다.")

        if any("급성" in symptom for symptom in symptoms):
            general_diagnoses.append("급성 질환이 의심됩니다.")

        if any("만성" in symptom for symptom in symptoms):
            general_diagnoses.append("만성 질환이 의심됩니다.")

        return general_diagnoses

    def _select_best_diagnosis(self, symptoms: List[str], diagnoses: List[str]) -> str:
        """최선의 진단 선택"""
        if not diagnoses:
            return "진단을 생성할 수 없습니다."

        # 각 진단의 점수 계산
        diagnosis_scores = []
        for diagnosis in diagnoses:
            score = self._calculate_diagnosis_score(symptoms, diagnosis)
            diagnosis_scores.append((diagnosis, score))

        # 점수가 가장 높은 진단 선택
        best_diagnosis = max(diagnosis_scores, key=lambda x: x[1])

        return best_diagnosis[0]

    def _calculate_diagnosis_score(self, symptoms: List[str], diagnosis: str) -> float:
        """진단 점수 계산"""
        score = 0.0

        # 1. 증상 설명력
        explanatory_score = self._evaluate_explanatory_power(symptoms, diagnosis)
        score += explanatory_score * 0.5

        # 2. 진단의 구체성
        specificity_score = self._evaluate_specificity(diagnosis)
        score += specificity_score * 0.3

        # 3. 진단의 가능성
        probability_score = self._evaluate_probability(diagnosis)
        score += probability_score * 0.2

        return score

    def _evaluate_specificity(self, diagnosis: str) -> float:
        """진단의 구체성 평가"""
        if not diagnosis:
            return 0.0

        # 구체적인 진단일수록 높은 점수
        specific_indicators = ["질환", "증후군", "염증", "감염", "종양"]
        specificity_score = 0.5  # 기본 점수

        for indicator in specific_indicators:
            if indicator in diagnosis:
                specificity_score += 0.1

        return min(specificity_score, 1.0)

    def _evaluate_probability(self, diagnosis: str) -> float:
        """진단의 가능성 평가"""
        if not diagnosis:
            return 0.0

        # 일반적인 진단일수록 높은 가능성
        probability_score = 0.7  # 기본 점수

        # 특정 질환명이 언급되면 가능성 조정
        if "의심" in diagnosis:
            probability_score *= 0.8
        elif "확실" in diagnosis:
            probability_score *= 1.2

        return min(probability_score, 1.0)

    def _calculate_diagnostic_confidence(
        self, symptoms: List[str], diagnoses: List[str], best_diagnosis: str
    ) -> float:
        """진단적 추론 신뢰도 계산"""
        if not symptoms or not diagnoses:
            return 0.1

        # 기본 신뢰도
        base_confidence = 0.6

        # 증상 수에 따른 조정
        symptom_factor = min(1.0, len(symptoms) * 0.1)

        # 진단 수에 따른 조정
        diagnosis_factor = min(1.0, len(diagnoses) * 0.05)

        # 최선의 진단의 품질에 따른 조정
        best_diagnosis_score = self._calculate_diagnosis_score(symptoms, best_diagnosis)
        quality_factor = best_diagnosis_score

        # 최종 신뢰도 계산
        confidence = base_confidence * symptom_factor * diagnosis_factor * quality_factor

        return min(confidence, 1.0)

    def _create_invalid_premise(
        self, observations: List[str], pattern: AbductivePattern
    ) -> AbductivePremise:
        """유효하지 않은 전제 생성"""
        return AbductivePremise(
            observations=observations,
            hypotheses=[],
            best_hypothesis="가설을 생성할 수 없습니다.",
            pattern=pattern,
            confidence=0.1,
            explanatory_power=0.1,
            simplicity=0.1,
            semantic_vectors={},
        )
