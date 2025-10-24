#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 생성 시스템 - 감정적 표현 생성기

감정적 표현을 생성하는 기능을 제공합니다.
- 감정적 표현 생성
- 감정적 표현 분석
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class EmotionalExpression:
    """감정적 표현 결과"""

    expression_text: str
    emotion_type: str
    intensity: float
    confidence: float


class EmotionalGenerator:
    """감정적 표현 생성기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("감정적 표현 생성기 초기화 완료")

    async def generate_emotional_expression(self, context: Dict[str, Any]) -> str:
        """감정적 표현 생성"""
        try:
            emotion = context.get("emotion", "중립")
            intensity = context.get("emotion_intensity", 0.5)

            if emotion == "기쁨":
                if intensity > 0.7:
                    return "정말 정말 기뻐요! 마음이 가벼워지는 것 같아요!"
                else:
                    return "기쁘네요. 좋은 일이 있으신가요?"
            elif emotion == "슬픔":
                if intensity > 0.7:
                    return "정말 마음이 아프시겠어요. 제가 함께 있어드릴게요."
                else:
                    return "슬픈 일이 있으신가요? 이야기해 주세요."
            elif emotion == "화남":
                if intensity > 0.7:
                    return "정말 화가 나시는 것 같아요. 차분히 생각해 보세요."
                else:
                    return "화가 나시는군요. 어떤 일이 있으셨나요?"
            else:
                return "감정을 표현해 주셔서 감사합니다."
        except Exception as e:
            self.logger.error(f"감정적 표현 생성 중 오류 발생: {e}")
            return "감정을 표현해 주셔서 감사합니다."

    async def analyze_emotional_expression(self, text: str) -> str:
        """감정적 표현 분석"""
        try:
            emotion_keywords = {
                "기쁨": ["기뻐요", "좋아요", "행복해요", "즐거워요"],
                "슬픔": ["아프시겠어요", "슬프시겠어요", "힘드시겠어요"],
                "화남": ["화가 나시는", "짜증나시는", "답답하시는"],
                "사랑": ["사랑", "좋아", "그립", "보고싶"],
            }

            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        return emotion

            return "중립"
        except Exception as e:
            self.logger.error(f"감정적 표현 분석 중 오류: {e}")
            return "중립"
