#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 이해 시스템 - 맥락 분석기

텍스트의 다양한 맥락을 분석하는 기능을 제공합니다.
- 시간적 맥락 분석
- 공간적 맥락 분석
- 사회적 맥락 분석
- 주제적 맥락 분석
- 감정적 맥락 분석
"""

from dataclasses import dataclass
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ContextAnalysisResult:
    """맥락 분석 결과"""

    temporal_context: Dict[str, Any]
    spatial_context: Dict[str, Any]
    social_context: Dict[str, Any]
    topical_context: Dict[str, Any]
    emotional_context: Dict[str, Any]
    context_meaning: str
    confidence: float


class ContextAnalyzer:
    """맥락 분석기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("맥락 분석기 초기화 완료")

    async def analyze_context(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """맥락 분석"""
        try:
            # 시간적 맥락
            temporal_context = self._extract_temporal_context(text)

            # 공간적 맥락
            spatial_context = self._extract_spatial_context(text)

            # 사회적 맥락
            social_context = self._extract_social_context(text)

            # 주제적 맥락
            topical_context = self._extract_topical_context(text)

            # 감정적 맥락
            emotional_context = self._extract_emotional_context(text)

            # 통합 맥락 의미
            context_meaning = self._integrate_context_meaning(
                temporal_context,
                spatial_context,
                social_context,
                topical_context,
                emotional_context,
            )

            return {
                "temporal_context": temporal_context,
                "spatial_context": spatial_context,
                "social_context": social_context,
                "topical_context": topical_context,
                "emotional_context": emotional_context,
                "context_meaning": context_meaning,
                "confidence": 0.85,
            }
        except Exception as e:
            self.logger.error(f"맥락 분석 중 오류 발생: {e}")
            return self._create_fallback_context()

    def _extract_temporal_context(self, text: str) -> Dict[str, Any]:
        """시간적 맥락 추출"""
        # 시간 관련 키워드 패턴
        time_patterns = [
            r"오늘|어제|내일|이번|다음|지난|이전",
            r"년|월|일|시|분|초",
            r"아침|점심|저녁|밤|새벽",
        ]

        temporal_keywords = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            temporal_keywords.extend(matches)

        return {
            "temporal_keywords": temporal_keywords,
            "temporal_relevance": (
                len(temporal_keywords) / len(text.split()) if text.split() else 0
            ),
        }

    def _extract_spatial_context(self, text: str) -> Dict[str, Any]:
        """공간적 맥락 추출"""
        # 공간 관련 키워드 패턴
        spatial_patterns = [
            r"집|학교|회사|병원|상점|공원|역|공항",
            r"위|아래|앞|뒤|왼쪽|오른쪽|안|밖",
            r"서울|부산|대구|인천|광주|대전|울산",
        ]

        spatial_keywords = []
        for pattern in spatial_patterns:
            matches = re.findall(pattern, text)
            spatial_keywords.extend(matches)

        return {
            "spatial_keywords": spatial_keywords,
            "spatial_relevance": (
                len(spatial_keywords) / len(text.split()) if text.split() else 0
            ),
        }

    def _extract_social_context(self, text: str) -> Dict[str, Any]:
        """사회적 맥락 추출"""
        # 사회적 관계 키워드
        social_keywords = re.findall(
            r"가족|친구|동료|선생님|학생|부모|자식|형제|자매", text
        )

        return {
            "social_keywords": social_keywords,
            "social_relevance": (
                len(social_keywords) / len(text.split()) if text.split() else 0
            ),
        }

    def _extract_topical_context(self, text: str) -> Dict[str, Any]:
        """주제적 맥락 추출"""
        # 주제 관련 키워드
        topic_keywords = re.findall(
            r"학습|교육|일|취미|운동|음식|여행|영화|음악|책", text
        )

        return {
            "topic_keywords": topic_keywords,
            "topic_relevance": (
                len(topic_keywords) / len(text.split()) if text.split() else 0
            ),
        }

    def _extract_emotional_context(self, text: str) -> Dict[str, Any]:
        """감정적 맥락 추출"""
        # 감정 관련 키워드
        emotion_keywords = re.findall(
            r"기쁨|슬픔|화남|놀람|두려움|사랑|미움|희망|절망|감사", text
        )

        return {
            "emotion_keywords": emotion_keywords,
            "emotion_relevance": (
                len(emotion_keywords) / len(text.split()) if text.split() else 0
            ),
        }

    def _integrate_context_meaning(
        self,
        temporal_context: Dict,
        spatial_context: Dict,
        social_context: Dict,
        topical_context: Dict,
        emotional_context: Dict,
    ) -> str:
        """맥락 의미 통합"""
        context_elements = []

        if temporal_context["temporal_relevance"] > 0.1:
            context_elements.append("시간적 맥락이 중요한 대화")

        if spatial_context["spatial_relevance"] > 0.1:
            context_elements.append("공간적 맥락이 중요한 대화")

        if social_context["social_relevance"] > 0.1:
            context_elements.append("사회적 관계가 중요한 대화")

        if topical_context["topic_relevance"] > 0.1:
            context_elements.append("특정 주제에 관한 대화")

        if emotional_context["emotion_relevance"] > 0.1:
            context_elements.append("감정적 표현이 중요한 대화")

        if not context_elements:
            return "일반적인 대화"

        return " + ".join(context_elements)

    def _create_fallback_context(self) -> Dict[str, Any]:
        """폴백 맥락 생성"""
        return {
            "temporal_context": {"temporal_keywords": [], "temporal_relevance": 0.0},
            "spatial_context": {"spatial_keywords": [], "spatial_relevance": 0.0},
            "social_context": {"social_keywords": [], "social_relevance": 0.0},
            "topical_context": {"topic_keywords": [], "topic_relevance": 0.0},
            "emotional_context": {"emotion_keywords": [], "emotion_relevance": 0.0},
            "context_meaning": "일반적인 대화",
            "confidence": 0.0,
        }
