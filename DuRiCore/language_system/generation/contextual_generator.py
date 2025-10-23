#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 생성 시스템 - 맥락 기반 생성기

맥락을 고려한 텍스트를 생성하는 기능을 제공합니다.
- 맥락 기반 텍스트 생성
- 맥락 관련성 평가
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

logger = logging.getLogger(__name__)


@dataclass
class ContextualText:
    """맥락 기반 텍스트 결과"""

    text: str
    context_type: str
    relevance_score: float
    confidence: float


class ContextualGenerator:
    """맥락 기반 생성기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("맥락 기반 생성기 초기화 완료")

    async def generate_contextual_text(self, context: Dict[str, Any]) -> str:
        """맥락 기반 텍스트 생성"""
        try:
            context_type = context.get("context_type", "일반")

            if context_type == "학습":
                return "학습에 대한 이야기를 나누고 계시는군요. 어떤 부분에서 도움이 필요하신가요?"
            elif context_type == "가족":
                return "가족에 대한 이야기네요. 가족 관계는 정말 중요한 부분이에요."
            elif context_type == "일":
                return "일에 대한 이야기를 하고 계시는군요. 어떤 어려움이 있으신가요?"
            else:
                return "맥락을 고려한 응답을 드리고 싶습니다. 더 구체적으로 말씀해 주세요."
        except Exception as e:
            self.logger.error(f"맥락 기반 텍스트 생성 중 오류 발생: {e}")
            return "맥락을 고려한 응답을 드리고 싶습니다. 더 구체적으로 말씀해 주세요."

    async def evaluate_contextual_relevance(self, text: str, context: Dict[str, Any]) -> float:
        """맥락 관련성 평가"""
        try:
            # 간단한 관련성 평가 (실제로는 더 정교한 방법 사용)
            context_keywords = context.get("keywords", [])
            text_words = text.split()

            if not context_keywords:
                return 0.5

            relevant_words = sum(1 for word in text_words if word in context_keywords)
            relevance = relevant_words / len(text_words) if text_words else 0.0

            return min(relevance, 1.0)
        except Exception as e:
            self.logger.error(f"맥락 관련성 평가 중 오류: {e}")
            return 0.5
