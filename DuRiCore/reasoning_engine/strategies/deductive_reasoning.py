#!/usr/bin/env python3
"""
DuRi 추론 엔진 - 연역적 추론 전략
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..core.logical_processor import (InferenceType, LogicalProcessor,
                                      LogicalStep, PremiseType,
                                      SemanticPremise)

logger = logging.getLogger(__name__)


class DeductivePattern(Enum):
    """연역적 추론 패턴"""

    SYLLOGISM = "syllogism"
    MODUS_PONENS = "modus_ponens"
    MODUS_TOLLENS = "modus_tollens"
    HYPOTHETICAL_SYLLOGISM = "hypothetical_syllogism"
    DISJUNCTIVE_SYLLOGISM = "disjunctive_syllogism"
    CONSTRUCTIVE_DILEMMA = "constructive_dilemma"
    DESTRUCTIVE_DILEMMA = "destructive_dilemma"


@dataclass
class DeductivePremise:
    """연역적 전제"""

    major_premise: str
    minor_premise: str
    conclusion: str
    pattern: DeductivePattern
    validity: float
    soundness: float
    semantic_vectors: Dict[str, np.ndarray]


class DeductiveReasoning:
    """연역적 추론 전략 클래스"""

    def __init__(self, logical_processor: LogicalProcessor):
        """연역적 추론 초기화"""
        self.logical_processor = logical_processor
        self.deductive_patterns = self._initialize_deductive_patterns()
        logger.info("연역적 추론 전략 초기화 완료")

    def _initialize_deductive_patterns(self) -> Dict[DeductivePattern, Dict[str, Any]]:
        """연역적 추론 패턴 초기화"""
        return {
            DeductivePattern.SYLLOGISM: {
                "structure": ["major_premise", "minor_premise", "conclusion"],
                "validity_rules": [
                    "middle_term_distribution",
                    "term_distribution",
                    "negative_premises",
                ],
                "strength_multiplier": 1.0,
            },
            DeductivePattern.MODUS_PONENS: {
                "structure": ["conditional", "antecedent", "consequent"],
                "validity_rules": ["conditional_validity", "antecedent_truth"],
                "strength_multiplier": 1.2,
            },
            DeductivePattern.MODUS_TOLLENS: {
                "structure": [
                    "conditional",
                    "negated_consequent",
                    "negated_antecedent",
                ],
                "validity_rules": ["conditional_validity", "consequent_falsity"],
                "strength_multiplier": 1.1,
            },
            DeductivePattern.HYPOTHETICAL_SYLLOGISM: {
                "structure": ["conditional_1", "conditional_2", "conclusion"],
                "validity_rules": ["chain_validity", "antecedent_consequent_chain"],
                "strength_multiplier": 1.0,
            },
            DeductivePattern.DISJUNCTIVE_SYLLOGISM: {
                "structure": ["disjunction", "negated_disjunct", "other_disjunct"],
                "validity_rules": ["disjunction_validity", "exclusive_disjunction"],
                "strength_multiplier": 0.9,
            },
        }

    def construct_syllogism(
        self, major_premise: str, minor_premise: str
    ) -> DeductivePremise:
        """삼단논법 구성"""
        logger.info("삼단논법 구성 시작")

        # 전제들의 의미 벡터 인코딩
        major_vector = self.logical_processor.encode_semantics(major_premise)
        minor_vector = self.logical_processor.encode_semantics(minor_premise)

        # 결론 도출
        conclusion = self._derive_syllogistic_conclusion(major_premise, minor_premise)
        conclusion_vector = self.logical_processor.encode_semantics(conclusion)

        # 유효성 검증
        validity = self._validate_syllogism(major_premise, minor_premise, conclusion)

        # 건전성 평가
        soundness = self._evaluate_syllogistic_soundness(
            major_premise, minor_premise, conclusion
        )

        semantic_vectors = {
            "major_premise": major_vector,
            "minor_premise": minor_vector,
            "conclusion": conclusion_vector,
        }

        return DeductivePremise(
            major_premise=major_premise,
            minor_premise=minor_premise,
            conclusion=conclusion,
            pattern=DeductivePattern.SYLLOGISM,
            validity=validity,
            soundness=soundness,
            semantic_vectors=semantic_vectors,
        )

    def _derive_syllogistic_conclusion(
        self, major_premise: str, minor_premise: str
    ) -> str:
        """삼단논법 결론 도출"""
        # 간단한 규칙 기반 결론 도출
        major_terms = self._extract_terms(major_premise)
        minor_terms = self._extract_terms(minor_premise)

        if len(major_terms) >= 2 and len(minor_terms) >= 2:
            # 중간항 찾기
            middle_term = self._find_middle_term(major_terms, minor_terms)
            if middle_term:
                # 결론 구성
                subject = self._get_subject_term(major_terms, minor_terms, middle_term)
                predicate = self._get_predicate_term(
                    major_terms, minor_terms, middle_term
                )

                if subject and predicate:
                    return f"{subject}는 {predicate}입니다."

        return "결론을 도출할 수 없습니다."

    def _extract_terms(self, premise: str) -> List[str]:
        """전제에서 용어 추출"""
        # 간단한 용어 추출 로직
        terms = []
        words = premise.split()

        # 주요 명사와 형용사 추출
        for word in words:
            if len(word) > 2 and word.isalpha():
                terms.append(word)

        return terms

    def _find_middle_term(
        self, major_terms: List[str], minor_terms: List[str]
    ) -> Optional[str]:
        """중간항 찾기"""
        for term in major_terms:
            if term in minor_terms:
                return term
        return None

    def _get_subject_term(
        self, major_terms: List[str], minor_terms: List[str], middle_term: str
    ) -> Optional[str]:
        """주어 용어 찾기"""
        for term in minor_terms:
            if term != middle_term:
                return term
        return None

    def _get_predicate_term(
        self, major_terms: List[str], minor_terms: List[str], middle_term: str
    ) -> Optional[str]:
        """술어 용어 찾기"""
        for term in major_terms:
            if term != middle_term:
                return term
        return None

    def _validate_syllogism(
        self, major_premise: str, minor_premise: str, conclusion: str
    ) -> float:
        """삼단논법 유효성 검증"""
        # 기본적인 유효성 검증 규칙들
        validity_score = 1.0

        # 1. 중간항 분포 검증
        if not self._check_middle_term_distribution(major_premise, minor_premise):
            validity_score *= 0.7

        # 2. 용어 분포 검증
        if not self._check_term_distribution(major_premise, minor_premise, conclusion):
            validity_score *= 0.8

        # 3. 부정 전제 검증
        if self._has_negative_premises(major_premise, minor_premise):
            validity_score *= 0.9

        return validity_score

    def _check_middle_term_distribution(
        self, major_premise: str, minor_premise: str
    ) -> bool:
        """중간항 분포 검증"""
        # 간단한 중간항 분포 검증
        major_terms = self._extract_terms(major_premise)
        minor_terms = self._extract_terms(minor_premise)

        middle_term = self._find_middle_term(major_terms, minor_terms)
        if middle_term:
            # 중간항이 두 전제에 모두 나타나는지 확인
            return middle_term in major_terms and middle_term in minor_terms

        return False

    def _check_term_distribution(
        self, major_premise: str, minor_premise: str, conclusion: str
    ) -> bool:
        """용어 분포 검증"""
        # 간단한 용어 분포 검증
        major_terms = self._extract_terms(major_premise)
        minor_terms = self._extract_terms(minor_premise)
        conclusion_terms = self._extract_terms(conclusion)

        # 결론의 용어들이 전제들에 나타나는지 확인
        all_premise_terms = set(major_terms + minor_terms)
        for term in conclusion_terms:
            if term not in all_premise_terms:
                return False

        return True

    def _has_negative_premises(self, major_premise: str, minor_premise: str) -> bool:
        """부정 전제 확인"""
        negative_words = ["아니다", "아니", "없다", "않다", "못하다", "하지 않다"]

        for word in negative_words:
            if word in major_premise or word in minor_premise:
                return True

        return False

    def _evaluate_syllogistic_soundness(
        self, major_premise: str, minor_premise: str, conclusion: str
    ) -> float:
        """삼단논법 건전성 평가"""
        # 건전성은 전제의 진리성과 결론의 진리성을 평가
        soundness_score = 1.0

        # 전제의 신뢰도 평가
        major_confidence = self._evaluate_premise_confidence(major_premise)
        minor_confidence = self._evaluate_premise_confidence(minor_premise)

        # 평균 신뢰도 계산
        average_confidence = (major_confidence + minor_confidence) / 2
        soundness_score *= average_confidence

        return soundness_score

    def _evaluate_premise_confidence(self, premise: str) -> float:
        """전제 신뢰도 평가"""
        # 간단한 신뢰도 평가 로직
        confidence = 0.8  # 기본 신뢰도

        # 전제의 길이와 복잡성에 따른 조정
        if len(premise) > 50:
            confidence *= 0.9  # 긴 전제는 신뢰도 감소

        # 부정적 표현이 있으면 신뢰도 감소
        if self._has_negative_premises(premise, ""):
            confidence *= 0.95

        return confidence

    def apply_modus_ponens(self, conditional: str, antecedent: str) -> Optional[str]:
        """가언적 삼단논법 적용"""
        logger.info("가언적 삼단논법 적용")

        # 조건문과 전건이 주어졌을 때 후건 도출
        if self._validate_conditional(conditional, antecedent):
            consequent = self._extract_consequent(conditional)
            if consequent:
                return consequent

        return None

    def _validate_conditional(self, conditional: str, antecedent: str) -> bool:
        """조건문 유효성 검증"""
        # 조건문과 전건의 일치성 검증
        antecedent_terms = self._extract_terms(antecedent)
        conditional_terms = self._extract_terms(conditional)

        # 전건이 조건문에 포함되는지 확인
        for term in antecedent_terms:
            if term in conditional_terms:
                return True

        return False

    def _extract_consequent(self, conditional: str) -> Optional[str]:
        """조건문에서 후건 추출"""
        # 간단한 후건 추출 로직
        if "이면" in conditional:
            parts = conditional.split("이면")
            if len(parts) > 1:
                return parts[1].strip()
        elif "면" in conditional:
            parts = conditional.split("면")
            if len(parts) > 1:
                return parts[1].strip()

        return None
