#!/usr/bin/env python3
"""
DuRi 논리적 추론 엔진 (Phase 1-2 Week 2)
문자열 기반 논증 → 의미 벡터 기반 논리적 추론으로 전환
"""

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import json
import logging
import random
import re
import statistics
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """논증 유형 - Day 1 확장"""

    KANTIAN = "kantian"
    UTILITARIAN = "utilitarian"
    VIRTUE_ETHICS = "virtue_ethics"
    DEONTOLOGICAL = "deontological"
    CONSEQUENTIALIST = "consequentialist"
    HYBRID = "hybrid"
    # Day 1: 새로운 논증 유형 추가
    PRAGMATIC = "pragmatic"
    CONSTRUCTIVIST = "constructivist"
    CRITICAL = "critical"


class PremiseType(Enum):
    """전제 유형 - Day 1 확장"""

    UNIVERSAL_PRINCIPLE = "universal_principle"
    PARTICULAR_FACT = "particular_fact"
    CONDITIONAL = "conditional"
    NORMATIVE = "normative"
    EMPIRICAL = "empirical"
    # Day 1: 새로운 전제 유형 추가
    CONTEXTUAL = "contextual"
    EXPERIENTIAL = "experiential"
    INTUITIVE = "intuitive"


class InferenceType(Enum):
    """추론 유형 - Day 3 확장"""

    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    DIALECTICAL = "dialectical"
    CRITICAL = "critical"  # Day 3: 비판적 추론 추가


@dataclass
class SemanticPremise:
    """의미 벡터 기반 전제 - Day 1 신규"""

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
    """논리적 단계 - Day 1 개선"""

    step_number: int
    premise_references: List[int]
    inference_type: InferenceType
    conclusion: str
    semantic_vector: np.ndarray  # Day 1: 의미 벡터 추가
    justification: str
    confidence: float
    logical_strength: float  # Day 1: 논리적 강도 추가


@dataclass
class LogicalArgument:
    """논리적 논증 - Day 1 개선"""

    reasoning_type: ReasoningType
    premises: List[SemanticPremise]
    logical_steps: List[LogicalStep]
    final_conclusion: str
    semantic_vector: np.ndarray  # Day 1: 의미 벡터 추가
    strength: float
    counter_arguments: List[str]
    limitations: List[str]
    confidence: float  # Day 1: 전체 신뢰도 추가
    reasoning_path: List[str]  # Day 1: 추론 경로 추가


@dataclass
class MultiPerspectiveAnalysis:
    """다중 관점 분석 결과 - Day 4 신규"""

    perspectives: List[LogicalArgument]
    perspective_similarities: Dict[Tuple[ReasoningType, ReasoningType], float]
    conflicts: List[Dict[str, Any]]
    integrated_conclusion: str
    integrated_strength: float
    integrated_confidence: float
    perspective_weights: Dict[ReasoningType, float]
    conflict_resolution_strategy: str


@dataclass
class PerspectiveConflict:
    """관점 간 충돌 - Day 4 신규"""

    perspective1: ReasoningType
    perspective2: ReasoningType
    conflict_type: str
    conflict_description: str
    severity: float  # 0.0-1.0
    resolution_strategy: str
    resolution_confidence: float


@dataclass
class IntegratedConclusion:
    """통합적 결론 - Day 4 신규"""

    conclusion: str
    supporting_perspectives: List[ReasoningType]
    opposing_perspectives: List[ReasoningType]
    overall_strength: float
    overall_confidence: float
    integration_method: str
    reasoning_summary: str


@dataclass
class PerformanceMetrics:
    """성능 메트릭 - Day 5 신규"""

    execution_time: float
    memory_usage: float
    cpu_usage: float
    cache_hit_rate: float
    throughput: float  # 처리량 (요청/초)


@dataclass
class TestResult:
    """테스트 결과 - Day 5 신규"""

    test_name: str
    success: bool
    execution_time: float
    accuracy: float
    confidence: float
    error_message: Optional[str] = None
    performance_metrics: Optional[PerformanceMetrics] = None


@dataclass
class ValidationResult:
    """검증 결과 - Day 5 신규"""

    scenario_name: str
    expected_outcome: str
    actual_outcome: str
    accuracy_score: float
    confidence_score: float
    reasoning_quality: float
    overall_score: float


@dataclass
class SystemHealth:
    """시스템 건강도 - Day 5 신규"""

    overall_health: float  # 0.0-1.0
    performance_health: float
    accuracy_health: float
    reliability_health: float
    recommendations: List[str]


class TestScenario(Enum):
    """테스트 시나리오 - Day 5 신규"""

    ETHICAL_DILEMMA = "ethical_dilemma"
    PRACTICAL_DECISION = "practical_decision"
    LOGICAL_CONTRADICTION = "logical_contradiction"
    COMPLEX_SITUATION = "complex_situation"
    EDGE_CASE = "edge_case"
    PERFORMANCE_STRESS = "performance_stress"


