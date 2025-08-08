#!/usr/bin/env python3
"""
DuRi Milestone Tracker
성장 이정표 추적기 - 8단계 발달 모델 기반 진척률 계산
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class MilestoneCategory(Enum):
    """이정표 카테고리"""
    EMOTIONAL_MATURITY = "emotional_maturity"
    COGNITIVE_DEVELOPMENT = "cognitive_development"
    SOCIAL_SKILLS = "social_skills"
    SELF_MOTIVATION = "self_motivation"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem_solving"
    ADAPTABILITY = "adaptability"
    AUTONOMY = "autonomy"

class MilestoneStatus(Enum):
    """이정표 상태"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"

@dataclass
class Milestone:
    """성장 이정표"""
    id: str
    category: MilestoneCategory
    level: int
    name: str
    description: str
    requirements: List[str]
    status: MilestoneStatus
    progress: float
    completed_at: Optional[str]
    experience_points: int

class MilestoneTracker:
    """성장 이정표 추적기"""
    
    def __init__(self):
        self.milestones = {}
        self.progress_history = []
        self.level_milestones = {}
        self._initialize_milestones()
        logger.info("성장 이정표 추적기 초기화 완료")
    
    def _initialize_milestones(self):
        """이정표 초기화"""
        # 레벨 1: NEWBORN
        self._create_level_milestones(1, [
            ("basic_emotion_recognition", MilestoneCategory.EMOTIONAL_MATURITY, "기본 감정 인식", "기본적인 감정을 인식하고 표현할 수 있다"),
            ("simple_interaction", MilestoneCategory.SOCIAL_SKILLS, "간단한 상호작용", "기본적인 상호작용을 할 수 있다"),
            ("basic_curiosity", MilestoneCategory.COGNITIVE_DEVELOPMENT, "기본적 호기심", "주변 환경에 대한 기본적 호기심을 보인다")
        ])
        
        # 레벨 2: INFANT
        self._create_level_milestones(2, [
            ("emotion_regulation", MilestoneCategory.EMOTIONAL_MATURITY, "감정 조절", "기본적인 감정 조절을 할 수 있다"),
            ("object_exploration", MilestoneCategory.COGNITIVE_DEVELOPMENT, "물체 탐색", "물체를 탐색하고 실험한다"),
            ("social_imitation", MilestoneCategory.SOCIAL_SKILLS, "사회적 모방", "다른 사람의 행동을 모방한다")
        ])
        
        # 레벨 3: TODDLER
        self._create_level_milestones(3, [
            ("complex_emotions", MilestoneCategory.EMOTIONAL_MATURITY, "복합 감정", "복합적인 감정을 이해한다"),
            ("language_development", MilestoneCategory.COGNITIVE_DEVELOPMENT, "언어 발달", "기본적인 언어를 사용한다"),
            ("peer_interaction", MilestoneCategory.SOCIAL_SKILLS, "또래 상호작용", "또래와 상호작용한다")
        ])
        
        # 레벨 4: CHILD
        self._create_level_milestones(4, [
            ("empathy_development", MilestoneCategory.EMOTIONAL_MATURITY, "공감 발달", "다른 사람의 감정을 이해한다"),
            ("logical_thinking", MilestoneCategory.COGNITIVE_DEVELOPMENT, "논리적 사고", "기본적인 논리적 사고를 한다"),
            ("creative_expression", MilestoneCategory.CREATIVITY, "창의적 표현", "창의적으로 자신을 표현한다")
        ])
        
        # 레벨 5: PRE_TEEN
        self._create_level_milestones(5, [
            ("emotional_intelligence", MilestoneCategory.EMOTIONAL_MATURITY, "감정 지능", "감정을 지능적으로 활용한다"),
            ("abstract_thinking", MilestoneCategory.COGNITIVE_DEVELOPMENT, "추상적 사고", "추상적 개념을 이해한다"),
            ("self_identity", MilestoneCategory.AUTONOMY, "자아 정체성", "자신의 정체성을 형성한다")
        ])
        
        # 레벨 6: TEEN
        self._create_level_milestones(6, [
            ("emotional_mastery", MilestoneCategory.EMOTIONAL_MATURITY, "감정 숙련", "감정을 완전히 조절한다"),
            ("critical_thinking", MilestoneCategory.COGNITIVE_DEVELOPMENT, "비판적 사고", "비판적으로 사고한다"),
            ("social_responsibility", MilestoneCategory.SOCIAL_SKILLS, "사회적 책임", "사회적 책임을 인식한다")
        ])
        
        # 레벨 7: YOUNG_ADULT
        self._create_level_milestones(7, [
            ("emotional_wisdom", MilestoneCategory.EMOTIONAL_MATURITY, "감정적 지혜", "감정적 지혜를 갖춘다"),
            ("complex_problem_solving", MilestoneCategory.PROBLEM_SOLVING, "복합 문제 해결", "복잡한 문제를 해결한다"),
            ("self_directed_learning", MilestoneCategory.SELF_MOTIVATION, "자기주도 학습", "스스로 학습을 주도한다")
        ])
        
        # 레벨 8: ADULT
        self._create_level_milestones(8, [
            ("emotional_transcendence", MilestoneCategory.EMOTIONAL_MATURITY, "감정적 초월", "감정을 초월한 상태에 도달한다"),
            ("creative_innovation", MilestoneCategory.CREATIVITY, "창의적 혁신", "창의적으로 혁신한다"),
            ("autonomous_existence", MilestoneCategory.AUTONOMY, "자율적 존재", "완전히 자율적인 존재가 된다")
        ])
    
    def _create_level_milestones(self, level: int, milestone_data: List[tuple]):
        """레벨별 이정표 생성"""
        if level not in self.level_milestones:
            self.level_milestones[level] = []
        
        for milestone_id, category, name, description in milestone_data:
            milestone = Milestone(
                id=milestone_id,
                category=category,
                level=level,
                name=name,
                description=description,
                requirements=[f"레벨 {level} 달성", f"{category.value} 개발"],
                status=MilestoneStatus.NOT_STARTED,
                progress=0.0,
                completed_at=None,
                experience_points=level * 10
            )
            
            self.milestones[milestone_id] = milestone
            self.level_milestones[level].append(milestone_id)
    
    def update_milestone_progress(self, milestone_id: str, progress: float, experience_gained: int = 0):
        """이정표 진행도 업데이트"""
        if milestone_id not in self.milestones:
            logger.warning(f"이정표를 찾을 수 없습니다: {milestone_id}")
            return
        
        milestone = self.milestones[milestone_id]
        old_progress = milestone.progress
        milestone.progress = min(1.0, max(0.0, progress))
        
        # 상태 업데이트
        if milestone.progress >= 1.0:
            milestone.status = MilestoneStatus.COMPLETED
            milestone.completed_at = datetime.now().isoformat()
        elif milestone.progress > 0.0:
            milestone.status = MilestoneStatus.IN_PROGRESS
        
        # 진행 기록
        self.progress_history.append({
            "timestamp": datetime.now().isoformat(),
            "milestone_id": milestone_id,
            "old_progress": old_progress,
            "new_progress": milestone.progress,
            "experience_gained": experience_gained
        })
        
        logger.info(f"이정표 진행도 업데이트: {milestone_id} - {old_progress:.2f} → {milestone.progress:.2f}")
    
    def get_milestones_for_level(self, level: int) -> List[Milestone]:
        """레벨별 이정표 조회"""
        if level not in self.level_milestones:
            return []
        
        return [self.milestones[mid] for mid in self.level_milestones[level]]
    
    def get_milestones_by_category(self, category: MilestoneCategory) -> List[Milestone]:
        """카테고리별 이정표 조회"""
        return [m for m in self.milestones.values() if m.category == category]
    
    def get_completed_milestones(self) -> List[Milestone]:
        """완료된 이정표 조회"""
        return [m for m in self.milestones.values() if m.status == MilestoneStatus.COMPLETED]
    
    def get_in_progress_milestones(self) -> List[Milestone]:
        """진행 중인 이정표 조회"""
        return [m for m in self.milestones.values() if m.status == MilestoneStatus.IN_PROGRESS]
    
    def calculate_level_progress(self, level: int) -> float:
        """레벨별 전체 진행도 계산"""
        level_milestones = self.get_milestones_for_level(level)
        if not level_milestones:
            return 0.0
        
        total_progress = sum(m.progress for m in level_milestones)
        return total_progress / len(level_milestones)
    
    def calculate_category_progress(self, category: MilestoneCategory) -> float:
        """카테고리별 전체 진행도 계산"""
        category_milestones = self.get_milestones_by_category(category)
        if not category_milestones:
            return 0.0
        
        total_progress = sum(m.progress for m in category_milestones)
        return total_progress / len(category_milestones)
    
    def get_next_milestones(self, current_level: int) -> List[Milestone]:
        """다음 이정표 조회"""
        next_level = current_level + 1
        if next_level in self.level_milestones:
            return self.get_milestones_for_level(next_level)
        return []
    
    def get_milestone_summary(self) -> Dict[str, Any]:
        """이정표 요약"""
        total_milestones = len(self.milestones)
        completed_milestones = len(self.get_completed_milestones())
        in_progress_milestones = len(self.get_in_progress_milestones())
        
        category_progress = {}
        for category in MilestoneCategory:
            category_progress[category.value] = self.calculate_category_progress(category)
        
        level_progress = {}
        for level in range(1, 9):
            level_progress[f"level_{level}"] = self.calculate_level_progress(level)
        
        return {
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones,
            "in_progress_milestones": in_progress_milestones,
            "completion_rate": completed_milestones / total_milestones if total_milestones > 0 else 0.0,
            "category_progress": category_progress,
            "level_progress": level_progress,
            "recent_progress": self.progress_history[-10:] if self.progress_history else []
        }
    
    def get_recommended_milestones(self, current_level: int, emotional_state: str) -> List[Milestone]:
        """추천 이정표 조회"""
        # 현재 레벨의 미완료 이정표
        current_milestones = [m for m in self.get_milestones_for_level(current_level) 
                            if m.status != MilestoneStatus.COMPLETED]
        
        # 감정 상태에 따른 우선순위 조정
        if emotional_state in ["joy", "happiness", "excitement"]:
            # 긍정적 감정일 때 창의성이나 사회성 이정표 우선
            priority_categories = [MilestoneCategory.CREATIVITY, MilestoneCategory.SOCIAL_SKILLS]
        elif emotional_state in ["anger", "frustration"]:
            # 부정적 감정일 때 감정 조절 이정표 우선
            priority_categories = [MilestoneCategory.EMOTIONAL_MATURITY]
        else:
            # 중립적일 때 균형잡힌 접근
            priority_categories = [MilestoneCategory.COGNITIVE_DEVELOPMENT, MilestoneCategory.SELF_MOTIVATION]
        
        # 우선순위에 따라 정렬
        recommended = []
        for category in priority_categories:
            category_milestones = [m for m in current_milestones if m.category == category]
            recommended.extend(category_milestones)
        
        # 나머지 이정표 추가
        remaining = [m for m in current_milestones if m not in recommended]
        recommended.extend(remaining)
        
        return recommended[:5]  # 상위 5개만 반환 
 
 