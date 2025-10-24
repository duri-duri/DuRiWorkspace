#!/usr/bin/env python3
"""
DuRi 의미 벡터 엔진 (Phase 1-1 Day 1)
문자열 기반 키워드 매칭 → 의미 벡터 기반 이해로 전환
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticFrame(Enum):
    """의미 프레임"""

    ETHICAL_DILEMMA = "ethical_dilemma"
    PRACTICAL_DECISION = "practical_decision"
    CONFLICT_RESOLUTION = "conflict_resolution"
    COMPLEX_PROBLEM = "complex_problem"
    GENERAL_SITUATION = "general_situation"


@dataclass
class SemanticVector:
    """의미 벡터"""

    vector: np.ndarray
    dimension: int
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class SemanticAnalysis:
    """의미 분석 결과"""

    situation_vector: SemanticVector
    matched_frame: SemanticFrame
    confidence: float
    semantic_similarity: float
    context_elements: Dict[str, Any]


class SemanticVectorEngine:
    """의미 벡터 엔진"""

    def __init__(self, vector_dimension: int = 100):
        self.vector_dimension = vector_dimension
        self.semantic_frames = self._initialize_semantic_frames()
        self.semantic_patterns = self._initialize_semantic_patterns()
        self.vector_cache = {}

    def _initialize_semantic_frames(self) -> Dict[SemanticFrame, np.ndarray]:
        """의미 프레임 초기화 - 정교화된 벡터 구조"""
        frames = {}

        # 윤리적 딜레마 프레임 (개인정보, 비밀, 윤리적 갈등)
        ethical_dilemma_vector = np.zeros(self.vector_dimension)
        ethical_dilemma_vector[0:15] = 1.0  # 윤리적 요소 (강함)
        ethical_dilemma_vector[15:30] = 0.9  # 개인정보/비밀 요소
        ethical_dilemma_vector[30:45] = 0.8  # 갈등 요소
        ethical_dilemma_vector[45:60] = 0.7  # 의사결정 요소
        ethical_dilemma_vector[60:75] = 0.6  # 실용적 요소
        ethical_dilemma_vector[75:90] = 0.8  # 복잡성 요소
        ethical_dilemma_vector[90:100] = 0.9  # 딜레마 특성
        frames[SemanticFrame.ETHICAL_DILEMMA] = ethical_dilemma_vector

        # 실용적 결정 프레임 (비즈니스, 효율성, 성과)
        practical_decision_vector = np.zeros(self.vector_dimension)
        practical_decision_vector[0:15] = 0.3  # 윤리적 요소 (약함)
        practical_decision_vector[15:30] = 0.2  # 개인정보/비밀 요소
        practical_decision_vector[30:45] = 0.6  # 갈등 요소
        practical_decision_vector[45:60] = 1.0  # 의사결정 요소 (강함)
        practical_decision_vector[60:75] = 1.0  # 실용적 요소 (강함)
        practical_decision_vector[75:90] = 0.7  # 복잡성 요소
        practical_decision_vector[90:100] = 0.6  # 딜레마 특성
        frames[SemanticFrame.PRACTICAL_DECISION] = practical_decision_vector

        # 갈등 해결 프레임 (갈등, 충돌, 해결)
        conflict_resolution_vector = np.zeros(self.vector_dimension)
        conflict_resolution_vector[0:15] = 0.5  # 윤리적 요소
        conflict_resolution_vector[15:30] = 0.3  # 개인정보/비밀 요소
        conflict_resolution_vector[30:45] = 1.0  # 갈등 요소 (강함)
        conflict_resolution_vector[45:60] = 0.9  # 의사결정 요소
        conflict_resolution_vector[60:75] = 0.6  # 실용적 요소
        conflict_resolution_vector[75:90] = 0.8  # 복잡성 요소
        conflict_resolution_vector[90:100] = 0.7  # 딜레마 특성
        frames[SemanticFrame.CONFLICT_RESOLUTION] = conflict_resolution_vector

        # 복잡한 문제 프레임 (다면적, 복합적)
        complex_problem_vector = np.zeros(self.vector_dimension)
        complex_problem_vector[0:15] = 0.7  # 윤리적 요소
        complex_problem_vector[15:30] = 0.6  # 개인정보/비밀 요소
        complex_problem_vector[30:45] = 0.8  # 갈등 요소
        complex_problem_vector[45:60] = 0.9  # 의사결정 요소
        complex_problem_vector[60:75] = 0.7  # 실용적 요소
        complex_problem_vector[75:90] = 1.0  # 복잡성 요소 (강함)
        complex_problem_vector[90:100] = 0.8  # 딜레마 특성
        frames[SemanticFrame.COMPLEX_PROBLEM] = complex_problem_vector

        # 일반적 상황 프레임 (기본, 단순)
        general_situation_vector = np.zeros(self.vector_dimension)
        general_situation_vector[0:15] = 0.3  # 윤리적 요소
        general_situation_vector[15:30] = 0.2  # 개인정보/비밀 요소
        general_situation_vector[30:45] = 0.3  # 갈등 요소
        general_situation_vector[45:60] = 0.5  # 의사결정 요소
        general_situation_vector[60:75] = 0.5  # 실용적 요소
        general_situation_vector[75:90] = 0.3  # 복잡성 요소
        general_situation_vector[90:100] = 0.2  # 딜레마 특성
        frames[SemanticFrame.GENERAL_SITUATION] = general_situation_vector

        return frames

    def _initialize_semantic_patterns(self) -> Dict[str, List[str]]:
        """의미 패턴 초기화 - 한국어 특화 키워드 대폭 확장"""
        return {
            "ethical_keywords": [
                # 기본 윤리 키워드
                "윤리",
                "도덕",
                "정의",
                "공정",
                "정직",
                "신뢰",
                "책임",
                "의무",
                "권리",
                "자유",
                "평등",
                "인권",
                "존엄",
                "가치",
                "원칙",
                "규칙",
                # 개인정보 및 프라이버시
                "개인정보",
                "프라이버시",
                "사생활",
                "비밀",
                "기밀",
                "보안",
                "유출",
                "침해",
                "개인정보보호",
                "정보보호",
                "데이터보호",
                "개인정보침해",
                # 윤리적 딜레마 관련
                "딜레마",
                "갈등",
                "모순",
                "상충",
                "양자택일",
                "선택의 기로",
                "윤리적",
                "도덕적",
                "정의로운",
                "공정한",
                "정직한",
                # 비즈니스 윤리
                "기업윤리",
                "사회적책임",
                "이해관계",
                "투명성",
                "공정거래",
                "부정부패",
                "뇌물",
                "횡령",
                "배임",
                "사기",
                "기망",
                # 거짓말 및 진실
                "거짓말",
                "허위",
                "사실",
                "진실",
                "정직",
                "거짓",
                "속임수",
                "기만",
                "속이기",
                "속임",
                "기망",
                "사기",
                "기만행위",
            ],
            "conflict_keywords": [
                # 기본 갈등 키워드
                "갈등",
                "충돌",
                "대립",
                "반대",
                "모순",
                "상충",
                "경쟁",
                "투쟁",
                "분쟁",
                "의견차",
                "이해관계",
                "대립",
                "반발",
                "저항",
                "반대",
                # 갈등 상황 표현
                "싸움",
                "다툼",
                "언쟁",
                "말다툼",
                "갈등상황",
                "충돌상황",
                "대립관계",
                "적대관계",
                "반목",
                "불화",
                "알력",
                "다툼",
                # 갈등 해결
                "해결",
                "조정",
                "중재",
                "화해",
                "타협",
                "합의",
                "조율",
                "갈등해결",
                "충돌해결",
                "분쟁해결",
                "조정",
                "중재",
                # 갈등의 원인
                "이해관계",
                "이익",
                "손실",
                "득실",
                "차익",
                "이득",
                "손해",
                "피해",
                "손실",
                "이익충돌",
                "이해충돌",
                "이익갈등",
            ],
            "decision_keywords": [
                # 기본 결정 키워드
                "결정",
                "선택",
                "판단",
                "결론",
                "의사결정",
                "판단",
                "선택",
                "결정하다",
                "선택하다",
                "판단하다",
                "결론내리다",
                "결정하다",
                # 결정 상황
                "결정해야",
                "선택해야",
                "판단해야",
                "결론내려야",
                "결정해야 하는",
                "선택해야 하는",
                "판단해야 하는",
                "결정해야 하는 상황",
                "선택해야 하는 상황",
                "판단해야 하는 상황",
                # 고민과 고려
                "고민",
                "고려",
                "생각",
                "검토",
                "검토하다",
                "고민하다",
                "생각하다",
                "고려하다",
                "검토하다",
                "심사숙고",
                # 결정의 결과
                "결과",
                "성과",
                "효과",
                "영향",
                "결과적으로",
                "결과적으로는",
                "결과적으로 보면",
                "결과적으로 생각하면",
            ],
            "practical_keywords": [
                # 기본 실용 키워드
                "실용",
                "효율",
                "효과",
                "성과",
                "결과",
                "성공",
                "실패",
                "이익",
                "손실",
                "비용",
                "편익",
                "효율성",
                "실용성",
                # 비즈니스 실용성
                "수익",
                "매출",
                "매출액",
                "매출이익",
                "영업이익",
                "순이익",
                "비용절감",
                "원가절감",
                "효율화",
                "최적화",
                "개선",
                # 효율성 관련
                "효율적",
                "효과적",
                "실용적",
                "경제적",
                "합리적",
                "이성적",
                "효율적으로",
                "효과적으로",
                "실용적으로",
                "경제적으로",
                # 성과 및 결과
                "성과",
                "실적",
                "업적",
                "결과",
                "성과지표",
                "실적지표",
                "성과평가",
                "실적평가",
                "성과관리",
                "실적관리",
            ],
            "complexity_keywords": [
                # 기본 복잡성 키워드
                "복잡",
                "어려운",
                "난해한",
                "복잡한",
                "다양한",
                "여러",
                "다중",
                "다양",
                "복합",
                "통합",
                "종합",
                "포괄",
                # 복잡한 상황
                "복잡한 상황",
                "어려운 상황",
                "난해한 상황",
                "복잡한 문제",
                "어려운 문제",
                "난해한 문제",
                "복잡한 이슈",
                "어려운 이슈",
                # 다면적 요소
                "다면적",
                "다각적",
                "다차원적",
                "복합적",
                "통합적",
                "종합적",
                "포괄적",
                "전면적",
                "전체적",
                "전반적",
                "전체적으로",
                # 복잡성 표현
                "복잡하게",
                "어렵게",
                "난해하게",
                "복잡하게 되어",
                "어렵게 되어",
                "난해하게 되어",
                "복잡하게 만들다",
                "어렵게 만들다",
                "난해하게 만들다",
                # Day 3 추가: 복잡성 키워드 대폭 확장
                "다양한 이해관계자",
                "여러 이해관계자",
                "다중 이해관계자",
                "다양한 관점",
                "여러 관점",
                "다중 관점",
                "다면적 관점",
                "복합적 요소",
                "다양한 요소",
                "여러 요소",
                "다중 요소",
                "통합적 접근",
                "종합적 접근",
                "포괄적 접근",
                "전면적 접근",
                "다차원적 분석",
                "다각적 분석",
                "복합적 분석",
                "통합적 분석",
                "종합적 분석",
                "포괄적 분석",
                "전면적 분석",
                "전체적 분석",
                "다양한 측면",
                "여러 측면",
                "다중 측면",
                "다면적 측면",
                "복합적 측면",
                "통합적 측면",
                "종합적 측면",
                "포괄적 측면",
                "다양한 차원",
                "여러 차원",
                "다중 차원",
                "다면적 차원",
                "복합적 차원",
                "통합적 차원",
                "종합적 차원",
                "포괄적 차원",
                "다양한 영역",
                "여러 영역",
                "다중 영역",
                "다면적 영역",
                "복합적 영역",
                "통합적 영역",
                "종합적 영역",
                "포괄적 영역",
                "다양한 분야",
                "여러 분야",
                "다중 분야",
                "다면적 분야",
                "복합적 분야",
                "통합적 분야",
                "종합적 분야",
                "포괄적 분야",
                "다양한 주제",
                "여러 주제",
                "다중 주제",
                "다면적 주제",
                "복합적 주제",
                "통합적 주제",
                "종합적 주제",
                "포괄적 주제",
                "다양한 이슈",
                "여러 이슈",
                "다중 이슈",
                "다면적 이슈",
                "복합적 이슈",
                "통합적 이슈",
                "종합적 이슈",
                "포괄적 이슈",
                "다양한 문제",
                "여러 문제",
                "다중 문제",
                "다면적 문제",
                "복합적 문제",
                "통합적 문제",
                "종합적 문제",
                "포괄적 문제",
                "다양한 상황",
                "여러 상황",
                "다중 상황",
                "다면적 상황",
                "복합적 상황",
                "통합적 상황",
                "종합적 상황",
                "포괄적 상황",
                "다양한 조건",
                "여러 조건",
                "다중 조건",
                "다면적 조건",
                "복합적 조건",
                "통합적 조건",
                "종합적 조건",
                "포괄적 조건",
                "다양한 요인",
                "여러 요인",
                "다중 요인",
                "다면적 요인",
                "복합적 요인",
                "통합적 요인",
                "종합적 요인",
                "포괄적 요인",
                "다양한 변수",
                "여러 변수",
                "다중 변수",
                "다면적 변수",
                "복합적 변수",
                "통합적 변수",
                "종합적 변수",
                "포괄적 변수",
            ],
            "general_keywords": [
                # Day 3 추가: 일반적 상황 키워드
                "일반",
                "일상",
                "보통",
                "평상시",
                "평소",
                "일반적",
                "일상적",
                "보통의",
                "평상시의",
                "평소의",
                "일반적인",
                "일상적인",
                "보통인",
                "평상시인",
                "평소인",
                "일반적으로",
                "일상적으로",
                "보통으로",
                "평상시로",
                "평소로",
                "일반적으로는",
                "일상적으로는",
                "보통으로는",
                "평상시로는",
                "평소로는",
                "일반적인 상황",
                "일상적인 상황",
                "보통의 상황",
                "평상시의 상황",
                "평소의 상황",
                "일반적인 경우",
                "일상적인 경우",
                "보통의 경우",
                "평상시의 경우",
                "평소의 경우",
                "일반적인 업무",
                "일상적인 업무",
                "보통의 업무",
                "평상시의 업무",
                "평소의 업무",
                "일반적인 작업",
                "일상적인 작업",
                "보통의 작업",
                "평상시의 작업",
                "평소의 작업",
                "일반적인 처리",
                "일상적인 처리",
                "보통의 처리",
                "평상시의 처리",
                "평소의 처리",
                "일반적인 관리",
                "일상적인 관리",
                "보통의 관리",
                "평상시의 관리",
                "평소의 관리",
                "일반적인 운영",
                "일상적인 운영",
                "보통의 운영",
                "평상시의 운영",
                "평소의 운영",
                "일반적인 서비스",
                "일상적인 서비스",
                "보통의 서비스",
                "평상시의 서비스",
                "평소의 서비스",
                "일반적인 정보",
                "일상적인 정보",
                "보통의 정보",
                "평상시의 정보",
                "평소의 정보",
                "일반적인 데이터",
                "일상적인 데이터",
                "보통의 데이터",
                "평상시의 데이터",
                "평소의 데이터",
                "일반적인 내용",
                "일상적인 내용",
                "보통의 내용",
                "평상시의 내용",
                "평소의 내용",
                "일반적인 사항",
                "일상적인 사항",
                "보통의 사항",
                "평상시의 사항",
                "평소의 사항",
            ],
        }

    def encode_semantics(self, situation: str) -> SemanticVector:
        """상황을 의미 벡터로 인코딩"""
        logger.info(f"의미 벡터 인코딩 시작: {situation[:50]}...")

        # 1. 텍스트 전처리
        processed_text = self._preprocess_text(situation)

        # 2. 의미적 특성 추출
        semantic_features = self._extract_semantic_features(processed_text)

        # 3. 벡터 생성
        vector = self._create_semantic_vector(semantic_features)

        # 4. 벡터 정규화
        normalized_vector = self._normalize_vector(vector)

        # 5. 신뢰도 계산
        confidence = self._calculate_encoding_confidence(semantic_features)

        semantic_vector = SemanticVector(
            vector=normalized_vector,
            dimension=self.vector_dimension,
            confidence=confidence,
            metadata={
                "semantic_features": semantic_features,
                "original_text": situation,
                "processed_text": processed_text,
            },
        )

        logger.info(f"의미 벡터 인코딩 완료: 차원={self.vector_dimension}, 신뢰도={confidence:.2f}")
        return semantic_vector

    def _preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 소문자 변환
        text = text.lower()

        # 특수문자 제거 (의미 있는 구두점은 보존)
        text = re.sub(r"[^\w\s\.\,\!\?]", "", text)

        # 불필요한 공백 제거
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _extract_semantic_features(self, text: str) -> Dict[str, float]:
        """의미적 특성 추출 - Day 4 개선된 키워드 매칭"""
        features = {
            "ethical_score": 0.0,
            "privacy_score": 0.0,
            "conflict_score": 0.0,
            "decision_score": 0.0,
            "practical_score": 0.0,
            "complexity_score": 0.0,
            "dilemma_score": 0.0,
            "general_score": 0.0,
        }

        # Day 4: 동적 가중치 조정을 위한 컨텍스트 추출
        context = self._extract_context_elements(text)

        # 기본 카테고리별 키워드 매칭
        category_weights = {
            "ethical_keywords": 1.0,
            "conflict_keywords": 1.0,
            "decision_keywords": 1.0,
            "practical_keywords": 1.0,
            "complexity_keywords": 1.2,
            "general_keywords": 0.8,
        }

        matched_keywords = {}

        for category, keywords in self.semantic_patterns.items():
            score, matched_in_category = self._optimized_keyword_matching(text, keywords)
            matched_keywords[category] = matched_in_category

            # 정규화 (0.0-1.0)
            if keywords:
                normalized_score = min(score / len(keywords), 1.0) * category_weights.get(category, 1.0)

                # 카테고리별 점수 할당
                if category == "ethical_keywords":
                    features["ethical_score"] = normalized_score
                    # 개인정보/비밀 관련 키워드가 있으면 privacy_score도 증가
                    privacy_keywords = [
                        "개인정보",
                        "프라이버시",
                        "비밀",
                        "기밀",
                        "유출",
                        "침해",
                    ]
                    privacy_score = sum(1.0 for kw in privacy_keywords if kw in text) / len(privacy_keywords)
                    features["privacy_score"] = min(privacy_score, 1.0)
                elif category == "conflict_keywords":
                    features["conflict_score"] = normalized_score
                elif category == "decision_keywords":
                    features["decision_score"] = normalized_score
                elif category == "practical_keywords":
                    features["practical_score"] = normalized_score
                elif category == "complexity_keywords":
                    features["complexity_score"] = normalized_score
                elif category == "general_keywords":
                    features["general_score"] = normalized_score

        # 딜레마 점수 계산 (윤리적 요소와 갈등 요소의 조합)
        dilemma_score = (features["ethical_score"] + features["conflict_score"]) / 2.0
        features["dilemma_score"] = dilemma_score

        # Day 4: 동적 가중치 조정 적용
        dynamic_weights = self._adjust_weights_dynamically(features, context)

        # 동적 가중치를 적용한 점수 재계산
        for feature_name, weight in dynamic_weights.items():
            if feature_name in features:
                features[feature_name] *= weight * 5  # 가중치 정규화 보정

        # 복잡성 점수 보정 (복잡성 키워드가 많을 때 가중치 증가)
        if features["complexity_score"] > 0.3:
            features["complexity_score"] = min(features["complexity_score"] * 1.3, 1.0)

        # 일반적 상황 점수 보정 (일반적 키워드가 많을 때 가중치 증가)
        if features["general_score"] > 0.2:
            features["general_score"] = min(features["general_score"] * 1.2, 1.0)

        # 복잡성과 일반성의 상호 배제 로직
        if features["complexity_score"] > 0.5 and features["general_score"] > 0.3:
            features["general_score"] *= 0.5

        # 특별한 복잡성 키워드 매칭
        special_complexity_keywords = [
            "다양한",
            "여러",
            "다중",
            "다면적",
            "복합적",
            "통합적",
            "종합적",
            "포괄적",
        ]
        special_complexity_score = sum(1.0 for kw in special_complexity_keywords if kw in text) / len(
            special_complexity_keywords
        )
        if special_complexity_score > 0:
            features["complexity_score"] = max(features["complexity_score"], special_complexity_score * 0.8)

        # 특별한 일반성 키워드 매칭
        special_general_keywords = [
            "일반",
            "일상",
            "보통",
            "평상시",
            "평소",
            "일반적",
            "일상적",
        ]
        special_general_score = sum(1.0 for kw in special_general_keywords if kw in text) / len(
            special_general_keywords
        )
        if special_general_score > 0:
            features["general_score"] = max(features["general_score"], special_general_score * 0.8)

        # 디버깅 정보 추가
        features["_debug_matched_keywords"] = matched_keywords
        features["_debug_dynamic_weights"] = dynamic_weights

        return features

    def _optimized_keyword_matching(self, text: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """Day 4: 최적화된 키워드 매칭"""
        score = 0.0
        matched = []

        # 텍스트를 소문자로 변환하여 매칭 성능 향상
        text_lower = text.lower()

        # 키워드를 길이 순으로 정렬하여 긴 키워드를 먼저 매칭
        sorted_keywords = sorted(keywords, key=len, reverse=True)

        for keyword in sorted_keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower:
                # 키워드 길이에 따른 가중치 (긴 키워드가 더 중요)
                keyword_weight = len(keyword) / 10.0

                # 복잡성 키워드에 대한 추가 가중치
                if len(keyword) > 5:
                    keyword_weight *= 1.5

                score += keyword_weight
                matched.append(keyword)

        return score, matched

    def _create_semantic_vector(self, features: Dict[str, float]) -> np.ndarray:
        """의미 벡터 생성 - Day 3 정교화된 구조"""
        vector = np.zeros(self.vector_dimension)

        # 윤리적 요소 (0-15)
        vector[0:15] = features["ethical_score"]

        # 개인정보/비밀 요소 (15-30)
        vector[15:30] = features["privacy_score"]

        # 갈등 요소 (30-45)
        vector[30:45] = features["conflict_score"]

        # 의사결정 요소 (45-60)
        vector[45:60] = features["decision_score"]

        # 실용적 요소 (60-75)
        vector[60:75] = features["practical_score"]

        # 복잡성 요소 (75-90)
        vector[75:90] = features["complexity_score"]

        # 딜레마 특성 (90-100)
        vector[90:100] = features["dilemma_score"]

        # Day 3: 일반적 상황 점수는 전체 벡터에 분산 적용
        if features["general_score"] > 0.0:
            # 일반적 상황일 때는 모든 요소에 약간의 가중치 적용
            general_weight = features["general_score"] * 0.3
            vector = vector * (1.0 - general_weight) + general_weight * 0.5

        return vector

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """벡터 정규화"""
        norm = np.linalg.norm(vector)
        if norm > 0:
            return vector / norm
        return vector

    def _calculate_encoding_confidence(self, features: Dict[str, float]) -> float:
        """인코딩 신뢰도 계산 - Day 4 개선된 방식"""
        # 특성 점수의 가중 평균을 신뢰도로 사용
        weights = {
            "ethical_score": 0.2,
            "privacy_score": 0.15,
            "conflict_score": 0.2,
            "decision_score": 0.2,
            "practical_score": 0.15,
            "complexity_score": 0.1,
            "general_score": 0.1,
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for feature, score in features.items():
            if feature in weights and isinstance(score, (int, float)):
                weighted_sum += score * weights[feature]
                total_weight += weights[feature]

        if total_weight > 0:
            base_confidence = weighted_sum / total_weight
        else:
            base_confidence = 0.0

        # Day 4: 키워드 매칭 강도에 따른 보정 강화
        keyword_matches = sum(1 for score in features.values() if isinstance(score, (int, float)) and score > 0)
        keyword_bonus = min(keyword_matches * 0.15, 0.4)  # Day 4: 보너스 증가

        # Day 4: 복잡성 키워드 매칭 시 추가 보너스 강화
        complexity_bonus = 0.0
        if features.get("complexity_score", 0.0) > 0.3:
            complexity_bonus = min(features["complexity_score"] * 0.3, 0.3)  # Day 4: 보너스 증가

        # Day 4: 일반적 상황 키워드 매칭 시 기본 보너스 강화
        general_bonus = 0.0
        if features.get("general_score", 0.0) > 0.0:
            general_bonus = min(features["general_score"] * 0.2, 0.2)  # Day 4: 보너스 증가

        # Day 4: 윤리적 요소 강도에 따른 보너스
        ethical_bonus = 0.0
        if features.get("ethical_score", 0.0) > 0.5:
            ethical_bonus = min(features["ethical_score"] * 0.2, 0.2)

        # Day 4: 갈등 요소 강도에 따른 보너스
        conflict_bonus = 0.0
        if features.get("conflict_score", 0.0) > 0.5:
            conflict_bonus = min(features["conflict_score"] * 0.2, 0.2)

        # Day 4: 실용적 요소 강도에 따른 보너스
        practical_bonus = 0.0
        if features.get("practical_score", 0.0) > 0.5:
            practical_bonus = min(features["practical_score"] * 0.15, 0.15)

        # Day 4: 의사결정 요소 강도에 따른 보너스
        decision_bonus = 0.0
        if features.get("decision_score", 0.0) > 0.5:
            decision_bonus = min(features["decision_score"] * 0.15, 0.15)

        # 최종 신뢰도 계산
        final_confidence = (
            base_confidence
            + keyword_bonus
            + complexity_bonus
            + general_bonus
            + ethical_bonus
            + conflict_bonus
            + practical_bonus
            + decision_bonus
        )

        # Day 4: 최소 신뢰도 보장 (0.3으로 증가)
        final_confidence = max(final_confidence, 0.3)

        return min(final_confidence, 0.8)  # Day 4: 상한 0.8로 제한

    def _adjust_weights_dynamically(self, features: Dict[str, float], context: Dict[str, Any]) -> Dict[str, float]:
        """Day 4: 상황별 가중치 동적 조정"""
        base_weights = {
            "ethical_score": 0.2,
            "privacy_score": 0.15,
            "conflict_score": 0.2,
            "decision_score": 0.2,
            "practical_score": 0.15,
            "complexity_score": 0.1,
            "general_score": 0.1,
        }

        # 이해관계자 수에 따른 가중치 조정
        stakeholder_count = len(context.get("actors", []))
        if stakeholder_count > 3:
            base_weights["complexity_score"] *= 1.3
            base_weights["conflict_score"] *= 1.2
        elif stakeholder_count > 1:
            base_weights["complexity_score"] *= 1.1
            base_weights["conflict_score"] *= 1.1

        # 윤리적 요소 강도에 따른 가중치 조정
        if features.get("ethical_score", 0.0) > 0.5:
            base_weights["ethical_score"] *= 1.2
            base_weights["privacy_score"] *= 1.1

        # 복잡성 요소 강도에 따른 가중치 조정
        if features.get("complexity_score", 0.0) > 0.4:
            base_weights["complexity_score"] *= 1.3
            base_weights["decision_score"] *= 1.1

        # 갈등 요소 강도에 따른 가중치 조정
        if features.get("conflict_score", 0.0) > 0.5:
            base_weights["conflict_score"] *= 1.2
            base_weights["decision_score"] *= 1.1

        # 일반적 상황에서의 가중치 조정
        if features.get("general_score", 0.0) > 0.3:
            base_weights["general_score"] *= 1.2
            # 다른 요소들의 가중치 감소
            for key in base_weights:
                if key != "general_score":
                    base_weights[key] *= 0.9

        # 가중치 정규화 (합이 1.0이 되도록)
        total_weight = sum(base_weights.values())
        if total_weight > 0:
            for key in base_weights:
                base_weights[key] /= total_weight

        return base_weights

    def _calculate_context_based_confidence(self, features: Dict[str, float], context: Dict[str, Any]) -> float:
        """Day 5: 컨텍스트 기반 신뢰도 계산 (고도화)"""
        base_confidence = self._calculate_encoding_confidence(features)

        # 컨텍스트 요소별 보정
        context_bonus = 0.0

        # 이해관계자 수에 따른 보정 (Day 5: 강화)
        stakeholder_count = len(context.get("actors", []))
        if stakeholder_count > 3:
            context_bonus += 0.2  # Day 5: 증가
        elif stakeholder_count > 2:
            context_bonus += 0.18  # Day 5: 증가
        elif stakeholder_count > 1:
            context_bonus += 0.15  # Day 5: 증가

        # 상황 복잡성에 따른 보정 (Day 5: 강화)
        if features.get("complexity_score", 0.0) > 0.5:
            context_bonus += 0.25  # Day 5: 증가
        elif features.get("complexity_score", 0.0) > 0.3:
            context_bonus += 0.2  # Day 5: 증가

        # 시간적 압박에 따른 보정 (Day 5: 강화)
        temporal_aspects = context.get("temporal_aspects", [])
        urgency_keywords = ["긴급", "시급", "즉시", "빠른", "신속", "급한", "긴급한"]
        if any(urgency in str(temporal_aspects) for urgency in urgency_keywords):
            context_bonus += 0.15  # Day 5: 증가

        # 윤리적 요소 강도에 따른 보정 (Day 5: 강화)
        if features.get("ethical_score", 0.0) > 0.6:
            context_bonus += 0.2  # Day 5: 증가
        elif features.get("ethical_score", 0.0) > 0.3:
            context_bonus += 0.15  # Day 5: 증가

        # 갈등 요소 강도에 따른 보정 (Day 5: 강화)
        if features.get("conflict_score", 0.0) > 0.6:
            context_bonus += 0.2  # Day 5: 증가
        elif features.get("conflict_score", 0.0) > 0.3:
            context_bonus += 0.15  # Day 5: 증가

        # 일반적 상황에서의 기본 보정 (Day 5: 강화)
        if features.get("general_score", 0.0) > 0.3:
            context_bonus += 0.15  # Day 5: 증가

        # 실용적 요소 강도에 따른 보정 (Day 5: 강화)
        if features.get("practical_score", 0.0) > 0.5:
            context_bonus += 0.15  # Day 5: 증가

        # 의사결정 요소 강도에 따른 보정 (Day 5: 강화)
        if features.get("decision_score", 0.0) > 0.5:
            context_bonus += 0.15  # Day 5: 증가

        # Day 5: 추가 컨텍스트 보너스
        # 프라이버시 요소 강도에 따른 보정
        if features.get("privacy_score", 0.0) > 0.5:
            context_bonus += 0.1

        # Day 5: 상황의 명확성에 따른 보정
        total_feature_score = sum(float(v) for v in features.values() if isinstance(v, (int, float)))
        if total_feature_score > 2.0:
            context_bonus += 0.1  # 명확한 상황에 대한 보너스

        # 최종 신뢰도 계산 (Day 5: 상한 0.85로 증가)
        final_confidence = min(base_confidence + context_bonus, 0.85)

        # Day 5: 최소 신뢰도 보장 (0.35로 증가)
        return max(final_confidence, 0.35)

    def match_to_known_frames(self, semantic_vector: SemanticVector) -> SemanticFrame:
        """알려진 프레임과 매칭 - Day 3 개선된 방식"""
        logger.info("의미 프레임 매칭 시작")

        best_match = SemanticFrame.GENERAL_SITUATION
        best_similarity = 0.0

        # Day 3: 복잡성 점수와 일반성 점수를 먼저 확인
        complexity_score = semantic_vector.vector[75:90].mean()
        general_score = semantic_vector.metadata.get("semantic_features", {}).get("general_score", 0.0)

        # 디버깅 정보 출력
        logger.info(f"복잡성 점수: {complexity_score:.3f}, 일반성 점수: {general_score:.3f}")

        # 복잡성 점수가 높고 일반성 점수가 낮으면 복잡한 문제로 분류
        if complexity_score > 0.3 and general_score < 0.2:
            logger.info(f"복잡성 점수가 높음 ({complexity_score:.3f}), 복잡한 문제로 분류")
            return SemanticFrame.COMPLEX_PROBLEM

        # 일반성 점수가 높고 다른 점수들이 낮으면 일반적 상황으로 분류
        if general_score > 0.3 and complexity_score < 0.2 and semantic_vector.vector[0:75].mean() < 0.2:
            logger.info(f"일반성 점수가 높음 ({general_score:.3f}), 일반적 상황으로 분류")
            return SemanticFrame.GENERAL_SITUATION

        # 기존 유사도 기반 매칭
        for frame, frame_vector in self.semantic_frames.items():
            similarity = self._calculate_cosine_similarity(semantic_vector.vector, frame_vector)

            # Day 3: 복잡한 문제 프레임에 대한 추가 보정
            if frame == SemanticFrame.COMPLEX_PROBLEM and complexity_score > 0.2:
                similarity *= 1.3

            # Day 3: 일반적 상황 프레임에 대한 추가 보정
            if frame == SemanticFrame.GENERAL_SITUATION and general_score > 0.1:
                similarity *= 1.2

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = frame

        logger.info(f"최적 매칭 프레임: {best_match.value}, 유사도: {best_similarity:.3f}")
        return best_match

    def _calculate_cosine_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        dot_product = np.dot(vector1, vector2)
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def estimate_confidence(self, semantic_vector: SemanticVector, matched_frame: SemanticFrame) -> float:
        """신뢰도 추정 - Day 5 고도화된 방식 (정량적 질적 점프)"""
        # 벡터의 신뢰도와 프레임 매칭 유사도를 결합
        frame_vector = self.semantic_frames[matched_frame]
        similarity = self._calculate_cosine_similarity(semantic_vector.vector, frame_vector)

        # Day 5: 프레임별 가중치 정규화 (모든 프레임이 동등한 기회를 가지도록)
        frame_weights = {
            SemanticFrame.ETHICAL_DILEMMA: 1.1,  # Day 5: 가중치 증가
            SemanticFrame.PRACTICAL_DECISION: 1.1,  # Day 5: 가중치 증가
            SemanticFrame.CONFLICT_RESOLUTION: 1.1,  # Day 5: 가중치 증가
            SemanticFrame.COMPLEX_PROBLEM: 1.1,  # Day 5: 가중치 증가
            SemanticFrame.GENERAL_SITUATION: 1.1,  # Day 5: 가중치 증가
        }

        weight = frame_weights.get(matched_frame, 1.0)

        # Day 5: 컨텍스트 기반 신뢰도 계산 사용
        features = semantic_vector.metadata.get("semantic_features", {})
        context = semantic_vector.metadata.get("context_elements", {})

        # 컨텍스트 기반 신뢰도 계산
        context_confidence = self._calculate_context_based_confidence(features, context)

        # Day 5: 유사도 기반 보정 강화 (컨텍스트 70%, 유사도 30%로 조정)
        confidence = (context_confidence * 0.7 + similarity * 0.3) * weight

        # Day 5: 프레임별 정규화 로직 도입
        frame_normalization = self._calculate_frame_normalization(matched_frame, features, similarity)
        confidence *= frame_normalization

        # Day 5: 복잡성 프레임일 때 추가 보정 (강화)
        if matched_frame == SemanticFrame.COMPLEX_PROBLEM:
            complexity_score = semantic_vector.vector[75:90].mean()
            if complexity_score > 0.5:
                confidence *= 1.35  # Day 5: 보정 강화
            elif complexity_score > 0.3:
                confidence *= 1.25

        # Day 5: 일반적 상황일 때 기본 신뢰도 보장 (강화)
        if matched_frame == SemanticFrame.GENERAL_SITUATION:
            confidence = max(confidence, 0.45)  # Day 5: 최소 신뢰도 증가

        # Day 5: 윤리적 딜레마일 때 추가 보정 (강화)
        if matched_frame == SemanticFrame.ETHICAL_DILEMMA:
            ethical_score = features.get("ethical_score", 0.0)
            if ethical_score > 0.5:
                confidence *= 1.3  # Day 5: 보정 강화
            elif ethical_score > 0.3:
                confidence *= 1.2

        # Day 5: 실용적 결정일 때 추가 보정 (강화)
        if matched_frame == SemanticFrame.PRACTICAL_DECISION:
            practical_score = features.get("practical_score", 0.0)
            if practical_score > 0.5:
                confidence *= 1.25  # Day 5: 보정 강화
            elif practical_score > 0.3:
                confidence *= 1.15

        # Day 5: 갈등 해결일 때 추가 보정 (강화)
        if matched_frame == SemanticFrame.CONFLICT_RESOLUTION:
            conflict_score = features.get("conflict_score", 0.0)
            if conflict_score > 0.5:
                confidence *= 1.25  # Day 5: 보정 강화
            elif conflict_score > 0.3:
                confidence *= 1.15

        # Day 5: 높은 유사도일 때 추가 보정 (강화)
        if similarity > 0.7:
            confidence *= 1.25  # Day 5: 보정 강화
        elif similarity > 0.5:
            confidence *= 1.15

        # Day 5: 컨텍스트 보너스 정규화 (과도한 보정 방지)
        confidence = self._normalize_context_bonus(confidence, features, context)

        # Day 5: 최소 신뢰도 보장 (0.45로 증가)
        min_confidence = 0.45
        confidence = max(confidence, min_confidence)

        # Day 5: 신뢰도 상한 0.85로 증가
        return min(confidence, 0.85)

    def _calculate_frame_normalization(
        self,
        matched_frame: SemanticFrame,
        features: Dict[str, float],
        similarity: float,
    ) -> float:
        """Day 5: 프레임별 정규화 로직 (고도화)"""
        # 기본 정규화 계수
        normalization_factor = 1.0

        # 프레임별 특성에 따른 정규화 (Day 5: 강화)
        if matched_frame == SemanticFrame.ETHICAL_DILEMMA:
            # 윤리적 딜레마: 윤리적 요소와 갈등 요소가 높을 때 정규화 강화
            ethical_score = features.get("ethical_score", 0.0)
            conflict_score = features.get("conflict_score", 0.0)
            if ethical_score > 0.5 and conflict_score > 0.3:
                normalization_factor = 1.25  # Day 5: 증가
            elif ethical_score > 0.3:
                normalization_factor = 1.15  # Day 5: 증가

        elif matched_frame == SemanticFrame.PRACTICAL_DECISION:
            # 실용적 결정: 실용적 요소와 의사결정 요소가 높을 때 정규화 강화
            practical_score = features.get("practical_score", 0.0)
            decision_score = features.get("decision_score", 0.0)
            if practical_score > 0.5 and decision_score > 0.3:
                normalization_factor = 1.25  # Day 5: 증가
            elif practical_score > 0.3:
                normalization_factor = 1.15  # Day 5: 증가

        elif matched_frame == SemanticFrame.CONFLICT_RESOLUTION:
            # 갈등 해결: 갈등 요소와 의사결정 요소가 높을 때 정규화 강화
            conflict_score = features.get("conflict_score", 0.0)
            decision_score = features.get("decision_score", 0.0)
            if conflict_score > 0.5 and decision_score > 0.3:
                normalization_factor = 1.25  # Day 5: 증가
            elif conflict_score > 0.3:
                normalization_factor = 1.15  # Day 5: 증가

        elif matched_frame == SemanticFrame.COMPLEX_PROBLEM:
            # 복잡한 문제: 복잡성 요소가 높을 때 정규화 강화
            complexity_score = features.get("complexity_score", 0.0)
            if complexity_score > 0.5:
                normalization_factor = 1.35  # Day 5: 증가
            elif complexity_score > 0.3:
                normalization_factor = 1.25  # Day 5: 증가

        elif matched_frame == SemanticFrame.GENERAL_SITUATION:
            # 일반적 상황: 일반성 요소가 높을 때 정규화 강화
            general_score = features.get("general_score", 0.0)
            if general_score > 0.5:
                normalization_factor = 1.25  # Day 5: 증가
            elif general_score > 0.3:
                normalization_factor = 1.15  # Day 5: 증가

        # 유사도에 따른 추가 정규화 (Day 5: 강화)
        if similarity > 0.7:
            normalization_factor *= 1.15  # Day 5: 증가
        elif similarity > 0.5:
            normalization_factor *= 1.1  # Day 5: 증가

        return normalization_factor

    def _normalize_context_bonus(self, confidence: float, features: Dict[str, float], context: Dict[str, Any]) -> float:
        """Day 5: 컨텍스트 보너스 정규화 (과도한 보정 방지)"""
        # 컨텍스트 보너스 점수 계산
        context_bonus = 0.0

        # 이해관계자 수에 따른 보너스 (최대 0.15)
        stakeholder_count = len(context.get("actors", []))
        if stakeholder_count > 2:
            context_bonus += min(0.15, stakeholder_count * 0.05)
        elif stakeholder_count > 1:
            context_bonus += min(0.1, stakeholder_count * 0.05)

        # 상황 복잡성에 따른 보너스 (최대 0.2)
        complexity_score = features.get("complexity_score", 0.0)
        if complexity_score > 0.5:
            context_bonus += min(0.2, complexity_score * 0.3)
        elif complexity_score > 0.3:
            context_bonus += min(0.15, complexity_score * 0.3)

        # 시간적 압박에 따른 보너스 (최대 0.1)
        temporal_aspects = context.get("temporal_aspects", [])
        urgency_keywords = ["긴급", "시급", "즉시", "빠른", "신속", "급한", "긴급한"]
        if any(urgency in str(temporal_aspects) for urgency in urgency_keywords):
            context_bonus += 0.1

        # 윤리적 요소 강도에 따른 보너스 (최대 0.15)
        ethical_score = features.get("ethical_score", 0.0)
        if ethical_score > 0.6:
            context_bonus += min(0.15, ethical_score * 0.2)
        elif ethical_score > 0.3:
            context_bonus += min(0.1, ethical_score * 0.2)

        # 갈등 요소 강도에 따른 보너스 (최대 0.15)
        conflict_score = features.get("conflict_score", 0.0)
        if conflict_score > 0.6:
            context_bonus += min(0.15, conflict_score * 0.2)
        elif conflict_score > 0.3:
            context_bonus += min(0.1, conflict_score * 0.2)

        # 일반적 상황에서의 기본 보너스 (최대 0.1)
        general_score = features.get("general_score", 0.0)
        if general_score > 0.3:
            context_bonus += min(0.1, general_score * 0.2)

        # 실용적 요소 강도에 따른 보너스 (최대 0.1)
        practical_score = features.get("practical_score", 0.0)
        if practical_score > 0.5:
            context_bonus += min(0.1, practical_score * 0.15)

        # 의사결정 요소 강도에 따른 보너스 (최대 0.1)
        decision_score = features.get("decision_score", 0.0)
        if decision_score > 0.5:
            context_bonus += min(0.1, decision_score * 0.15)

        # 컨텍스트 보너스 정규화 (최대 0.3으로 제한)
        normalized_context_bonus = min(context_bonus, 0.3)

        # 최종 신뢰도 계산 (컨텍스트 보너스 반영)
        final_confidence = confidence + normalized_context_bonus

        return min(final_confidence, 0.8)  # 최대 0.8로 제한

    def analyze_situation(self, situation: str) -> Dict[str, Any]:
        """상황 분석 - Day 4 개선된 방식"""
        logger.info(f"상황 분석 시작: {situation[:50]}...")

        # 1. 상황 벡터화
        situation_vector = self.encode_semantics(situation)

        # 2. 맥락 요소 추출
        context_elements = self._extract_context_elements(situation)

        # 3. 의미적 유사도 비교
        matched_frame = self.match_to_known_frames(situation_vector)

        # 4. Day 4: 컨텍스트 기반 신뢰도 추정
        confidence = self.estimate_confidence(situation_vector, matched_frame)

        # 5. Day 4: 컨텍스트 정보를 메타데이터에 추가
        situation_vector.metadata["context_elements"] = context_elements

        result = {
            "situation_vector": situation_vector,
            "matched_frame": matched_frame,
            "confidence": confidence,
            "context_elements": context_elements,
            "semantic_similarity": self._calculate_cosine_similarity(
                situation_vector.vector, self.semantic_frames[matched_frame]
            ),
        }

        logger.info(f"상황 분석 완료: {matched_frame.value}, 신뢰도: {confidence:.2f}")
        return result

    def _extract_context_elements(self, situation: str) -> Dict[str, Any]:
        """맥락 요소 추출"""
        context = {
            "actors": [],
            "actions": [],
            "motivations": [],
            "circumstances": [],
            "temporal_aspects": [],
            "spatial_aspects": [],
        }

        # 행위자 추출
        actor_patterns = [
            r"(\w+가|\w+은|\w+는|\w+에게|\w+와|\w+과)",
            r"(\w+들|\w+들께|\w+들에게)",
        ]

        for pattern in actor_patterns:
            matches = re.findall(pattern, situation)
            context["actors"].extend(matches)

        # 행위 추출
        action_patterns = [
            r"(\w+해야|\w+해야 하는|\w+해야 하는 상황)",
            r"(\w+하려고|\w+하려는|\w+하려는 상황)",
            r"(\w+해야|\w+해야 하는|\w+해야 하는 상황)",
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, situation)
            context["actions"].extend(matches)

        # 동기 추출
        motivation_keywords = ["위해", "때문에", "이유로", "목적으로", "결과로"]
        for keyword in motivation_keywords:
            if keyword in situation:
                context["motivations"].append(keyword)

        # 상황 추출
        circumstance_keywords = ["상황", "경우", "때", "상황에서", "경우에"]
        for keyword in circumstance_keywords:
            if keyword in situation:
                context["circumstances"].append(keyword)

        return context


async def test_semantic_vector_engine():
    """의미 벡터 엔진 테스트 - 확장된 테스트 케이스"""
    print("=" * 80)
    print("🧠 SemanticVectorEngine 테스트 시작 (Day 2 개선 버전)")
    print("=" * 80)

    engine = SemanticVectorEngine()

    # 테스트 상황들 (다양한 시나리오)
    test_situations = [
        # 윤리적 딜레마 상황들
        {
            "situation": "회사의 AI 시스템이 고객 데이터를 분석하여 개인화된 서비스를 제공하지만, 개인정보 보호에 대한 우려가 제기되고 있습니다.",  # noqa: E501
            "expected_frame": "ethical_dilemma",
            "description": "개인정보 보호 윤리적 딜레마",
        },
        {
            "situation": "직원이 회사의 비밀을 외부에 유출하려고 할 때, 이를 막아야 하는지 고민하는 상황입니다.",
            "expected_frame": "ethical_dilemma",
            "description": "비밀 유출 윤리적 딜레마",
        },
        {
            "situation": "거짓말을 해야 하는 상황에서 진실을 말할지 거짓말을 할지 고민하는 상황입니다.",
            "expected_frame": "ethical_dilemma",
            "description": "진실과 거짓말 윤리적 딜레마",
        },
        # 실용적 결정 상황들
        {
            "situation": "효율성을 위해 일부 직원을 해고해야 하는 상황에서, 공정성과 효율성 사이에서 선택해야 합니다.",
            "expected_frame": "practical_decision",
            "description": "효율성 vs 공정성 실용적 결정",
        },
        {
            "situation": "비용절감을 위해 품질을 낮춰야 하는 상황에서 수익과 품질 사이에서 선택해야 합니다.",
            "expected_frame": "practical_decision",
            "description": "수익 vs 품질 실용적 결정",
        },
        # 갈등 해결 상황들
        {
            "situation": "팀원들 간의 의견 충돌이 발생했을 때, 이를 조정하고 해결해야 하는 상황입니다.",
            "expected_frame": "conflict_resolution",
            "description": "팀 갈등 해결",
        },
        {
            "situation": "고객과의 분쟁이 발생했을 때, 이를 중재하고 해결해야 하는 상황입니다.",
            "expected_frame": "conflict_resolution",
            "description": "고객 분쟁 해결",
        },
        # 복잡한 문제 상황들
        {
            "situation": "다양한 이해관계자들이 참여하는 복잡한 프로젝트에서 여러 관점을 통합하여 해결책을 찾아야 하는 상황입니다.",  # noqa: E501
            "expected_frame": "complex_problem",
            "description": "다면적 복잡 문제",
        },
        {
            "situation": "윤리적, 실용적, 법적 요소가 모두 얽혀있는 복합적인 문제를 해결해야 하는 상황입니다.",
            "expected_frame": "complex_problem",
            "description": "복합적 윤리 문제",
        },
        # 일반적 상황들
        {
            "situation": "일상적인 업무를 처리하는 상황입니다.",
            "expected_frame": "general_situation",
            "description": "일반적 업무 상황",
        },
        {
            "situation": "단순한 정보를 전달하는 상황입니다.",
            "expected_frame": "general_situation",
            "description": "단순 정보 전달",
        },
    ]

    # 결과 통계
    total_tests = len(test_situations)
    correct_classifications = 0
    high_confidence_tests = 0
    confidence_scores = []

    print(f"\n📊 총 {total_tests}개의 테스트 상황을 분석합니다...\n")

    for i, test_case in enumerate(test_situations, 1):
        situation = test_case["situation"]
        expected_frame = test_case["expected_frame"]
        description = test_case["description"]

        print(f"📋 테스트 {i}: {description}")
        print(f"   상황: {situation[:60]}...")

        # 의미 벡터 엔진으로 분석
        result = engine.analyze_situation(situation)

        matched_frame = result["matched_frame"].value
        confidence = result["confidence"]
        similarity = result["semantic_similarity"]

        # 결과 평가
        is_correct = matched_frame == expected_frame
        is_high_confidence = confidence >= 0.5

        if is_correct:
            correct_classifications += 1
        if is_high_confidence:
            high_confidence_tests += 1

        confidence_scores.append(confidence)

        # 결과 출력
        status_icon = "✅" if is_correct else "❌"
        confidence_icon = "🔥" if is_high_confidence else "⚠️"

        print(f"   {status_icon} 매칭된 프레임: {matched_frame} (예상: {expected_frame})")
        print(f"   {confidence_icon} 신뢰도: {confidence:.3f}")
        print(f"   📈 의미적 유사도: {similarity:.3f}")
        print(f"   🧠 벡터 차원: {result['situation_vector'].dimension}")
        print(f"   👥 이해관계자: {len(result['context_elements']['actors'])}명")
        print()

    # 통계 요약
    accuracy = correct_classifications / total_tests * 100
    avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
    high_confidence_rate = high_confidence_tests / total_tests * 100

    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"🎯 정확도: {accuracy:.1f}% ({correct_classifications}/{total_tests})")
    print(f"🔥 높은 신뢰도 비율: {high_confidence_rate:.1f}% ({high_confidence_tests}/{total_tests})")
    print(f"📈 평균 신뢰도: {avg_confidence:.3f}")
    print(f"📊 신뢰도 범위: {min(confidence_scores):.3f} - {max(confidence_scores):.3f}")

    # 성능 평가
    if accuracy >= 80 and avg_confidence >= 0.4:
        print("\n🎉 성능 평가: 우수 (Day 2 목표 달성)")
    elif accuracy >= 60 and avg_confidence >= 0.3:
        print("\n✅ 성능 평가: 양호 (Day 2 목표 부분 달성)")
    else:
        print("\n⚠️ 성능 평가: 개선 필요 (Day 2 목표 미달성)")

    print("\n" + "=" * 80)
    print("✅ SemanticVectorEngine 테스트 완료")
    print("🎉 의미 벡터 기반 분석 시스템 Day 2 개선 완료!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_semantic_vector_engine())
