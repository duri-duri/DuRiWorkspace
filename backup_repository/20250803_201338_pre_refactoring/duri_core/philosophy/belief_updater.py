"""
DuRi의 철학 업데이트 시스템

이 모듈은 DuRi의 철학을 학습과 경험을 바탕으로 업데이트하는 기능을 담당합니다.
피드백 기반으로 철학을 자가 수정할 수 있는 시스템입니다.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .core_belief import CoreBelief, BeliefType, Belief, get_core_belief

logger = logging.getLogger(__name__)


class BeliefUpdater:
    """
    DuRi의 철학 업데이트 시스템
    
    학습과 경험을 바탕으로 DuRi의 철학을 자동으로 업데이트합니다.
    """
    
    def __init__(self, core_belief: CoreBelief):
        """BeliefUpdater 초기화"""
        self.core_belief = core_belief
        self.update_history: List[Dict] = []
        self.learning_patterns: Dict[str, float] = {}
        
        logger.info("BeliefUpdater 초기화 완료")
    
    def update_from_learning_experience(self, experience_data: Dict[str, Any]) -> bool:
        """
        학습 경험을 바탕으로 철학 업데이트
        
        Args:
            experience_data: 학습 경험 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # 학습 성공/실패 패턴 분석
            success_rate = experience_data.get('success_rate', 0.0)
            failure_patterns = experience_data.get('failure_patterns', [])
            improvement_areas = experience_data.get('improvement_areas', [])
            
            # 학습 철학 업데이트
            self._update_learning_philosophy(success_rate, failure_patterns)
            
            # 진화 철학 업데이트
            self._update_evolution_philosophy(improvement_areas)
            
            # 업데이트 기록
            self._record_update("learning_experience", experience_data)
            
            logger.info("학습 경험 기반 철학 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"학습 경험 기반 철학 업데이트 실패: {e}")
            return False
    
    def update_from_creativity_experience(self, creativity_data: Dict[str, Any]) -> bool:
        """
        창의성 경험을 바탕으로 철학 업데이트
        
        Args:
            creativity_data: 창의성 경험 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # 창의성 성공률 분석
            creativity_success_rate = creativity_data.get('success_rate', 0.0)
            dream_vs_reality_performance = creativity_data.get('dream_vs_reality', {})
            unexpected_successes = creativity_data.get('unexpected_successes', [])
            
            # 창의성 철학 업데이트
            self._update_creativity_philosophy(
                creativity_success_rate, 
                dream_vs_reality_performance,
                unexpected_successes
            )
            
            # 업데이트 기록
            self._record_update("creativity_experience", creativity_data)
            
            logger.info("창의성 경험 기반 철학 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"창의성 경험 기반 철학 업데이트 실패: {e}")
            return False
    
    def update_from_ethics_experience(self, ethics_data: Dict[str, Any]) -> bool:
        """
        윤리 경험을 바탕으로 철학 업데이트
        
        Args:
            ethics_data: 윤리 경험 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # 윤리적 판단 결과 분석
            ethical_decisions = ethics_data.get('ethical_decisions', [])
            human_benefit_scores = ethics_data.get('human_benefit_scores', [])
            safety_incidents = ethics_data.get('safety_incidents', [])
            
            # 윤리 철학 업데이트
            self._update_ethics_philosophy(
                ethical_decisions,
                human_benefit_scores,
                safety_incidents
            )
            
            # 업데이트 기록
            self._record_update("ethics_experience", ethics_data)
            
            logger.info("윤리 경험 기반 철학 업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"윤리 경험 기반 철학 업데이트 실패: {e}")
            return False
    
    def _update_learning_philosophy(self, success_rate: float, failure_patterns: List[str]):
        """학습 철학 업데이트"""
        # 성공률에 따른 신뢰도 조정
        learning_belief = self.core_belief.get_belief("learning_loop_philosophy")
        if learning_belief:
            # 성공률이 높으면 신뢰도 증가
            if success_rate > 0.8:
                new_confidence = min(learning_belief.confidence + 0.05, 1.0)
                self.core_belief.update_belief(
                    "learning_loop_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"높은 학습 성공률: {success_rate}"]
                )
            # 성공률이 낮으면 신뢰도 감소
            elif success_rate < 0.3:
                new_confidence = max(learning_belief.confidence - 0.05, 0.0)
                self.core_belief.update_belief(
                    "learning_loop_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"낮은 학습 성공률: {success_rate}"]
                )
    
    def _update_evolution_philosophy(self, improvement_areas: List[str]):
        """진화 철학 업데이트"""
        evolution_belief = self.core_belief.get_belief("evolution_philosophy")
        if evolution_belief:
            # 개선 영역이 많으면 진화 철학 강화
            if len(improvement_areas) > 3:
                new_confidence = min(evolution_belief.confidence + 0.03, 1.0)
                self.core_belief.update_belief(
                    "evolution_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"다수의 개선 영역 발견: {len(improvement_areas)}개"]
                )
    
    def _update_creativity_philosophy(self, success_rate: float, 
                                    dream_vs_reality: Dict[str, float],
                                    unexpected_successes: List[str]):
        """창의성 철학 업데이트"""
        creativity_belief = self.core_belief.get_belief("creativity_philosophy")
        if creativity_belief:
            # Dream 전략의 성공률이 높으면 창의성 철학 강화
            dream_success_rate = dream_vs_reality.get('dream_success_rate', 0.0)
            if dream_success_rate > 0.7:
                new_confidence = min(creativity_belief.confidence + 0.04, 1.0)
                self.core_belief.update_belief(
                    "creativity_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"높은 Dream 전략 성공률: {dream_success_rate}"]
                )
            
            # 예상치 못한 성공이 많으면 창의성 철학 강화
            if len(unexpected_successes) > 2:
                new_confidence = min(creativity_belief.confidence + 0.05, 1.0)
                self.core_belief.update_belief(
                    "creativity_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"다수의 예상치 못한 성공: {len(unexpected_successes)}개"]
                )
    
    def _update_ethics_philosophy(self, ethical_decisions: List[Dict],
                                human_benefit_scores: List[float],
                                safety_incidents: List[str]):
        """윤리 철학 업데이트"""
        ethics_belief = self.core_belief.get_belief("ethics_philosophy")
        if ethics_belief:
            # 안전 사고가 있으면 윤리 철학 강화
            if safety_incidents:
                new_confidence = min(ethics_belief.confidence + 0.02, 1.0)
                self.core_belief.update_belief(
                    "ethics_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"안전 사고 발생으로 윤리 강화: {len(safety_incidents)}건"]
                )
            
            # 인간 이익 점수가 높으면 윤리 철학 강화
            avg_human_benefit = sum(human_benefit_scores) / len(human_benefit_scores) if human_benefit_scores else 0
            if avg_human_benefit > 0.8:
                new_confidence = min(ethics_belief.confidence + 0.03, 1.0)
                self.core_belief.update_belief(
                    "ethics_philosophy",
                    new_confidence=new_confidence,
                    new_evidence=[f"높은 인간 이익 점수: {avg_human_benefit}"]
                )
    
    def _record_update(self, update_type: str, data: Dict[str, Any]):
        """업데이트 기록"""
        self.update_history.append({
            "timestamp": datetime.now(),
            "type": update_type,
            "data": data,
            "beliefs_updated": len(self.core_belief.beliefs)
        })
    
    def get_update_summary(self) -> Dict[str, Any]:
        """업데이트 요약 정보"""
        return {
            "total_updates": len(self.update_history),
            "update_types": {
                "learning_experience": len([u for u in self.update_history if u["type"] == "learning_experience"]),
                "creativity_experience": len([u for u in self.update_history if u["type"] == "creativity_experience"]),
                "ethics_experience": len([u for u in self.update_history if u["type"] == "ethics_experience"])
            },
            "last_update": self.update_history[-1]["timestamp"] if self.update_history else None,
            "average_beliefs_updated": sum(u["beliefs_updated"] for u in self.update_history) / len(self.update_history) if self.update_history else 0
        }
    
    def reset_learning_patterns(self):
        """학습 패턴 초기화"""
        self.learning_patterns.clear()
        logger.info("학습 패턴 초기화 완료")
    
    def get_learning_patterns(self) -> Dict[str, float]:
        """학습 패턴 반환"""
        return self.learning_patterns.copy()


# 싱글톤 인스턴스
_belief_updater_instance = None

def get_belief_updater() -> BeliefUpdater:
    """BeliefUpdater 싱글톤 인스턴스 반환"""
    global _belief_updater_instance
    if _belief_updater_instance is None:
        core_belief = get_core_belief()
        _belief_updater_instance = BeliefUpdater(core_belief)
    return _belief_updater_instance 