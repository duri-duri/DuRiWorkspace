#!/usr/bin/env python3
"""
DuRi 퀘스트 엔진 - 자율적인 퀘스트 생성 및 관리
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .quest_calculator import QuestCalculator, Quest, QuestEvaluation
from .quest_registry import QuestRegistry
from .quest_manager import QuestManager

logger = logging.getLogger(__name__)

class QuestEngine:
    """퀘스트 엔진 - 자율적인 퀘스트 생성 및 관리"""
    
    def __init__(self):
        self.calculator = QuestCalculator()
        self.registry = QuestRegistry()
        self.manager = QuestManager()
        self.judgment_manager = None  # Judgment 연동을 위한 플레이스홀더
        
        logger.info("퀘스트 엔진 초기화 완료")
    
    def set_judgment_manager(self, judgment_manager):
        """판단 관리자 설정 (연동용)"""
        self.judgment_manager = judgment_manager
        logger.info("판단 관리자 연동 완료")
    
    def get_current_quest(self) -> Optional[Quest]:
        """현재 진행 중인 퀘스트 반환"""
        return self.manager.get_active_quest()
    
    def update_progress(self, user_input: str, emotion_result: Dict[str, Any]) -> Dict[str, Any]:
        """퀘스트 진행도 업데이트"""
        current_quest = self.get_current_quest()
        if not current_quest:
            return {"is_completed": False, "progress": 0.0, "status": "no_active_quest"}
        
        # 사용자 입력을 퀘스트 기준으로 평가
        evaluation = self.calculator.evaluate_input_for_quest(
            user_input, emotion_result, current_quest
        )
        
        # 진행도 업데이트
        updated_progress = self.manager.update_quest_progress(
            current_quest.id, evaluation
        )
        
        return updated_progress
    
    def generate_next_quest(self) -> Optional[Quest]:
        """승인 후 다음 퀘스트 생성"""
        current_level = self._get_current_growth_level()
        available_quests = self.registry.get_quests_for_level(current_level)
        
        # 자율적 퀘스트 선택 (약점 기반)
        weak_points = self._get_weak_points()
        selected_quest = self._select_optimal_quest(available_quests, weak_points)
        
        return self.manager.activate_quest(selected_quest)
    
    def generate_improvement_quest(self, rejection_reason: str) -> Optional[Quest]:
        """개선 퀘스트 생성"""
        return self.manager.create_improvement_quest(rejection_reason)
    
    def generate_autonomous_quest(self, current_state: Dict[str, Any]) -> Optional[Quest]:
        """자율적 퀘스트 생성"""
        weak_points = self._analyze_weak_points(current_state)
        return self._create_custom_quest(weak_points)
    
    def evaluate_growth_condition(self, quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """성장 조건 평가 (judgment 연동)"""
        if not self.judgment_manager:
            # 기본 평가 (judgment 연동 없이)
            return self._basic_growth_evaluation(quest_result)
        
        # Judgment 연동 평가
        return self.judgment_manager.approve_level_up(quest_result)
    
    def _get_current_growth_level(self) -> int:
        """현재 성장 레벨 반환 (플레이스홀더)"""
        # 실제로는 growth_manager에서 가져와야 함
        return 1
    
    def _get_weak_points(self) -> List[str]:
        """약점 분석 (플레이스홀더)"""
        # 실제로는 self_reflection에서 가져와야 함
        return ["emotional_regulation", "cognitive_processing"]
    
    def _select_optimal_quest(self, available_quests: List[Quest], weak_points: List[str]) -> Quest:
        """최적 퀘스트 선택"""
        if not available_quests:
            return self._create_default_quest()
        
        # 약점과 매칭되는 퀘스트 선택
        for quest in available_quests:
            for weak_point in weak_points:
                if weak_point in quest.description.lower():
                    return quest
        
        # 매칭되는 것이 없으면 첫 번째 퀘스트 선택
        return available_quests[0]
    
    def _analyze_weak_points(self, current_state: Dict[str, Any]) -> List[str]:
        """약점 분석"""
        weak_points = []
        
        # 감정 상태 분석
        emotion_state = current_state.get("emotion_state", {})
        if emotion_state.get("bias_level", 0.0) > 0.7:
            weak_points.append("emotional_bias")
        
        # 성장 지표 분석
        growth_metrics = current_state.get("growth_metrics", {})
        if growth_metrics.get("emotional_maturity", 0.0) < 0.5:
            weak_points.append("emotional_maturity")
        if growth_metrics.get("cognitive_development", 0.0) < 0.5:
            weak_points.append("cognitive_development")
        
        return weak_points
    
    def _create_custom_quest(self, weak_points: List[str]) -> Quest:
        """맞춤 퀘스트 생성"""
        if not weak_points:
            return self._create_default_quest()
        
        # 약점에 따른 퀘스트 생성
        quest_templates = {
            "emotional_bias": {
                "title": "감정 편향 극복",
                "description": "감정적 편향을 인식하고 객관적 판단을 연습하세요.",
                "category": "emotional",
                "difficulty": "medium"
            },
            "emotional_maturity": {
                "title": "감정 성숙도 향상",
                "description": "다양한 감정을 이해하고 조절하는 능력을 키우세요.",
                "category": "emotional",
                "difficulty": "medium"
            },
            "cognitive_development": {
                "title": "인지 능력 개발",
                "description": "논리적 사고와 문제 해결 능력을 향상시키세요.",
                "category": "cognitive",
                "difficulty": "medium"
            }
        }
        
        # 첫 번째 약점에 대한 퀘스트 생성
        weak_point = weak_points[0]
        template = quest_templates.get(weak_point, quest_templates["emotional_maturity"])
        
        return Quest(
            id=f"custom_quest_{datetime.now().timestamp()}",
            title=template["title"],
            description=template["description"],
            category=template["category"],
            difficulty=template["difficulty"],
            requirements=[],
            rewards={"experience_points": 50, "growth_points": 10, "skill_points": {}, "unlock_features": []},
            created_at=datetime.now().isoformat()
        )
    
    def _create_default_quest(self) -> Quest:
        """기본 퀘스트 생성"""
        return Quest(
            id=f"default_quest_{datetime.now().timestamp()}",
            title="기본 성장 퀘스트",
            description="기본적인 성장과 학습을 위한 퀘스트입니다.",
            category="cognitive",
            difficulty="easy",
            requirements=[],
            rewards={"experience_points": 30, "growth_points": 5, "skill_points": {}, "unlock_features": []},
            created_at=datetime.now().isoformat()
        )
    
    def _basic_growth_evaluation(self, quest_result: Dict[str, Any]) -> Dict[str, Any]:
        """기본 성장 평가 (judgment 연동 없이)"""
        score = quest_result.get("score", 0.0)
        
        return {
            "approved": score >= 0.7,
            "confidence": score,
            "reason": "기본 평가 기준에 따른 승인" if score >= 0.7 else "점수 부족으로 승인 거부"
        }
    
    def evaluate_input_for_quest(self, user_input: str, emotion_result: Dict[str, Any], quest: Quest) -> Dict[str, Any]:
        """퀘스트를 위한 입력 평가"""
        # 간소화된 평가 로직
        performance_data = {
            "emotion_recognition": emotion_result.get("emotion_awareness", 0.0),
            "emotion_regulation": emotion_result.get("regulation_capability", 0.0),
            "empathy_level": emotion_result.get("empathy_level", 0.0),
            "cognitive_load": emotion_result.get("cognitive_load", 0.0)
        }
        
        evaluation = self.calculator.calculate_quest_score(quest, performance_data)
        
        return {
            "score": evaluation.score,
            "passed": evaluation.passed,
            "feedback": evaluation.feedback,
            "completion_time": evaluation.completion_time
        } 
 
 