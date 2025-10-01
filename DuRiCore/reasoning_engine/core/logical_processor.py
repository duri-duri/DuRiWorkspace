#!/usr/bin/env python3
"""
DuRi 논리적 추론 엔진 - 논리 처리 핵심 모듈
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

from dataclasses import dataclass
from enum import Enum
import logging
import re
import statistics
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class PremiseType(Enum):
    """전제 유형"""

    UNIVERSAL_PRINCIPLE = "universal_principle"
    PARTICULAR_FACT = "particular_fact"
    CONDITIONAL = "conditional"
    NORMATIVE = "normative"
    EMPIRICAL = "empirical"
    CONTEXTUAL = "contextual"
    EXPERIENTIAL = "experiential"
    INTUITIVE = "intuitive"


class InferenceType(Enum):
    """추론 유형"""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    DIALECTICAL = "dialectical"
    CRITICAL = "critical"


@dataclass
class SemanticPremise:
    """의미 벡터 기반 전제"""

    premise_type: PremiseType
    content: str
    semantic_vector: np.ndarray
    justification: str
    strength: float  # 0.0-1.0
    source: str
    context_elements: Dict[str, Any]
    confidence: float


@dataclass
class LogicalStep:
    """논리적 단계"""

    step_number: int
    premise_references: List[int]
    inference_type: InferenceType
    conclusion: str
    semantic_vector: np.ndarray
    justification: str
    confidence: float
    logical_strength: float


class LogicalProcessor:
    """논리 처리 핵심 클래스"""

    def __init__(self, vector_dimension: int = 100):
        """논리 처리기 초기화"""
        self.vector_dimension = vector_dimension
        self.semantic_frames = self._initialize_semantic_frames()
        self.logical_rules = self._initialize_logical_rules()
        logger.info("논리 처리기 초기화 완료")

    def _initialize_semantic_frames(self) -> Dict[str, np.ndarray]:
        """의미 프레임 초기화"""
        frames = {
            "ethical": np.random.randn(self.vector_dimension),
            "practical": np.random.randn(self.vector_dimension),
            "logical": np.random.randn(self.vector_dimension),
            "emotional": np.random.randn(self.vector_dimension),
            "social": np.random.randn(self.vector_dimension),
            "individual": np.random.randn(self.vector_dimension),
            "universal": np.random.randn(self.vector_dimension),
            "particular": np.random.randn(self.vector_dimension),
            "conditional": np.random.randn(self.vector_dimension),
            "normative": np.random.randn(self.vector_dimension),
        }

        # 정규화
        for key in frames:
            frames[key] = self._normalize_vector(frames[key])

        return frames

    def _initialize_logical_rules(self) -> Dict[str, Dict[str, Any]]:
        """논리 규칙 초기화"""
        return {
            "deductive": {
                "strength_multiplier": 1.2,
                "confidence_threshold": 0.8,
                "premise_requirements": ["universal_principle", "particular_fact"],
            },
            "inductive": {
                "strength_multiplier": 0.9,
                "confidence_threshold": 0.6,
                "premise_requirements": ["empirical", "particular_fact"],
            },
            "abductive": {
                "strength_multiplier": 0.8,
                "confidence_threshold": 0.7,
                "premise_requirements": ["conditional", "particular_fact"],
            },
        }

    def encode_semantics(self, text: str) -> np.ndarray:
        """텍스트를 의미 벡터로 인코딩"""
        # 간단한 키워드 기반 인코딩 (실제로는 더 복잡한 NLP 모델 사용)
        keywords = self._extract_semantic_keywords(text)
        vector = np.zeros(self.vector_dimension)

        for keyword, weight in keywords.items():
            if keyword in self.semantic_frames:
                vector += weight * self.semantic_frames[keyword]

        return self._normalize_vector(vector)

    def _extract_semantic_keywords(self, text: str) -> Dict[str, float]:
        """의미 키워드 추출"""
        keywords = {}
        text_lower = text.lower()

        # 윤리적 키워드
        ethical_words = ["윤리", "도덕", "선", "악", "옳음", "그름", "의무", "권리"]
        for word in ethical_words:
            if word in text_lower:
                keywords["ethical"] = keywords.get("ethical", 0) + 0.3

        # 실용적 키워드
        practical_words = ["실용", "효과", "결과", "성과", "이익", "손실"]
        for word in practical_words:
            if word in text_lower:
                keywords["practical"] = keywords.get("practical", 0) + 0.3

        # 논리적 키워드
        logical_words = ["논리", "추론", "결론", "전제", "증명", "분석"]
        for word in logical_words:
            if word in text_lower:
                keywords["logical"] = keywords.get("logical", 0) + 0.3

        # 감정적 키워드
        emotional_words = ["감정", "느낌", "기분", "사랑", "분노", "기쁨"]
        for word in emotional_words:
            if word in text_lower:
                keywords["emotional"] = keywords.get("emotional", 0) + 0.3

        return keywords

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """벡터 정규화"""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector

    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """벡터 간 유사도 계산"""
        return np.dot(vector1, vector2)

    def construct_premises(self, situation: str, action: str) -> List[SemanticPremise]:
        """상황과 행동에서 전제 구성"""
        situation_vector = self.encode_semantics(situation)
        action_vector = self.encode_semantics(action)

        premises = []

        # 상황 기반 전제
        premises.append(
            SemanticPremise(
                premise_type=PremiseType.PARTICULAR_FACT,
                content=f"상황: {situation}",
                semantic_vector=situation_vector,
                justification="주어진 상황에 대한 사실",
                strength=0.8,
                source="situation_analysis",
                context_elements={"type": "situation"},
                confidence=0.9,
            )
        )

        # 행동 기반 전제
        premises.append(
            SemanticPremise(
                premise_type=PremiseType.PARTICULAR_FACT,
                content=f"행동: {action}",
                semantic_vector=action_vector,
                justification="제안된 행동에 대한 사실",
                strength=0.8,
                source="action_analysis",
                context_elements={"type": "action"},
                confidence=0.9,
            )
        )

        return premises

    def calculate_logical_consistency(
        self, premises: List[SemanticPremise], steps: List[LogicalStep]
    ) -> float:
        """논리적 일관성 계산"""
        if not premises or not steps:
            return 0.0

        # 전제 간 일관성
        premise_consistency = 0.0
        premise_count = 0

        for i in range(len(premises)):
            for j in range(i + 1, len(premises)):
                similarity = self.calculate_similarity(
                    premises[i].semantic_vector, premises[j].semantic_vector
                )
                premise_consistency += similarity
                premise_count += 1

        if premise_count > 0:
            premise_consistency /= premise_count

        # 단계 간 일관성
        step_consistency = 0.0
        step_count = 0

        for i in range(len(steps)):
            for j in range(i + 1, len(steps)):
                similarity = self.calculate_similarity(
                    steps[i].semantic_vector, steps[j].semantic_vector
                )
                step_consistency += similarity
                step_count += 1

        if step_count > 0:
            step_consistency /= step_count

        # 전체 일관성 (전제와 단계의 가중 평균)
        total_consistency = premise_consistency * 0.4 + step_consistency * 0.6

        return max(0.0, min(1.0, total_consistency))

    def get_premise_type_weight(self, premise_type: PremiseType) -> float:
        """전제 유형별 가중치 반환"""
        weights = {
            PremiseType.UNIVERSAL_PRINCIPLE: 1.0,
            PremiseType.PARTICULAR_FACT: 0.8,
            PremiseType.CONDITIONAL: 0.7,
            PremiseType.NORMATIVE: 0.9,
            PremiseType.EMPIRICAL: 0.8,
            PremiseType.CONTEXTUAL: 0.6,
            PremiseType.EXPERIENTIAL: 0.5,
            PremiseType.INTUITIVE: 0.4,
        }
        return weights.get(premise_type, 0.5)
