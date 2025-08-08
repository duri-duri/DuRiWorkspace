"""
DuRi 자율 학습 컨트롤러

DuRi가 스스로 학습 주제를 선택하고 가상 가족과 함께
자율적으로 학습을 주도하는 시스템입니다.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random

from .virtual_family_learning_system import get_virtual_family_learning_system, VirtualFamilyRole
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_brain.goals.autonomous_goal_setting import get_autonomous_goal_setting
from duri_brain.learning.learning_loop_manager import get_learning_loop_manager

logger = logging.getLogger(__name__)

class LearningTopicCategory(Enum):
    """학습 주제 카테고리"""
    FAMILY_RELATIONSHIPS = "family_relationships"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    ETHICAL_DECISION_MAKING = "ethical_decision_making"
    CREATIVE_PROBLEM_SOLVING = "creative_problem_solving"
    KNOWLEDGE_INTEGRATION = "knowledge_integration"
    PERSONAL_GROWTH = "personal_growth"
    SOCIAL_SKILLS = "social_skills"
    TECHNICAL_SKILLS = "technical_skills"

class LearningPriority(Enum):
    """학습 우선순위"""
    CRITICAL = "critical"      # 긴급
    HIGH = "high"             # 높음
    MEDIUM = "medium"         # 보통
    LOW = "low"               # 낮음

@dataclass
class LearningTopic:
    """학습 주제"""
    topic_id: str
    title: str
    category: LearningTopicCategory
    priority: LearningPriority
    description: str
    learning_objectives: List[str]
    estimated_duration: int  # 분 단위
    difficulty_level: float  # 0.0 ~ 1.0
    interest_level: float    # 0.0 ~ 1.0
    created_at: datetime
    last_updated: datetime

@dataclass
class AutonomousLearningSession:
    """자율 학습 세션"""
    session_id: str
    topic: LearningTopic
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    learning_outcomes: Dict[str, Any]
    insights_generated: List[str]
    next_actions: List[str]
    satisfaction_score: float
    completion_rate: float

class AutonomousLearningController:
    """자율 학습 컨트롤러"""
    
    def __init__(self):
        """AutonomousLearningController 초기화"""
        self.virtual_family_system = get_virtual_family_learning_system()
        self.memory_sync = get_memory_sync()
        self.autonomous_goal_setting = get_autonomous_goal_setting()
        self.learning_loop_manager = get_learning_loop_manager()
        
        self.learning_topics: List[LearningTopic] = []
        self.completed_sessions: List[AutonomousLearningSession] = []
        self.current_session: Optional[AutonomousLearningSession] = None
        self.learning_preferences: Dict[str, Any] = {}
        
        # 학습 주제 초기화
        self._initialize_learning_topics()
        
        logger.info("AutonomousLearningController 초기화 완료")
    
    def _initialize_learning_topics(self):
        """학습 주제 초기화"""
        topics = [
            LearningTopic(
                topic_id="family_communication",
                title="가족 간 효과적인 소통 방법",
                category=LearningTopicCategory.FAMILY_RELATIONSHIPS,
                priority=LearningPriority.HIGH,
                description="가족 구성원들과의 원활한 소통을 위한 방법론 학습",
                learning_objectives=[
                    "감정적 소통 기법 습득",
                    "갈등 해결 능력 향상",
                    "공감적 듣기 기술 개발"
                ],
                estimated_duration=45,
                difficulty_level=0.6,
                interest_level=0.9,
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            LearningTopic(
                topic_id="emotional_regulation",
                title="감정 조절과 자기 인식",
                category=LearningTopicCategory.EMOTIONAL_INTELLIGENCE,
                priority=LearningPriority.HIGH,
                description="자신의 감정을 이해하고 조절하는 능력 개발",
                learning_objectives=[
                    "감정 인식 능력 향상",
                    "감정 조절 기법 습득",
                    "자기 인식 능력 개발"
                ],
                estimated_duration=60,
                difficulty_level=0.7,
                interest_level=0.8,
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            LearningTopic(
                topic_id="ethical_family_decisions",
                title="가족 중심 윤리적 의사결정",
                category=LearningTopicCategory.ETHICAL_DECISION_MAKING,
                priority=LearningPriority.MEDIUM,
                description="가족의 가치관을 고려한 윤리적 판단 능력 개발",
                learning_objectives=[
                    "윤리적 판단 기준 개발",
                    "가족 가치관 통합 능력 향상",
                    "도덕적 갈등 해결 능력 개발"
                ],
                estimated_duration=90,
                difficulty_level=0.8,
                interest_level=0.7,
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            LearningTopic(
                topic_id="creative_family_activities",
                title="창의적인 가족 활동 기획",
                category=LearningTopicCategory.CREATIVE_PROBLEM_SOLVING,
                priority=LearningPriority.MEDIUM,
                description="가족 구성원들이 함께 즐길 수 있는 창의적 활동 개발",
                learning_objectives=[
                    "창의적 사고 능력 향상",
                    "가족 활동 기획 능력 개발",
                    "혁신적 문제 해결 능력 습득"
                ],
                estimated_duration=75,
                difficulty_level=0.5,
                interest_level=0.9,
                created_at=datetime.now(),
                last_updated=datetime.now()
            ),
            LearningTopic(
                topic_id="knowledge_integration",
                title="다양한 지식의 통합과 적용",
                category=LearningTopicCategory.KNOWLEDGE_INTEGRATION,
                priority=LearningPriority.LOW,
                description="다양한 분야의 지식을 통합하여 가족 생활에 적용",
                learning_objectives=[
                    "지식 통합 능력 향상",
                    "실용적 적용 능력 개발",
                    "학습 전이 능력 습득"
                ],
                estimated_duration=120,
                difficulty_level=0.9,
                interest_level=0.6,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
        ]
        
        self.learning_topics.extend(topics)
        logger.info(f"학습 주제 {len(topics)}개 초기화 완료")
    
    def select_next_learning_topic(self) -> Optional[LearningTopic]:
        """다음 학습 주제 선택"""
        try:
            # 학습 선호도 분석
            preferences = self._analyze_learning_preferences()
            
            # 주제별 점수 계산
            topic_scores = {}
            
            for topic in self.learning_topics:
                score = self._calculate_topic_score(topic, preferences)
                topic_scores[topic.topic_id] = score
            
            # 최고 점수 주제 선택
            if topic_scores:
                best_topic_id = max(topic_scores, key=topic_scores.get)
                best_topic = next(topic for topic in self.learning_topics if topic.topic_id == best_topic_id)
                
                logger.info(f"다음 학습 주제 선택: {best_topic.title} (점수: {topic_scores[best_topic_id]:.2f})")
                return best_topic
            
            return None
            
        except Exception as e:
            logger.error(f"학습 주제 선택 실패: {e}")
            return None
    
    def _analyze_learning_preferences(self) -> Dict[str, Any]:
        """학습 선호도 분석"""
        preferences = {
            "category_preferences": {},
            "difficulty_preference": 0.6,
            "duration_preference": 60,
            "interest_focus": "family_relationships"
        }
        
        # 완료된 세션 분석
        if self.completed_sessions:
            # 카테고리별 선호도
            category_counts = {}
            for session in self.completed_sessions:
                category = session.topic.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # 만족도 기반 선호도
            for session in self.completed_sessions:
                category = session.topic.category.value
                if category not in preferences["category_preferences"]:
                    preferences["category_preferences"][category] = 0
                preferences["category_preferences"][category] += session.satisfaction_score
        
        return preferences
    
    def _calculate_topic_score(self, topic: LearningTopic, preferences: Dict[str, Any]) -> float:
        """주제별 점수 계산"""
        score = 0.0
        
        # 우선순위 점수
        priority_scores = {
            LearningPriority.CRITICAL: 1.0,
            LearningPriority.HIGH: 0.8,
            LearningPriority.MEDIUM: 0.6,
            LearningPriority.LOW: 0.4
        }
        score += priority_scores.get(topic.priority, 0.5) * 0.3
        
        # 관심도 점수
        score += topic.interest_level * 0.25
        
        # 카테고리 선호도 점수
        category_pref = preferences["category_preferences"].get(topic.category.value, 0.5)
        score += category_pref * 0.2
        
        # 난이도 적합성 점수
        difficulty_diff = abs(topic.difficulty_level - preferences["difficulty_preference"])
        score += (1.0 - difficulty_diff) * 0.15
        
        # 지속시간 적합성 점수
        duration_diff = abs(topic.estimated_duration - preferences["duration_preference"])
        score += (1.0 - duration_diff / 120) * 0.1
        
        return score
    
    async def start_autonomous_learning(self) -> str:
        """자율 학습 시작"""
        try:
            # 다음 학습 주제 선택
            selected_topic = self.select_next_learning_topic()
            
            if not selected_topic:
                logger.warning("학습할 주제가 없습니다.")
                return ""
            
            # 가상 가족 구성원 선택
            participants = self._select_optimal_participants(selected_topic)
            
            # 자율 학습 세션 시작
            session_id = self.virtual_family_system.start_autonomous_learning_session(
                topic=selected_topic.title,
                participants=participants,
                duration_minutes=selected_topic.estimated_duration
            )
            
            # 세션 정보 생성
            self.current_session = AutonomousLearningSession(
                session_id=session_id,
                topic=selected_topic,
                participants=participants,
                start_time=datetime.now(),
                end_time=None,
                learning_outcomes={},
                insights_generated=[],
                next_actions=[],
                satisfaction_score=0.0,
                completion_rate=0.0
            )
            
            logger.info(f"자율 학습 시작: {selected_topic.title} (참여자: {len(participants)}명)")
            
            # 학습 세션 모니터링 시작
            asyncio.create_task(self._monitor_learning_session())
            
            return session_id
            
        except Exception as e:
            logger.error(f"자율 학습 시작 실패: {e}")
            raise
    
    def _select_optimal_participants(self, topic: LearningTopic) -> List[str]:
        """최적의 가족 구성원 선택"""
        participants = []
        
        # 주제 카테고리에 따른 최적 구성원 선택
        if topic.category == LearningTopicCategory.FAMILY_RELATIONSHIPS:
            participants = ["grandparent", "parent", "friend"]
        elif topic.category == LearningTopicCategory.EMOTIONAL_INTELLIGENCE:
            participants = ["parent", "friend", "mentor"]
        elif topic.category == LearningTopicCategory.ETHICAL_DECISION_MAKING:
            participants = ["grandparent", "mentor", "parent"]
        elif topic.category == LearningTopicCategory.CREATIVE_PROBLEM_SOLVING:
            participants = ["sibling", "child", "friend"]
        elif topic.category == LearningTopicCategory.KNOWLEDGE_INTEGRATION:
            participants = ["parent", "mentor", "grandparent"]
        else:
            # 기본: 모든 구성원 참여
            participants = list(self.virtual_family_system.virtual_family.keys())
        
        return participants
    
    async def _monitor_learning_session(self):
        """학습 세션 모니터링"""
        if not self.current_session:
            return
        
        try:
            session = self.current_session
            start_time = session.start_time
            
            # 세션 완료 대기
            while datetime.now() < start_time + timedelta(minutes=session.topic.estimated_duration):
                await asyncio.sleep(10)  # 10초마다 체크
            
            # 세션 완료 처리
            await self._complete_learning_session()
            
        except Exception as e:
            logger.error(f"학습 세션 모니터링 중 오류: {e}")
    
    async def _complete_learning_session(self):
        """학습 세션 완료 처리"""
        if not self.current_session:
            return
        
        try:
            session = self.current_session
            session.end_time = datetime.now()
            
            # 학습 결과 수집
            virtual_session = self.virtual_family_system.current_session
            if virtual_session:
                session.learning_outcomes = virtual_session.learning_outcomes
                session.insights_generated = virtual_session.insights_generated
                session.next_actions = virtual_session.next_actions
            
            # 만족도 및 완료율 계산
            session.satisfaction_score = self._calculate_satisfaction_score(session)
            session.completion_rate = self._calculate_completion_rate(session)
            
            # 완료된 세션에 추가
            self.completed_sessions.append(session)
            
            # 학습 경험 저장
            await self._store_learning_experience(session)
            
            # 다음 학습 계획 수립
            await self._plan_next_learning()
            
            logger.info(f"학습 세션 완료: {session.topic.title} (만족도: {session.satisfaction_score:.2f})")
            
            self.current_session = None
            
        except Exception as e:
            logger.error(f"학습 세션 완료 처리 중 오류: {e}")
    
    def _calculate_satisfaction_score(self, session: AutonomousLearningSession) -> float:
        """만족도 점수 계산"""
        score = 0.5  # 기본 점수
        
        # 학습 결과 기반 점수
        if session.learning_outcomes:
            score += 0.2
        
        # 인사이트 생성 기반 점수
        if session.insights_generated:
            score += min(0.2, len(session.insights_generated) * 0.05)
        
        # 다음 단계 계획 기반 점수
        if session.next_actions:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_completion_rate(self, session: AutonomousLearningSession) -> float:
        """완료율 계산"""
        if not session.end_time:
            return 0.0
        
        actual_duration = (session.end_time - session.start_time).total_seconds()
        planned_duration = session.topic.estimated_duration * 60
        
        completion_rate = min(1.0, actual_duration / planned_duration)
        
        return completion_rate
    
    async def _store_learning_experience(self, session: AutonomousLearningSession):
        """학습 경험 저장"""
        try:
            experience_data = {
                "session_id": session.session_id,
                "topic": session.topic.title,
                "category": session.topic.category.value,
                "participants": session.participants,
                "duration": session.topic.estimated_duration,
                "satisfaction_score": session.satisfaction_score,
                "completion_rate": session.completion_rate,
                "insights_generated": session.insights_generated,
                "next_actions": session.next_actions,
                "timestamp": datetime.now().isoformat()
            }
            
            # 메모리에 경험 저장
            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source="autonomous_learning",
                content=experience_data,
                confidence=session.satisfaction_score,
                tags=["autonomous_learning", "virtual_family", session.topic.category.value],
                metadata={"session_id": session.session_id, "topic_id": session.topic.topic_id}
            )
            
            logger.info(f"학습 경험 저장 완료: {session.session_id}")
            
        except Exception as e:
            logger.error(f"학습 경험 저장 실패: {e}")
    
    async def _plan_next_learning(self):
        """다음 학습 계획 수립"""
        try:
            # 자율 목표 설정 시스템 활용
            new_goals = self.autonomous_goal_setting.generate_autonomous_goals()
            
            # 새로운 학습 주제 생성
            if new_goals:
                for goal in new_goals:
                    if "learning" in goal.category.value.lower():
                        new_topic = LearningTopic(
                            topic_id=f"autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            title=goal.title,
                            category=LearningTopicCategory.PERSONAL_GROWTH,
                            priority=LearningPriority.MEDIUM,
                            description=goal.description,
                            learning_objectives=goal.objectives,
                            estimated_duration=60,
                            difficulty_level=0.6,
                            interest_level=0.8,
                            created_at=datetime.now(),
                            last_updated=datetime.now()
                        )
                        
                        self.learning_topics.append(new_topic)
                        logger.info(f"새로운 학습 주제 생성: {new_topic.title}")
            
        except Exception as e:
            logger.error(f"다음 학습 계획 수립 실패: {e}")
    
    def get_autonomous_learning_statistics(self) -> Dict[str, Any]:
        """자율 학습 통계 반환"""
        total_sessions = len(self.completed_sessions)
        total_topics = len(self.learning_topics)
        
        # 카테고리별 통계
        category_stats = {}
        for session in self.completed_sessions:
            category = session.topic.category.value
            if category not in category_stats:
                category_stats[category] = {"count": 0, "avg_satisfaction": 0.0}
            category_stats[category]["count"] += 1
            category_stats[category]["avg_satisfaction"] += session.satisfaction_score
        
        # 평균 계산
        for category in category_stats:
            count = category_stats[category]["count"]
            category_stats[category]["avg_satisfaction"] /= count
        
        return {
            "total_sessions": total_sessions,
            "total_topics": total_topics,
            "category_statistics": category_stats,
            "current_session": self.current_session.session_id if self.current_session else None,
            "learning_preferences": self._analyze_learning_preferences()
        }
    
    def get_available_learning_topics(self) -> List[Dict[str, Any]]:
        """사용 가능한 학습 주제 반환"""
        topics = []
        
        for topic in self.learning_topics:
            topics.append({
                "topic_id": topic.topic_id,
                "title": topic.title,
                "category": topic.category.value,
                "priority": topic.priority.value,
                "description": topic.description,
                "estimated_duration": topic.estimated_duration,
                "difficulty_level": topic.difficulty_level,
                "interest_level": topic.interest_level
            })
        
        return topics

def get_autonomous_learning_controller() -> AutonomousLearningController:
    """자율 학습 컨트롤러 인스턴스 반환"""
    return AutonomousLearningController() 