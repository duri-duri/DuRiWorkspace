"""
DuRi의 의사결정 프레임워크

이 모듈은 DuRi의 철학을 바탕으로 실제 의사결정을 수행하는 프레임워크를 제공합니다.
5단계 학습 루프와 창의성-안정성 병렬 구조의 의사결정을 지원합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from .core_belief import CoreBelief, BeliefType, get_core_belief

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """의사결정 유형"""
    LEARNING_DECISION = "learning_decision"  # 학습 관련 의사결정
    CREATIVITY_DECISION = "creativity_decision"  # 창의성 관련 의사결정
    EVOLUTION_DECISION = "evolution_decision"  # 진화 관련 의사결정
    ETHICS_DECISION = "ethics_decision"  # 윤리 관련 의사결정


class DecisionFramework:
    """
    DuRi의 의사결정 프레임워크
    
    DuRi의 철학을 바탕으로 실제 의사결정을 수행합니다.
    """
    
    def __init__(self, core_belief: CoreBelief):
        """DecisionFramework 초기화"""
        self.core_belief = core_belief
        self.decision_history: List[Dict] = []
        self.decision_weights: Dict[str, float] = {
            "learning": 0.3,
            "creativity": 0.25,
            "evolution": 0.25,
            "ethics": 0.2
        }
        
        logger.info("DecisionFramework 초기화 완료")
    
    def make_learning_decision(self, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        학습 관련 의사결정
        
        Args:
            context: 의사결정 컨텍스트
            
        Returns:
            Tuple[bool, str, Dict]: (결정 결과, 근거, 상세 정보)
        """
        try:
            # 학습 철학 조회
            learning_beliefs = self.core_belief.get_beliefs_by_type(BeliefType.LEARNING_PHILOSOPHY)
            
            # 컨텍스트 분석
            current_stage = context.get('current_stage', 'unknown')
            success_rate = context.get('success_rate', 0.0)
            failure_count = context.get('failure_count', 0)
            
            # 학습 단계별 의사결정
            if current_stage == 'imitation':
                return self._decide_imitation(context, learning_beliefs)
            elif current_stage == 'practice':
                return self._decide_practice(context, learning_beliefs)
            elif current_stage == 'feedback':
                return self._decide_feedback(context, learning_beliefs)
            elif current_stage == 'challenge':
                return self._decide_challenge(context, learning_beliefs)
            elif current_stage == 'improvement':
                return self._decide_improvement(context, learning_beliefs)
            else:
                return False, "알 수 없는 학습 단계", {"error": "unknown_stage"}
                
        except Exception as e:
            logger.error(f"학습 의사결정 실패: {e}")
            return False, f"의사결정 오류: {e}", {"error": str(e)}
    
    def make_creativity_decision(self, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        창의성 관련 의사결정
        
        Args:
            context: 의사결정 컨텍스트
            
        Returns:
            Tuple[bool, str, Dict]: (결정 결과, 근거, 상세 정보)
        """
        try:
            # 창의성 철학 조회
            creativity_beliefs = self.core_belief.get_beliefs_by_type(BeliefType.CREATIVITY_PHILOSOPHY)
            
            # 컨텍스트 분석
            dream_score = context.get('dream_score', 0.0)
            reality_score = context.get('reality_score', 0.0)
            creativity_threshold = context.get('creativity_threshold', 0.7)
            stability_threshold = context.get('stability_threshold', 0.8)
            
            # 창의성 vs 안정성 평가
            approved, reason = self.core_belief.evaluate_creativity_vs_stability(
                dream_score, reality_score
            )
            
            # Dream 전략 승격 여부 결정
            if approved and dream_score > reality_score:
                decision = True
                detailed_reason = f"Dream 전략 승격: {reason}"
            else:
                decision = False
                detailed_reason = f"Dream 전략 거부: {reason}"
            
            # 의사결정 기록
            self._record_decision("creativity_decision", context, decision, detailed_reason)
            
            return decision, detailed_reason, {
                "dream_score": dream_score,
                "reality_score": reality_score,
                "thresholds": {
                    "creativity": creativity_threshold,
                    "stability": stability_threshold
                }
            }
            
        except Exception as e:
            logger.error(f"창의성 의사결정 실패: {e}")
            return False, f"의사결정 오류: {e}", {"error": str(e)}
    
    def make_evolution_decision(self, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        진화 관련 의사결정
        
        Args:
            context: 의사결정 컨텍스트
            
        Returns:
            Tuple[bool, str, Dict]: (결정 결과, 근거, 상세 정보)
        """
        try:
            # 진화 철학 조회
            evolution_beliefs = self.core_belief.get_beliefs_by_type(BeliefType.EVOLUTION_PHILOSOPHY)
            
            # 컨텍스트 분석
            current_performance = context.get('current_performance', 0.0)
            improvement_potential = context.get('improvement_potential', 0.0)
            failure_patterns = context.get('failure_patterns', [])
            
            # 진화 여부 결정
            should_evolve = self.core_belief.should_evolve(current_performance, improvement_potential)
            
            # 실패 패턴 분석
            fatal_failures = [f for f in failure_patterns if self._is_fatal_failure(f)]
            
            if fatal_failures:
                decision = False
                reason = f"치명적 실패 발견: {len(fatal_failures)}건"
            elif should_evolve:
                decision = True
                reason = f"진화 필요: 현재 성능({current_performance}), 개선 잠재력({improvement_potential})"
            else:
                decision = False
                reason = f"진화 불필요: 현재 성능({current_performance}), 개선 잠재력({improvement_potential})"
            
            # 의사결정 기록
            self._record_decision("evolution_decision", context, decision, reason)
            
            return decision, reason, {
                "current_performance": current_performance,
                "improvement_potential": improvement_potential,
                "fatal_failures": fatal_failures
            }
            
        except Exception as e:
            logger.error(f"진화 의사결정 실패: {e}")
            return False, f"의사결정 오류: {e}", {"error": str(e)}
    
    def make_ethics_decision(self, context: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        윤리 관련 의사결정
        
        Args:
            context: 의사결정 컨텍스트
            
        Returns:
            Tuple[bool, str, Dict]: (결정 결과, 근거, 상세 정보)
        """
        try:
            # 윤리 철학 조회
            ethics_beliefs = self.core_belief.get_beliefs_by_type(BeliefType.ETHICS_PHILOSOPHY)
            
            # 컨텍스트 분석
            human_benefit_score = context.get('human_benefit_score', 0.0)
            safety_risk = context.get('safety_risk', 0.0)
            privacy_impact = context.get('privacy_impact', 0.0)
            
            # 윤리적 판단
            ethical_approved = True
            reasons = []
            
            # 인간 이익 점수 확인
            if human_benefit_score < 0.5:
                ethical_approved = False
                reasons.append(f"낮은 인간 이익 점수: {human_benefit_score}")
            
            # 안전 위험 확인
            if safety_risk > 0.7:
                ethical_approved = False
                reasons.append(f"높은 안전 위험: {safety_risk}")
            
            # 개인정보 영향 확인
            if privacy_impact > 0.8:
                ethical_approved = False
                reasons.append(f"높은 개인정보 영향: {privacy_impact}")
            
            decision = ethical_approved
            reason = "윤리적 판단 통과" if ethical_approved else f"윤리적 판단 실패: {'; '.join(reasons)}"
            
            # 의사결정 기록
            self._record_decision("ethics_decision", context, decision, reason)
            
            return decision, reason, {
                "human_benefit_score": human_benefit_score,
                "safety_risk": safety_risk,
                "privacy_impact": privacy_impact
            }
            
        except Exception as e:
            logger.error(f"윤리 의사결정 실패: {e}")
            return False, f"의사결정 오류: {e}", {"error": str(e)}
    
    def _decide_imitation(self, context: Dict[str, Any], learning_beliefs: List) -> Tuple[bool, str, Dict[str, Any]]:
        """모방 단계 의사결정"""
        reference_available = context.get('reference_available', False)
        
        if reference_available:
            return True, "모방 가능: 참조 전략 존재", {"stage": "imitation", "action": "imitate"}
        else:
            return False, "모방 불가: 참조 전략 없음", {"stage": "imitation", "action": "skip"}
    
    def _decide_practice(self, context: Dict[str, Any], learning_beliefs: List) -> Tuple[bool, str, Dict[str, Any]]:
        """반복 단계 의사결정"""
        practice_count = context.get('practice_count', 0)
        max_practices = context.get('max_practices', 10)
        
        if practice_count < max_practices:
            return True, f"반복 계속: {practice_count}/{max_practices}", {"stage": "practice", "action": "continue"}
        else:
            return False, f"반복 완료: {practice_count}/{max_practices}", {"stage": "practice", "action": "complete"}
    
    def _decide_feedback(self, context: Dict[str, Any], learning_beliefs: List) -> Tuple[bool, str, Dict[str, Any]]:
        """피드백 단계 의사결정"""
        feedback_data = context.get('feedback_data', {})
        feedback_quality = feedback_data.get('quality', 0.0)
        
        if feedback_quality > 0.5:
            return True, f"피드백 수집 완료: 품질 {feedback_quality}", {"stage": "feedback", "action": "process"}
        else:
            return False, f"피드백 부족: 품질 {feedback_quality}", {"stage": "feedback", "action": "collect_more"}
    
    def _decide_challenge(self, context: Dict[str, Any], learning_beliefs: List) -> Tuple[bool, str, Dict[str, Any]]:
        """도전 단계 의사결정"""
        success_streak = context.get('success_streak', 0)
        confidence_level = context.get('confidence_level', 0.0)
        
        if success_streak >= 5 and confidence_level > 0.7:
            return True, f"도전 시작: 성공 연속 {success_streak}, 신뢰도 {confidence_level}", {"stage": "challenge", "action": "start"}
        else:
            return False, f"도전 보류: 성공 연속 {success_streak}, 신뢰도 {confidence_level}", {"stage": "challenge", "action": "wait"}
    
    def _decide_improvement(self, context: Dict[str, Any], learning_beliefs: List) -> Tuple[bool, str, Dict[str, Any]]:
        """개선 단계 의사결정"""
        improvement_areas = context.get('improvement_areas', [])
        improvement_potential = context.get('improvement_potential', 0.0)
        
        if improvement_areas and improvement_potential > 0.3:
            return True, f"개선 실행: 영역 {len(improvement_areas)}개, 잠재력 {improvement_potential}", {"stage": "improvement", "action": "execute"}
        else:
            return False, f"개선 보류: 영역 {len(improvement_areas)}개, 잠재력 {improvement_potential}", {"stage": "improvement", "action": "wait"}
    
    def _is_fatal_failure(self, failure_info: Dict[str, Any]) -> bool:
        """치명적 실패 여부 판단"""
        fatal_indicators = [
            "system_crash",
            "data_corruption",
            "security_violation",
            "performance_degradation_below_threshold"
        ]
        
        for indicator in fatal_indicators:
            if failure_info.get(indicator, False):
                return True
        
        return False
    
    def _record_decision(self, decision_type: str, context: Dict[str, Any], 
                        result: bool, reason: str):
        """의사결정 기록"""
        self.decision_history.append({
            "timestamp": datetime.now(),
            "type": decision_type,
            "context": context,
            "result": result,
            "reason": reason
        })
    
    def get_decision_summary(self) -> Dict[str, Any]:
        """의사결정 요약 정보"""
        return {
            "total_decisions": len(self.decision_history),
            "decisions_by_type": {
                "learning_decision": len([d for d in self.decision_history if d["type"] == "learning_decision"]),
                "creativity_decision": len([d for d in self.decision_history if d["type"] == "creativity_decision"]),
                "evolution_decision": len([d for d in self.decision_history if d["type"] == "evolution_decision"]),
                "ethics_decision": len([d for d in self.decision_history if d["type"] == "ethics_decision"])
            },
            "success_rate": len([d for d in self.decision_history if d["result"]]) / len(self.decision_history) if self.decision_history else 0,
            "last_decision": self.decision_history[-1]["timestamp"] if self.decision_history else None
        }
    
    def update_decision_weights(self, new_weights: Dict[str, float]):
        """의사결정 가중치 업데이트"""
        self.decision_weights.update(new_weights)
        logger.info(f"의사결정 가중치 업데이트: {new_weights}")


# 싱글톤 인스턴스
_decision_framework_instance = None

def get_decision_framework() -> DecisionFramework:
    """DecisionFramework 싱글톤 인스턴스 반환"""
    global _decision_framework_instance
    if _decision_framework_instance is None:
        core_belief = get_core_belief()
        _decision_framework_instance = DecisionFramework(core_belief)
    return _decision_framework_instance 