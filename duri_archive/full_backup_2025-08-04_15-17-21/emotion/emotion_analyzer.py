#!/usr/bin/env python3
"""
DuRi 감정 분석기 - 감정 분석 로직 분리
"""

import logging
from typing import Dict, Any, List
from .emotion_filter import EmotionCategory, EmotionIntensity, EmotionAnalysis

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    """감정 분석기"""
    
    def __init__(self):
        self.analysis_history = []
        logger.info("감정 분석기 초기화 완료")
    
    def analyze_emotion_patterns(self, emotion_history: List[EmotionAnalysis]) -> Dict[str, Any]:
        """감정 패턴 분석"""
        if not emotion_history:
            return {"pattern": "none", "stability": 0.0, "trend": "stable"}
        
        # 감정 변화 패턴 분석
        emotions = [e.primary_emotion for e in emotion_history]
        intensities = [e.intensity.value for e in emotion_history]
        
        # 안정성 계산
        stability = self._calculate_emotion_stability(emotions, intensities)
        
        # 트렌드 분석
        trend = self._analyze_emotion_trend(emotions, intensities)
        
        # 주요 감정 패턴
        pattern = self._identify_emotion_pattern(emotions)
        
        return {
            "pattern": pattern,
            "stability": stability,
            "trend": trend,
            "dominant_emotion": self._find_dominant_emotion(emotions)
        }
    
    def _calculate_emotion_stability(self, emotions: List[EmotionCategory], intensities: List[float]) -> float:
        """감정 안정성 계산"""
        if len(emotions) < 2:
            return 1.0
        
        # 감정 변화 횟수
        emotion_changes = 0
        for i in range(1, len(emotions)):
            if emotions[i] != emotions[i-1]:
                emotion_changes += 1
        
        # 강도 변화
        intensity_variance = sum(abs(intensities[i] - intensities[i-1]) for i in range(1, len(intensities)))
        
        # 안정성 점수 (높을수록 안정적)
        stability = 1.0 - (emotion_changes / len(emotions)) - (intensity_variance / len(intensities))
        return max(0.0, min(1.0, stability))
    
    def _analyze_emotion_trend(self, emotions: List[EmotionCategory], intensities: List[float]) -> str:
        """감정 트렌드 분석"""
        if len(intensities) < 3:
            return "stable"
        
        # 최근 3개 강도 변화
        recent_intensities = intensities[-3:]
        
        if recent_intensities[2] > recent_intensities[1] > recent_intensities[0]:
            return "increasing"
        elif recent_intensities[2] < recent_intensities[1] < recent_intensities[0]:
            return "decreasing"
        else:
            return "fluctuating"
    
    def _identify_emotion_pattern(self, emotions: List[EmotionCategory]) -> str:
        """감정 패턴 식별"""
        if not emotions:
            return "none"
        
        # 가장 빈번한 감정
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        dominant_ratio = emotion_counts[dominant_emotion] / len(emotions)
        
        if dominant_ratio > 0.7:
            return f"dominant_{dominant_emotion.value}"
        elif dominant_ratio > 0.5:
            return f"frequent_{dominant_emotion.value}"
        else:
            return "mixed"
    
    def _find_dominant_emotion(self, emotions: List[EmotionCategory]) -> EmotionCategory:
        """주요 감정 찾기"""
        if not emotions:
            return EmotionCategory.NEUTRAL
        
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return max(emotion_counts.items(), key=lambda x: x[1])[0] 