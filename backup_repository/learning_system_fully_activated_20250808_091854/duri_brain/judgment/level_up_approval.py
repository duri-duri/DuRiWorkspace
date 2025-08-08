#!/usr/bin/env python3
"""
DuRi 레벨업 승인 시스템 - 판단 기반 성장
"""

import logging
from typing import Dict, Any, Optional
from .bias_detector import BiasDetector

logger = logging.getLogger(__name__)

class LevelUpApproval:
    """레벨업 승인 시스템 - 판단 기반 성장"""
    
    def __init__(self):
        self.bias_detector = BiasDetector()
        self.growth_analyzer = GrowthAnalyzer()
        
        logger.info("레벨업 승인 시스템 초기화 완료")
    
    def approve_level_up(self, growth_metrics: Dict[str, Any], 
                        emotion_state: Dict[str, Any], 
                        quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """레벨업 승인 판단"""
        try:
            # 1. 편향 분석
            bias_analysis = self._analyze_emotion_bias(emotion_state)
            
            # 2. 성장 지표 평가
            growth_score = self._evaluate_growth_metrics(growth_metrics)
            
            # 3. 퀘스트 결과 평가
            quest_score = self._evaluate_quest_result(quest_result)
            
            # 4. 종합 판단
            approval_result = self._make_final_decision(bias_analysis, growth_score, quest_score)
            
            logger.info(f"레벨업 승인 판단 완료: {approval_result['approved']}")
            
            return approval_result
            
        except Exception as e:
            logger.error(f"레벨업 승인 오류: {e}")
            return self._create_error_approval(str(e))
    
    def _analyze_emotion_bias(self, emotion_state: Dict[str, Any]) -> Dict[str, Any]:
        """감정 편향 분석"""
        bias_level = emotion_state.get("bias_level", 0.0)
        cognitive_load = emotion_state.get("cognitive_load", 0.0)
        regulation_capability = emotion_state.get("regulation_capability", 1.0)
        
        # 편향 탐지기 호출
        judgment_context = f"bias_level: {bias_level}, cognitive_load: {cognitive_load}"
        decision_data = {
            "bias_level": bias_level,
            "cognitive_load": cognitive_load,
            "regulation_capability": regulation_capability
        }
        
        bias_analysis = self.bias_detector.detect_biases(judgment_context, decision_data)
        
        return {
            "overall_bias_score": bias_analysis.overall_bias_score,
            "detected_biases": len(bias_analysis.detected_biases),
            "bias_mitigation_plan": bias_analysis.bias_mitigation_plan,
            "reliability": self._calculate_reliability(bias_analysis.overall_bias_score)
        }
    
    def _evaluate_growth_metrics(self, growth_metrics: Dict[str, Any]) -> float:
        """성장 지표 평가"""
        # 간소화된 성장 지표 평가
        emotional_maturity = growth_metrics.get("emotional_maturity", 0.0)
        cognitive_development = growth_metrics.get("cognitive_development", 0.0)
        social_skills = growth_metrics.get("social_skills", 0.0)
        self_motivation = growth_metrics.get("self_motivation", 0.0)
        
        # 가중 평균 계산
        weights = {
            "emotional_maturity": 0.3,
            "cognitive_development": 0.3,
            "social_skills": 0.2,
            "self_motivation": 0.2
        }
        
        total_score = (
            emotional_maturity * weights["emotional_maturity"] +
            cognitive_development * weights["cognitive_development"] +
            social_skills * weights["social_skills"] +
            self_motivation * weights["self_motivation"]
        )
        
        return min(1.0, total_score)
    
    def _evaluate_quest_result(self, quest_result: Dict[str, Any]) -> float:
        """퀘스트 결과 평가"""
        score = quest_result.get("score", 0.0)
        passed = quest_result.get("passed", False)
        attempts = quest_result.get("attempts", 1)
        
        # 점수 기반 평가
        base_score = score
        
        # 통과 여부 보정
        if passed:
            base_score += 0.1
        
        # 시도 횟수 페널티
        attempt_penalty = (attempts - 1) * 0.05
        final_score = max(0.0, base_score - attempt_penalty)
        
        return min(1.0, final_score)
    
    def _make_final_decision(self, bias_analysis: Dict[str, Any], 
                            growth_score: float, quest_score: float) -> Dict[str, Any]:
        """최종 판단"""
        # 편향 점수에 따른 신뢰도 계산
        bias_score = bias_analysis["overall_bias_score"]
        reliability = bias_analysis["reliability"]
        
        # 종합 점수 계산
        combined_score = (growth_score + quest_score) / 2
        
        # 승인 기준
        approval_threshold = 0.7
        reliability_threshold = 0.6
        
        # 승인 여부 결정
        approved = (combined_score >= approval_threshold and 
                   reliability >= reliability_threshold and 
                   bias_score < 0.5)
        
        # 신뢰도 계산
        confidence = min(1.0, (combined_score + reliability) / 2)
        
        # 거부 이유 생성
        reason = self._generate_approval_reason(approved, combined_score, reliability, bias_score)
        
        return {
            "approved": approved,
            "confidence": confidence,
            "reason": reason,
            "bias_score": bias_score,
            "growth_score": growth_score,
            "quest_score": quest_score,
            "reliability": reliability,
            "bias_mitigation_plan": bias_analysis["bias_mitigation_plan"]
        }
    
    def _calculate_reliability(self, bias_score: float) -> float:
        """신뢰도 계산"""
        # 편향 점수가 낮을수록 신뢰도가 높음
        reliability = 1.0 - bias_score
        return max(0.0, min(1.0, reliability))
    
    def _generate_approval_reason(self, approved: bool, combined_score: float, 
                                 reliability: float, bias_score: float) -> str:
        """승인 이유 생성"""
        if approved:
            return "모든 조건을 만족하여 레벨업을 승인합니다."
        
        reasons = []
        
        if combined_score < 0.7:
            reasons.append("성장 점수 부족")
        
        if reliability < 0.6:
            reasons.append("신뢰도 부족")
        
        if bias_score >= 0.5:
            reasons.append("편향 감지")
        
        if not reasons:
            reasons.append("기타 사유")
        
        return f"레벨업 거부: {' + '.join(reasons)}"
    
    def _create_error_approval(self, error_message: str) -> Dict[str, Any]:
        """오류 승인 결과 생성"""
        return {
            "approved": False,
            "confidence": 0.0,
            "reason": f"오류 발생: {error_message}",
            "bias_score": 1.0,
            "growth_score": 0.0,
            "quest_score": 0.0,
            "reliability": 0.0,
            "bias_mitigation_plan": "오류로 인해 분석 불가"
        }

class GrowthAnalyzer:
    """성장 분석기"""
    
    def __init__(self):
        logger.info("성장 분석기 초기화 완료")
    
    def evaluate_growth_trend(self, growth_history: list) -> Dict[str, Any]:
        """성장 트렌드 평가"""
        if not growth_history:
            return {"trend": "stable", "growth_rate": 0.0, "consistency": 0.0}
        
        # 간소화된 트렌드 분석
        recent_scores = [item.get("score", 0.0) for item in growth_history[-5:]]
        
        if len(recent_scores) < 2:
            return {"trend": "stable", "growth_rate": 0.0, "consistency": 1.0}
        
        # 성장률 계산
        growth_rate = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
        
        # 일관성 계산
        variance = sum((score - sum(recent_scores) / len(recent_scores)) ** 2 for score in recent_scores)
        consistency = 1.0 - min(1.0, variance / len(recent_scores))
        
        # 트렌드 결정
        if growth_rate > 0.1:
            trend = "increasing"
        elif growth_rate < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "growth_rate": growth_rate,
            "consistency": consistency
        } 
 
 