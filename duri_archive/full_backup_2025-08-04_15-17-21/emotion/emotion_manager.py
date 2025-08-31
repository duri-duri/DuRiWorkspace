#!/usr/bin/env python3
"""
DuRi 감정 관리자 - 감정 시스템 통합 관리
"""

import logging
from typing import Dict, Any, Optional
from .emotion_filter import EnhancedEmotionFilter, EmotionAnalysis
from .emotion_analyzer import EmotionAnalyzer
from .emotion_regulator import EmotionRegulator

logger = logging.getLogger(__name__)

class EmotionManager:
    """감정 시스템 통합 관리자"""
    
    def __init__(self):
        self.emotion_filter = EnhancedEmotionFilter()
        self.emotion_analyzer = EmotionAnalyzer()
        self.emotion_regulator = EmotionRegulator()
        
        # 감정 필터 활성화
        self.emotion_filter.set_active(True)
        
        logger.info("감정 관리자 초기화 완료")
    
    def analyze_emotion(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """감정 분석 통합 처리"""
        # 1. 감정 분석
        emotion_analysis = self.emotion_filter.analyze_emotion(text, context)
        
        # 2. 감정 조절 필요 여부 확인
        regulation_result = self.emotion_regulator.regulate_emotion(emotion_analysis)
        
        # 3. 감정 패턴 분석
        emotion_history = self.emotion_filter.get_emotion_history()
        pattern_analysis = self.emotion_analyzer.analyze_emotion_patterns(emotion_history)
        
        # 4. 통합 결과 반환
        return {
            "emotion_analysis": emotion_analysis,
            "regulation_result": regulation_result,
            "pattern_analysis": pattern_analysis,
            "processing_recommendations": self.emotion_filter.get_processing_recommendations(),
            "emotion_weight": self.emotion_filter.get_emotion_weight()
        }
    
    def get_emotion_state(self) -> Dict[str, Any]:
        """현재 감정 상태 반환"""
        current_emotion = self.emotion_filter.current_emotion
        
        if not current_emotion:
            return {
                "current_emotion": "neutral",
                "intensity": 0.0,
                "bias_detected": False,
                "regulation_needed": False
            }
        
        return {
            "current_emotion": current_emotion.primary_emotion.value,
            "intensity": current_emotion.intensity.value,
            "bias_detected": current_emotion.bias_detected.value != "none",
            "regulation_needed": current_emotion.bias_detected.value != "none",
            "confidence": current_emotion.confidence,
            "meta_cognition": current_emotion.meta_cognition
        }
    
    def get_emotion_history(self, limit: int = 10) -> Dict[str, Any]:
        """감정 히스토리 반환"""
        emotion_history = self.emotion_filter.get_emotion_history(limit)
        regulation_history = self.emotion_regulator.get_regulation_history(limit)
        
        return {
            "emotion_history": emotion_history,
            "regulation_history": regulation_history,
            "pattern_analysis": self.emotion_analyzer.analyze_emotion_patterns(emotion_history),
            "regulation_effectiveness": self.emotion_regulator.get_regulation_effectiveness()
        }
    
    def set_emotion_filter_active(self, status: bool):
        """감정 필터 활성화/비활성화"""
        self.emotion_filter.set_active(status)
        logger.info(f"감정 필터 활성화 상태 변경: {status}")
    
    def get_emotion_for_judgment(self) -> Dict[str, Any]:
        """판단 시스템용 감정 정보 반환"""
        current_emotion = self.emotion_filter.current_emotion
        
        if not current_emotion:
            return {
                "emotion_state": "neutral",
                "bias_level": 0.0,
                "cognitive_load": 0.0,
                "regulation_capability": 1.0
            }
        
        return {
            "emotion_state": current_emotion.primary_emotion.value,
            "bias_level": 0.8 if current_emotion.bias_detected.value != "none" else 0.0,
            "cognitive_load": current_emotion.meta_cognition.get("cognitive_load", 0.0),
            "regulation_capability": current_emotion.meta_cognition.get("regulation_capability", 1.0),
            "emotion_awareness": current_emotion.meta_cognition.get("emotion_awareness", 0.0),
            "empathy_level": current_emotion.meta_cognition.get("empathy_level", 0.0)
        } 