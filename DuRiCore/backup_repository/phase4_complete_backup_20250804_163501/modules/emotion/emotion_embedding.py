#!/usr/bin/env python3
"""
DuRiCore - NLP 기반 감정 임베딩 모듈
실제 AI 기능: 규칙 기반 → NLP 기반 감정 분석
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class EmotionCategory(Enum):
    """감정 카테고리"""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    LOVE = "love"
    CONTEMPT = "contempt"
    ANTICIPATION = "anticipation"


@dataclass
class EmotionEmbedding:
    """감정 임베딩 결과"""

    primary_emotion: EmotionCategory
    secondary_emotions: List[EmotionCategory]
    intensity: float  # 0.0 ~ 1.0
    confidence: float  # 0.0 ~ 1.0
    emotional_context: str
    sentiment_score: float  # -1.0 ~ 1.0
    emotional_keywords: List[str]
    emotional_patterns: List[str]


class NLPEmotionEmbedding:
    """NLP 기반 감정 임베딩 시스템"""

    def __init__(self):
        # 감정 키워드 사전
        self.emotion_keywords = {
            EmotionCategory.JOY: [
                "기쁘다",
                "행복하다",
                "즐겁다",
                "신나다",
                "좋다",
                "만족하다",
                "웃다",
                "미소",
                "환호",
                "축하",
                "성공",
                "승리",
                "희망",
            ],
            EmotionCategory.SADNESS: [
                "슬프다",
                "우울하다",
                "속상하다",
                "실망하다",
                "외롭다",
                "그립다",
                "눈물",
                "한숨",
                "절망",
                "상실",
                "이별",
                "고독",
                "비통",
            ],
            EmotionCategory.ANGER: [
                "화나다",
                "분노하다",
                "짜증나다",
                "열받다",
                "격분하다",
                "욱하다",
                "폭발",
                "참을수없다",
                "억울하다",
                "원망",
                "적대",
                "복수",
            ],
            EmotionCategory.FEAR: [
                "무섭다",
                "겁나다",
                "두렵다",
                "불안하다",
                "걱정하다",
                "공포",
                "떨다",
                "긴장",
                "불안",
                "공포",
                "위험",
                "위협",
                "불안정",
            ],
            EmotionCategory.SURPRISE: [
                "놀라다",
                "깜짝",
                "충격",
                "예상밖",
                "어이없다",
                "헉",
                "어쩌지",
                "어떻게",
                "갑자기",
                "뜻밖",
                "예상외",
            ],
            EmotionCategory.DISGUST: [
                "역겹다",
                "싫다",
                "혐오",
                "구역질",
                "더럽다",
                "지저분",
                "불쾌",
                "악취",
                "더러움",
                "혐오감",
                "싫어하다",
            ],
            EmotionCategory.LOVE: [
                "사랑하다",
                "좋아하다",
                "그립다",
                "그리워하다",
                "보고싶다",
                "애정",
                "따뜻함",
                "포근함",
                "안전함",
                "신뢰",
                "믿음",
            ],
            EmotionCategory.CONTEMPT: [
                "경멸",
                "무시",
                "하찮다",
                "별거아니다",
                "실망",
                "실망하다",
                "무가치",
                "쓸모없다",
                "허무",
                "허탈",
            ],
            EmotionCategory.ANTICIPATION: [
                "기대하다",
                "설레다",
                "긴장하다",
                "준비하다",
                "계획하다",
                "미래",
                "희망",
                "꿈",
                "목표",
                "동경",
                "열망",
            ],
        }

        # 감정 강도 표현어
        self.intensity_indicators = {
            "매우": 0.9,
            "정말": 0.8,
            "너무": 0.8,
            "완전": 0.9,
            "진짜": 0.7,
            "그냥": 0.3,
            "약간": 0.2,
            "조금": 0.2,
            "별로": 0.1,
            "전혀": 0.0,
        }

        # 부정어
        self.negation_words = ["아니", "안", "못", "없", "하지않", "안되", "못하"]

        # 문맥 키워드
        self.context_keywords = {
            "일상": ["오늘", "어제", "내일", "평소", "보통", "일반적"],
            "일": ["업무", "회사", "직장", "일하다", "업무", "프로젝트"],
            "관계": ["친구", "가족", "연인", "동료", "사람", "관계"],
            "건강": ["병", "아프다", "건강", "운동", "식사", "수면"],
            "취미": ["취미", "관심", "좋아하다", "즐기다", "시간"],
        }

        logger.info("NLP 감정 임베딩 시스템 초기화 완료")

    def analyze_emotion(self, text: str) -> EmotionEmbedding:
        """텍스트의 감정을 분석하여 임베딩 생성"""
        try:
            # 1. 감정 키워드 검출
            detected_emotions = self._detect_emotion_keywords(text)

            # 2. 감정 강도 계산
            intensity = self._calculate_emotion_intensity(text, detected_emotions)

            # 3. 주요 감정 결정
            primary_emotion = self._determine_primary_emotion(
                detected_emotions, intensity
            )

            # 4. 보조 감정들
            secondary_emotions = self._get_secondary_emotions(
                detected_emotions, primary_emotion
            )

            # 5. 감정 신뢰도 계산
            confidence = self._calculate_confidence(detected_emotions, intensity)

            # 6. 감정적 맥락 분석
            emotional_context = self._analyze_emotional_context(text)

            # 7. 감정 점수 계산
            sentiment_score = self._calculate_sentiment_score(
                text, primary_emotion, intensity
            )

            # 8. 감정 키워드 추출
            emotional_keywords = self._extract_emotional_keywords(
                text, detected_emotions
            )

            # 9. 감정 패턴 추출
            emotional_patterns = self._extract_emotional_patterns(text)

            return EmotionEmbedding(
                primary_emotion=primary_emotion,
                secondary_emotions=secondary_emotions,
                intensity=intensity,
                confidence=confidence,
                emotional_context=emotional_context,
                sentiment_score=sentiment_score,
                emotional_keywords=emotional_keywords,
                emotional_patterns=emotional_patterns,
            )

        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return self._create_default_embedding()

    def _detect_emotion_keywords(self, text: str) -> Dict[EmotionCategory, List[str]]:
        """감정 키워드 검출"""
        detected = {}
        text_lower = text.lower()

        for emotion, keywords in self.emotion_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)

            if found_keywords:
                detected[emotion] = found_keywords

        return detected

    def _calculate_emotion_intensity(
        self, text: str, detected_emotions: Dict[EmotionCategory, List[str]]
    ) -> float:
        """감정 강도 계산"""
        if not detected_emotions:
            return 0.1  # 기본값

        # 강도 표현어 검출
        intensity_score = 0.5  # 기본 강도

        for indicator, score in self.intensity_indicators.items():
            if indicator in text:
                intensity_score = max(intensity_score, score)

        # 감정 키워드 수에 따른 보정
        total_keywords = sum(len(keywords) for keywords in detected_emotions.values())
        if total_keywords > 3:
            intensity_score = min(1.0, intensity_score + 0.2)

        # 부정어 처리
        if self._has_negation(text):
            intensity_score = max(0.1, intensity_score - 0.3)

        return intensity_score

    def _determine_primary_emotion(
        self, detected_emotions: Dict[EmotionCategory, List[str]], intensity: float
    ) -> EmotionCategory:
        """주요 감정 결정"""
        if not detected_emotions:
            return EmotionCategory.NEUTRAL

        # 가장 많은 키워드를 가진 감정을 주요 감정으로
        max_keywords = 0
        primary_emotion = EmotionCategory.NEUTRAL

        for emotion, keywords in detected_emotions.items():
            if len(keywords) > max_keywords:
                max_keywords = len(keywords)
                primary_emotion = emotion

        return primary_emotion

    def _get_secondary_emotions(
        self,
        detected_emotions: Dict[EmotionCategory, List[str]],
        primary: EmotionCategory,
    ) -> List[EmotionCategory]:
        """보조 감정들 추출"""
        secondary = []
        for emotion in detected_emotions.keys():
            if emotion != primary:
                secondary.append(emotion)

        return secondary[:3]  # 최대 3개까지만

    def _calculate_confidence(
        self, detected_emotions: Dict[EmotionCategory, List[str]], intensity: float
    ) -> float:
        """감정 분석 신뢰도 계산"""
        if not detected_emotions:
            return 0.1

        # 키워드 수에 따른 신뢰도
        total_keywords = sum(len(keywords) for keywords in detected_emotions.values())
        keyword_confidence = min(1.0, total_keywords / 5.0)

        # 강도에 따른 신뢰도
        intensity_confidence = intensity

        # 종합 신뢰도
        confidence = (keyword_confidence + intensity_confidence) / 2.0

        return min(1.0, confidence)

    def _analyze_emotional_context(self, text: str) -> str:
        """감정적 맥락 분석"""
        context_matches = []

        for context, keywords in self.context_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    context_matches.append(context)
                    break

        if context_matches:
            return ", ".join(context_matches)
        else:
            return "일반적"

    def _calculate_sentiment_score(
        self, text: str, primary_emotion: EmotionCategory, intensity: float
    ) -> float:
        """감정 점수 계산 (-1.0 ~ 1.0)"""
        # 감정별 기본 점수
        emotion_scores = {
            EmotionCategory.JOY: 0.8,
            EmotionCategory.LOVE: 0.7,
            EmotionCategory.ANTICIPATION: 0.6,
            EmotionCategory.SURPRISE: 0.0,  # 중립
            EmotionCategory.NEUTRAL: 0.0,
            EmotionCategory.SADNESS: -0.6,
            EmotionCategory.FEAR: -0.7,
            EmotionCategory.ANGER: -0.8,
            EmotionCategory.DISGUST: -0.9,
            EmotionCategory.CONTEMPT: -0.5,
        }

        base_score = emotion_scores.get(primary_emotion, 0.0)

        # 강도에 따른 조정
        adjusted_score = base_score * intensity

        # 부정어 처리
        if self._has_negation(text):
            adjusted_score = -adjusted_score

        return max(-1.0, min(1.0, adjusted_score))

    def _extract_emotional_keywords(
        self, text: str, detected_emotions: Dict[EmotionCategory, List[str]]
    ) -> List[str]:
        """감정 키워드 추출"""
        keywords = []
        for emotion_keywords in detected_emotions.values():
            keywords.extend(emotion_keywords)

        return list(set(keywords))  # 중복 제거

    def _extract_emotional_patterns(self, text: str) -> List[str]:
        """감정 패턴 추출"""
        patterns = []

        # 감탄사 패턴
        exclamation_patterns = [
            r"[!！]{2,}",  # 연속된 느낌표
            r"[?？]{2,}",  # 연속된 물음표
            r"[ㅋㅋㅋ]+",  # 웃음
            r"[ㅠㅠ]+",  # 울음
        ]

        for pattern in exclamation_patterns:
            if re.search(pattern, text):
                patterns.append("강한 감정 표현")

        # 반복 패턴
        if re.search(r"(.)\1{2,}", text):
            patterns.append("감정 강조 반복")

        # 대문자 패턴
        if re.search(r"[A-Z]{3,}", text):
            patterns.append("강조 표현")

        return patterns

    def _has_negation(self, text: str) -> bool:
        """부정어 포함 여부"""
        for negation in self.negation_words:
            if negation in text:
                return True
        return False

    def _create_default_embedding(self) -> EmotionEmbedding:
        """기본 임베딩 생성"""
        return EmotionEmbedding(
            primary_emotion=EmotionCategory.NEUTRAL,
            secondary_emotions=[],
            intensity=0.1,
            confidence=0.1,
            emotional_context="일반적",
            sentiment_score=0.0,
            emotional_keywords=[],
            emotional_patterns=[],
        )

    def get_emotion_summary(self, embedding: EmotionEmbedding) -> Dict[str, Any]:
        """감정 임베딩 요약"""
        return {
            "primary_emotion": embedding.primary_emotion.value,
            "intensity": embedding.intensity,
            "confidence": embedding.confidence,
            "sentiment": embedding.sentiment_score,
            "context": embedding.emotional_context,
            "keywords": embedding.emotional_keywords,
            "patterns": embedding.emotional_patterns,
        }
