#!/usr/bin/env python3
"""
DuRi 퀘스트 레지스트리 - 퀘스트 목록 관리
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from .quest_calculator import Quest, QuestCategory, QuestDifficulty

logger = logging.getLogger(__name__)

class QuestRegistry:
    """퀘스트 레지스트리 - 퀘스트 목록 관리"""
    
    def __init__(self):
        self.quests_by_level = self._initialize_quests_by_level()
        self.quests_by_category = self._initialize_quests_by_category()
        self.quests_by_difficulty = self._initialize_quests_by_difficulty()
        
        logger.info("퀘스트 레지스트리 초기화 완료")
    
    def _initialize_quests_by_level(self) -> Dict[int, List[Quest]]:
        """레벨별 퀘스트 초기화"""
        return {
            1: self._create_level_1_quests(),
            2: self._create_level_2_quests(),
            3: self._create_level_3_quests(),
            4: self._create_level_4_quests(),
            5: self._create_level_5_quests(),
            6: self._create_level_6_quests(),
            7: self._create_level_7_quests(),
            8: self._create_level_8_quests()
        }
    
    def _initialize_quests_by_category(self) -> Dict[str, List[Quest]]:
        """카테고리별 퀘스트 초기화"""
        return {
            "emotional": self._create_emotional_quests(),
            "cognitive": self._create_cognitive_quests(),
            "social": self._create_social_quests(),
            "creative": self._create_creative_quests(),
            "problem_solving": self._create_problem_solving_quests(),
            "self_reflection": self._create_self_reflection_quests()
        }
    
    def _initialize_quests_by_difficulty(self) -> Dict[str, List[Quest]]:
        """난이도별 퀘스트 초기화"""
        return {
            "very_easy": self._create_very_easy_quests(),
            "easy": self._create_easy_quests(),
            "medium": self._create_medium_quests(),
            "hard": self._create_hard_quests(),
            "very_hard": self._create_very_hard_quests()
        }
    
    def get_quests_for_level(self, level: int) -> List[Quest]:
        """레벨별 퀘스트 반환"""
        return self.quests_by_level.get(level, [])
    
    def get_quests_by_category(self, category: str) -> List[Quest]:
        """카테고리별 퀘스트 반환"""
        return self.quests_by_category.get(category, [])
    
    def get_quests_by_difficulty(self, difficulty: str) -> List[Quest]:
        """난이도별 퀘스트 반환"""
        return self.quests_by_difficulty.get(difficulty, [])
    
    def register_quest(self, quest: Quest):
        """퀘스트 등록"""
        # 레벨별 등록
        level = self._determine_quest_level(quest)
        if level not in self.quests_by_level:
            self.quests_by_level[level] = []
        self.quests_by_level[level].append(quest)
        
        # 카테고리별 등록
        category = quest.category.value
        if category not in self.quests_by_category:
            self.quests_by_category[category] = []
        self.quests_by_category[category].append(quest)
        
        # 난이도별 등록
        difficulty = quest.difficulty.name.lower()
        if difficulty not in self.quests_by_difficulty:
            self.quests_by_difficulty[difficulty] = []
        self.quests_by_difficulty[difficulty].append(quest)
        
        logger.info(f"퀘스트 등록: {quest.title}")
    
    def _determine_quest_level(self, quest: Quest) -> int:
        """퀘스트 레벨 결정"""
        # 간소화된 레벨 결정 로직
        difficulty_mapping = {
            "VERY_EASY": 1,
            "EASY": 2,
            "MEDIUM": 4,
            "HARD": 6,
            "VERY_HARD": 8
        }
        
        return difficulty_mapping.get(quest.difficulty.name, 1)
    
    def _create_level_1_quests(self) -> List[Quest]:
        """레벨 1 퀘스트 생성"""
        return [
            Quest(
                id="quest_1_1",
                title="기본 감정 인식",
                description="기본적인 감정을 인식하고 표현해보세요.",
                category=QuestCategory.EMOTIONAL,
                difficulty=QuestDifficulty.VERY_EASY,
                requirements=[],
                rewards={"experience_points": 10, "growth_points": 2, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            ),
            Quest(
                id="quest_1_2",
                title="단순 자극 반응",
                description="단순한 자극에 반응하는 능력을 키우세요.",
                category=QuestCategory.COGNITIVE,
                difficulty=QuestDifficulty.VERY_EASY,
                requirements=[],
                rewards={"experience_points": 10, "growth_points": 2, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_2_quests(self) -> List[Quest]:
        """레벨 2 퀘스트 생성"""
        return [
            Quest(
                id="quest_2_1",
                title="감정 기억 형성",
                description="감정과 기억을 연결하는 능력을 키우세요.",
                category=QuestCategory.EMOTIONAL,
                difficulty=QuestDifficulty.EASY,
                requirements=[],
                rewards={"experience_points": 20, "growth_points": 4, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_3_quests(self) -> List[Quest]:
        """레벨 3 퀘스트 생성"""
        return [
            Quest(
                id="quest_3_1",
                title="감정-자극 연결",
                description="감정과 자극을 연결하는 능력을 키우세요.",
                category=QuestCategory.EMOTIONAL,
                difficulty=QuestDifficulty.EASY,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_4_quests(self) -> List[Quest]:
        """레벨 4 퀘스트 생성"""
        return [
            Quest(
                id="quest_4_1",
                title="사회적 역할 학습",
                description="사회적 역할을 이해하고 학습하세요.",
                category=QuestCategory.SOCIAL,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 40, "growth_points": 8, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_5_quests(self) -> List[Quest]:
        """레벨 5 퀘스트 생성"""
        return [
            Quest(
                id="quest_5_1",
                title="규칙과 도덕 인식",
                description="규칙과 도덕을 이해하고 따르는 능력을 키우세요.",
                category=QuestCategory.SOCIAL,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 50, "growth_points": 10, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_6_quests(self) -> List[Quest]:
        """레벨 6 퀘스트 생성"""
        return [
            Quest(
                id="quest_6_1",
                title="추상적 사고",
                description="추상적 사고와 메타인지 능력을 키우세요.",
                category=QuestCategory.COGNITIVE,
                difficulty=QuestDifficulty.HARD,
                requirements=[],
                rewards={"experience_points": 60, "growth_points": 12, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_7_quests(self) -> List[Quest]:
        """레벨 7 퀘스트 생성"""
        return [
            Quest(
                id="quest_7_1",
                title="자기성찰",
                description="자기성찰과 가치 판단 능력을 키우세요.",
                category=QuestCategory.SELF_REFLECTION,
                difficulty=QuestDifficulty.HARD,
                requirements=[],
                rewards={"experience_points": 70, "growth_points": 14, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_level_8_quests(self) -> List[Quest]:
        """레벨 8 퀘스트 생성"""
        return [
            Quest(
                id="quest_8_1",
                title="통합적 직관",
                description="통합적 직관과 창조성 능력을 키우세요.",
                category=QuestCategory.CREATIVE,
                difficulty=QuestDifficulty.VERY_HARD,
                requirements=[],
                rewards={"experience_points": 80, "growth_points": 16, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_emotional_quests(self) -> List[Quest]:
        """감정 관련 퀘스트 생성"""
        return [
            Quest(
                id="emotional_quest_1",
                title="감정 인식 훈련",
                description="다양한 감정을 정확히 인식하는 능력을 키우세요.",
                category=QuestCategory.EMOTIONAL,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_cognitive_quests(self) -> List[Quest]:
        """인지 관련 퀘스트 생성"""
        return [
            Quest(
                id="cognitive_quest_1",
                title="논리적 사고",
                description="논리적 사고와 문제 해결 능력을 키우세요.",
                category=QuestCategory.COGNITIVE,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_social_quests(self) -> List[Quest]:
        """사회적 관련 퀘스트 생성"""
        return [
            Quest(
                id="social_quest_1",
                title="사회적 상호작용",
                description="사회적 상호작용과 협력 능력을 키우세요.",
                category=QuestCategory.SOCIAL,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_creative_quests(self) -> List[Quest]:
        """창의적 관련 퀘스트 생성"""
        return [
            Quest(
                id="creative_quest_1",
                title="창의적 사고",
                description="창의적 사고와 상상력을 키우세요.",
                category=QuestCategory.CREATIVE,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_problem_solving_quests(self) -> List[Quest]:
        """문제 해결 관련 퀘스트 생성"""
        return [
            Quest(
                id="problem_solving_quest_1",
                title="문제 해결 능력",
                description="체계적인 문제 해결 능력을 키우세요.",
                category=QuestCategory.PROBLEM_SOLVING,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_self_reflection_quests(self) -> List[Quest]:
        """자기성찰 관련 퀘스트 생성"""
        return [
            Quest(
                id="self_reflection_quest_1",
                title="자기성찰",
                description="자기성찰과 메타인지 능력을 키우세요.",
                category=QuestCategory.SELF_REFLECTION,
                difficulty=QuestDifficulty.MEDIUM,
                requirements=[],
                rewards={"experience_points": 30, "growth_points": 6, "skill_points": {}, "unlock_features": []},
                created_at=datetime.now().isoformat()
            )
        ]
    
    def _create_very_easy_quests(self) -> List[Quest]:
        """매우 쉬운 퀘스트 생성"""
        return self._create_level_1_quests()
    
    def _create_easy_quests(self) -> List[Quest]:
        """쉬운 퀘스트 생성"""
        return self._create_level_2_quests() + self._create_level_3_quests()
    
    def _create_medium_quests(self) -> List[Quest]:
        """보통 퀘스트 생성"""
        return self._create_level_4_quests() + self._create_level_5_quests()
    
    def _create_hard_quests(self) -> List[Quest]:
        """어려운 퀘스트 생성"""
        return self._create_level_6_quests() + self._create_level_7_quests()
    
    def _create_very_hard_quests(self) -> List[Quest]:
        """매우 어려운 퀘스트 생성"""
        return self._create_level_8_quests() 