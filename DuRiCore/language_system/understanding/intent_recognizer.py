#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 이해 시스템 - 의도 인식기

텍스트의 의도를 인식하는 기능을 제공합니다.
- 질문 의도 인식
- 요청 의도 인식
- 명령 의도 인식
- 감정표현 의도 인식
"""

from dataclasses import dataclass
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class IntentRecognitionResult:
    """의도 인식 결과"""

    primary_intent: str
    intent_scores: Dict[str, int]
    confidence: float


class IntentRecognizer:
    """의도 인식기"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.intent_patterns = {
            "질문": [r"\?$", r"무엇|어떤|어디|언제|누가|왜|어떻게"],
            "요청": [r"해주세요", r"부탁", r"도와", r"좀", r"해달라"],
            "명령": [r"해라", r"하라", r"해야", r"필요", r"해야지"],
            "감정표현": [r"기쁘다", r"슬프다", r"화나다", r"좋다", r"싫다"],
            "정보제공": [r"~입니다", r"~이에요", r"~야", r"~다"],
            "동의": [r"맞다", r"그렇다", r"옳다", r"좋다", r"네"],
            "반대": [r"아니다", r"틀렸다", r"싫다", r"안된다", r"아니요"],
        }
        self.logger.info("의도 인식기 초기화 완료")

    async def recognize_intent(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """의도 인식"""
        try:
            intent_scores = {}

            # 각 의도별 점수 계산
            for intent, patterns in self.intent_patterns.items():
                score = 0
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    score += len(matches)
                intent_scores[intent] = score

            # 주요 의도 결정
            primary_intent = (
                max(intent_scores.items(), key=lambda x: x[1])[0]
                if intent_scores
                else "일반"
            )

            return {
                "primary_intent": primary_intent,
                "intent_scores": intent_scores,
                "confidence": 0.8 if intent_scores else 0.5,
            }
        except Exception as e:
            self.logger.error(f"의도 인식 중 오류 발생: {e}")
            return self._create_fallback_intent()

    def _create_fallback_intent(self) -> Dict[str, Any]:
        """폴백 의도 생성"""
        return {"primary_intent": "일반", "intent_scores": {}, "confidence": 0.0}
