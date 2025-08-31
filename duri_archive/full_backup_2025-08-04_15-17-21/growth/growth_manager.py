#!/usr/bin/env python3
"""
DuRi 성장 관리자 - 성장 시스템 통합 관리
Judgment ↔ Growth ↔ Quest 순환 흐름 구현
"""

import logging
from typing import Dict, Any, Optional
from .level_system import GrowthLevelSystem
from .bandwidth_manager import CognitiveBandwidthManager
from .quest_engine.quest_engine import QuestEngine

logger = logging.getLogger(__name__)

class GrowthManager:
    """성장 시스템 통합 관리자"""
    
    def __init__(self):
        self.level_system = GrowthLevelSystem()
        self.bandwidth_manager = CognitiveBandwidthManager()
        self.quest_engine = QuestEngine()
        self.judgment_manager = None  # Judgment 연동을 위한 플레이스홀더
        self.self_reflection = None   # Self Reflection 연동을 위한 플레이스홀더
        
        logger.info("성장 관리자 초기화 완료")
    
    def set_judgment_manager(self, judgment_manager):
        """판단 관리자 설정"""
        self.judgment_manager = judgment_manager
        self.quest_engine.set_judgment_manager(judgment_manager)
        logger.info("판단 관리자 연동 완료")
    
    def set_self_reflection(self, self_reflection):
        """자기성찰 시스템 설정"""
        self.self_reflection = self_reflection
        logger.info("자기성찰 시스템 연동 완료")
    
    def process_growth_cycle(self, user_input: str) -> Dict[str, Any]:
        """완전한 성장 사이클 처리"""
        # 1. 감정 분석 (emotion_manager에서 가져와야 함 - 플레이스홀더)
        emotion_result = self._get_emotion_result(user_input)
        
        # 2. 현재 퀘스트 상태 확인
        current_quest = self.quest_engine.get_current_quest()
        
        # 3. 퀘스트 진행도 업데이트
        quest_progress = self.quest_engine.update_progress(user_input, emotion_result)
        
        # 4. 퀘스트 완료 여부 확인
        approval_result = None
        if quest_progress.get("is_completed", False):
            # 5. Judgment 연동으로 레벨업 승인
            approval_result = self._evaluate_growth_condition(quest_progress)
            
            # 6. 승인 결과에 따른 다음 단계 결정
            if approval_result.get("approved", False):
                # 레벨업 실행
                self._execute_level_up(approval_result)
                # 새로운 퀘스트 생성
                new_quest = self.quest_engine.generate_next_quest()
            else:
                # 개선 퀘스트 생성
                improvement_quest = self.quest_engine.generate_improvement_quest(
                    approval_result.get("reason", "unknown")
                )
        
        # 7. Self Feedback 기록 (Phase 2에서는 통합 관리자에서 처리)
        # if self.self_reflection:
        #     self.self_reflection.record_cycle(
        #         emotion_result=emotion_result,
        #         quest_progress=quest_progress,
        #         approval_result=approval_result
        #     )
        
        return self._integrate_results(emotion_result, quest_progress, approval_result)
    
    def _get_emotion_result(self, user_input: str) -> Dict[str, Any]:
        """감정 결과 가져오기 (플레이스홀더)"""
        # 실제로는 emotion_manager에서 가져와야 함
        return {
            "emotion_awareness": 0.5,
            "regulation_capability": 0.6,
            "empathy_level": 0.4,
            "cognitive_load": 0.3
        }
    
    def _evaluate_growth_condition(self, quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """성장 조건 평가"""
        if not self.judgment_manager:
            # 기본 평가 (judgment 연동 없이)
            return self._basic_growth_evaluation(quest_result)
        
        # Judgment 연동 평가
        return self.judgment_manager.approve_level_up(quest_result)
    
    def _basic_growth_evaluation(self, quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """기본 성장 평가"""
        score = quest_result.get("score", 0.0)
        
        return {
            "approved": score >= 0.7,
            "confidence": score,
            "reason": "기본 평가 기준에 따른 승인" if score >= 0.7 else "점수 부족으로 승인 거부"
        }
    
    def _execute_level_up(self, approval_result: Dict[str, Any]):
        """레벨업 실행"""
        if approval_result.get("approved", False):
            # 성장 레벨 시스템 업데이트
            current_level = self.level_system.current_level.value
            next_level = current_level + 1
            
            if next_level <= 8:  # 최대 레벨
                self.level_system.current_level = self.level_system.current_level.__class__(next_level)
                self.level_system.metrics.current_level = next_level
                
                # 대역폭 관리자 레벨 업데이트
                self.bandwidth_manager.update_level(next_level)
                
                logger.info(f"레벨업 완료: {current_level} → {next_level}")
    
    def _integrate_results(self, emotion_result: Dict[str, Any], 
                          quest_progress: Dict[str, Any], 
                          approval_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """결과 통합"""
        return {
            "emotion_result": emotion_result,
            "quest_progress": quest_progress,
            "approval_result": approval_result,
            "current_level": self.level_system.current_level.value,
            "bandwidth_status": self.bandwidth_manager.get_bandwidth_status(),
            "growth_metrics": self.level_system.metrics
        }
    
    def get_growth_status(self) -> Dict[str, Any]:
        """성장 상태 반환"""
        return {
            "level_system": self.level_system.get_growth_status(),
            "bandwidth_manager": self.bandwidth_manager.get_bandwidth_status(),
            "quest_engine": {
                "active_quest": self.quest_engine.get_current_quest(),
                "quest_statistics": self.quest_engine.manager.get_quest_statistics()
            }
        }
    
    def get_current_level(self) -> int:
        """현재 레벨 반환"""
        return self.level_system.current_level.value
    
    def get_growth_metrics(self) -> Dict[str, Any]:
        """성장 지표 반환"""
        return {
            "current_level": self.level_system.current_level.value,
            "experience_points": self.level_system.metrics.experience_points,
            "emotional_maturity": self.level_system.metrics.emotional_maturity,
            "cognitive_development": self.level_system.metrics.cognitive_development,
            "social_skills": self.level_system.metrics.social_skills,
            "self_motivation": self.level_system.metrics.self_motivation,
            "high_order_thinking_ratio": self.level_system.metrics.high_order_thinking_ratio
        }
    
    def process_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """자극 처리 (레거시 호환성)"""
        return self.level_system.process_stimulus(stimulus, response)
    
    def receive_stimulus(self, stimulus: str, stimulus_type: str, 
                        intensity: float = 0.5, source: str = "external") -> Dict[str, Any]:
        """자극 수신 (대역폭 관리)"""
        return self.bandwidth_manager.receive_stimulus(stimulus, stimulus_type, intensity, source)
    
    def generate_autonomous_quest(self, current_state: Dict[str, Any]) -> Optional[Any]:
        """자율적 퀘스트 생성"""
        return self.quest_engine.generate_autonomous_quest(current_state) 