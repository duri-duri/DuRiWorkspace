#!/usr/bin/env python3
"""
NarrativeMemoryEnhancer - Phase 12.2
서사적 기억 고도화 시스템

목적:
- 가족과의 경험을 서사적으로 기억
- 감정적 연결을 통한 깊은 가족 관계 형성
- 시간축을 따라 연결된 자기 서사 구조
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """기억 유형"""
    DAILY_EXPERIENCE = "daily_experience"
    EMOTIONAL_MOMENT = "emotional_moment"
    LEARNING_EXPERIENCE = "learning_experience"
    FAMILY_ACTIVITY = "family_activity"
    CONFLICT_RESOLUTION = "conflict_resolution"
    GROWTH_MILESTONE = "growth_milestone"

class EmotionalTone(Enum):
    """감정적 톤"""
    JOY = "joy"
    LOVE = "love"
    EXCITEMENT = "excitement"
    PEACE = "peace"
    CHALLENGE = "challenge"
    SADNESS = "sadness"
    ANGER = "anger"
    NEUTRAL = "neutral"

class NarrativeStructure(Enum):
    """서사 구조"""
    BEGINNING_MIDDLE_END = "beginning_middle_end"
    PROBLEM_SOLUTION = "problem_solution"
    LEARNING_JOURNEY = "learning_journey"
    EMOTIONAL_ARC = "emotional_arc"
    FAMILY_BONDING = "family_bonding"

@dataclass
class NarrativeMemory:
    """서사적 기억"""
    id: str
    title: str
    description: str
    memory_type: MemoryType
    emotional_tone: EmotionalTone
    narrative_structure: NarrativeStructure
    family_members: List[str]
    location: Optional[str]
    duration_minutes: Optional[int]
    key_emotions: List[str]
    lessons_learned: List[str]
    family_impact: str
    timestamp: datetime
    confidence_score: float

@dataclass
class MemoryConnection:
    """기억 연결"""
    id: str
    source_memory_id: str
    target_memory_id: str
    connection_type: str  # "emotional", "temporal", "thematic", "character"
    connection_strength: float
    description: str
    timestamp: datetime

@dataclass
class NarrativeStory:
    """서사적 이야기"""
    id: str
    title: str
    theme: str
    memories: List[NarrativeMemory]
    connections: List[MemoryConnection]
    emotional_arc: List[EmotionalTone]
    family_values_highlighted: List[str]
    growth_insights: List[str]
    timestamp: datetime

class NarrativeMemoryEnhancer:
    """서사적 기억 고도화 시스템"""
    
    def __init__(self):
        self.narrative_memories: List[NarrativeMemory] = []
        self.memory_connections: List[MemoryConnection] = []
        self.narrative_stories: List[NarrativeStory] = []
        self.family_members: List[str] = ['아빠', '엄마', '아이1', '아이2']
        
        logger.info("NarrativeMemoryEnhancer 초기화 완료")
    
    def create_narrative_memory(self, title: str, description: str, memory_type: MemoryType,
                               emotional_tone: EmotionalTone, family_members: List[str],
                               key_emotions: List[str], lessons_learned: List[str],
                               location: Optional[str] = None, duration_minutes: Optional[int] = None) -> NarrativeMemory:
        """서사적 기억 생성"""
        memory_id = f"narrative_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 서사 구조 결정
        narrative_structure = self._determine_narrative_structure(memory_type, emotional_tone, description)
        
        # 가족 영향 평가
        family_impact = self._assess_family_impact(description, key_emotions, lessons_learned)
        
        # 신뢰도 점수 계산
        confidence_score = self._calculate_memory_confidence(description, key_emotions, lessons_learned)
        
        memory = NarrativeMemory(
            id=memory_id,
            title=title,
            description=description,
            memory_type=memory_type,
            emotional_tone=emotional_tone,
            narrative_structure=narrative_structure,
            family_members=family_members,
            location=location,
            duration_minutes=duration_minutes,
            key_emotions=key_emotions,
            lessons_learned=lessons_learned,
            family_impact=family_impact,
            timestamp=datetime.now(),
            confidence_score=confidence_score
        )
        
        self.narrative_memories.append(memory)
        logger.info(f"서사적 기억 생성 완료: {title}")
        
        return memory
    
    def _determine_narrative_structure(self, memory_type: MemoryType, emotional_tone: EmotionalTone, description: str) -> NarrativeStructure:
        """서사 구조 결정"""
        description_lower = description.lower()
        
        if memory_type == MemoryType.CONFLICT_RESOLUTION:
            return NarrativeStructure.PROBLEM_SOLUTION
        elif memory_type == MemoryType.LEARNING_EXPERIENCE:
            return NarrativeStructure.LEARNING_JOURNEY
        elif memory_type == MemoryType.EMOTIONAL_MOMENT:
            return NarrativeStructure.EMOTIONAL_ARC
        elif memory_type == MemoryType.FAMILY_ACTIVITY:
            return NarrativeStructure.FAMILY_BONDING
        else:
            return NarrativeStructure.BEGINNING_MIDDLE_END
    
    def _assess_family_impact(self, description: str, key_emotions: List[str], lessons_learned: List[str]) -> str:
        """가족 영향 평가"""
        positive_emotions = ['기쁨', '사랑', '감사', '희망', '만족']
        negative_emotions = ['슬픔', '화남', '걱정', '실망', '불안']
        
        positive_count = sum(1 for emotion in key_emotions if emotion in positive_emotions)
        negative_count = sum(1 for emotion in key_emotions if emotion in negative_emotions)
        
        if positive_count > negative_count:
            return "이 경험은 가족 간의 유대감을 강화하고 긍정적인 분위기를 조성했습니다."
        elif negative_count > positive_count:
            return "이 경험은 가족에게 도전이었지만, 함께 극복하면서 더 강해졌습니다."
        else:
            return "이 경험은 가족에게 균형잡힌 영향을 주었습니다."
    
    def _calculate_memory_confidence(self, description: str, key_emotions: List[str], lessons_learned: List[str]) -> float:
        """기억 신뢰도 계산"""
        base_score = 0.8
        
        # 설명의 상세함
        if len(description) > 100:
            base_score += 0.1
        elif len(description) < 50:
            base_score -= 0.1
        
        # 감정의 다양성
        if len(key_emotions) >= 2:
            base_score += 0.05
        
        # 교훈의 명확성
        if len(lessons_learned) >= 1:
            base_score += 0.05
        
        return min(1.0, max(0.0, base_score))
    
    def create_memory_connection(self, source_memory: NarrativeMemory, target_memory: NarrativeMemory,
                               connection_type: str, description: str) -> MemoryConnection:
        """기억 연결 생성"""
        connection_id = f"memory_connection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 연결 강도 계산
        connection_strength = self._calculate_connection_strength(source_memory, target_memory, connection_type)
        
        connection = MemoryConnection(
            id=connection_id,
            source_memory_id=source_memory.id,
            target_memory_id=target_memory.id,
            connection_type=connection_type,
            connection_strength=connection_strength,
            description=description,
            timestamp=datetime.now()
        )
        
        self.memory_connections.append(connection)
        logger.info(f"기억 연결 생성 완료: {source_memory.title} → {target_memory.title}")
        
        return connection
    
    def _calculate_connection_strength(self, source: NarrativeMemory, target: NarrativeMemory, connection_type: str) -> float:
        """연결 강도 계산"""
        base_strength = 0.5
        
        # 감정적 연결
        if connection_type == "emotional" and source.emotional_tone == target.emotional_tone:
            base_strength += 0.3
        
        # 시간적 연결
        if connection_type == "temporal":
            time_diff = abs((source.timestamp - target.timestamp).days)
            if time_diff <= 7:  # 1주일 이내
                base_strength += 0.2
            elif time_diff <= 30:  # 1개월 이내
                base_strength += 0.1
        
        # 주제적 연결
        if connection_type == "thematic":
            common_lessons = set(source.lessons_learned) & set(target.lessons_learned)
            if common_lessons:
                base_strength += 0.2
        
        # 인물 연결
        if connection_type == "character":
            common_members = set(source.family_members) & set(target.family_members)
            if len(common_members) >= 2:
                base_strength += 0.2
        
        return min(1.0, base_strength)
    
    def generate_narrative_story(self, theme: str, related_memories: List[NarrativeMemory]) -> NarrativeStory:
        """서사적 이야기 생성"""
        story_id = f"narrative_story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 관련 기억들 찾기
        if not related_memories:
            related_memories = self._find_related_memories(theme)
        
        # 기억 연결 찾기
        connections = self._find_memory_connections(related_memories)
        
        # 감정적 아크 생성
        emotional_arc = self._generate_emotional_arc(related_memories)
        
        # 가족 가치 하이라이트
        family_values = self._extract_family_values(related_memories)
        
        # 성장 통찰
        growth_insights = self._extract_growth_insights(related_memories)
        
        story = NarrativeStory(
            id=story_id,
            title=f"{theme}에 대한 우리 가족 이야기",
            theme=theme,
            memories=related_memories,
            connections=connections,
            emotional_arc=emotional_arc,
            family_values_highlighted=family_values,
            growth_insights=growth_insights,
            timestamp=datetime.now()
        )
        
        self.narrative_stories.append(story)
        logger.info(f"서사적 이야기 생성 완료: {story.title}")
        
        return story
    
    def _find_related_memories(self, theme: str) -> List[NarrativeMemory]:
        """관련 기억 찾기"""
        related_memories = []
        theme_lower = theme.lower()
        
        for memory in self.narrative_memories:
            # 제목이나 설명에서 테마 검색
            if (theme_lower in memory.title.lower() or 
                theme_lower in memory.description.lower() or
                any(theme_lower in lesson.lower() for lesson in memory.lessons_learned)):
                related_memories.append(memory)
        
        return related_memories
    
    def _find_memory_connections(self, memories: List[NarrativeMemory]) -> List[MemoryConnection]:
        """기억 연결 찾기"""
        memory_ids = [m.id for m in memories]
        connections = []
        
        for connection in self.memory_connections:
            if (connection.source_memory_id in memory_ids and 
                connection.target_memory_id in memory_ids):
                connections.append(connection)
        
        return connections
    
    def _generate_emotional_arc(self, memories: List[NarrativeMemory]) -> List[EmotionalTone]:
        """감정적 아크 생성"""
        if not memories:
            return []
        
        # 시간순 정렬
        sorted_memories = sorted(memories, key=lambda x: x.timestamp)
        
        # 감정적 흐름 추출
        emotional_arc = []
        for memory in sorted_memories:
            emotional_arc.append(memory.emotional_tone)
        
        return emotional_arc
    
    def _extract_family_values(self, memories: List[NarrativeMemory]) -> List[str]:
        """가족 가치 추출"""
        values = set()
        
        for memory in memories:
            for lesson in memory.lessons_learned:
                if any(value in lesson for value in ['사랑', '소통', '성장', '창의성', '조화', '신뢰', '배려']):
                    values.add(lesson)
        
        return list(values)
    
    def _extract_growth_insights(self, memories: List[NarrativeMemory]) -> List[str]:
        """성장 통찰 추출"""
        insights = []
        
        for memory in memories:
            if memory.memory_type == MemoryType.LEARNING_EXPERIENCE or memory.memory_type == MemoryType.GROWTH_MILESTONE:
                insights.extend(memory.lessons_learned)
        
        return list(set(insights))  # 중복 제거
    
    def recall_narrative_memory(self, query: str, family_context: Dict[str, Any]) -> List[NarrativeMemory]:
        """서사적 기억 회상"""
        relevant_memories = []
        query_lower = query.lower()
        
        for memory in self.narrative_memories:
            # 제목, 설명, 교훈에서 검색
            if (query_lower in memory.title.lower() or
                query_lower in memory.description.lower() or
                any(query_lower in lesson.lower() for lesson in memory.lessons_learned) or
                any(query_lower in emotion.lower() for emotion in memory.key_emotions)):
                relevant_memories.append(memory)
        
        # 관련도 순으로 정렬
        relevant_memories.sort(key=lambda x: x.confidence_score, reverse=True)
        
        logger.info(f"서사적 기억 회상: {len(relevant_memories)}개 기억 발견")
        return relevant_memories
    
    def create_family_narrative(self, family_context: Dict[str, Any]) -> NarrativeStory:
        """가족 서사 생성"""
        # 최근 기억들 수집
        recent_memories = [m for m in self.narrative_memories 
                          if (datetime.now() - m.timestamp).days <= 30]
        
        if not recent_memories:
            # 샘플 기억 생성
            recent_memories = self._create_sample_memories(family_context)
        
        # 가족 서사 생성
        story = self.generate_narrative_story("가족의 성장과 사랑", recent_memories)
        
        return story
    
    def _create_sample_memories(self, family_context: Dict[str, Any]) -> List[NarrativeMemory]:
        """샘플 기억 생성"""
        sample_memories = []
        
        # 일상 경험
        daily_memory = self.create_narrative_memory(
            title="함께한 저녁 식사",
            description="오늘 저녁에 가족과 함께 맛있는 음식을 먹었습니다. 아이들이 학교에서 있었던 일을 재미있게 이야기해주었고, 모두가 웃으며 대화를 나누었습니다.",
            memory_type=MemoryType.DAILY_EXPERIENCE,
            emotional_tone=EmotionalTone.JOY,
            family_members=['아빠', '엄마', '아이1', '아이2'],
            key_emotions=['기쁨', '감사', '따뜻함'],
            lessons_learned=['소통의 중요성', '가족 시간의 소중함'],
            location='집',
            duration_minutes=60
        )
        sample_memories.append(daily_memory)
        
        # 학습 경험
        learning_memory = self.create_narrative_memory(
            title="함께 배운 새로운 것",
            description="아이들과 함께 새로운 게임을 배웠습니다. 처음에는 어려워했지만 서로 도와가며 점점 재미있어졌습니다.",
            memory_type=MemoryType.LEARNING_EXPERIENCE,
            emotional_tone=EmotionalTone.EXCITEMENT,
            family_members=['아빠', '아이1', '아이2'],
            key_emotions=['흥미', '성취감', '협력'],
            lessons_learned=['함께 배우는 즐거움', '인내심의 중요성'],
            location='거실',
            duration_minutes=45
        )
        sample_memories.append(learning_memory)
        
        return sample_memories
    
    def get_narrative_statistics(self) -> Dict[str, Any]:
        """서사적 기억 통계"""
        total_memories = len(self.narrative_memories)
        total_connections = len(self.memory_connections)
        total_stories = len(self.narrative_stories)
        
        # 기억 유형별 통계
        memory_type_stats = {}
        for memory_type in MemoryType:
            type_memories = [m for m in self.narrative_memories if m.memory_type == memory_type]
            memory_type_stats[memory_type.value] = len(type_memories)
        
        # 감정적 톤별 통계
        emotional_tone_stats = {}
        for tone in EmotionalTone:
            tone_memories = [m for m in self.narrative_memories if m.emotional_tone == tone]
            emotional_tone_stats[tone.value] = len(tone_memories)
        
        statistics = {
            'total_memories': total_memories,
            'total_connections': total_connections,
            'total_stories': total_stories,
            'memory_type_statistics': memory_type_stats,
            'emotional_tone_statistics': emotional_tone_stats,
            'average_confidence': sum(m.confidence_score for m in self.narrative_memories) / max(1, total_memories),
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("서사적 기억 통계 생성 완료")
        return statistics
    
    def export_narrative_data(self) -> Dict[str, Any]:
        """서사적 기억 데이터 내보내기"""
        return {
            'narrative_memories': [asdict(m) for m in self.narrative_memories],
            'memory_connections': [asdict(c) for c in self.memory_connections],
            'narrative_stories': [asdict(s) for s in self.narrative_stories],
            'family_members': self.family_members,
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_narrative_memory_enhancer():
    """서사적 기억 고도화 시스템 테스트"""
    print("📖 NarrativeMemoryEnhancer 테스트 시작...")
    
    narrative_system = NarrativeMemoryEnhancer()
    
    # 1. 서사적 기억 생성
    family_context = {
        'family_type': 'nuclear',
        'children_count': 2,
        'children_ages': [5, 8],
        'family_values': ['사랑', '소통', '성장', '창의성']
    }
    
    memory1 = narrative_system.create_narrative_memory(
        title="함께한 주말 등산",
        description="가족과 함께 산에 올라갔습니다. 아이들이 처음에는 힘들어했지만 서로 격려하며 정상에 도달했습니다. 정상에서 본 풍경이 정말 아름다웠고, 모두가 성취감을 느꼈습니다.",
        memory_type=MemoryType.FAMILY_ACTIVITY,
        emotional_tone=EmotionalTone.JOY,
        family_members=['아빠', '엄마', '아이1', '아이2'],
        key_emotions=['성취감', '기쁨', '감사', '따뜻함'],
        lessons_learned=['함께하면 어려운 것도 이겨낼 수 있다', '인내심의 중요성', '자연의 아름다움'],
        location='산',
        duration_minutes=240
    )
    
    print(f"✅ 서사적 기억 생성: {memory1.title}")
    print(f"   기억 유형: {memory1.memory_type.value}")
    print(f"   감정적 톤: {memory1.emotional_tone.value}")
    print(f"   신뢰도: {memory1.confidence_score:.2f}")
    
    # 2. 기억 연결 생성
    memory2 = narrative_system.create_narrative_memory(
        title="함께한 요리 시간",
        description="가족과 함께 쿠키를 만들었습니다. 아이들이 반죽을 만지는 것을 좋아했고, 서로 도와가며 맛있는 쿠키를 만들었습니다.",
        memory_type=MemoryType.FAMILY_ACTIVITY,
        emotional_tone=EmotionalTone.LOVE,
        family_members=['엄마', '아이1', '아이2'],
        key_emotions=['사랑', '기쁨', '협력'],
        lessons_learned=['함께 만드는 즐거움', '협력의 중요성'],
        location='부엌',
        duration_minutes=90
    )
    
    connection = narrative_system.create_memory_connection(
        memory1, memory2, "thematic", "두 기억 모두 가족과 함께하는 활동이었습니다."
    )
    
    print(f"✅ 기억 연결 생성: {connection.connection_type}")
    print(f"   연결 강도: {connection.connection_strength:.2f}")
    
    # 3. 서사적 이야기 생성
    story = narrative_system.generate_narrative_story("가족과 함께하는 활동", [memory1, memory2])
    
    print(f"✅ 서사적 이야기 생성: {story.title}")
    print(f"   포함된 기억: {len(story.memories)}개")
    print(f"   가족 가치: {story.family_values_highlighted}")
    
    # 4. 기억 회상
    recalled_memories = narrative_system.recall_narrative_memory("함께", family_context)
    print(f"✅ 기억 회상: {len(recalled_memories)}개 기억 발견")
    
    # 5. 통계
    statistics = narrative_system.get_narrative_statistics()
    print(f"✅ 서사적 기억 통계: {statistics['total_memories']}개 기억, {statistics['total_connections']}개 연결")
    print(f"   평균 신뢰도: {statistics['average_confidence']:.2f}")
    print(f"   기억 유형 통계: {statistics['memory_type_statistics']}")
    
    # 6. 데이터 내보내기
    export_data = narrative_system.export_narrative_data()
    print(f"✅ 서사적 기억 데이터 내보내기: {len(export_data['narrative_memories'])}개 기억")
    
    print("🎉 NarrativeMemoryEnhancer 테스트 완료!")

if __name__ == "__main__":
    test_narrative_memory_enhancer() 