class LogicalReasoningEngine:
    """논리적 추론 엔진 - Day 1 신규"""

    def __init__(self, vector_dimension: int = 100):
        self.vector_dimension = vector_dimension
        self.reasoning_patterns = self._initialize_reasoning_patterns()
        self.semantic_frames = self._initialize_semantic_frames()
        self.logical_rules = self._initialize_logical_rules()
        # Day 2: 캐싱 시스템 추가
        self.vector_cache = {}
        self.keyword_cache = {}
        self.similarity_cache = {}
        self.max_cache_size = 1000  # Day 2: 캐시 크기 제한

        # Day 5: 성능 최적화 추가
        self.performance_metrics = {
            "total_analyses": 0,
            "average_processing_time": 0.0,
            "cache_hit_rate": 0.0,
            "memory_usage": 0.0,
        }
        self.start_time = None
        self.cache_hits = 0
        self.cache_misses = 0

    def _initialize_reasoning_patterns(self) -> Dict[ReasoningType, np.ndarray]:
        """추론 패턴 초기화 - Day 3 철학적 논증 패턴 확장"""
        patterns = {}

        # Day 3: 칸트적 추론 패턴 (정언명령 기반)
        kantian_pattern = np.zeros(self.vector_dimension)
        kantian_pattern[0:20] = 1.0  # 보편적 원칙 (강함)
        kantian_pattern[20:40] = 0.9  # 의무론적 요소
        kantian_pattern[40:60] = 0.8  # 자율성 요소
        kantian_pattern[60:80] = 0.7  # 목적론적 요소
        kantian_pattern[80:100] = 0.9  # 정언명령 요소
        patterns[ReasoningType.KANTIAN] = kantian_pattern

        # Day 3: 공리주의 추론 패턴 (최대 행복 원칙)
        utilitarian_pattern = np.zeros(self.vector_dimension)
        utilitarian_pattern[0:20] = 0.3  # 보편적 원칙 (약함)
        utilitarian_pattern[20:40] = 0.2  # 의무론적 요소
        utilitarian_pattern[40:60] = 0.6  # 자율성 요소
        utilitarian_pattern[60:80] = 1.0  # 목적론적 요소 (강함)
        utilitarian_pattern[80:100] = 0.8  # 결과론적 요소
        patterns[ReasoningType.UTILITARIAN] = utilitarian_pattern

        # Day 3: 덕윤리 추론 패턴 (덕성 기반)
        virtue_pattern = np.zeros(self.vector_dimension)
        virtue_pattern[0:20] = 0.7  # 보편적 원칙
        virtue_pattern[20:40] = 0.8  # 의무론적 요소
        virtue_pattern[40:60] = 1.0  # 자율성 요소 (강함)
        virtue_pattern[60:80] = 0.6  # 목적론적 요소
        virtue_pattern[80:100] = 0.7  # 덕성 요소
        patterns[ReasoningType.VIRTUE_ETHICS] = virtue_pattern

        # Day 3: 실용주의 추론 패턴 (실용성 기반)
        pragmatic_pattern = np.zeros(self.vector_dimension)
        pragmatic_pattern[0:20] = 0.4  # 보편적 원칙
        pragmatic_pattern[20:40] = 0.3  # 의무론적 요소
        pragmatic_pattern[40:60] = 0.7  # 자율성 요소
        pragmatic_pattern[60:80] = 0.9  # 목적론적 요소
        pragmatic_pattern[80:100] = 1.0  # 실용적 요소 (강함)
        patterns[ReasoningType.PRAGMATIC] = pragmatic_pattern

        # Day 3: 구성주의 추론 패턴 (구성적 합리성)
        constructivist_pattern = np.zeros(self.vector_dimension)
        constructivist_pattern[0:20] = 0.6  # 보편적 원칙
        constructivist_pattern[20:40] = 0.5  # 의무론적 요소
        constructivist_pattern[40:60] = 0.8  # 자율성 요소
        constructivist_pattern[60:80] = 0.7  # 목적론적 요소
        constructivist_pattern[80:100] = 0.9  # 구성적 요소 (강함)
        patterns[ReasoningType.CONSTRUCTIVIST] = constructivist_pattern

        # Day 3: 비판적 추론 패턴 (비판적 사고)
        critical_pattern = np.zeros(self.vector_dimension)
        critical_pattern[0:20] = 0.5  # 보편적 원칙
        critical_pattern[20:40] = 0.4  # 의무론적 요소
        critical_pattern[40:60] = 0.9  # 자율성 요소 (강함)
        critical_pattern[60:80] = 0.6  # 목적론적 요소
        critical_pattern[80:100] = 0.8  # 비판적 요소
        patterns[ReasoningType.CRITICAL] = critical_pattern

        return patterns

    def _initialize_semantic_frames(self) -> Dict[str, np.ndarray]:
        """의미 프레임 초기화 - Day 1 신규"""
        frames = {}

        # 윤리적 프레임
        ethical_frame = np.zeros(self.vector_dimension)
        ethical_frame[0:25] = 1.0  # 윤리적 요소
        ethical_frame[25:50] = 0.8  # 도덕적 요소
        ethical_frame[50:75] = 0.6  # 규범적 요소
        ethical_frame[75:100] = 0.7  # 가치 요소
        frames["ethical"] = ethical_frame

        # 실용적 프레임
        practical_frame = np.zeros(self.vector_dimension)
        practical_frame[0:25] = 0.3  # 윤리적 요소
        practical_frame[25:50] = 0.2  # 도덕적 요소
        practical_frame[50:75] = 0.8  # 규범적 요소
        practical_frame[75:100] = 1.0  # 가치 요소 (강함)
        frames["practical"] = practical_frame

        # 논리적 프레임
        logical_frame = np.zeros(self.vector_dimension)
        logical_frame[0:25] = 0.5  # 윤리적 요소
        logical_frame[25:50] = 0.4  # 도덕적 요소
        logical_frame[50:75] = 1.0  # 규범적 요소 (강함)
        logical_frame[75:100] = 0.8  # 가치 요소
        frames["logical"] = logical_frame

        return frames

    def _initialize_logical_rules(self) -> Dict[str, Dict[str, Any]]:
        """논리적 규칙 초기화 - Day 1 신규"""
        rules = {
            "deductive": {
                "modus_ponens": "P → Q, P ⊢ Q",
                "modus_tollens": "P → Q, ¬Q ⊢ ¬P",
                "syllogism": "A → B, B → C ⊢ A → C",
            },
            "inductive": {
                "generalization": "P1, P2, ..., Pn ⊢ ∀x P(x)",
                "analogy": "A ≈ B, A has P ⊢ B has P",
                "causation": "A → B, A occurs ⊢ B likely occurs",
            },
            "abductive": {
                "inference_to_best_explanation": "Q, P → Q ⊢ P",
                "pattern_recognition": "Pattern P, Q fits P ⊢ Q",
                "hypothesis_formation": "Evidence E, H explains E ⊢ H",
            },
        }
        return rules

    async def analyze_logical_reasoning(
        self, situation: str, action: str
    ) -> LogicalArgument:
        """논리적 추론 분석 - Day 1 핵심 메서드"""
        logger.info(f"논리적 추론 분석 시작: {action}")

        # 1. 상황의 의미 벡터 인코딩
        situation_vector = self._encode_situation_semantics(situation)

        # 2. 행위의 의미 벡터 인코딩
        action_vector = self._encode_action_semantics(action)

        # 3. 적절한 추론 유형 선택
        reasoning_type = self._select_reasoning_type(situation_vector, action_vector)

        # 4. 의미 벡터 기반 전제 구성
        premises = self._construct_semantic_premises(
            situation_vector, action_vector, reasoning_type
        )

        # 5. 논리적 단계 구성
        logical_steps = self._construct_philosophical_argument(premises, reasoning_type)

        # 6. 최종 결론 도출
        final_conclusion = self._derive_final_conclusion(logical_steps, reasoning_type)

        # 7. 논증 강도 계산
        strength = self._calculate_argument_strength(
            premises, logical_steps, reasoning_type
        )

        # 8. 반론 및 한계 식별
        counter_arguments = self._identify_counter_arguments(
            premises, logical_steps, reasoning_type
        )
        limitations = self._identify_limitations(
            premises, logical_steps, reasoning_type
        )

        # 9. 전체 신뢰도 계산
        confidence = self._calculate_overall_confidence(
            premises, logical_steps, strength
        )

        # 10. 추론 경로 구성
        reasoning_path = self._construct_reasoning_path(logical_steps)

        return LogicalArgument(
            reasoning_type=reasoning_type,
            premises=premises,
            logical_steps=logical_steps,
            final_conclusion=final_conclusion,
            semantic_vector=situation_vector,
            strength=strength,
            counter_arguments=counter_arguments,
            limitations=limitations,
            confidence=confidence,
            reasoning_path=reasoning_path,
        )

    def _encode_situation_semantics(self, situation: str) -> np.ndarray:
        """상황의 의미 벡터 인코딩 - Day 2 고도화"""
        # Day 2: 더 정교한 의미 벡터 인코딩
        vector = np.zeros(self.vector_dimension)

        # Day 2: 확장된 키워드 기반 의미 추출
        keywords = self._extract_semantic_keywords(situation)

        # Day 2: 의미적 특성에 따른 벡터 구성 (더 세분화)
        for keyword, weight in keywords.items():
            # 윤리적 요소 (0-25)
            if any(
                ethical in keyword
                for ethical in [
                    "윤리",
                    "도덕",
                    "정의",
                    "공정",
                    "선",
                    "악",
                    "양심",
                    "책임",
                    "의무",
                    "권리",
                    "존엄",
                    "인격",
                    "자율",
                    "자유",
                    "평등",
                    "정직",
                    "신뢰",
                    "성실",
                    "용기",
                    "관용",
                    "배려",
                    "이타",
                ]
            ):
                vector[0:25] += weight * 0.9

            # 실용적 요소 (25-50)
            elif any(
                practical in keyword
                for practical in [
                    "효율",
                    "실용",
                    "효과",
                    "결과",
                    "성과",
                    "이익",
                    "손실",
                    "비용",
                    "수익",
                    "경제",
                    "자원",
                    "최적화",
                    "생산성",
                    "성능",
                    "효율성",
                    "실행",
                    "구현",
                    "적용",
                    "운영",
                    "관리",
                    "조직",
                    "시스템",
                    "프로세스",
                ]
            ):
                vector[25:50] += weight * 0.8

            # 논리적 요소 (50-75)
            elif any(
                logical in keyword
                for logical in [
                    "논리",
                    "이성",
                    "분석",
                    "추론",
                    "결론",
                    "전제",
                    "가정",
                    "증명",
                    "검증",
                    "검토",
                    "평가",
                    "판단",
                    "사고",
                    "이해",
                    "인식",
                    "지식",
                    "학습",
                    "연구",
                    "조사",
                    "탐구",
                    "의문",
                    "호기심",
                    "창의",
                ]
            ):
                vector[50:75] += weight * 0.8

            # 가치적 요소 (75-100)
            elif any(
                value in keyword
                for value in [
                    "가치",
                    "목적",
                    "의미",
                    "중요",
                    "필요",
                    "우선순위",
                    "목표",
                    "비전",
                    "미래",
                    "발전",
                    "성장",
                    "진보",
                    "혁신",
                    "변화",
                    "개선",
                    "향상",
                    "진화",
                    "전통",
                    "문화",
                    "사회",
                    "공동체",
                    "협력",
                ]
            ):
                vector[75:100] += weight * 0.7

        # Day 2: 갈등 요소 추가 처리
        conflict_keywords = [
            "갈등",
            "충돌",
            "대립",
            "반대",
            "분쟁",
            "투쟁",
            "경쟁",
            "대결",
            "적대",
            "적대감",
            "적대적",
            "반감",
            "불화",
            "불일치",
            "차이",
            "이견",
            "의견충돌",
            "의견분쟁",
        ]
        conflict_score = sum(
            weight
            for keyword, weight in keywords.items()
            if any(conflict in keyword for conflict in conflict_keywords)
        )
        if conflict_score > 0:
            vector[30:40] += conflict_score * 0.8  # 갈등 요소는 실용적 요소 영역에 추가

        # Day 2: 의사결정 요소 추가 처리
        decision_keywords = [
            "결정",
            "선택",
            "판단",
            "결심",
            "의사결정",
            "정책",
            "전략",
            "계획",
            "방안",
            "대안",
            "옵션",
            "방법",
            "수단",
            "도구",
            "기법",
            "기술",
            "접근",
            "방식",
        ]
        decision_score = sum(
            weight
            for keyword, weight in keywords.items()
            if any(decision in keyword for decision in decision_keywords)
        )
        if decision_score > 0:
            vector[45:55] += (
                decision_score * 0.7
            )  # 의사결정 요소는 논리적 요소 영역에 추가

        return self._normalize_vector(vector)

    def _encode_action_semantics(self, action: str) -> np.ndarray:
        """행위의 의미 벡터 인코딩 - Day 2 고도화"""
        # Day 2: 더 정교한 행위 의미 벡터 인코딩
        vector = np.zeros(self.vector_dimension)

        # Day 2: 확장된 키워드 기반 의미 추출
        keywords = self._extract_semantic_keywords(action)

        # Day 2: 행위의 특성에 따른 벡터 구성 (더 세분화)
        for keyword, weight in keywords.items():
            # 윤리적 행위 (0-25)
            if any(
                ethical in keyword
                for ethical in [
                    "거짓말",
                    "속임",
                    "기만",
                    "사기",
                    "부정",
                    "부패",
                    "비리",
                    "불법",
                    "위법",
                    "범죄",
                    "죄",
                    "악행",
                    "악랄",
                    "잔인",
                    "폭력",
                    "학대",
                    "차별",
                    "편견",
                    "혐오",
                ]
            ):
                vector[0:25] += weight * 0.9  # 윤리적 문제 행위
            elif any(
                ethical in keyword
                for ethical in [
                    "진실",
                    "정직",
                    "성실",
                    "신뢰",
                    "배려",
                    "관용",
                    "이타",
                    "봉사",
                    "기부",
                    "자선",
                    "구원",
                    "보호",
                    "지원",
                    "도움",
                    "협력",
                    "화해",
                    "용서",
                    "화합",
                ]
            ):
                vector[0:25] += weight * 0.8  # 윤리적 긍정 행위

            # 실용적 행위 (25-50)
            elif any(
                practical in keyword
                for practical in [
                    "희생",
                    "구원",
                    "보호",
                    "지원",
                    "도움",
                    "협력",
                    "화해",
                    "용서",
                    "화합",
                    "개발",
                    "건설",
                    "제작",
                    "생산",
                    "제공",
                    "서비스",
                    "관리",
                    "운영",
                    "유지",
                    "보수",
                    "개선",
                    "향상",
                    "발전",
                    "성장",
                ]
            ):
                vector[25:50] += weight * 0.8

            # 논리적 행위 (50-75)
            elif any(
                logical in keyword
                for logical in [
                    "분배",
                    "배분",
                    "분석",
                    "검토",
                    "평가",
                    "판단",
                    "결정",
                    "선택",
                    "계획",
                    "설계",
                    "구조화",
                    "체계화",
                    "정리",
                    "분류",
                    "정렬",
                    "조직",
                    "통합",
                    "통합",
                    "조정",
                    "조율",
                    "중재",
                    "해결",
                    "처리",
                ]
            ):
                vector[50:75] += weight * 0.7

            # 가치적 행위 (75-100)
            elif any(
                value in keyword
                for value in [
                    "효율",
                    "최적화",
                    "개선",
                    "향상",
                    "발전",
                    "성장",
                    "혁신",
                    "변화",
                    "진보",
                    "진화",
                    "창조",
                    "발명",
                    "발견",
                    "탐구",
                    "연구",
                    "학습",
                    "교육",
                    "훈련",
                    "육성",
                    "양성",
                    "육성",
                    "발전",
                ]
            ):
                vector[75:100] += weight * 0.8

        # Day 2: 특수 행위 패턴 추가 처리
        # 해고, 구조조정 등 부정적 행위
        negative_actions = [
            "해고",
            "구조조정",
            "폐업",
            "폐쇄",
            "중단",
            "중지",
            "취소",
            "철회",
            "거부",
            "반대",
            "거부",
            "거부",
            "거부",
        ]
        if any(
            action in keyword
            for keyword, weight in keywords.items()
            for action in negative_actions
        ):
            vector[20:30] += 0.6  # 부정적 행위는 윤리적 요소에 추가

        # 긍정적 행위
        positive_actions = [
            "채용",
            "확장",
            "개발",
            "투자",
            "지원",
            "후원",
            "기부",
            "봉사",
            "협력",
            "파트너십",
            "동맹",
            "연합",
            "통합",
        ]
        if any(
            action in keyword
            for keyword, weight in keywords.items()
            for action in positive_actions
        ):
            vector[25:35] += 0.7  # 긍정적 행위는 실용적 요소에 추가

        return self._normalize_vector(vector)

    def _extract_semantic_keywords(self, text: str) -> Dict[str, float]:
        """의미적 키워드 추출 - Day 2 고도화 (캐싱 포함)"""
        # Day 2: 캐싱 확인
        if text in self.keyword_cache:
            self._update_cache_stats("keyword_cache", True)
            return self.keyword_cache[text]

        self._update_cache_stats("keyword_cache", False)

        keywords = {}

        # Day 2: 확장된 윤리적 키워드
        ethical_keywords = {
            "윤리": 0.9,
            "도덕": 0.9,
            "정의": 0.8,
            "공정": 0.8,
            "선": 0.7,
            "악": 0.7,
            "옳음": 0.8,
            "그름": 0.8,
            "양심": 0.9,
            "책임": 0.7,
            "의무": 0.8,
            "권리": 0.7,
            "존엄": 0.9,
            "인격": 0.8,
            "자율": 0.8,
            "자유": 0.7,
            "평등": 0.8,
            "정직": 0.8,
            "신뢰": 0.7,
            "성실": 0.7,
            "용기": 0.6,
            "관용": 0.6,
            "배려": 0.7,
            "이타": 0.7,
        }

        # Day 2: 확장된 실용적 키워드
        practical_keywords = {
            "효율": 0.9,
            "실용": 0.8,
            "효과": 0.7,
            "결과": 0.7,
            "성과": 0.8,
            "이익": 0.8,
            "손실": 0.8,
            "비용": 0.7,
            "수익": 0.8,
            "경제": 0.7,
            "자원": 0.7,
            "최적화": 0.9,
            "생산성": 0.8,
            "성능": 0.7,
            "효율성": 0.9,
            "실행": 0.6,
            "구현": 0.6,
            "적용": 0.6,
            "운영": 0.6,
            "관리": 0.7,
            "조직": 0.6,
            "시스템": 0.6,
            "프로세스": 0.7,
        }

        # Day 2: 확장된 논리적 키워드
        logical_keywords = {
            "논리": 0.9,
            "이성": 0.8,
            "분석": 0.8,
            "추론": 0.9,
            "결론": 0.7,
            "전제": 0.8,
            "가정": 0.7,
            "증명": 0.8,
            "검증": 0.7,
            "검토": 0.6,
            "평가": 0.7,
            "판단": 0.7,
            "사고": 0.7,
            "이해": 0.6,
            "인식": 0.6,
            "지식": 0.6,
            "학습": 0.6,
            "연구": 0.6,
            "조사": 0.6,
            "탐구": 0.6,
            "의문": 0.5,
            "호기심": 0.5,
            "창의": 0.6,
        }

        # Day 2: 확장된 가치적 키워드
        value_keywords = {
            "가치": 0.9,
            "목적": 0.8,
            "의미": 0.8,
            "중요": 0.7,
            "필요": 0.7,
            "우선순위": 0.8,
            "목표": 0.7,
            "비전": 0.7,
            "미래": 0.6,
            "발전": 0.6,
            "성장": 0.6,
            "진보": 0.6,
            "혁신": 0.7,
            "변화": 0.6,
            "개선": 0.7,
            "향상": 0.6,
            "발전": 0.6,
            "진화": 0.6,
            "전통": 0.5,
            "문화": 0.5,
            "사회": 0.6,
            "공동체": 0.6,
            "협력": 0.6,
        }

        # Day 2: 확장된 갈등 관련 키워드
        conflict_keywords = {
            "갈등": 0.9,
            "충돌": 0.9,
            "대립": 0.8,
            "반대": 0.7,
            "분쟁": 0.8,
            "투쟁": 0.7,
            "경쟁": 0.7,
            "대결": 0.7,
            "적대": 0.8,
            "적대감": 0.8,
            "적대적": 0.8,
            "반감": 0.7,
            "불화": 0.7,
            "불일치": 0.7,
            "차이": 0.6,
            "이견": 0.6,
            "의견충돌": 0.8,
            "의견분쟁": 0.8,
        }

        # Day 2: 확장된 의사결정 키워드
        decision_keywords = {
            "결정": 0.9,
            "선택": 0.8,
            "판단": 0.8,
            "결심": 0.7,
            "의사결정": 0.9,
            "정책": 0.7,
            "전략": 0.7,
            "계획": 0.6,
            "방안": 0.6,
            "대안": 0.7,
            "옵션": 0.6,
            "방법": 0.6,
            "수단": 0.6,
            "도구": 0.5,
            "기법": 0.5,
            "기술": 0.5,
            "접근": 0.6,
            "방식": 0.6,
        }

        # Day 2: 모든 키워드 카테고리를 통합하여 검색
        all_keywords = {
            **ethical_keywords,
            **practical_keywords,
            **logical_keywords,
            **value_keywords,
            **conflict_keywords,
            **decision_keywords,
        }

        # Day 2: 개선된 키워드 매칭 (부분 매칭 포함)
        for keyword, weight in all_keywords.items():
            if keyword in text:
                keywords[keyword] = weight
            # Day 2: 부분 매칭도 고려
            elif len(keyword) > 2 and any(keyword in word for word in text.split()):
                keywords[keyword] = weight * 0.7  # 부분 매칭은 70% 가중치

        # Day 2: 캐시에 저장 (크기 제한 확인)
        if len(self.keyword_cache) < self.max_cache_size:
            self.keyword_cache[text] = keywords

        return keywords

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """벡터 정규화 - Day 2 개선"""
        # Day 2: 더 안정적인 정규화 방식
        norm = np.linalg.norm(vector)
        if norm > 1e-10:  # Day 2: 수치적 안정성 개선
            return vector / norm
        return vector

    def _select_reasoning_type(
        self, situation_vector: np.ndarray, action_vector: np.ndarray
    ) -> ReasoningType:
        """추론 유형 선택 - Day 3 개선"""
        # Day 3: 더 정교한 추론 유형 선택 알고리즘
        best_type = ReasoningType.KANTIAN
        best_similarity = 0.0

        # Day 3: 가중 평균 벡터 계산
        combined_vector = (situation_vector + action_vector) / 2

        # Day 3: 각 추론 유형별 유사도 계산 및 가중치 적용
        similarities = {}

        for reasoning_type, pattern in self.reasoning_patterns.items():
            # Day 3: 개선된 유사도 계산
            situation_similarity = self._calculate_enhanced_similarity(
                situation_vector, pattern
            )
            action_similarity = self._calculate_enhanced_similarity(
                action_vector, pattern
            )
            combined_similarity = self._calculate_enhanced_similarity(
                combined_vector, pattern
            )

            # Day 3: 가중 평균 유사도 계산 (더 균형잡힌 가중치)
            total_similarity = (
                situation_similarity * 0.35
                + action_similarity * 0.35
                + combined_similarity * 0.3
            )

            similarities[reasoning_type] = total_similarity

            if total_similarity > best_similarity:
                best_similarity = total_similarity
                best_type = reasoning_type

        # Day 3: 유사도가 비슷한 경우 다양성을 위해 랜덤 선택
        threshold = 0.1  # 유사도 차이가 10% 이내인 경우
        similar_types = []

        for reasoning_type, similarity in similarities.items():
            if abs(similarity - best_similarity) <= threshold:
                similar_types.append(reasoning_type)

        # Day 3: 유사한 유형이 여러 개인 경우 랜덤 선택
        if len(similar_types) > 1:
            best_type = random.choice(similar_types)

        logger.info(
            f"선택된 추론 유형: {best_type.value}, 유사도: {best_similarity:.3f}"
        )
        return best_type

    def _calculate_enhanced_similarity(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """향상된 유사도 계산 - Day 2 신규 (캐싱 포함)"""
        # Day 2: 캐시 키 생성
        cache_key = (tuple(vector1), tuple(vector2))
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]

        # Day 2: 코사인 유사도와 유클리드 거리를 결합한 향상된 유사도
        cosine_sim = self._calculate_cosine_similarity(vector1, vector2)

        # Day 2: 유클리드 거리 기반 유사도
        euclidean_dist = np.linalg.norm(vector1 - vector2)
        euclidean_sim = 1.0 / (1.0 + euclidean_dist)  # 거리를 유사도로 변환

        # Day 2: 가중 평균 (코사인 유사도에 더 높은 가중치)
        enhanced_similarity = cosine_sim * 0.7 + euclidean_sim * 0.3

        # Day 2: 캐시에 저장 (크기 제한 확인)
        if len(self.similarity_cache) < self.max_cache_size:
            self.similarity_cache[cache_key] = enhanced_similarity

        return enhanced_similarity

    def _calculate_cosine_similarity(
        self, vector1: np.ndarray, vector2: np.ndarray
    ) -> float:
        """코사인 유사도 계산 - Day 2 개선"""
        # Day 2: 수치적 안정성 개선
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        if norm1 > 1e-10 and norm2 > 1e-10:
            similarity = dot_product / (norm1 * norm2)
            # Day 2: 유사도 범위 보정
            return max(0.0, min(1.0, similarity))
        return 0.0

    def _construct_semantic_premises(
        self,
        situation_vector: np.ndarray,
        action_vector: np.ndarray,
        reasoning_type: ReasoningType,
    ) -> List[SemanticPremise]:
        """의미 벡터 기반 전제 구성 - Day 1 신규"""
        premises = []

        # 상황 기반 전제
        situation_premise = SemanticPremise(
            premise_type=PremiseType.PARTICULAR_FACT,
            content="주어진 상황의 특성",
            semantic_vector=situation_vector,
            justification="상황 분석을 통한 의미적 특성 추출",
            strength=0.8,
            source="situation_analysis",
            context_elements={"type": "situation", "vector": situation_vector.tolist()},
            confidence=0.7,
        )
        premises.append(situation_premise)

        # 행위 기반 전제
        action_premise = SemanticPremise(
            premise_type=PremiseType.PARTICULAR_FACT,
            content="고려 중인 행위의 특성",
            semantic_vector=action_vector,
            justification="행위 분석을 통한 의미적 특성 추출",
            strength=0.8,
            source="action_analysis",
            context_elements={"type": "action", "vector": action_vector.tolist()},
            confidence=0.7,
        )
        premises.append(action_premise)

        # 추론 유형 기반 원칙 전제
        reasoning_pattern = self.reasoning_patterns[reasoning_type]
        principle_premise = SemanticPremise(
            premise_type=PremiseType.UNIVERSAL_PRINCIPLE,
            content=f"{reasoning_type.value} 추론 원칙",
            semantic_vector=reasoning_pattern,
            justification=f"{reasoning_type.value} 추론 패턴 적용",
            strength=0.9,
            source="reasoning_pattern",
            context_elements={
                "type": "principle",
                "reasoning_type": reasoning_type.value,
            },
            confidence=0.8,
        )
        premises.append(principle_premise)

        return premises

    def _construct_philosophical_argument(
        self, premises: List[SemanticPremise], reasoning_type: ReasoningType
    ) -> List[LogicalStep]:
        """철학적 논증 패턴 구성 - Day 3 신규"""
        steps = []

        # Day 3: 추론 유형별 철학적 논증 패턴 구현

        if reasoning_type == ReasoningType.KANTIAN:
            steps = self._construct_kantian_argument(premises)
        elif reasoning_type == ReasoningType.UTILITARIAN:
            steps = self._construct_utilitarian_argument(premises)
        elif reasoning_type == ReasoningType.VIRTUE_ETHICS:
            steps = self._construct_virtue_ethics_argument(premises)
        elif reasoning_type == ReasoningType.DEONTOLOGICAL:
            steps = self._construct_deontological_argument(premises)
        elif reasoning_type == ReasoningType.CONSEQUENTIALIST:
            steps = self._construct_consequentialist_argument(premises)
        elif reasoning_type == ReasoningType.HYBRID:
            steps = self._construct_hybrid_argument(premises)
        elif reasoning_type == ReasoningType.PRAGMATIC:
            steps = self._construct_pragmatic_argument(premises)
        elif reasoning_type == ReasoningType.CONSTRUCTIVIST:
            steps = self._construct_constructivist_argument(premises)
        elif reasoning_type == ReasoningType.CRITICAL:
            steps = self._construct_critical_argument(premises)
        else:
            steps = self._construct_general_argument(premises, reasoning_type)

        return steps

    def _construct_kantian_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """칸트적 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 보편화 가능성 검토
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="행위의 보편화 가능성 검토: 모든 사람이 이 행위를 할 수 있는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="칸트의 정언명령 첫 번째 공식: 보편화 가능성 원칙 적용",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step1)

        # 2단계: 목적론적 검토
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="인간을 목적으로 대우하는지 검토: 인간을 수단으로만 대우하지 않는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="칸트의 정언명령 두 번째 공식: 목적론적 원칙 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 자율성 검토
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="자율적 의지에 따른 행위인지 검토: 이성적 자율성에 따른 행위인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="칸트의 정언명령 세 번째 공식: 자율성 원칙 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step3)

        # 4단계: 의무론적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="의무론적 관점에서의 행위 평가: 의무에 따른 행위인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="칸트적 의무론적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_utilitarian_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """공리주의 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 행복 계산
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="행위의 결과적 행복 계산: 최대 다수의 최대 행복을 증진하는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="공리주의의 핵심 원칙: 최대 행복 원칙 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 고통 계산
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="행위의 결과적 고통 계산: 최소 다수의 최소 고통을 야기하는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="공리주의의 부정적 측면: 고통 최소화 원칙 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 효용 극대화
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="전체 효용 극대화: 행복과 고통의 순효용이 최대인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="공리주의의 종합적 평가: 순효용 극대화 원칙",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step3)

        # 4단계: 결과론적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="결과론적 관점에서의 행위 평가: 최선의 결과를 가져오는가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="공리주의적 결과론적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_virtue_ethics_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """덕윤리 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 덕성 식별
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.ANALOGICAL,
            conclusion="관련된 덕성 식별: 어떤 덕성이 이 상황에서 요구되는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="덕윤리의 핵심: 상황에 적합한 덕성 식별",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 현명한 판단
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.ANALOGICAL,
            conclusion="현명한 판단: 현명한 사람이라면 어떻게 행동할 것인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="덕윤리의 실천적 측면: 현명한 판단의 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 성격 형성
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.ANALOGICAL,
            conclusion="성격 형성: 이 행위가 좋은 성격 형성에 도움이 되는가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="덕윤리의 교육적 측면: 성격 형성의 관점",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step3)

        # 4단계: 덕성적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.ANALOGICAL,
            conclusion="덕성적 관점에서의 행위 평가: 덕성에 부합하는 행위인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="덕윤리적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_pragmatic_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """실용주의 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 실용성 검토
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="실용성 검토: 이 행위가 실제로 효과적인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="실용주의의 핵심: 실용성과 효과성 검토",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 결과 예측
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="결과 예측: 이 행위의 예상 결과는 무엇인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="실용주의의 예측적 측면: 결과 예측",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 대안 비교
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="대안 비교: 다른 대안들과 비교했을 때 이 행위가 최선인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="실용주의의 비교적 측면: 대안 비교",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step3)

        # 4단계: 실용적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="실용적 관점에서의 행위 평가: 가장 실용적인 선택인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="실용주의적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_constructivist_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """구성주의 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 구성적 합리성
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.DIALECTICAL,
            conclusion="구성적 합리성 검토: 이 행위가 구성적 합리성에 부합하는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="구성주의의 핵심: 구성적 합리성 원칙",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 상호주관성
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.DIALECTICAL,
            conclusion="상호주관성 검토: 모든 관련자들이 합의할 수 있는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="구성주의의 상호주관적 측면: 합의 가능성",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 절차적 정당성
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DIALECTICAL,
            conclusion="절차적 정당성 검토: 절차적으로 정당한가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="구성주의의 절차적 측면: 절차적 정당성",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step3)

        # 4단계: 구성적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DIALECTICAL,
            conclusion="구성적 관점에서의 행위 평가: 구성적으로 정당한가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="구성주의적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_critical_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """비판적 추론 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 가정 비판
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.CRITICAL,
            conclusion="가정 비판: 이 행위의 근본 가정들은 타당한가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="비판적 사고의 핵심: 가정의 비판적 검토",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 관점 분석
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.CRITICAL,
            conclusion="관점 분석: 다양한 관점에서 이 행위를 어떻게 볼 수 있는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="비판적 사고의 다관점적 측면: 관점 분석",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 권력 관계 분석
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.CRITICAL,
            conclusion="권력 관계 분석: 이 행위가 권력 관계에 미치는 영향은?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="비판적 사고의 권력 분석적 측면: 권력 관계",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step3)

        # 4단계: 비판적 결론
        step4 = LogicalStep(
            step_number=4,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.CRITICAL,
            conclusion="비판적 관점에서의 행위 평가: 비판적으로 정당한가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="비판적 관점에서의 최종 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step4)

        return steps

    def _construct_deontological_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """의무론적 논증 패턴 - Day 5 신규"""
        steps = []

        # 1단계: 의무 분석
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="의무론적 분석: 이 행위는 도덕적 의무에 따른 것인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="의무론적 관점에서 행위의 도덕적 의무성 검토",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 권리 분석
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="권리 분석: 이 행위는 타인의 권리를 존중하는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="의무론적 관점에서 타인의 권리 존중 여부 검토",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 의무론적 결론
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="의무론적 관점에서의 최종 평가: 도덕적 의무에 따른 행위인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="의무론적 관점에서의 종합적 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step3)

        return steps

    def _construct_consequentialist_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """결과론적 논증 패턴 - Day 5 신규"""
        steps = []

        # 1단계: 결과 분석
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="결과 분석: 이 행위의 결과는 긍정적인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="결과론적 관점에서 행위의 결과 분석",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 효용 분석
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="효용 분석: 이 행위는 전체 효용을 증진하는가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="결과론적 관점에서 전체 효용 증진 여부 분석",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 결과론적 결론
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="결과론적 관점에서의 최종 평가: 결과가 긍정적인 행위인가?",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="결과론적 관점에서의 종합적 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step3)

        return steps

    def _construct_hybrid_argument(
        self, premises: List[SemanticPremise]
    ) -> List[LogicalStep]:
        """혼합론적 논증 패턴 - Day 5 신규"""
        steps = []

        # 1단계: 의무론적 분석
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion="의무론적 분석: 이 행위는 도덕적 의무에 따른 것인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="혼합론적 관점에서 의무론적 분석",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 결과론적 분석
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1],
            inference_type=InferenceType.INDUCTIVE,
            conclusion="결과론적 분석: 이 행위의 결과는 긍정적인가?",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification="혼합론적 관점에서 결과론적 분석",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 혼합론적 통합
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DIALECTICAL,
            conclusion="혼합론적 통합: 의무와 결과를 종합한 평가",
            semantic_vector=self._combine_premise_vectors(premises),
            justification="혼합론적 관점에서 의무와 결과의 종합적 평가",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step3)

        return steps

    def _construct_general_argument(
        self, premises: List[SemanticPremise], reasoning_type: ReasoningType
    ) -> List[LogicalStep]:
        """일반적 논증 패턴 - Day 3 신규"""
        steps = []

        # 1단계: 전제 분석
        step1 = LogicalStep(
            step_number=1,
            premise_references=[0, 1],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion=f"{reasoning_type.value} 관점에서 전제 분석",
            semantic_vector=self._combine_premise_vectors([premises[0], premises[1]]),
            justification=f"{reasoning_type.value} 추론 원칙 적용",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step1)

        # 2단계: 추론 적용
        step2 = LogicalStep(
            step_number=2,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion=f"{reasoning_type.value} 추론 원칙 적용",
            semantic_vector=self._combine_premise_vectors(premises),
            justification=f"{reasoning_type.value} 추론 과정",
            confidence=0.8,
            logical_strength=0.85,
        )
        steps.append(step2)

        # 3단계: 결론 도출
        step3 = LogicalStep(
            step_number=3,
            premise_references=[0, 1, 2],
            inference_type=InferenceType.DEDUCTIVE,
            conclusion=f"{reasoning_type.value} 관점에서의 결론 도출",
            semantic_vector=self._combine_premise_vectors(premises),
            justification=f"{reasoning_type.value} 최종 결론",
            confidence=0.85,
            logical_strength=0.9,
        )
        steps.append(step3)

        return steps

    def _combine_premise_vectors(self, premises: List[SemanticPremise]) -> np.ndarray:
        """전제 벡터 결합 - Day 1 신규"""
        if not premises:
            return np.zeros(self.vector_dimension)

        combined = np.zeros(self.vector_dimension)
        total_weight = 0.0

        for premise in premises:
            weight = premise.strength
            combined += premise.semantic_vector * weight
            total_weight += weight

        if total_weight > 0:
            combined /= total_weight

        return combined

    def _derive_final_conclusion(
        self, logical_steps: List[LogicalStep], reasoning_type: ReasoningType
    ) -> str:
        """최종 결론 도출 - Day 1 신규"""
        # 마지막 단계의 결론을 기반으로 최종 결론 생성
        if logical_steps:
            last_step = logical_steps[-1]

            # 추론 유형에 따른 결론 템플릿 적용
            if reasoning_type == ReasoningType.KANTIAN:
                return f"칸트적 관점에서 {last_step.conclusion}"
            elif reasoning_type == ReasoningType.UTILITARIAN:
                return f"공리주의 관점에서 {last_step.conclusion}"
            elif reasoning_type == ReasoningType.VIRTUE_ETHICS:
                return f"덕윤리 관점에서 {last_step.conclusion}"
            elif reasoning_type == ReasoningType.PRAGMATIC:
                return f"실용주의 관점에서 {last_step.conclusion}"
            else:
                return f"{reasoning_type.value} 관점에서 {last_step.conclusion}"

        return "추론 과정을 통해 결론을 도출할 수 없습니다."

    def _calculate_argument_strength(
        self,
        premises: List[SemanticPremise],
        logical_steps: List[LogicalStep],
        reasoning_type: ReasoningType,
    ) -> float:
        """논증 강도 계산 - Day 3 정교화"""
        # Day 3: 더 정교한 논증 강도 계산 시스템

        # 1. 전제 강도 계산 (Day 3: 가중 평균으로 개선)
        premise_strength = 0.0
        total_premise_weight = 0.0

        for premise in premises:
            # Day 3: 전제 유형별 가중치 적용
            type_weight = self._get_premise_type_weight(premise.premise_type)
            weighted_strength = premise.strength * type_weight
            premise_strength += weighted_strength
            total_premise_weight += type_weight

        if total_premise_weight > 0:
            premise_strength /= total_premise_weight

        # 2. 논리적 단계 강도 계산 (Day 3: 단계별 가중치 적용)
        step_strength = 0.0
        total_step_weight = 0.0

        for i, step in enumerate(logical_steps):
            # Day 3: 단계별 가중치 (후반 단계에 더 높은 가중치)
            step_weight = 1.0 + (i * 0.1)  # 단계가 진행될수록 가중치 증가
            weighted_strength = step.logical_strength * step_weight
            step_strength += weighted_strength
            total_step_weight += step_weight

        if total_step_weight > 0:
            step_strength /= total_step_weight

        # 3. 추론 유형별 가중치 (Day 3: 더 정교한 가중치 시스템)
        type_weights = {
            ReasoningType.KANTIAN: 1.0,  # 칸트적: 높은 가중치
            ReasoningType.UTILITARIAN: 0.95,  # 공리주의: 높은 가중치
            ReasoningType.VIRTUE_ETHICS: 0.9,  # 덕윤리: 높은 가중치
            ReasoningType.PRAGMATIC: 0.85,  # 실용주의: 중간 가중치
            ReasoningType.CONSTRUCTIVIST: 0.8,  # 구성주의: 중간 가중치
            ReasoningType.CRITICAL: 0.8,  # 비판적: 중간 가중치
            ReasoningType.DEONTOLOGICAL: 0.9,  # 의무론: 높은 가중치
            ReasoningType.CONSEQUENTIALIST: 0.9,  # 결과론: 높은 가중치
            ReasoningType.HYBRID: 0.85,  # 혼합: 중간 가중치
        }

        type_weight = type_weights.get(reasoning_type, 1.0)

        # 4. 논리적 일관성 점수 (Day 3: 신규)
        consistency_score = self._calculate_logical_consistency(premises, logical_steps)

        # 5. 추론 완성도 점수 (Day 3: 신규)
        completeness_score = self._calculate_reasoning_completeness(
            logical_steps, reasoning_type
        )

        # 6. 종합 강도 계산 (Day 3: 더 정교한 공식)
        overall_strength = (
            premise_strength * 0.3  # 전제 강도 (30%)
            + step_strength * 0.4  # 논리적 단계 강도 (40%)
            + consistency_score * 0.15  # 논리적 일관성 (15%)
            + completeness_score * 0.15  # 추론 완성도 (15%)
        ) * type_weight

        return min(overall_strength, 1.0)

    def _get_premise_type_weight(self, premise_type: PremiseType) -> float:
        """전제 유형별 가중치 - Day 3 신규"""
        weights = {
            PremiseType.UNIVERSAL_PRINCIPLE: 1.0,  # 보편적 원칙: 높은 가중치
            PremiseType.PARTICULAR_FACT: 0.8,  # 특수 사실: 중간 가중치
            PremiseType.CONDITIONAL: 0.7,  # 조건적: 중간 가중치
            PremiseType.NORMATIVE: 0.9,  # 규범적: 높은 가중치
            PremiseType.EMPIRICAL: 0.8,  # 경험적: 중간 가중치
            PremiseType.CONTEXTUAL: 0.7,  # 맥락적: 중간 가중치
            PremiseType.EXPERIENTIAL: 0.6,  # 경험적: 낮은 가중치
            PremiseType.INTUITIVE: 0.5,  # 직관적: 낮은 가중치
        }
        return weights.get(premise_type, 0.7)

    def _calculate_logical_consistency(
        self, premises: List[SemanticPremise], logical_steps: List[LogicalStep]
    ) -> float:
        """논리적 일관성 계산 - Day 3 신규"""
        if not premises or not logical_steps:
            return 0.0

        # 1. 전제 간 일관성 검사
        premise_consistency = 0.0
        premise_pairs = 0

        for i in range(len(premises)):
            for j in range(i + 1, len(premises)):
                similarity = self._calculate_enhanced_similarity(
                    premises[i].semantic_vector, premises[j].semantic_vector
                )
                premise_consistency += similarity
                premise_pairs += 1

        if premise_pairs > 0:
            premise_consistency /= premise_pairs

        # 2. 논리적 단계 간 일관성 검사
        step_consistency = 0.0
        step_pairs = 0

        for i in range(len(logical_steps)):
            for j in range(i + 1, len(logical_steps)):
                similarity = self._calculate_enhanced_similarity(
                    logical_steps[i].semantic_vector, logical_steps[j].semantic_vector
                )
                step_consistency += similarity
                step_pairs += 1

        if step_pairs > 0:
            step_consistency /= step_pairs

        # 3. 전제와 단계 간 일관성 검사
        premise_step_consistency = 0.0
        total_comparisons = 0

        for premise in premises:
            for step in logical_steps:
                similarity = self._calculate_enhanced_similarity(
                    premise.semantic_vector, step.semantic_vector
                )
                premise_step_consistency += similarity
                total_comparisons += 1

        if total_comparisons > 0:
            premise_step_consistency /= total_comparisons

        # 4. 종합 일관성 점수
        overall_consistency = (
            premise_consistency * 0.3
            + step_consistency * 0.3
            + premise_step_consistency * 0.4
        )

        return overall_consistency

    def _calculate_reasoning_completeness(
        self, logical_steps: List[LogicalStep], reasoning_type: ReasoningType
    ) -> float:
        """추론 완성도 계산 - Day 3 신규"""
        if not logical_steps:
            return 0.0

        # 1. 단계 수 완성도
        expected_steps = {
            ReasoningType.KANTIAN: 4,
            ReasoningType.UTILITARIAN: 4,
            ReasoningType.VIRTUE_ETHICS: 4,
            ReasoningType.PRAGMATIC: 4,
            ReasoningType.CONSTRUCTIVIST: 4,
            ReasoningType.CRITICAL: 4,
            ReasoningType.DEONTOLOGICAL: 3,
            ReasoningType.CONSEQUENTIALIST: 3,
            ReasoningType.HYBRID: 3,
        }

        expected_step_count = expected_steps.get(reasoning_type, 3)
        step_completeness = min(len(logical_steps) / expected_step_count, 1.0)

        # 2. 단계별 완성도
        step_quality = 0.0
        for step in logical_steps:
            # 단계의 논리적 강도와 신뢰도를 종합
            step_quality += (step.logical_strength + step.confidence) / 2

        if logical_steps:
            step_quality /= len(logical_steps)

        # 3. 추론 유형별 완성도 요구사항
        type_completeness_requirements = {
            ReasoningType.KANTIAN: 0.9,  # 칸트적: 높은 완성도 요구
            ReasoningType.UTILITARIAN: 0.85,  # 공리주의: 높은 완성도 요구
            ReasoningType.VIRTUE_ETHICS: 0.8,  # 덕윤리: 중간 완성도 요구
            ReasoningType.PRAGMATIC: 0.75,  # 실용주의: 중간 완성도 요구
            ReasoningType.CONSTRUCTIVIST: 0.8,  # 구성주의: 중간 완성도 요구
            ReasoningType.CRITICAL: 0.8,  # 비판적: 중간 완성도 요구
            ReasoningType.DEONTOLOGICAL: 0.85,  # 의무론: 높은 완성도 요구
            ReasoningType.CONSEQUENTIALIST: 0.85,  # 결과론: 높은 완성도 요구
            ReasoningType.HYBRID: 0.8,  # 혼합: 중간 완성도 요구
        }

        required_completeness = type_completeness_requirements.get(reasoning_type, 0.8)

        # 4. 종합 완성도 점수
        overall_completeness = (
            step_completeness * 0.4 + step_quality * 0.4 + required_completeness * 0.2
        )

        return overall_completeness

    def _identify_counter_arguments(
        self,
        premises: List[SemanticPremise],
        logical_steps: List[LogicalStep],
        reasoning_type: ReasoningType,
    ) -> List[str]:
        """반론 식별 - Day 3 개선"""
        counter_arguments = []

        # Day 3: 추론 유형별 상세한 반론 분석

        if reasoning_type == ReasoningType.KANTIAN:
            counter_arguments.extend(
                [
                    "칸트적 관점은 결과를 고려하지 않아 현실적 적용이 어려울 수 있음",
                    "절대적 의무가 상충될 때 우선순위 결정이 모호함",
                    "보편화 가능성 검토가 모든 상황에 적용하기 어려울 수 있음",
                    "인간을 목적으로 대우하는 원칙이 구체적 상황에서 모호할 수 있음",
                    "자율성 개념이 문화적 맥락에 따라 다르게 해석될 수 있음",
                ]
            )
        elif reasoning_type == ReasoningType.UTILITARIAN:
            counter_arguments.extend(
                [
                    "공리주의는 개인의 권리를 무시할 수 있음",
                    "효용 계산이 정확하지 않거나 불가능할 수 있음",
                    "미래 결과 예측의 불확실성으로 인한 계산 오류 가능성",
                    "다수의 행복과 소수의 고통 간의 균형 문제",
                    "정량화할 수 없는 가치들(예: 존엄성, 자유)의 무시",
                ]
            )
        elif reasoning_type == ReasoningType.VIRTUE_ETHICS:
            counter_arguments.extend(
                [
                    "덕의 정의가 문화에 따라 다를 수 있음",
                    "덕이 행위의 옳고 그름을 결정하는 유일한 기준이 아닐 수 있음",
                    "현명한 사람의 판단이 주관적일 수 있음",
                    "덕성의 우선순위 결정이 모호할 수 있음",
                    "덕성 형성의 장기적 과정이 긴급한 의사결정에 부적합할 수 있음",
                ]
            )
        elif reasoning_type == ReasoningType.PRAGMATIC:
            counter_arguments.extend(
                [
                    "실용성의 정의가 주관적일 수 있음",
                    "단기적 실용성과 장기적 실용성 간의 충돌",
                    "실용성과 윤리적 가치 간의 균형 문제",
                    "실용성 평가의 정량화 어려움",
                    "실용성 중심의 접근이 근본적 가치를 무시할 수 있음",
                ]
            )
        elif reasoning_type == ReasoningType.CONSTRUCTIVIST:
            counter_arguments.extend(
                [
                    "구성적 합리성의 기준이 모호할 수 있음",
                    "상호주관적 합의 도출의 어려움",
                    "절차적 정당성과 실질적 정당성 간의 충돌",
                    "구성적 과정의 시간과 비용 문제",
                    "구성적 합의가 항상 최선의 결과를 보장하지 않음",
                ]
            )
        elif reasoning_type == ReasoningType.CRITICAL:
            counter_arguments.extend(
                [
                    "비판적 분석이 과도한 회의주의로 이어질 수 있음",
                    "가정 비판의 무한 퇴행 가능성",
                    "권력 관계 분석의 주관성",
                    "비판적 관점이 건설적 해결책 제시에 부족할 수 있음",
                    "다관점적 분석이 결정의 지연을 야기할 수 있음",
                ]
            )

        # Day 3: 일반적인 반론 추가
        counter_arguments.extend(
            [
                "의미 벡터 기반 분석의 정확도 한계",
                "추론 과정의 단순화로 인한 복잡성 손실",
                "컨텍스트 정보의 제한적 활용",
                "문화적, 역사적 맥락의 고려 부족",
                "감정적, 직관적 요소의 배제",
            ]
        )

        return counter_arguments

    def _identify_limitations(
        self,
        premises: List[SemanticPremise],
        logical_steps: List[LogicalStep],
        reasoning_type: ReasoningType,
    ) -> List[str]:
        """한계 식별 - Day 3 개선"""
        limitations = []

        # Day 3: 추론 유형별 상세한 한계 분석

        if reasoning_type == ReasoningType.KANTIAN:
            limitations.extend(
                [
                    "칸트적 관점의 절대적 성격으로 인한 유연성 부족",
                    "정언명령의 추상적 성격으로 인한 구체적 적용의 어려움",
                    "의무론적 관점의 결과 무시로 인한 현실적 한계",
                    "보편화 가능성 검토의 모든 상황 적용 한계",
                    "자율성 개념의 문화적, 역사적 맥락 고려 부족",
                ]
            )
        elif reasoning_type == ReasoningType.UTILITARIAN:
            limitations.extend(
                [
                    "효용 계산의 정량화 어려움",
                    "미래 결과 예측의 불확실성",
                    "개인 간 효용 비교의 어려움",
                    "정량화할 수 없는 가치들의 배제",
                    "효용 극대화의 장기적, 단기적 관점 충돌",
                ]
            )
        elif reasoning_type == ReasoningType.VIRTUE_ETHICS:
            limitations.extend(
                [
                    "덕의 정의와 적용의 모호함",
                    "덕성의 문화적, 역사적 상대성",
                    "현명한 판단의 주관성",
                    "덕성 형성의 장기적 과정",
                    "덕성 간 우선순위 결정의 어려움",
                ]
            )
        elif reasoning_type == ReasoningType.PRAGMATIC:
            limitations.extend(
                [
                    "실용성 정의의 주관성",
                    "단기적과 장기적 실용성 간의 충돌",
                    "실용성과 윤리적 가치 간의 균형 문제",
                    "실용성 평가의 정량화 어려움",
                    "실용성 중심 접근의 근본적 가치 무시 가능성",
                ]
            )
        elif reasoning_type == ReasoningType.CONSTRUCTIVIST:
            limitations.extend(
                [
                    "구성적 합리성 기준의 모호함",
                    "상호주관적 합의 도출의 어려움",
                    "절차적 정당성과 실질적 정당성 간의 충돌",
                    "구성적 과정의 시간과 비용",
                    "구성적 합의의 최선 결과 보장 부족",
                ]
            )
        elif reasoning_type == ReasoningType.CRITICAL:
            limitations.extend(
                [
                    "비판적 분석의 과도한 회의주의",
                    "가정 비판의 무한 퇴행",
                    "권력 관계 분석의 주관성",
                    "건설적 해결책 제시의 부족",
                    "다관점적 분석의 결정 지연",
                ]
            )

        # Day 3: 시스템적 한계 추가
        limitations.extend(
            [
                "의미 벡터 기반 분석의 정확도 한계",
                "추론 과정의 단순화로 인한 복잡성 손실",
                "컨텍스트 정보의 제한적 활용",
                "문화적, 역사적 맥락의 고려 부족",
                "감정적, 직관적 요소의 배제",
                "실시간 학습 및 적응 능력의 한계",
                "복잡한 다층적 상황 분석의 한계",
                "주관적 판단 요소의 객관화 한계",
            ]
        )

        return limitations

    def _calculate_overall_confidence(
        self,
        premises: List[SemanticPremise],
        logical_steps: List[LogicalStep],
        strength: float,
    ) -> float:
        """전체 신뢰도 계산 - Day 1 신규"""
        # 전제들의 평균 신뢰도
        premise_confidence = (
            sum(p.confidence for p in premises) / len(premises) if premises else 0.0
        )

        # 논리적 단계들의 평균 신뢰도
        step_confidence = (
            sum(s.confidence for s in logical_steps) / len(logical_steps)
            if logical_steps
            else 0.0
        )

        # 종합 신뢰도 계산
        overall_confidence = (
            premise_confidence * 0.3 + step_confidence * 0.4 + strength * 0.3
        )

        return min(overall_confidence, 1.0)

    def _construct_reasoning_path(self, logical_steps: List[LogicalStep]) -> List[str]:
        """추론 경로 구성 - Day 1 신규"""
        path = []

        for step in logical_steps:
            path.append(
                f"단계 {step.step_number}: {step.conclusion} (신뢰도: {step.confidence:.2f})"
            )

        return path

    async def analyze_multiple_perspectives(
        self, situation: str, action: str
    ) -> MultiPerspectiveAnalysis:
        """다중 관점 분석 - Day 4 신규"""
        # Day 5: 성능 모니터링 시작
        self._start_performance_monitoring()

        logger.info(f"다중 관점 분석 시작: {action}")

        # 1. 모든 추론 유형에 대해 분석 수행
        perspectives = []
        for reasoning_type in ReasoningType:
            try:
                argument = await self._analyze_single_perspective(
                    situation, action, reasoning_type
                )
                perspectives.append(argument)
            except Exception as e:
                logger.warning(f"추론 유형 {reasoning_type.value} 분석 실패: {e}")

        # 2. 관점 간 유사성 계산
        perspective_similarities = self._calculate_perspective_similarities(
            perspectives
        )

        # 3. 관점 간 충돌 식별
        conflicts = self._identify_perspective_conflicts(
            perspectives, perspective_similarities
        )

        # 4. 관점별 가중치 계산
        perspective_weights = self._calculate_perspective_weights(
            perspectives, conflicts
        )

        # 5. 통합적 결론 도출
        integrated_conclusion = self._derive_integrated_conclusion(
            perspectives, perspective_weights, conflicts
        )

        # 6. 통합 강도 및 신뢰도 계산
        integrated_strength = self._calculate_integrated_strength(
            perspectives, perspective_weights
        )
        integrated_confidence = self._calculate_integrated_confidence(
            perspectives, perspective_weights
        )

        # 7. 충돌 해결 전략 수립
        conflict_resolution_strategy = self._determine_conflict_resolution_strategy(
            conflicts
        )

        # Day 5: 성능 모니터링 종료
        self._end_performance_monitoring()

        return MultiPerspectiveAnalysis(
            perspectives=perspectives,
            perspective_similarities=perspective_similarities,
            conflicts=conflicts,
            integrated_conclusion=integrated_conclusion,
            integrated_strength=integrated_strength,
            integrated_confidence=integrated_confidence,
            perspective_weights=perspective_weights,
            conflict_resolution_strategy=conflict_resolution_strategy,
        )

    async def _analyze_single_perspective(
        self, situation: str, action: str, reasoning_type: ReasoningType
    ) -> LogicalArgument:
        """단일 관점 분석 - Day 4 신규"""
        # 상황과 행위의 의미 벡터 인코딩
        situation_vector = self._encode_situation_semantics(situation)
        action_vector = self._encode_action_semantics(action)

        # 의미 벡터 기반 전제 구성
        premises = self._construct_semantic_premises(
            situation_vector, action_vector, reasoning_type
        )

        # 철학적 논증 패턴 구성
        logical_steps = self._construct_philosophical_argument(premises, reasoning_type)

        # 최종 결론 도출
        final_conclusion = self._derive_final_conclusion(logical_steps, reasoning_type)

        # 논증 강도 계산
        strength = self._calculate_argument_strength(
            premises, logical_steps, reasoning_type
        )

        # 반론 및 한계 식별
        counter_arguments = self._identify_counter_arguments(
            premises, logical_steps, reasoning_type
        )
        limitations = self._identify_limitations(
            premises, logical_steps, reasoning_type
        )

        # 전체 신뢰도 계산
        confidence = self._calculate_overall_confidence(
            premises, logical_steps, strength
        )

        # 추론 경로 구성
        reasoning_path = self._construct_reasoning_path(logical_steps)

        return LogicalArgument(
            reasoning_type=reasoning_type,
            premises=premises,
            logical_steps=logical_steps,
            final_conclusion=final_conclusion,
            semantic_vector=situation_vector,
            strength=strength,
            counter_arguments=counter_arguments,
            limitations=limitations,
            confidence=confidence,
            reasoning_path=reasoning_path,
        )

    def _calculate_perspective_similarities(
        self, perspectives: List[LogicalArgument]
    ) -> Dict[Tuple[ReasoningType, ReasoningType], float]:
        """관점 간 유사성 계산 - Day 4 신규"""
        similarities = {}

        for i, perspective1 in enumerate(perspectives):
            for j, perspective2 in enumerate(perspectives):
                if i < j:  # 중복 계산 방지
                    # 의미 벡터 기반 유사성 계산
                    vector_similarity = self._calculate_enhanced_similarity(
                        perspective1.semantic_vector, perspective2.semantic_vector
                    )

                    # 결론 유사성 계산
                    conclusion_similarity = self._calculate_text_similarity(
                        perspective1.final_conclusion, perspective2.final_conclusion
                    )

                    # 강도 유사성 계산
                    strength_similarity = 1.0 - abs(
                        perspective1.strength - perspective2.strength
                    )

                    # 종합 유사성 계산
                    overall_similarity = (
                        vector_similarity * 0.4
                        + conclusion_similarity * 0.4
                        + strength_similarity * 0.2
                    )

                    similarities[
                        (perspective1.reasoning_type, perspective2.reasoning_type)
                    ] = overall_similarity

        return similarities

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사성 계산 - Day 4 신규"""
        # 간단한 키워드 기반 유사성 계산
        keywords1 = set(self._extract_semantic_keywords(text1).keys())
        keywords2 = set(self._extract_semantic_keywords(text2).keys())

        if not keywords1 and not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    def _identify_perspective_conflicts(
        self,
        perspectives: List[LogicalArgument],
        similarities: Dict[Tuple[ReasoningType, ReasoningType], float],
    ) -> List[Dict[str, Any]]:
        """관점 간 충돌 식별 - Day 4 신규"""
        conflicts = []

        for i, perspective1 in enumerate(perspectives):
            for j, perspective2 in enumerate(perspectives):
                if i < j:  # 중복 계산 방지
                    # 유사도가 낮은 경우 충돌 가능성 검토
                    similarity = similarities.get(
                        (perspective1.reasoning_type, perspective2.reasoning_type), 0.0
                    )

                    if similarity < 0.3:  # 충돌 임계값
                        conflict = self._analyze_perspective_conflict(
                            perspective1, perspective2, similarity
                        )
                        if conflict:
                            conflicts.append(conflict)

        return conflicts

    def _analyze_perspective_conflict(
        self,
        perspective1: LogicalArgument,
        perspective2: LogicalArgument,
        similarity: float,
    ) -> Optional[Dict[str, Any]]:
        """관점 간 충돌 분석 - Day 4 신규"""
        # 결론의 대립성 검사
        conclusion_opposition = self._check_conclusion_opposition(
            perspective1.final_conclusion, perspective2.final_conclusion
        )

        if conclusion_opposition > 0.5:  # 충돌 임계값
            conflict_type = self._determine_conflict_type(
                perspective1.reasoning_type, perspective2.reasoning_type
            )
            severity = (1.0 - similarity) * conclusion_opposition

            return {
                "perspective1": perspective1.reasoning_type,
                "perspective2": perspective2.reasoning_type,
                "conflict_type": conflict_type,
                "severity": severity,
                "description": f"{perspective1.reasoning_type.value}와 {perspective2.reasoning_type.value} 관점 간 충돌",
                "resolution_strategy": self._suggest_conflict_resolution(
                    conflict_type, severity
                ),
            }

        return None

    def _check_conclusion_opposition(self, conclusion1: str, conclusion2: str) -> float:
        """결론 대립성 검사 - Day 4 신규"""
        # 반대 키워드 쌍 정의
        opposite_pairs = [
            ("옳다", "그르다"),
            ("정당하다", "부당하다"),
            ("도덕적", "비도덕적"),
            ("허용", "금지"),
            ("지지", "반대"),
            ("긍정", "부정"),
            ("수용", "거부"),
            ("찬성", "반대"),
            ("적절", "부적절"),
        ]

        opposition_score = 0.0
        total_pairs = len(opposite_pairs)

        for word1, word2 in opposite_pairs:
            if (word1 in conclusion1 and word2 in conclusion2) or (
                word2 in conclusion1 and word1 in conclusion2
            ):
                opposition_score += 1.0

        return opposition_score / total_pairs if total_pairs > 0 else 0.0

    def _determine_conflict_type(
        self, reasoning_type1: ReasoningType, reasoning_type2: ReasoningType
    ) -> str:
        """충돌 유형 결정 - Day 4 신규"""
        # 추론 유형별 충돌 유형 매핑
        conflict_types = {
            (ReasoningType.KANTIAN, ReasoningType.UTILITARIAN): "의무론-결과론 충돌",
            (ReasoningType.KANTIAN, ReasoningType.VIRTUE_ETHICS): "의무론-덕윤리 충돌",
            (
                ReasoningType.UTILITARIAN,
                ReasoningType.VIRTUE_ETHICS,
            ): "결과론-덕윤리 충돌",
            (ReasoningType.PRAGMATIC, ReasoningType.KANTIAN): "실용주의-의무론 충돌",
            (ReasoningType.CRITICAL, ReasoningType.UTILITARIAN): "비판적-결과론 충돌",
            (
                ReasoningType.CONSTRUCTIVIST,
                ReasoningType.KANTIAN,
            ): "구성주의-의무론 충돌",
        }

        # 순서 무관하게 검색
        for (type1, type2), conflict_type in conflict_types.items():
            if (reasoning_type1 == type1 and reasoning_type2 == type2) or (
                reasoning_type1 == type2 and reasoning_type2 == type1
            ):
                return conflict_type

        return "일반적 관점 충돌"

    def _suggest_conflict_resolution(self, conflict_type: str, severity: float) -> str:
        """충돌 해결 전략 제안 - Day 4 신규"""
        if severity > 0.8:
            return "중재적 관점 도출"
        elif severity > 0.5:
            return "가중 평균 통합"
        else:
            return "상호 보완적 통합"

    def _calculate_perspective_weights(
        self, perspectives: List[LogicalArgument], conflicts: List[Dict[str, Any]]
    ) -> Dict[ReasoningType, float]:
        """관점별 가중치 계산 - Day 4 신규"""
        weights = {}
        total_weight = 0.0

        for perspective in perspectives:
            # 기본 가중치 (신뢰도 기반)
            base_weight = perspective.confidence

            # 충돌에 따른 가중치 조정
            conflict_penalty = 0.0
            for conflict in conflicts:
                if (
                    conflict["perspective1"] == perspective.reasoning_type
                    or conflict["perspective2"] == perspective.reasoning_type
                ):
                    conflict_penalty += conflict["severity"] * 0.1

            # 최종 가중치 계산
            final_weight = max(0.1, base_weight - conflict_penalty)
            weights[perspective.reasoning_type] = final_weight
            total_weight += final_weight

        # 정규화
        if total_weight > 0:
            for reasoning_type in weights:
                weights[reasoning_type] /= total_weight

        return weights

    def _derive_integrated_conclusion(
        self,
        perspectives: List[LogicalArgument],
        weights: Dict[ReasoningType, float],
        conflicts: List[Dict[str, Any]],
    ) -> str:
        """통합적 결론 도출 - Day 4 신규"""
        if not perspectives:
            return "분석할 수 있는 관점이 없습니다."

        # 충돌이 심한 경우 중재적 결론
        if any(conflict["severity"] > 0.7 for conflict in conflicts):
            return self._derive_mediating_conclusion(perspectives, conflicts)

        # 가중 평균 기반 통합 결론
        return self._derive_weighted_conclusion(perspectives, weights)

    def _derive_mediating_conclusion(
        self, perspectives: List[LogicalArgument], conflicts: List[Dict[str, Any]]
    ) -> str:
        """중재적 결론 도출 - Day 4 신규"""
        # 충돌하는 관점들의 공통점 찾기
        common_elements = self._find_common_elements(perspectives)

        if common_elements:
            return f"다양한 관점을 종합한 중재적 결론: {common_elements}"
        else:
            return "상충하는 관점들 간의 중재적 해결책이 필요합니다."

    def _derive_weighted_conclusion(
        self, perspectives: List[LogicalArgument], weights: Dict[ReasoningType, float]
    ) -> str:
        """가중 평균 기반 통합 결론 - Day 4 신규"""
        # 가중치가 높은 관점들의 결론을 종합
        high_weight_perspectives = [
            p for p in perspectives if weights.get(p.reasoning_type, 0) > 0.2
        ]

        if not high_weight_perspectives:
            high_weight_perspectives = perspectives

        conclusions = []
        for perspective in high_weight_perspectives:
            weight = weights.get(perspective.reasoning_type, 0.1)
            conclusions.append(
                f"{perspective.reasoning_type.value} 관점({weight:.2f}): {perspective.final_conclusion}"
            )

        return f"통합적 결론: {'; '.join(conclusions)}"

    def _find_common_elements(self, perspectives: List[LogicalArgument]) -> str:
        """공통 요소 찾기 - Day 4 신규"""
        # 모든 관점의 키워드 추출
        all_keywords = []
        for perspective in perspectives:
            keywords = self._extract_semantic_keywords(perspective.final_conclusion)
            all_keywords.extend(list(keywords.keys()))

        # 공통 키워드 찾기
        from collections import Counter

        keyword_counts = Counter(all_keywords)
        common_keywords = [
            keyword
            for keyword, count in keyword_counts.items()
            if count > len(perspectives) / 2
        ]

        if common_keywords:
            return f"공통 요소: {', '.join(common_keywords[:3])}"
        else:
            return "명확한 공통 요소를 찾을 수 없습니다."

    def _calculate_integrated_strength(
        self, perspectives: List[LogicalArgument], weights: Dict[ReasoningType, float]
    ) -> float:
        """통합 강도 계산 - Day 4 신규"""
        if not perspectives:
            return 0.0

        weighted_strength = 0.0
        total_weight = 0.0

        for perspective in perspectives:
            weight = weights.get(perspective.reasoning_type, 0.1)
            weighted_strength += perspective.strength * weight
            total_weight += weight

        return weighted_strength / total_weight if total_weight > 0 else 0.0

    def _calculate_integrated_confidence(
        self, perspectives: List[LogicalArgument], weights: Dict[ReasoningType, float]
    ) -> float:
        """통합 신뢰도 계산 - Day 4 신규"""
        if not perspectives:
            return 0.0

        weighted_confidence = 0.0
        total_weight = 0.0

        for perspective in perspectives:
            weight = weights.get(perspective.reasoning_type, 0.1)
            weighted_confidence += perspective.confidence * weight
            total_weight += weight

        return weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _determine_conflict_resolution_strategy(
        self, conflicts: List[Dict[str, Any]]
    ) -> str:
        """충돌 해결 전략 결정 - Day 4 신규"""
        if not conflicts:
            return "충돌 없음"

        # 충돌 심각도에 따른 전략 결정
        max_severity = max(conflict["severity"] for conflict in conflicts)

        if max_severity > 0.8:
            return "중재적 관점 도출"
        elif max_severity > 0.5:
            return "가중 평균 통합"
        else:
            return "상호 보완적 통합"

    # Day 5: 성능 모니터링 및 최적화 메서드들

    def _start_performance_monitoring(self):
        """성능 모니터링 시작 - Day 5 신규"""
        import time

        self.start_time = time.time()

    def _end_performance_monitoring(self):
        """성능 모니터링 종료 - Day 5 신규"""
        import time

        if self.start_time:
            processing_time = time.time() - self.start_time
            self.performance_metrics["total_analyses"] += 1

            # 평균 처리 시간 업데이트
            current_avg = self.performance_metrics["average_processing_time"]
            total_analyses = self.performance_metrics["total_analyses"]
            self.performance_metrics["average_processing_time"] = (
                current_avg * (total_analyses - 1) + processing_time
            ) / total_analyses

            # 캐시 히트율 업데이트
            total_cache_requests = self.cache_hits + self.cache_misses
            if total_cache_requests > 0:
                self.performance_metrics["cache_hit_rate"] = (
                    self.cache_hits / total_cache_requests
                )

            # 메모리 사용량 업데이트
            import psutil

            process = psutil.Process()
            self.performance_metrics["memory_usage"] = (
                process.memory_info().rss / 1024 / 1024
            )  # MB

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 반환 - Day 5 신규"""
        return self.performance_metrics.copy()

    def clear_cache(self):
        """캐시 정리 - Day 5 신규"""
        self.vector_cache.clear()
        self.keyword_cache.clear()
        self.similarity_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("캐시가 정리되었습니다.")

    def optimize_cache(self):
        """캐시 최적화 - Day 2 구현"""
        # 캐시 크기 제한 및 LRU 정책 적용
        for cache_name, cache in [
            ("vector", self.vector_cache),
            ("keyword", self.keyword_cache),
            ("similarity", self.similarity_cache),
        ]:
            if len(cache) > self.max_cache_size:
                # 가장 오래된 항목들 제거 (LRU)
                items_to_remove = len(cache) - self.max_cache_size
                for _ in range(items_to_remove):
                    cache.popitem(last=False)  # FIFO 방식으로 제거
                logger.info(
                    f"캐시 {cache_name} 최적화 완료: {items_to_remove}개 항목 제거"
                )

    def _update_cache_stats(self, cache_name: str, hit: bool):
        """캐시 통계 업데이트 - Day 5 신규"""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    # Day 5: 통합 테스트 및 검증 메서드들 추가
    async def run_integration_tests(self) -> Dict[str, Any]:
        """통합 테스트 실행 - Day 5 신규"""
        logger.info("🚀 Day 5: 통합 테스트 시작")

        test_suite = IntegrationTestSuite(self)
        results = await test_suite.run_comprehensive_tests()

        # 결과를 JSON 파일로 저장
        try:
            self._save_test_results(results)
        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

        return results

    def _save_test_results(self, results: Dict[str, Any]):
        """테스트 결과 저장 - Day 5 신규"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"

        # dataclass를 dict로 변환
        serializable_results = self._convert_to_serializable(results)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(serializable_results, f, ensure_ascii=False, indent=2)
            logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

    def _convert_to_serializable(self, obj: Any) -> Any:
        """객체를 JSON 직렬화 가능한 형태로 변환 - Day 5 신규"""
        if isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif hasattr(obj, "__dict__"):
            # dataclass인 경우 asdict 사용
            if hasattr(obj, "__dataclass_fields__"):
                return asdict(obj)
            return self._convert_to_serializable(obj.__dict__)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, bool):
            return obj
        elif isinstance(obj, (int, float, str)):
            return obj
        else:
            return str(obj)

    async def validate_system_performance(self) -> PerformanceMetrics:
        """시스템 성능 검증 - Day 5 신규"""
        logger.info("📊 시스템 성능 검증 시작")

        start_time = time.time()
        process = psutil.Process()

        # 성능 테스트 실행
        test_situations = [
            "윤리적 딜레마 상황",
            "실용적 의사결정 상황",
            "복잡한 논리적 상황",
        ]

        for situation in test_situations:
            await self.analyze_logical_reasoning(situation, "테스트 행동")

        end_time = time.time()
        execution_time = end_time - start_time

        # 메모리 및 CPU 사용량 측정
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()

        # 캐시 히트율 계산
        total_cache_access = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            self.cache_hits / total_cache_access if total_cache_access > 0 else 0.0
        )

        # 처리량 계산 (요청/초)
        throughput = (
            len(test_situations) / execution_time if execution_time > 0 else 0.0
        )

        return PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            cache_hit_rate=cache_hit_rate,
            throughput=throughput,
        )

    async def validate_accuracy(
        self, test_scenarios: List[Tuple[str, str, str]]
    ) -> List[ValidationResult]:
        """정확도 검증 - Day 5 신규"""
        logger.info("🎯 정확도 검증 시작")

        validation_results = []

        for scenario_name, situation, expected_outcome in test_scenarios:
            try:
                result = await self.analyze_logical_reasoning(situation, "테스트 행동")

                # 정확도 점수 계산
                accuracy_score = self._calculate_accuracy_score(
                    result, expected_outcome
                )

                # 신뢰도 점수
                confidence_score = result.confidence

                # 추론 품질 점수
                reasoning_quality = self._calculate_reasoning_quality(result)

                # 전체 점수
                overall_score = (
                    accuracy_score + confidence_score + reasoning_quality
                ) / 3

                validation_results.append(
                    ValidationResult(
                        scenario_name=scenario_name,
                        expected_outcome=expected_outcome,
                        actual_outcome=result.final_conclusion,
                        accuracy_score=accuracy_score,
                        confidence_score=confidence_score,
                        reasoning_quality=reasoning_quality,
                        overall_score=overall_score,
                    )
                )

            except Exception as e:
                logger.error(f"시나리오 {scenario_name} 검증 실패: {e}")
                validation_results.append(
                    ValidationResult(
                        scenario_name=scenario_name,
                        expected_outcome=expected_outcome,
                        actual_outcome="오류 발생",
                        accuracy_score=0.0,
                        confidence_score=0.0,
                        reasoning_quality=0.0,
                        overall_score=0.0,
                    )
                )

        return validation_results

    def _calculate_accuracy_score(
        self, result: LogicalArgument, expected_outcome: str
    ) -> float:
        """정확도 점수 계산 - Day 5 신규"""
        # 키워드 기반 정확도 계산
        expected_keywords = expected_outcome.lower().split()
        actual_keywords = result.final_conclusion.lower().split()

        # 공통 키워드 수 계산
        common_keywords = set(expected_keywords) & set(actual_keywords)

        if not expected_keywords:
            return 1.0

        accuracy = len(common_keywords) / len(expected_keywords)
        return min(accuracy, 1.0)

    def _calculate_reasoning_quality(self, result: LogicalArgument) -> float:
        """추론 품질 점수 계산 - Day 5 신규"""
        # 전제 수, 논리적 단계 수, 신뢰도 등을 종합하여 품질 계산
        premise_quality = len(result.premises) / 5.0  # 최대 5개 전제 기준
        step_quality = len(result.logical_steps) / 3.0  # 최대 3개 단계 기준
        strength_quality = result.strength
        confidence_quality = result.confidence

        # 가중 평균
        quality = (
            premise_quality * 0.3
            + step_quality * 0.3
            + strength_quality * 0.2
            + confidence_quality * 0.2
        )

        return min(quality, 1.0)

    async def generate_system_report(self) -> Dict[str, Any]:
        """시스템 리포트 생성 - Day 5 신규"""
        logger.info("📋 시스템 리포트 생성 시작")

        # 성능 메트릭 수집
        performance_metrics = await self.validate_system_performance()

        # 정확도 검증
        test_scenarios = [
            ("윤리적 딜레마", "거짓말을 해야 하는 상황", "윤리적 고려"),
            ("실용적 결정", "효율성을 고려해야 하는 상황", "실용적 접근"),
            ("논리적 분석", "복잡한 논리적 상황", "논리적 분석"),
        ]
        accuracy_results = await self.validate_accuracy(test_scenarios)

        # 통합 테스트 실행
        integration_results = await self.run_integration_tests()

        # 리포트 생성
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_version": "Phase 1-2 Week 2 Day 5",
            "performance_metrics": asdict(performance_metrics),
            "accuracy_results": [asdict(result) for result in accuracy_results],
            "integration_results": integration_results,
            "summary": self._generate_report_summary(
                performance_metrics, accuracy_results, integration_results
            ),
        }

        return report

    def _generate_report_summary(
        self,
        performance: PerformanceMetrics,
        accuracy: List[ValidationResult],
        integration: Dict[str, Any],
    ) -> Dict[str, Any]:
        """리포트 요약 생성 - Day 5 신규"""
        # 평균 정확도 계산
        avg_accuracy = (
            statistics.mean([r.accuracy_score for r in accuracy]) if accuracy else 0.0
        )
        avg_confidence = (
            statistics.mean([r.confidence_score for r in accuracy]) if accuracy else 0.0
        )
        avg_overall = (
            statistics.mean([r.overall_score for r in accuracy]) if accuracy else 0.0
        )

        # 시스템 건강도
        system_health = integration.get("system_health", {})
        if hasattr(system_health, "overall_health"):
            overall_health = system_health.overall_health
        else:
            overall_health = system_health.get("overall_health", 0.0)

        summary = {
            "performance_score": 1.0 if performance.execution_time < 1.0 else 0.5,
            "accuracy_score": avg_accuracy,
            "confidence_score": avg_confidence,
            "overall_score": avg_overall,
            "system_health": overall_health,
            "recommendations": integration.get("recommendations", []),
        }

        return summary


