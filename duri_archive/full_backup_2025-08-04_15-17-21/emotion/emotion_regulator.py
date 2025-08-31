#!/usr/bin/env python3
"""
DuRi 감정 조절기 - 감정 조절 로직 분리
"""

import logging
from typing import Dict, Any, List
from .emotion_filter import EmotionCategory, EmotionIntensity, EmotionAnalysis, JudgmentBias

logger = logging.getLogger(__name__)

class EmotionRegulator:
    """감정 조절기"""
    
    def __init__(self):
        self.regulation_history = []
        self.regulation_strategies = self._initialize_strategies()
        logger.info("감정 조절기 초기화 완료")
    
    def _initialize_strategies(self) -> Dict[str, Dict[str, Any]]:
        """조절 전략 초기화"""
        return {
            EmotionCategory.ANGER: {
                "strategy": "deep_breathing",
                "priority": "high",
                "cooldown_time": 30
            },
            EmotionCategory.FEAR: {
                "strategy": "reassurance",
                "priority": "high", 
                "cooldown_time": 60
            },
            EmotionCategory.SADNESS: {
                "strategy": "comfort",
                "priority": "medium",
                "cooldown_time": 45
            },
            EmotionCategory.JOY: {
                "strategy": "moderation",
                "priority": "low",
                "cooldown_time": 15
            }
        }
    
    def regulate_emotion(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """감정 조절 수행"""
        if emotion_analysis.bias_detected == JudgmentBias.NONE:
            return {"regulated": False, "reason": "no_regulation_needed"}
        
        # 조절 전략 선택
        strategy = self._select_regulation_strategy(emotion_analysis)
        
        # 조절 수행
        regulation_result = self._apply_regulation_strategy(emotion_analysis, strategy)
        
        # 조절 기록
        self.regulation_history.append({
            "original_emotion": emotion_analysis.primary_emotion,
            "strategy": strategy,
            "result": regulation_result,
            "timestamp": emotion_analysis.timestamp
        })
        
        return regulation_result
    
    def _select_regulation_strategy(self, emotion_analysis: EmotionAnalysis) -> str:
        """조절 전략 선택"""
        emotion = emotion_analysis.primary_emotion
        intensity = emotion_analysis.intensity
        
        # 기본 전략
        base_strategy = self.regulation_strategies.get(emotion, {}).get("strategy", "default")
        
        # 강도에 따른 전략 조정
        if intensity in [EmotionIntensity.HIGH, EmotionIntensity.VERY_HIGH]:
            if emotion == EmotionCategory.ANGER:
                return "immediate_calm"
            elif emotion == EmotionCategory.FEAR:
                return "immediate_reassurance"
            else:
                return "intensive_regulation"
        else:
            return base_strategy
    
    def _apply_regulation_strategy(self, emotion_analysis: EmotionAnalysis, strategy: str) -> Dict[str, Any]:
        """조절 전략 적용"""
        strategies = {
            "deep_breathing": self._apply_deep_breathing,
            "reassurance": self._apply_reassurance,
            "comfort": self._apply_comfort,
            "moderation": self._apply_moderation,
            "immediate_calm": self._apply_immediate_calm,
            "immediate_reassurance": self._apply_immediate_reassurance,
            "intensive_regulation": self._apply_intensive_regulation,
            "default": self._apply_default_regulation
        }
        
        strategy_func = strategies.get(strategy, self._apply_default_regulation)
        return strategy_func(emotion_analysis)
    
    def _apply_deep_breathing(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """깊은 호흡 조절"""
        return {
            "regulated": True,
            "strategy": "deep_breathing",
            "effectiveness": 0.8,
            "duration": 30,
            "message": "깊은 호흡을 통해 감정을 조절해보세요."
        }
    
    def _apply_reassurance(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """안심 조절"""
        return {
            "regulated": True,
            "strategy": "reassurance",
            "effectiveness": 0.7,
            "duration": 60,
            "message": "걱정하지 마세요. 상황을 차분히 살펴보세요."
        }
    
    def _apply_comfort(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """위로 조절"""
        return {
            "regulated": True,
            "strategy": "comfort",
            "effectiveness": 0.6,
            "duration": 45,
            "message": "슬픈 감정을 인정하고 위로받으세요."
        }
    
    def _apply_moderation(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """절제 조절"""
        return {
            "regulated": True,
            "strategy": "moderation",
            "effectiveness": 0.5,
            "duration": 15,
            "message": "기쁨을 적절히 조절하여 지속하세요."
        }
    
    def _apply_immediate_calm(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """즉시 진정"""
        return {
            "regulated": True,
            "strategy": "immediate_calm",
            "effectiveness": 0.9,
            "duration": 10,
            "message": "즉시 진정하고 상황을 재평가하세요."
        }
    
    def _apply_immediate_reassurance(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """즉시 안심"""
        return {
            "regulated": True,
            "strategy": "immediate_reassurance",
            "effectiveness": 0.8,
            "duration": 20,
            "message": "즉시 안심하고 안전한 상황임을 확인하세요."
        }
    
    def _apply_intensive_regulation(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """집중 조절"""
        return {
            "regulated": True,
            "strategy": "intensive_regulation",
            "effectiveness": 0.7,
            "duration": 60,
            "message": "집중적인 감정 조절이 필요합니다."
        }
    
    def _apply_default_regulation(self, emotion_analysis: EmotionAnalysis) -> Dict[str, Any]:
        """기본 조절"""
        return {
            "regulated": True,
            "strategy": "default",
            "effectiveness": 0.5,
            "duration": 30,
            "message": "감정을 조절해보세요."
        }
    
    def get_regulation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """조절 히스토리 반환"""
        return self.regulation_history[-limit:]
    
    def get_regulation_effectiveness(self) -> float:
        """조절 효과성 계산"""
        if not self.regulation_history:
            return 0.0
        
        total_effectiveness = sum(r["result"]["effectiveness"] for r in self.regulation_history)
        return total_effectiveness / len(self.regulation_history) 