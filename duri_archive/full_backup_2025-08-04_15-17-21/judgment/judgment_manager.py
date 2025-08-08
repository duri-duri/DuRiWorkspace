#!/usr/bin/env python3
"""
DuRi 판단 관리자 - 판단 시스템 통합 관리
"""

import logging
from typing import Dict, Any, Optional
from .bias_detector import BiasDetector
from .level_up_approval import LevelUpApproval

logger = logging.getLogger(__name__)

class JudgmentManager:
    """판단 시스템 통합 관리자"""
    
    def __init__(self):
        self.bias_detector = BiasDetector()
        self.level_up_approval = LevelUpApproval()
        
        logger.info("판단 관리자 초기화 완료")
    
    def approve_level_up(self, quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """레벨업 승인 (Growth 연동용)"""
        # 플레이스홀더 데이터 (실제로는 growth_manager에서 가져와야 함)
        growth_metrics = {
            "emotional_maturity": 0.6,
            "cognitive_development": 0.5,
            "social_skills": 0.4,
            "self_motivation": 0.7
        }
        
        emotion_state = {
            "bias_level": 0.3,
            "cognitive_load": 0.4,
            "regulation_capability": 0.8
        }
        
        return self.level_up_approval.approve_level_up(
            growth_metrics=growth_metrics,
            emotion_state=emotion_state,
            quest_result=quest_result
        )
    
    def detect_biases(self, judgment_context: str, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """편향 탐지"""
        bias_analysis = self.bias_detector.detect_biases(judgment_context, decision_data)
        
        return {
            "overall_bias_score": bias_analysis.overall_bias_score,
            "detected_biases": len(bias_analysis.detected_biases),
            "bias_mitigation_plan": bias_analysis.bias_mitigation_plan,
            "reliability": 1.0 - bias_analysis.overall_bias_score
        }
    
    def get_judgment_status(self) -> Dict[str, Any]:
        """판단 상태 반환"""
        bias_metrics = self.bias_detector.get_bias_metrics()
        
        return {
            "bias_metrics": bias_metrics,
            "recent_analyses": len(self.bias_detector.get_bias_analysis_history()),
            "recent_detections": len(self.bias_detector.get_bias_detection_history())
        }
    
    def get_bias_history(self, limit: int = 10) -> Dict[str, Any]:
        """편향 히스토리 반환"""
        return {
            "detections": self.bias_detector.get_bias_detection_history(limit),
            "analyses": self.bias_detector.get_bias_analysis_history(limit)
        }
    
    def get_judgment_for_growth(self) -> Dict[str, Any]:
        """성장 시스템용 판단 정보 반환"""
        return {
            "bias_detection_enabled": True,
            "approval_system_enabled": True,
            "reliability_threshold": 0.6,
            "bias_threshold": 0.5
        } 