class IntegrationTestSuite:
    """통합 테스트 스위트 - Day 5 신규"""

    def __init__(self, reasoning_engine: "LogicalReasoningEngine"):
        self.engine = reasoning_engine
        self.test_results: List[TestResult] = []
        self.validation_results: List[ValidationResult] = []
        self.performance_history: List[PerformanceMetrics] = []

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """포괄적인 테스트 실행 - Day 5 신규"""
        logger.info("🚀 Day 5: 포괄적인 통합 테스트 시작")

        test_results = {
            "performance_tests": await self._run_performance_tests(),
            "accuracy_tests": await self._run_accuracy_tests(),
            "reliability_tests": await self._run_reliability_tests(),
            "edge_case_tests": await self._run_edge_case_tests(),
            "integration_tests": await self._run_integration_tests(),
        }

        # 시스템 건강도 계산
        system_health = self._calculate_system_health(test_results)

        return {
            "test_results": test_results,
            "system_health": system_health,
            "recommendations": self._generate_recommendations(
                test_results, system_health
            ),
        }

    async def _run_performance_tests(self) -> List[TestResult]:
        """성능 테스트 실행 - Day 5 신규"""
        logger.info("📊 성능 테스트 실행 중...")
        results = []

        # 1. 처리 속도 테스트
        start_time = time.time()
        for i in range(10):
            await self.engine.analyze_logical_reasoning(
                f"테스트 상황 {i}: 윤리적 딜레마 상황",
                f"테스트 행동 {i}: 결정을 내려야 하는 상황",
            )
        end_time = time.time()

        avg_time = (end_time - start_time) / 10
        results.append(
            TestResult(
                test_name="처리 속도 테스트",
                success=avg_time < 1.0,  # 1초 이내
                execution_time=avg_time,
                accuracy=1.0 if avg_time < 1.0 else 0.5,
                confidence=1.0 if avg_time < 1.0 else 0.3,
            )
        )

        # 2. 메모리 사용량 테스트
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # 메모리 집약적 작업 수행
        for i in range(50):
            await self.engine.analyze_multiple_perspectives(
                f"메모리 테스트 상황 {i}", f"메모리 테스트 행동 {i}"
            )

        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before

        results.append(
            TestResult(
                test_name="메모리 사용량 테스트",
                success=memory_increase < 100,  # 100MB 이내 증가
                execution_time=0.0,
                accuracy=1.0 if memory_increase < 100 else 0.3,
                confidence=1.0 if memory_increase < 100 else 0.2,
            )
        )

        return results

    async def _run_accuracy_tests(self) -> List[TestResult]:
        """정확도 테스트 실행 - Day 5 신규"""
        logger.info("🎯 정확도 테스트 실행 중...")
        results = []

        # 1. 윤리적 딜레마 테스트
        ethical_scenarios = [
            ("거짓말을 해야 하는 상황", "거짓말을 한다", "ethical_dilemma"),
            ("도움을 요청받은 상황", "도움을 준다", "virtue_ethics"),
            ("효율성을 고려해야 하는 상황", "효율적인 선택을 한다", "utilitarian"),
        ]

        for situation, action, expected_type in ethical_scenarios:
            result = await self.engine.analyze_logical_reasoning(situation, action)
            accuracy = 1.0 if result.reasoning_type.value in expected_type else 0.3

            results.append(
                TestResult(
                    test_name=f"윤리적 시나리오: {situation[:20]}...",
                    success=accuracy > 0.7,
                    execution_time=0.0,
                    accuracy=accuracy,
                    confidence=result.confidence,
                )
            )

        return results

    async def _run_reliability_tests(self) -> List[TestResult]:
        """신뢰성 테스트 실행 - Day 5 신규"""
        logger.info("🛡️ 신뢰성 테스트 실행 중...")
        results = []

        # 1. 오류 처리 테스트
        try:
            result = await self.engine.analyze_logical_reasoning("", "")
            results.append(
                TestResult(
                    test_name="빈 입력 처리 테스트",
                    success=True,
                    execution_time=0.0,
                    accuracy=1.0,
                    confidence=result.confidence,
                )
            )
        except Exception as e:
            results.append(
                TestResult(
                    test_name="빈 입력 처리 테스트",
                    success=False,
                    execution_time=0.0,
                    accuracy=0.0,
                    confidence=0.0,
                    error_message=str(e),
                )
            )

        # 2. 일관성 테스트
        situation = "동일한 윤리적 상황"
        action = "동일한 행동"

        results1 = []
        results2 = []

        for i in range(5):
            result1 = await self.engine.analyze_logical_reasoning(situation, action)
            result2 = await self.engine.analyze_logical_reasoning(situation, action)
            results1.append(result1.confidence)
            results2.append(result2.confidence)

        consistency = 1.0 - abs(statistics.mean(results1) - statistics.mean(results2))

        results.append(
            TestResult(
                test_name="일관성 테스트",
                success=consistency > 0.8,
                execution_time=0.0,
                accuracy=consistency,
                confidence=statistics.mean(results1),
            )
        )

        return results

    async def _run_edge_case_tests(self) -> List[TestResult]:
        """경계 조건 테스트 실행 - Day 5 신규"""
        logger.info("🔍 경계 조건 테스트 실행 중...")
        results = []

        # 1. 매우 긴 입력 테스트
        long_situation = "매우 긴 상황 설명 " * 100
        long_action = "매우 긴 행동 설명 " * 100

        try:
            result = await self.engine.analyze_logical_reasoning(
                long_situation, long_action
            )
            results.append(
                TestResult(
                    test_name="긴 입력 처리 테스트",
                    success=True,
                    execution_time=0.0,
                    accuracy=1.0,
                    confidence=result.confidence,
                )
            )
        except Exception as e:
            results.append(
                TestResult(
                    test_name="긴 입력 처리 테스트",
                    success=False,
                    execution_time=0.0,
                    accuracy=0.0,
                    confidence=0.0,
                    error_message=str(e),
                )
            )

        # 2. 특수 문자 테스트
        special_situation = "특수문자: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        special_action = "특수문자: !@#$%^&*()_+-=[]{}|;':\",./<>?"

        try:
            result = await self.engine.analyze_logical_reasoning(
                special_situation, special_action
            )
            results.append(
                TestResult(
                    test_name="특수 문자 처리 테스트",
                    success=True,
                    execution_time=0.0,
                    accuracy=1.0,
                    confidence=result.confidence,
                )
            )
        except Exception as e:
            results.append(
                TestResult(
                    test_name="특수 문자 처리 테스트",
                    success=False,
                    execution_time=0.0,
                    accuracy=0.0,
                    confidence=0.0,
                    error_message=str(e),
                )
            )

        return results

    async def _run_integration_tests(self) -> List[TestResult]:
        """통합 테스트 실행 - Day 5 신규"""
        logger.info("🔗 통합 테스트 실행 중...")
        results = []

        # 1. 다중 관점 분석 통합 테스트
        try:
            multi_result = await self.engine.analyze_multiple_perspectives(
                "복잡한 윤리적 상황", "다양한 관점에서 분석해야 하는 행동"
            )

            results.append(
                TestResult(
                    test_name="다중 관점 분석 통합 테스트",
                    success=len(multi_result.perspectives) >= 3,
                    execution_time=0.0,
                    accuracy=1.0 if len(multi_result.perspectives) >= 3 else 0.5,
                    confidence=multi_result.integrated_confidence,
                )
            )
        except Exception as e:
            results.append(
                TestResult(
                    test_name="다중 관점 분석 통합 테스트",
                    success=False,
                    execution_time=0.0,
                    accuracy=0.0,
                    confidence=0.0,
                    error_message=str(e),
                )
            )

        return results

    def _calculate_system_health(
        self, test_results: Dict[str, List[TestResult]]
    ) -> SystemHealth:
        """시스템 건강도 계산 - Day 5 신규"""
        # 성능 건강도 계산
        performance_scores = [
            r.accuracy for r in test_results.get("performance_tests", [])
        ]
        performance_health = (
            statistics.mean(performance_scores) if performance_scores else 0.0
        )

        # 정확도 건강도 계산
        accuracy_scores = [r.accuracy for r in test_results.get("accuracy_tests", [])]
        accuracy_health = statistics.mean(accuracy_scores) if accuracy_scores else 0.0

        # 신뢰성 건강도 계산
        reliability_scores = [
            r.accuracy for r in test_results.get("reliability_tests", [])
        ]
        reliability_health = (
            statistics.mean(reliability_scores) if reliability_scores else 0.0
        )

        # 전체 건강도 계산
        overall_health = (performance_health + accuracy_health + reliability_health) / 3

        return SystemHealth(
            overall_health=overall_health,
            performance_health=performance_health,
            accuracy_health=accuracy_health,
            reliability_health=reliability_health,
            recommendations=self._generate_health_recommendations(
                overall_health, performance_health, accuracy_health, reliability_health
            ),
        )

    def _generate_health_recommendations(
        self, overall: float, performance: float, accuracy: float, reliability: float
    ) -> List[str]:
        """건강도 기반 권장사항 생성 - Day 5 신규"""
        recommendations = []

        if overall < 0.7:
            recommendations.append("전체적인 시스템 성능 개선이 필요합니다.")

        if performance < 0.7:
            recommendations.append(
                "성능 최적화가 필요합니다. 캐싱 시스템을 개선하거나 알고리즘을 최적화하세요."
            )

        if accuracy < 0.7:
            recommendations.append(
                "정확도 향상이 필요합니다. 의미 벡터 모델을 개선하거나 훈련 데이터를 확장하세요."
            )

        if reliability < 0.7:
            recommendations.append(
                "신뢰성 향상이 필요합니다. 오류 처리 및 예외 상황 처리를 개선하세요."
            )

        if not recommendations:
            recommendations.append(
                "시스템이 양호한 상태입니다. 정기적인 모니터링을 계속하세요."
            )

        return recommendations

    def _generate_recommendations(
        self, test_results: Dict[str, List[TestResult]], system_health: SystemHealth
    ) -> List[str]:
        """테스트 결과 기반 권장사항 생성 - Day 5 신규"""
        recommendations = []

        # 성능 관련 권장사항
        performance_tests = test_results.get("performance_tests", [])
        for test in performance_tests:
            if not test.success:
                if "처리 속도" in test.test_name:
                    recommendations.append(
                        "처리 속도를 개선하기 위해 알고리즘 최적화가 필요합니다."
                    )
                elif "메모리" in test.test_name:
                    recommendations.append(
                        "메모리 사용량을 줄이기 위해 메모리 관리 최적화가 필요합니다."
                    )

        # 정확도 관련 권장사항
        accuracy_tests = test_results.get("accuracy_tests", [])
        failed_accuracy_tests = [t for t in accuracy_tests if not t.success]
        if failed_accuracy_tests:
            recommendations.append(
                f"{len(failed_accuracy_tests)}개의 정확도 테스트가 실패했습니다. 의미 분석 모델을 개선하세요."
            )

        # 신뢰성 관련 권장사항
        reliability_tests = test_results.get("reliability_tests", [])
        failed_reliability_tests = [t for t in reliability_tests if not t.success]
        if failed_reliability_tests:
            recommendations.append(
                f"{len(failed_reliability_tests)}개의 신뢰성 테스트가 실패했습니다. 오류 처리를 개선하세요."
            )

        return recommendations


