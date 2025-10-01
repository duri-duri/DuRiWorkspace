#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 이해 시스템 - 감정 분석기

텍스트의 감정을 분석하는 기능을 제공합니다.
- 감정 키워드 분석
- 감정 강도 계산
- 주요 감정 결정
"""

from dataclasses import dataclass
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class EmotionAnalysisResult:
    """감정 분석 결과"""

    primary_emotion: str
    emotion_scores: Dict[str, int]
    emotion_intensity: float
    confidence: float


class EmotionAnalyzer:
    """감정 분석기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.emotion_keywords = {
            "기쁨": ["기쁘다", "행복하다", "즐겁다", "신나다", "좋다", "만족하다"],
            "슬픔": ["슬프다", "우울하다", "속상하다", "아프다", "힘들다", "지치다"],
            "화남": ["화나다", "짜증나다", "분하다", "열받다", "화가나다", "답답하다"],
            "놀람": ["놀랍다", "깜짝", "어이없다", "헐", "와", "대박"],
            "두려움": ["무섭다", "겁나다", "불안하다", "걱정되다", "무서워하다"],
            "사랑": ["사랑하다", "좋아하다", "그립다", "보고싶다", "아끼다"],
            "미움": ["싫다", "미워하다", "짜증나다", "답답하다", "화나다"],
            "희망": ["희망적이다", "기대하다", "꿈꾸다", "바라다", "원하다"],
            "절망": ["절망적이다", "포기하다", "실망하다", "허탈하다"],
            "감사": ["감사하다", "고맙다", "은혜롭다", "축복받다"],
        }
        self.logger.info("감정 분석기 초기화 완료")

    async def analyze_emotion(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """감정 분석"""
        try:
            emotion_scores = {}

            # 각 감정별 점수 계산
            for emotion, keywords in self.emotion_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text:
                        score += 1
                emotion_scores[emotion] = score

            # 주요 감정 결정
            primary_emotion = (
                max(emotion_scores.items(), key=lambda x: x[1])[0]
                if emotion_scores
                else "중립"
            )

            # 감정 강도 계산
            total_emotion_words = sum(emotion_scores.values())
            emotion_intensity = (
                min(total_emotion_words / len(text.split()), 1.0)
                if text.split()
                else 0.0
            )

            return {
                "primary_emotion": primary_emotion,
                "emotion_scores": emotion_scores,
                "emotion_intensity": emotion_intensity,
                "confidence": 0.8 if emotion_scores else 0.5,
            }
        except Exception as e:
            self.logger.error(f"감정 분석 중 오류 발생: {e}")
            return self._create_fallback_emotion()

    def _create_fallback_emotion(self) -> Dict[str, Any]:
        """폴백 감정 생성"""
        return {
            "primary_emotion": "중립",
            "emotion_scores": {},
            "emotion_intensity": 0.0,
            "confidence": 0.0,
        }
