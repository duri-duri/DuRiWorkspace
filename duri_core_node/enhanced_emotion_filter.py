#!/usr/bin/env python3
"""
DuRi 고도화된 감정 필터 시스템
ChatGPT 제안 기반 감정 범주화, 세기 추정, 판단 연결, 메타 인식 구현
"""

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EmotionCategory(Enum):
    """감정 카테고리"""

    JOY = "joy"  # 기쁨
    ANGER = "anger"  # 분노
    FEAR = "fear"  # 두려움
    SADNESS = "sadness"  # 슬픔
    SURPRISE = "surprise"  # 놀람
    DISGUST = "disgust"  # 혐오
    TRUST = "trust"  # 신뢰
    ANTICIPATION = "anticipation"  # 기대
    NEUTRAL = "neutral"  # 중립


class EmotionIntensity(Enum):
    """감정 강도"""

    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


class JudgmentBias(Enum):
    """판단 편향 유형"""

    EMOTIONAL_BIAS = "emotional_bias"  # 감정 편향
    CONFIRMATION_BIAS = "confirmation_bias"  # 확인 편향
    ANCHORING_BIAS = "anchoring_bias"  # 정박 편향
    AVAILABILITY_BIAS = "availability_bias"  # 가용성 편향
    NONE = "none"  # 편향 없음


@dataclass
class EmotionAnalysis:
    """감정 분석 결과"""

    primary_emotion: EmotionCategory
    intensity: EmotionIntensity
    confidence: float
    secondary_emotions: List[EmotionCategory]
    bias_detected: JudgmentBias
    meta_cognition: Dict[str, Any]
    timestamp: str


@dataclass
class EmotionResponse:
    """감정 반응"""

    emotion: EmotionCategory
    intensity: float
    response_type: str  # "empathy", "regulation", "expression"
    cognitive_load: float
    processing_priority: float


