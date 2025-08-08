#!/usr/bin/env python3
"""
DuRi 퀘스트 관리자 - 퀘스트 생명주기 관리
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from .quest_calculator import Quest, QuestStatus

logger = logging.getLogger(__name__)

class QuestManager:
    """퀘스트 관리자 - 퀘스트 생명주기 관리"""
    
    def __init__(self):
        self.active_quests = {}
        self.completed_quests = {}
        self.failed_quests = {}
        self.quest_progress = {}
        
        logger.info("퀘스트 관리자 초기화 완료")
    
    def activate_quest(self, quest: Quest) -> Quest:
        """퀘스트 활성화"""
        quest.status = QuestStatus.IN_PROGRESS
        quest.started_at = datetime.now().isoformat()
        quest.progress = 0.0
        quest.attempts = 0
        
        self.active_quests[quest.id] = quest
        self.quest_progress[quest.id] = {
            "progress": 0.0,
            "attempts": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"퀘스트 활성화: {quest.title}")
        return quest
    
    def update_quest_progress(self, quest_id: str, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """퀘스트 진행도 업데이트"""
        if quest_id not in self.active_quests:
            return {"is_completed": False, "progress": 0.0, "status": "quest_not_found"}
        
        quest = self.active_quests[quest_id]
        progress_data = self.quest_progress[quest_id]
        
        # 진행도 업데이트
        score = evaluation.get("score", 0.0)
        progress_increment = score * 0.1  # 점수에 따른 진행도 증가
        
        current_progress = progress_data["progress"]
        new_progress = min(1.0, current_progress + progress_increment)
        
        progress_data["progress"] = new_progress
        progress_data["attempts"] += 1
        progress_data["last_updated"] = datetime.now().isoformat()
        
        quest.progress = new_progress
        quest.attempts = progress_data["attempts"]
        
        # 완료 여부 확인
        is_completed = new_progress >= 1.0 or evaluation.get("passed", False)
        
        if is_completed:
            self._complete_quest(quest_id, evaluation)
        
        return {
            "is_completed": is_completed,
            "progress": new_progress,
            "status": "completed" if is_completed else "in_progress",
            "score": score,
            "attempts": progress_data["attempts"]
        }
    
    def _complete_quest(self, quest_id: str, evaluation: Dict[str, Any]):
        """퀘스트 완료 처리"""
        quest = self.active_quests[quest_id]
        quest.status = QuestStatus.COMPLETED
        quest.completed_at = datetime.now().isoformat()
        quest.progress = 1.0
        
        # 완료된 퀘스트 이동
        self.completed_quests[quest_id] = quest
        del self.active_quests[quest_id]
        del self.quest_progress[quest_id]
        
        logger.info(f"퀘스트 완료: {quest.title}")
    
    def fail_quest(self, quest_id: str, reason: str = "unknown"):
        """퀘스트 실패 처리"""
        if quest_id not in self.active_quests:
            return
        
        quest = self.active_quests[quest_id]
        quest.status = QuestStatus.FAILED
        quest.progress = 0.0
        
        # 실패한 퀘스트 이동
        self.failed_quests[quest_id] = quest
        del self.active_quests[quest_id]
        del self.quest_progress[quest_id]
        
        logger.warning(f"퀘스트 실패: {quest.title} - {reason}")
    
    def get_active_quest(self) -> Optional[Quest]:
        """활성 퀘스트 반환"""
        if not self.active_quests:
            return None
        
        # 첫 번째 활성 퀘스트 반환
        return list(self.active_quests.values())[0]
    
    def get_all_active_quests(self) -> List[Quest]:
        """모든 활성 퀘스트 반환"""
        return list(self.active_quests.values())
    
    def get_completed_quests(self) -> List[Quest]:
        """완료된 퀘스트 반환"""
        return list(self.completed_quests.values())
    
    def get_failed_quests(self) -> List[Quest]:
        """실패한 퀘스트 반환"""
        return list(self.failed_quests.values())
    
    def create_improvement_quest(self, rejection_reason: str) -> Quest:
        """개선 퀘스트 생성"""
        # 거부 이유에 따른 개선 퀘스트 생성
        improvement_templates = {
            "emotional_bias": {
                "title": "감정 편향 개선",
                "description": "감정적 편향을 인식하고 객관적 판단을 연습하세요.",
                "category": "emotional",
                "difficulty": "medium"
            },
            "low_score": {
                "title": "기본 능력 향상",
                "description": "기본적인 능력을 향상시키는 퀘스트입니다.",
                "category": "cognitive",
                "difficulty": "easy"
            },
            "insufficient_progress": {
                "title": "진행도 개선",
                "description": "더 꾸준한 진행을 위한 퀘스트입니다.",
                "category": "cognitive",
                "difficulty": "easy"
            }
        }
        
        # 거부 이유에 따른 템플릿 선택
        template_key = "low_score"  # 기본값
        if "편향" in rejection_reason:
            template_key = "emotional_bias"
        elif "진행" in rejection_reason:
            template_key = "insufficient_progress"
        
        template = improvement_templates[template_key]
        
        improvement_quest = Quest(
            id=f"improvement_quest_{datetime.now().timestamp()}",
            title=template["title"],
            description=template["description"],
            category=template["category"],
            difficulty=template["difficulty"],
            requirements=[],
            rewards={"experience_points": 20, "growth_points": 4, "skill_points": {}, "unlock_features": []},
            created_at=datetime.now().isoformat()
        )
        
        logger.info(f"개선 퀘스트 생성: {improvement_quest.title}")
        return improvement_quest
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """퀘스트 통계 반환"""
        return {
            "active_quests": len(self.active_quests),
            "completed_quests": len(self.completed_quests),
            "failed_quests": len(self.failed_quests),
            "total_quests": len(self.active_quests) + len(self.completed_quests) + len(self.failed_quests),
            "completion_rate": len(self.completed_quests) / max(1, len(self.completed_quests) + len(self.failed_quests)),
            "average_progress": self._calculate_average_progress()
        }
    
    def _calculate_average_progress(self) -> float:
        """평균 진행도 계산"""
        if not self.quest_progress:
            return 0.0
        
        total_progress = sum(data["progress"] for data in self.quest_progress.values())
        return total_progress / len(self.quest_progress)
    
    def reset_quest_progress(self, quest_id: str):
        """퀘스트 진행도 초기화"""
        if quest_id in self.quest_progress:
            self.quest_progress[quest_id]["progress"] = 0.0
            self.quest_progress[quest_id]["attempts"] = 0
            self.quest_progress[quest_id]["last_updated"] = datetime.now().isoformat()
            
            if quest_id in self.active_quests:
                self.active_quests[quest_id].progress = 0.0
                self.active_quests[quest_id].attempts = 0
            
            logger.info(f"퀘스트 진행도 초기화: {quest_id}")
    
    def clear_completed_quests(self):
        """완료된 퀘스트 정리"""
        self.completed_quests.clear()
        logger.info("완료된 퀘스트 정리 완료")
    
    def clear_failed_quests(self):
        """실패한 퀘스트 정리"""
        self.failed_quests.clear()
        logger.info("실패한 퀘스트 정리 완료") 