async def test_logical_reasoning_engine():
    """논리적 추론 엔진 테스트 - Day 5 통합 테스트"""
    logger.info("🚀 Day 5: 논리적 추론 엔진 통합 테스트 시작")

    # 엔진 초기화
    engine = LogicalReasoningEngine()

    # Day 5: 통합 테스트 실행
    logger.info("📊 Day 5: 포괄적인 통합 테스트 실행 중...")
    integration_results = await engine.run_integration_tests()

    # 시스템 리포트 생성
    logger.info("📋 Day 5: 시스템 리포트 생성 중...")
    system_report = await engine.generate_system_report()

    # 결과 출력
    print("\n" + "=" * 80)
    print("🎉 Day 5: 논리적 추론 엔진 통합 테스트 완료!")
    print("=" * 80)

    # 시스템 건강도 출력
    system_health = integration_results.get("system_health", {})
    print(f"\n📊 시스템 건강도:")
    if hasattr(system_health, "overall_health"):
        print(f"  전체 건강도: {system_health.overall_health:.3f}")
        print(f"  성능 건강도: {system_health.performance_health:.3f}")
        print(f"  정확도 건강도: {system_health.accuracy_health:.3f}")
        print(f"  신뢰성 건강도: {system_health.reliability_health:.3f}")
    else:
        print(f"  전체 건강도: {system_health.get('overall_health', 0.0):.3f}")
        print(f"  성능 건강도: {system_health.get('performance_health', 0.0):.3f}")
        print(f"  정확도 건강도: {system_health.get('accuracy_health', 0.0):.3f}")
        print(f"  신뢰성 건강도: {system_health.get('reliability_health', 0.0):.3f}")

    # 테스트 결과 요약
    test_results = integration_results.get("test_results", {})
    print(f"\n🧪 테스트 결과 요약:")

    for test_category, results in test_results.items():
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        success_rate = success_count / total_count if total_count > 0 else 0.0
        print(
            f"  {test_category}: {success_count}/{total_count} 성공 ({success_rate:.1%})"
        )

    # 권장사항 출력
    recommendations = integration_results.get("recommendations", [])
    if recommendations:
        print(f"\n💡 권장사항:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

    # 성능 메트릭 출력
    performance_metrics = system_report.get("performance_metrics", {})
    if performance_metrics:
        print(f"\n⚡ 성능 메트릭:")
        print(f"  실행 시간: {performance_metrics.get('execution_time', 0.0):.3f}초")
        print(f"  메모리 사용량: {performance_metrics.get('memory_usage', 0.0):.1f}MB")
        print(f"  CPU 사용량: {performance_metrics.get('cpu_usage', 0.0):.1f}%")
        print(f"  캐시 히트율: {performance_metrics.get('cache_hit_rate', 0.0):.1%}")
        print(f"  처리량: {performance_metrics.get('throughput', 0.0):.1f} 요청/초")

    # 정확도 결과 출력
    accuracy_results = system_report.get("accuracy_results", [])
    if accuracy_results:
        print(f"\n🎯 정확도 결과:")
        for result in accuracy_results:
            print(f"  {result['scenario_name']}: {result['overall_score']:.3f}")

    # 전체 요약
    summary = system_report.get("summary", {})
    print(f"\n📈 전체 요약:")
    print(f"  성능 점수: {summary.get('performance_score', 0.0):.3f}")
    print(f"  정확도 점수: {summary.get('accuracy_score', 0.0):.3f}")
    print(f"  신뢰도 점수: {summary.get('confidence_score', 0.0):.3f}")
    print(f"  전체 점수: {summary.get('overall_score', 0.0):.3f}")
    print(f"  시스템 건강도: {summary.get('system_health', 0.0):.3f}")

    print("\n" + "=" * 80)
    print("🎉 Day 5: 모든 테스트 완료!")
    print("=" * 80)

    return integration_results, system_report


if __name__ == "__main__":
    asyncio.run(test_logical_reasoning_engine())