class EnhancedEmotionFilter:
    """고도화된 감정 필터 시스템"""

    def __init__(self):
        self.active = False
        self.current_emotion = None
        self.emotion_history = []
        self.bias_detection_enabled = True
        self.meta_cognition_enabled = True

        # 감정 키워드 매핑
        self.emotion_keywords = {
            EmotionCategory.JOY: {
                "keywords": [
                    "기쁘",
                    "좋아",
                    "행복",
                    "즐거",
                    "신나",
                    "만족",
                    "성공",
                    "완성",
                ],
                "intensity_indicators": ["매우", "정말", "완전", "대박", "최고"],
                "bias_risk": 0.3,
            },
            EmotionCategory.ANGER: {
                "keywords": ["화나", "짜증", "분노", "열받", "빡치", "짜증", "불만"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.8,
            },
            EmotionCategory.FEAR: {
                "keywords": [
                    "무서",
                    "두려",
                    "불안",
                    "걱정",
                    "공포",
                    "긴장",
                    "스트레스",
                ],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.7,
            },
            EmotionCategory.SADNESS: {
                "keywords": ["슬프", "우울", "속상", "실망", "절망", "외로"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.6,
            },
            EmotionCategory.SURPRISE: {
                "keywords": ["놀라", "깜짝", "예상", "갑자기", "뜻밖"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.4,
            },
            EmotionCategory.DISGUST: {
                "keywords": ["역겨", "싫어", "혐오", "불쾌", "거부"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.5,
            },
            EmotionCategory.TRUST: {
                "keywords": ["믿어", "신뢰", "확신", "안전", "보장"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.2,
            },
            EmotionCategory.ANTICIPATION: {
                "keywords": ["기대", "희망", "궁금", "궁금해", "알고싶"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.3,
            },
        }

        # 판단 편향 패턴
        self.bias_patterns = {
            JudgmentBias.EMOTIONAL_BIAS: [
                "감정적으로",
                "화가 나서",
                "기분이 나빠서",
                "짜증나서",
            ],
            JudgmentBias.CONFIRMATION_BIAS: ["역시", "예상대로", "당연히", "분명히"],
            JudgmentBias.ANCHORING_BIAS: ["처음부터", "원래", "본래", "기본적으로"],
            JudgmentBias.AVAILABILITY_BIAS: [
                "생각나는",
                "떠오르는",
                "기억나는",
                "보이는",
            ],
        }

        logger.info("고도화된 감정 필터 시스템 초기화 완료")

    def set_active(self, status: bool):
        """활성화 상태 설정"""
        self.active = status
        logger.info(f"[EnhancedEmotionFilter] {'활성화' if status else '비활성화'}")

    def analyze_emotion(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> EmotionAnalysis:
        """고도화된 감정 분석"""
        if not self.active:
            return self._create_neutral_analysis()

        # 1. 감정 카테고리 분석
        emotion_scores = self._analyze_emotion_categories(text)
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])

        # 2. 감정 강도 분석
        intensity = self._analyze_emotion_intensity(text, primary_emotion[0])

        # 3. 신뢰도 계산
        confidence = self._calculate_confidence(emotion_scores, text)

        # 4. 보조 감정 식별
        secondary_emotions = self._identify_secondary_emotions(
            emotion_scores, primary_emotion[0]
        )

        # 5. 판단 편향 감지
        bias_detected = self._detect_judgment_bias(text, primary_emotion[0])

        # 6. 메타 인식 분석
        meta_cognition = self._analyze_meta_cognition(
            text, primary_emotion[0], bias_detected
        )

        # 7. 분석 결과 저장
        analysis = EmotionAnalysis(
            primary_emotion=primary_emotion[0],
            intensity=intensity,
            confidence=confidence,
            secondary_emotions=secondary_emotions,
            bias_detected=bias_detected,
            meta_cognition=meta_cognition,
            timestamp=datetime.now().isoformat(),
        )

        self.emotion_history.append(analysis)
        self.current_emotion = primary_emotion[0]

        logger.info(
            f"[EnhancedEmotionFilter] 감정 분석: {primary_emotion[0].value} (강도: {intensity.value}, 편향: {bias_detected.value})"
        )

        return analysis

    def _analyze_emotion_categories(self, text: str) -> Dict[EmotionCategory, float]:
        """감정 카테고리 분석"""
        emotion_scores = {emotion: 0.0 for emotion in EmotionCategory}
        text_lower = text.lower()

        for emotion, config in self.emotion_keywords.items():
            score = 0.0

            # 키워드 매칭
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 0.3

            # 강도 지시어 확인
            for indicator in config["intensity_indicators"]:
                if indicator in text_lower:
                    score += 0.2

            emotion_scores[emotion] = min(1.0, score)

        return emotion_scores

    def _analyze_emotion_intensity(
        self, text: str, emotion: EmotionCategory
    ) -> EmotionIntensity:
        """감정 강도 분석"""
        text_lower = text.lower()
        intensity_score = 0.0

        if emotion in self.emotion_keywords:
            config = self.emotion_keywords[emotion]

            # 키워드 개수
            keyword_count = sum(
                1 for keyword in config["keywords"] if keyword in text_lower
            )
            intensity_score += keyword_count * 0.1

            # 강도 지시어 개수
            indicator_count = sum(
                1
                for indicator in config["intensity_indicators"]
                if indicator in text_lower
            )
            intensity_score += indicator_count * 0.2

            # 문장 길이와 복잡성
            if len(text) > 50:
                intensity_score += 0.1

            # 반복 표현
            if any(word in text_lower for word in ["매우", "정말", "완전", "진짜"]):
                intensity_score += 0.2

        # 강도 레벨 결정
        if intensity_score >= 0.8:
            return EmotionIntensity.VERY_HIGH
        elif intensity_score >= 0.6:
            return EmotionIntensity.HIGH
        elif intensity_score >= 0.4:
            return EmotionIntensity.MEDIUM
        elif intensity_score >= 0.2:
            return EmotionIntensity.LOW
        else:
            return EmotionIntensity.VERY_LOW

    def _calculate_confidence(
        self, emotion_scores: Dict[EmotionCategory, float], text: str
    ) -> float:
        """신뢰도 계산"""
        # 최고 점수와 두 번째 점수의 차이
        sorted_scores = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_scores) < 2:
            return 0.5

        top_score = sorted_scores[0][1]
        second_score = sorted_scores[1][1]

        # 점수 차이가 클수록 신뢰도 높음
        confidence = min(1.0, (top_score - second_score) * 2 + 0.3)

        # 텍스트 길이와 복잡성 반영
        if len(text) > 20:
            confidence += 0.1

        return min(1.0, confidence)

    def _identify_secondary_emotions(
        self, emotion_scores: Dict[EmotionCategory, float], primary: EmotionCategory
    ) -> List[EmotionCategory]:
        """보조 감정 식별"""
        secondary_emotions = []

        for emotion, score in emotion_scores.items():
            if emotion != primary and score > 0.3:
                secondary_emotions.append(emotion)

        return secondary_emotions[:2]  # 최대 2개

    def _detect_judgment_bias(
        self, text: str, emotion: EmotionCategory
    ) -> JudgmentBias:
        """판단 편향 감지"""
        if not self.bias_detection_enabled:
            return JudgmentBias.NONE

        text_lower = text.lower()

        # 감정 기반 편향 위험도 확인
        if emotion in self.emotion_keywords:
            bias_risk = self.emotion_keywords[emotion]["bias_risk"]
            if bias_risk > 0.6:
                return JudgmentBias.EMOTIONAL_BIAS

        # 패턴 기반 편향 감지
        for bias_type, patterns in self.bias_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return bias_type

        return JudgmentBias.NONE

    def _analyze_meta_cognition(
        self, text: str, emotion: EmotionCategory, bias: JudgmentBias
    ) -> Dict[str, Any]:
        """메타 인식 분석"""
        if not self.meta_cognition_enabled:
            return {}

        meta_analysis = {
            "emotion_awareness": self._assess_emotion_awareness(text),
            "regulation_capability": self._assess_regulation_capability(emotion, bias),
            "empathy_level": self._assess_empathy_level(text),
            "cognitive_load": self._assess_cognitive_load(emotion, bias),
        }

        return meta_analysis

    def _assess_emotion_awareness(self, text: str) -> float:
        """감정 인식 수준 평가"""
        awareness_indicators = ["느끼", "생각", "인식", "알겠", "이해"]

        score = 0.0
        for indicator in awareness_indicators:
            if indicator in text.lower():
                score += 0.2

        return min(1.0, score)

    def _assess_regulation_capability(
        self, emotion: EmotionCategory, bias: JudgmentBias
    ) -> float:
        """감정 조절 능력 평가"""
        # 강한 감정과 편향이 있으면 조절 능력 낮음
        if (
            emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]
            and bias != JudgmentBias.NONE
        ):
            return 0.3

        # 중립적이거나 약한 감정이면 조절 능력 높음
        if emotion in [EmotionCategory.NEUTRAL, EmotionCategory.TRUST]:
            return 0.8

        return 0.5

    def _assess_empathy_level(self, text: str) -> float:
        """공감 수준 평가"""
        empathy_indicators = ["이해", "공감", "동감", "같이", "함께", "도움"]

        score = 0.0
        for indicator in empathy_indicators:
            if indicator in text.lower():
                score += 0.2

        return min(1.0, score)

    def _assess_cognitive_load(
        self, emotion: EmotionCategory, bias: JudgmentBias
    ) -> float:
        """인지 부하 평가"""
        # 강한 감정과 편향이 있으면 인지 부하 높음
        if bias != JudgmentBias.NONE:
            return 0.8

        if emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]:
            return 0.7

        if emotion in [EmotionCategory.NEUTRAL, EmotionCategory.TRUST]:
            return 0.3

        return 0.5

    def get_emotion_weight(self) -> float:
        """감정 가중치 반환"""
        if not self.current_emotion:
            return 0.2

        # 현재 감정의 강도에 따른 가중치
        if self.current_emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]:
            return 0.8
        elif self.current_emotion in [EmotionCategory.JOY, EmotionCategory.TRUST]:
            return 0.6
        else:
            return 0.4

    def get_processing_recommendations(self) -> Dict[str, Any]:
        """처리 권장사항 반환"""
        if not self.current_emotion:
            return {"should_process": True, "priority": "normal"}

        # 감정 기반 권장사항
        if self.current_emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]:
            return {
                "should_process": True,
                "priority": "high",
                "bias_risk": "high",
                "regulation_needed": True,
            }
        elif self.current_emotion in [EmotionCategory.JOY, EmotionCategory.TRUST]:
            return {
                "should_process": True,
                "priority": "normal",
                "bias_risk": "low",
                "regulation_needed": False,
            }
        else:
            return {
                "should_process": True,
                "priority": "normal",
                "bias_risk": "medium",
                "regulation_needed": False,
            }

    def _create_neutral_analysis(self) -> EmotionAnalysis:
        """중립 분석 결과 생성"""
        return EmotionAnalysis(
            primary_emotion=EmotionCategory.NEUTRAL,
            intensity=EmotionIntensity.VERY_LOW,
            confidence=0.5,
            secondary_emotions=[],
            bias_detected=JudgmentBias.NONE,
            meta_cognition={},
            timestamp=datetime.now().isoformat(),
        )

    def get_emotion_history(self, limit: int = 10) -> List[EmotionAnalysis]:
        """감정 히스토리 반환"""
        return self.emotion_history[-limit:] if self.emotion_history else []


# 전역 인스턴스
enhanced_emotion_filter = EnhancedEmotionFilter()
