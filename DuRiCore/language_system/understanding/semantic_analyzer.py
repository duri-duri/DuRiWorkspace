#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 이해 시스템 - 의미 분석기

텍스트의 의미를 분석하는 기능을 제공합니다.
- 키워드 추출
- 핵심 개념 추출
- 학습 통찰 추출
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class SemanticAnalysisResult:
    """의미 분석 결과"""

    keywords: List[str]
    key_concepts: List[str]
    learning_insights: List[str]
    confidence: float


class SemanticAnalyzer:
    """의미 분석기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("의미 분석기 초기화 완료")

    async def analyze_semantics(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """의미 분석"""
        try:
            # 키워드 추출
            keywords = self._extract_keywords(text)

            # 핵심 개념 추출
            key_concepts = self._extract_key_concepts(text)

            # 학습 통찰 추출
            learning_insights = self._extract_learning_insights(text, context)

            return {
                "keywords": keywords,
                "key_concepts": key_concepts,
                "learning_insights": learning_insights,
                "confidence": 0.85,
            }
        except Exception as e:
            self.logger.error(f"의미 분석 중 오류 발생: {e}")
            return self._create_fallback_semantics()

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        try:
            # 기본 키워드 추출 (실제로는 더 정교한 NLP 기법 사용)
            words = text.split()
            word_freq = Counter(words)
            keywords = [
                word for word, freq in word_freq.most_common(5) if len(word) > 1
            ]
            return keywords
        except Exception as e:
            self.logger.error(f"키워드 추출 중 오류: {e}")
            return []

    def _extract_key_concepts(self, text: str) -> List[str]:
        """핵심 개념 추출"""
        try:
            # 핵심 개념 패턴
            concept_patterns = [
                r"학습|교육|지식|기술|능력|경험",
                r"가족|친구|관계|소통|이해|사랑",
                r"목표|계획|실행|결과|성공|실패",
                r"문제|해결|도전|어려움|극복|성장",
            ]

            concepts = []
            for pattern in concept_patterns:
                matches = re.findall(pattern, text)
                concepts.extend(matches)

            return list(set(concepts))
        except Exception as e:
            self.logger.error(f"핵심 개념 추출 중 오류: {e}")
            return []

    def _extract_learning_insights(
        self, text: str, context: Dict[str, Any] = None
    ) -> List[str]:
        """학습 통찰 추출"""
        try:
            insights = []

            # 학습 관련 패턴
            learning_patterns = [
                r"배우다|학습하다|익히다|훈련하다",
                r"경험하다|체험하다|실습하다",
                r"이해하다|깨닫다|알다|알게되다",
            ]

            for pattern in learning_patterns:
                if re.search(pattern, text):
                    insights.append("학습 경험 관련")
                    break

            # 성장 관련 패턴
            growth_patterns = [
                r"성장하다|발전하다|향상되다|개선되다",
                r"변화하다|달라지다|바뀌다",
            ]

            for pattern in growth_patterns:
                if re.search(pattern, text):
                    insights.append("성장 및 발전 관련")
                    break

            return insights
        except Exception as e:
            self.logger.error(f"학습 통찰 추출 중 오류: {e}")
            return []

    def _create_fallback_semantics(self) -> Dict[str, Any]:
        """폴백 의미 분석 생성"""
        return {
            "keywords": [],
            "key_concepts": [],
            "learning_insights": [],
            "confidence": 0.0,
        }
