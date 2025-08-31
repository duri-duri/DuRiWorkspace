#!/usr/bin/env python3
"""
DuRi 감정 필터 시스템 - 간소화된 버전
함수 depth 2단계 제한, 조건-매핑 방식 적용
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class EmotionCategory(Enum):
    """감정 카테고리"""
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"

class EmotionIntensity(Enum):
    """감정 강도"""
    VERY_LOW = 0.1
    LOW = 0.3
    MEDIUM = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9

class JudgmentBias(Enum):
    """판단 편향 유형"""
    EMOTIONAL_BIAS = "emotional_bias"
    CONFIRMATION_BIAS = "confirmation_bias"
    ANCHORING_BIAS = "anchoring_bias"
    AVAILABILITY_BIAS = "availability_bias"
    NONE = "none"

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
    response_type: str
    cognitive_load: float
    processing_priority: float

class EnhancedEmotionFilter:
    """고도화된 감정 필터 시스템 - 간소화된 버전"""
    
    def __init__(self):
        self.active = False
        self.current_emotion = None
        self.emotion_history = []
        self.bias_detection_enabled = True
        self.meta_cognition_enabled = True
        
        # 감정 키워드 매핑 (조건-매핑 방식)
        self.emotion_keywords = {
            EmotionCategory.JOY: {
                "keywords": ["기쁘", "좋아", "행복", "즐거", "신나", "만족", "성공", "완성"],
                "intensity_indicators": ["매우", "정말", "완전", "대박", "최고"],
                "bias_risk": 0.3
            },
            EmotionCategory.ANGER: {
                "keywords": ["화나", "짜증", "분노", "열받", "빡치", "불만"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.8
            },
            EmotionCategory.FEAR: {
                "keywords": ["무서", "두려", "불안", "걱정", "공포", "긴장", "스트레스"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.7
            },
            EmotionCategory.SADNESS: {
                "keywords": ["슬프", "우울", "속상", "실망", "절망", "외로"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.6
            },
            EmotionCategory.SURPRISE: {
                "keywords": ["놀라", "깜짝", "예상", "갑자기", "뜻밖"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.4
            },
            EmotionCategory.DISGUST: {
                "keywords": ["역겨", "싫어", "혐오", "짜증", "불쾌"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.5
            },
            EmotionCategory.TRUST: {
                "keywords": ["믿어", "신뢰", "확신", "안전", "보장"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.2
            },
            EmotionCategory.ANTICIPATION: {
                "keywords": ["기대", "희망", "미래", "계획", "준비"],
                "intensity_indicators": ["매우", "정말", "완전", "진짜", "너무"],
                "bias_risk": 0.3
            }
        }
        
        logger.info("고도화된 감정 필터 시스템 초기화 완료")
    
    def set_active(self, status: bool):
        """필터 활성화/비활성화"""
        self.active = status
        logger.info(f"감정 필터 활성화 상태: {status}")
    
    def analyze_emotion(self, text: str, context: Optional[Dict[str, Any]] = None) -> EmotionAnalysis:
        """감정 분석 (간소화된 구조)"""
        if not self.active:
            return self._create_neutral_analysis()
        
        # 1. 감정 카테고리 분석
        emotion_scores = self._analyze_emotion_categories(text)
        
        # 2. 주요 감정 결정
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        # 3. 강도 분석
        intensity = self._analyze_emotion_intensity(text, primary_emotion)
        
        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(emotion_scores, text)
        
        # 5. 보조 감정 식별
        secondary_emotions = self._identify_secondary_emotions(emotion_scores, primary_emotion)
        
        # 6. 편향 감지
        bias = self._detect_judgment_bias(text, primary_emotion)
        
        # 7. 메타 인식 분석
        meta_cognition = self._analyze_meta_cognition(text, primary_emotion, bias)
        
        analysis = EmotionAnalysis(
            primary_emotion=primary_emotion,
            intensity=intensity,
            confidence=confidence,
            secondary_emotions=secondary_emotions,
            bias_detected=bias,
            meta_cognition=meta_cognition,
            timestamp=datetime.now().isoformat()
        )
        
        self.current_emotion = analysis
        self.emotion_history.append(analysis)
        
        return analysis
    
    def _analyze_emotion_categories(self, text: str) -> Dict[EmotionCategory, float]:
        """감정 카테고리 분석 (조건-매핑 방식)"""
        emotion_scores = {category: 0.0 for category in EmotionCategory}
        
        for category, config in self.emotion_keywords.items():
            score = 0.0
            for keyword in config["keywords"]:
                if keyword in text:
                    score += 1.0
            
            # 강도 지시어 확인
            for indicator in config["intensity_indicators"]:
                if indicator in text:
                    score += 0.5
            
            emotion_scores[category] = min(1.0, score / len(config["keywords"]))
        
        return emotion_scores
    
    def _analyze_emotion_intensity(self, text: str, emotion: EmotionCategory) -> EmotionIntensity:
        """감정 강도 분석"""
        config = self.emotion_keywords.get(emotion, {})
        intensity_indicators = config.get("intensity_indicators", [])
        
        intensity_count = sum(1 for indicator in intensity_indicators if indicator in text)
        
        # 조건-매핑 방식으로 강도 결정
        intensity_mapping = {
            0: EmotionIntensity.LOW,
            1: EmotionIntensity.MEDIUM,
            2: EmotionIntensity.HIGH,
            3: EmotionIntensity.VERY_HIGH
        }
        
        return intensity_mapping.get(intensity_count, EmotionIntensity.MEDIUM)
    
    def _calculate_confidence(self, emotion_scores: Dict[EmotionCategory, float], text: str) -> float:
        """신뢰도 계산"""
        max_score = max(emotion_scores.values())
        total_score = sum(emotion_scores.values())
        
        if total_score == 0:
            return 0.0
        
        # 간소화된 신뢰도 계산
        confidence = max_score / total_score if total_score > 0 else 0.0
        return min(1.0, confidence)
    
    def _identify_secondary_emotions(self, emotion_scores: Dict[EmotionCategory, float], primary: EmotionCategory) -> List[EmotionCategory]:
        """보조 감정 식별"""
        threshold = 0.3
        secondary = []
        
        for category, score in emotion_scores.items():
            if category != primary and score > threshold:
                secondary.append(category)
        
        return secondary[:3]  # 최대 3개
    
    def _detect_judgment_bias(self, text: str, emotion: EmotionCategory) -> JudgmentBias:
        """판단 편향 감지"""
        config = self.emotion_keywords.get(emotion, {})
        bias_risk = config.get("bias_risk", 0.5)
        
        # 강도 지시어가 많을수록 편향 위험 증가
        intensity_indicators = config.get("intensity_indicators", [])
        intensity_count = sum(1 for indicator in intensity_indicators if indicator in text)
        
        if intensity_count >= 2 and bias_risk > 0.6:
            return JudgmentBias.EMOTIONAL_BIAS
        
        return JudgmentBias.NONE
    
    def _analyze_meta_cognition(self, text: str, emotion: EmotionCategory, bias: JudgmentBias) -> Dict[str, Any]:
        """메타 인식 분석"""
        return {
            "emotion_awareness": self._assess_emotion_awareness(text),
            "regulation_capability": self._assess_regulation_capability(emotion, bias),
            "empathy_level": self._assess_empathy_level(text),
            "cognitive_load": self._assess_cognitive_load(emotion, bias)
        }
    
    def _assess_emotion_awareness(self, text: str) -> float:
        """감정 인식 능력 평가"""
        awareness_indicators = ["느낌", "감정", "기분", "상태", "마음"]
        count = sum(1 for indicator in awareness_indicators if indicator in text)
        return min(1.0, count / len(awareness_indicators))
    
    def _assess_regulation_capability(self, emotion: EmotionCategory, bias: JudgmentBias) -> float:
        """감정 조절 능력 평가"""
        if bias == JudgmentBias.EMOTIONAL_BIAS:
            return 0.3
        elif emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]:
            return 0.5
        else:
            return 0.8
    
    def _assess_empathy_level(self, text: str) -> float:
        """공감 능력 평가"""
        empathy_indicators = ["이해", "공감", "같이", "함께", "도움"]
        count = sum(1 for indicator in empathy_indicators if indicator in text)
        return min(1.0, count / len(empathy_indicators))
    
    def _assess_cognitive_load(self, emotion: EmotionCategory, bias: JudgmentBias) -> float:
        """인지 부하 평가"""
        if bias == JudgmentBias.EMOTIONAL_BIAS:
            return 0.8
        elif emotion in [EmotionCategory.ANGER, EmotionCategory.FEAR]:
            return 0.7
        else:
            return 0.3
    
    def get_emotion_weight(self) -> float:
        """감정 가중치 반환"""
        if not self.current_emotion:
            return 0.0
        
        intensity_value = self.current_emotion.intensity.value
        bias_penalty = 0.2 if self.current_emotion.bias_detected != JudgmentBias.NONE else 0.0
        
        return max(0.0, intensity_value - bias_penalty)
    
    def get_processing_recommendations(self) -> Dict[str, Any]:
        """처리 권장사항 반환"""
        if not self.current_emotion:
            return {"should_process": True, "priority": "normal"}
        
        bias_detected = self.current_emotion.bias_detected != JudgmentBias.NONE
        high_intensity = self.current_emotion.intensity in [EmotionIntensity.HIGH, EmotionIntensity.VERY_HIGH]
        
        return {
            "should_process": True,
            "priority": "high" if bias_detected or high_intensity else "normal",
            "bias_warning": bias_detected,
            "intensity_warning": high_intensity
        }
    
    def _create_neutral_analysis(self) -> EmotionAnalysis:
        """중립 분석 생성"""
        return EmotionAnalysis(
            primary_emotion=EmotionCategory.NEUTRAL,
            intensity=EmotionIntensity.LOW,
            confidence=1.0,
            secondary_emotions=[],
            bias_detected=JudgmentBias.NONE,
            meta_cognition={
                "emotion_awareness": 0.0,
                "regulation_capability": 1.0,
                "empathy_level": 0.0,
                "cognitive_load": 0.0
            },
            timestamp=datetime.now().isoformat()
        )
    
    def get_emotion_history(self, limit: int = 10) -> List[EmotionAnalysis]:
        """감정 히스토리 반환"""
        return self.emotion_history[-limit:] 
 
 