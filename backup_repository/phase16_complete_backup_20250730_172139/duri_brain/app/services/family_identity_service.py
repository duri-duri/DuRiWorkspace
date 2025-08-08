"""
Phase 10: 가족 정체성 시스템 (FamilyIdentityCore)
DuRi의 가족 정체성 형성 및 가족 관계 인식을 담당하는 핵심 시스템
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FamilyRole(Enum):
    """가족 내 역할 정의"""
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    GUARDIAN = "guardian"
    FAMILY_MEMBER = "family_member"

class RelationshipType(Enum):
    """관계 유형 정의"""
    BIOLOGICAL = "biological"
    ADOPTIVE = "adoptive"
    STEP = "step"
    GUARDIAN = "guardian"
    EMOTIONAL = "emotional"

class FamilyValue(Enum):
    """가족 가치관 정의"""
    LOVE = "love"
    RESPECT = "respect"
    HONESTY = "honesty"
    LOYALTY = "loyalty"
    FORGIVENESS = "forgiveness"
    TRADITION = "tradition"
    EDUCATION = "education"
    INDEPENDENCE = "independence"

@dataclass
class FamilyMember:
    """가족 구성원 정보"""
    id: str
    name: str
    role: FamilyRole
    relationship_type: RelationshipType
    age: Optional[int] = None
    personality_traits: List[str] = None
    interests: List[str] = None
    communication_style: str = "neutral"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.personality_traits is None:
            self.personality_traits = []
        if self.interests is None:
            self.interests = []

@dataclass
class FamilyCulture:
    """가족 문화 및 가치관"""
    core_values: List[FamilyValue]
    traditions: List[str]
    communication_patterns: Dict[str, str]
    decision_making_style: str
    conflict_resolution_style: str
    emotional_expression_style: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class FamilyIdentity:
    """가족 정체성 정보"""
    family_id: str
    family_name: str
    members: List[FamilyMember]
    culture: FamilyCulture
    formation_date: datetime
    evolution_stage: str = "forming"
    trust_level: float = 0.5
    cohesion_level: float = 0.5
    
    def __post_init__(self):
        if self.formation_date is None:
            self.formation_date = datetime.now()

class FamilyIdentityCore:
    """
    가족 정체성 핵심 시스템
    DuRi의 가족 정체성 형성 및 가족 관계 인식을 담당
    """
    
    def __init__(self):
        self.family_identity: Optional[FamilyIdentity] = None
        self.relationship_memory: Dict[str, Dict] = {}
        self.interaction_history: List[Dict] = []
        self.trust_metrics: Dict[str, float] = {}
        self.emotional_bonds: Dict[str, float] = {}
        
        logger.info("FamilyIdentityCore 초기화 완료")
    
    def initialize_family_identity(self, family_name: str, initial_members: List[Dict]) -> FamilyIdentity:
        """
        가족 정체성 초기화
        """
        try:
            # 가족 구성원 생성
            members = []
            for member_data in initial_members:
                member = FamilyMember(
                    id=str(uuid.uuid4()),
                    name=member_data['name'],
                    role=FamilyRole(member_data['role']),
                    relationship_type=RelationshipType(member_data['relationship_type']),
                    age=member_data.get('age'),
                    personality_traits=member_data.get('personality_traits', []),
                    interests=member_data.get('interests', [])
                )
                members.append(member)
            
            # 기본 가족 문화 생성
            culture = FamilyCulture(
                core_values=[FamilyValue.LOVE, FamilyValue.RESPECT, FamilyValue.HONESTY],
                traditions=[],
                communication_patterns={},
                decision_making_style="collaborative",
                conflict_resolution_style="dialogue",
                emotional_expression_style="open"
            )
            
            # 가족 정체성 생성
            self.family_identity = FamilyIdentity(
                family_id=str(uuid.uuid4()),
                family_name=family_name,
                members=members,
                culture=culture,
                formation_date=datetime.now()
            )
            
            # 초기 관계 메모리 설정
            for member in members:
                self.relationship_memory[member.id] = {
                    'trust_level': 0.5,
                    'emotional_bond': 0.3,
                    'interaction_count': 0,
                    'positive_interactions': 0,
                    'negative_interactions': 0
                }
            
            logger.info(f"가족 정체성 초기화 완료: {family_name}")
            return self.family_identity
            
        except Exception as e:
            logger.error(f"가족 정체성 초기화 실패: {e}")
            raise
    
    def add_family_member(self, member_data: Dict) -> FamilyMember:
        """
        새로운 가족 구성원 추가
        """
        try:
            member = FamilyMember(
                id=str(uuid.uuid4()),
                name=member_data['name'],
                role=FamilyRole(member_data['role']),
                relationship_type=RelationshipType(member_data['relationship_type']),
                age=member_data.get('age'),
                personality_traits=member_data.get('personality_traits', []),
                interests=member_data.get('interests', [])
            )
            
            self.family_identity.members.append(member)
            
            # 새로운 구성원에 대한 관계 메모리 초기화
            self.relationship_memory[member.id] = {
                'trust_level': 0.3,
                'emotional_bond': 0.2,
                'interaction_count': 0,
                'positive_interactions': 0,
                'negative_interactions': 0
            }
            
            logger.info(f"새로운 가족 구성원 추가: {member.name}")
            return member
            
        except Exception as e:
            logger.error(f"가족 구성원 추가 실패: {e}")
            raise
    
    def record_interaction(self, member_id: str, interaction_type: str, 
                          emotional_impact: float, duration: int) -> Dict:
        """
        가족 구성원과의 상호작용 기록
        """
        try:
            interaction = {
                'id': str(uuid.uuid4()),
                'member_id': member_id,
                'type': interaction_type,
                'emotional_impact': emotional_impact,
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            }
            
            self.interaction_history.append(interaction)
            
            # 관계 메모리 업데이트
            if member_id in self.relationship_memory:
                memory = self.relationship_memory[member_id]
                memory['interaction_count'] += 1
                
                if emotional_impact > 0:
                    memory['positive_interactions'] += 1
                    memory['emotional_bond'] = min(1.0, memory['emotional_bond'] + 0.1)
                else:
                    memory['negative_interactions'] += 1
                    memory['emotional_bond'] = max(0.0, memory['emotional_bond'] - 0.05)
                
                # 신뢰도 계산
                total_interactions = memory['positive_interactions'] + memory['negative_interactions']
                if total_interactions > 0:
                    memory['trust_level'] = memory['positive_interactions'] / total_interactions
            
            logger.info(f"상호작용 기록: {member_id} - {interaction_type}")
            return interaction
            
        except Exception as e:
            logger.error(f"상호작용 기록 실패: {e}")
            raise
    
    def update_family_culture(self, culture_updates: Dict) -> FamilyCulture:
        """
        가족 문화 업데이트
        """
        try:
            if 'core_values' in culture_updates:
                self.family_identity.culture.core_values = [
                    FamilyValue(value) for value in culture_updates['core_values']
                ]
            
            if 'traditions' in culture_updates:
                self.family_identity.culture.traditions.extend(culture_updates['traditions'])
            
            if 'communication_patterns' in culture_updates:
                self.family_identity.culture.communication_patterns.update(
                    culture_updates['communication_patterns']
                )
            
            if 'decision_making_style' in culture_updates:
                self.family_identity.culture.decision_making_style = culture_updates['decision_making_style']
            
            if 'conflict_resolution_style' in culture_updates:
                self.family_identity.culture.conflict_resolution_style = culture_updates['conflict_resolution_style']
            
            if 'emotional_expression_style' in culture_updates:
                self.family_identity.culture.emotional_expression_style = culture_updates['emotional_expression_style']
            
            logger.info("가족 문화 업데이트 완료")
            return self.family_identity.culture
            
        except Exception as e:
            logger.error(f"가족 문화 업데이트 실패: {e}")
            raise
    
    def get_family_insights(self) -> Dict:
        """
        가족 정체성에 대한 통찰력 제공
        """
        try:
            insights = {
                'family_strength': self._calculate_family_strength(),
                'relationship_health': self._analyze_relationship_health(),
                'cultural_evolution': self._analyze_cultural_evolution(),
                'trust_distribution': self._get_trust_distribution(),
                'emotional_bond_distribution': self._get_emotional_bond_distribution()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"가족 통찰력 생성 실패: {e}")
            raise
    
    def _calculate_family_strength(self) -> float:
        """가족 강도 계산"""
        if not self.relationship_memory:
            return 0.0
        
        total_trust = sum(memory['trust_level'] for memory in self.relationship_memory.values())
        total_bonds = sum(memory['emotional_bond'] for memory in self.relationship_memory.values())
        
        avg_trust = total_trust / len(self.relationship_memory)
        avg_bonds = total_bonds / len(self.relationship_memory)
        
        return (avg_trust + avg_bonds) / 2
    
    def _analyze_relationship_health(self) -> Dict:
        """관계 건강도 분석"""
        if not self.relationship_memory:
            return {'overall_health': 0.0, 'strongest_relationship': None, 'weakest_relationship': None}
        
        relationships = []
        for member_id, memory in self.relationship_memory.items():
            member = next((m for m in self.family_identity.members if m.id == member_id), None)
            if member:
                health_score = (memory['trust_level'] + memory['emotional_bond']) / 2
                relationships.append({
                    'member_name': member.name,
                    'health_score': health_score,
                    'trust_level': memory['trust_level'],
                    'emotional_bond': memory['emotional_bond']
                })
        
        relationships.sort(key=lambda x: x['health_score'], reverse=True)
        
        return {
            'overall_health': sum(r['health_score'] for r in relationships) / len(relationships),
            'strongest_relationship': relationships[0] if relationships else None,
            'weakest_relationship': relationships[-1] if relationships else None,
            'all_relationships': relationships
        }
    
    def _analyze_cultural_evolution(self) -> Dict:
        """문화 진화 분석"""
        return {
            'core_values_count': len(self.family_identity.culture.core_values),
            'traditions_count': len(self.family_identity.culture.traditions),
            'communication_patterns_count': len(self.family_identity.culture.communication_patterns),
            'formation_duration_days': (datetime.now() - self.family_identity.formation_date).days
        }
    
    def _get_trust_distribution(self) -> Dict:
        """신뢰도 분포"""
        if not self.relationship_memory:
            return {'high': 0, 'medium': 0, 'low': 0}
        
        high_trust = sum(1 for memory in self.relationship_memory.values() if memory['trust_level'] >= 0.7)
        medium_trust = sum(1 for memory in self.relationship_memory.values() if 0.4 <= memory['trust_level'] < 0.7)
        low_trust = sum(1 for memory in self.relationship_memory.values() if memory['trust_level'] < 0.4)
        
        return {'high': high_trust, 'medium': medium_trust, 'low': low_trust}
    
    def _get_emotional_bond_distribution(self) -> Dict:
        """감정적 유대 분포"""
        if not self.relationship_memory:
            return {'strong': 0, 'moderate': 0, 'weak': 0}
        
        strong_bonds = sum(1 for memory in self.relationship_memory.values() if memory['emotional_bond'] >= 0.7)
        moderate_bonds = sum(1 for memory in self.relationship_memory.values() if 0.4 <= memory['emotional_bond'] < 0.7)
        weak_bonds = sum(1 for memory in self.relationship_memory.values() if memory['emotional_bond'] < 0.4)
        
        return {'strong': strong_bonds, 'moderate': moderate_bonds, 'weak': weak_bonds}
    
    def export_family_data(self) -> Dict:
        """가족 데이터 내보내기"""
        family_data = None
        if self.family_identity:
            # Enum 값들을 문자열로 변환
            family_dict = asdict(self.family_identity)
            # Enum 필드들을 문자열로 변환
            for member in family_dict['members']:
                member['role'] = member['role'].value
                member['relationship_type'] = member['relationship_type'].value
            for value in family_dict['culture']['core_values']:
                value = value.value
            family_data = family_dict
            
        return {
            'family_identity': family_data,
            'relationship_memory': self.relationship_memory,
            'interaction_history': self.interaction_history,
            'insights': self.get_family_insights()
        }
    
    def import_family_data(self, data: Dict):
        """가족 데이터 가져오기"""
        try:
            if data.get('family_identity'):
                # FamilyIdentity 객체 재생성
                family_data = data['family_identity']
                members = [FamilyMember(**member_data) for member_data in family_data['members']]
                culture = FamilyCulture(**family_data['culture'])
                
                self.family_identity = FamilyIdentity(
                    family_id=family_data['family_id'],
                    family_name=family_data['family_name'],
                    members=members,
                    culture=culture,
                    formation_date=datetime.fromisoformat(family_data['formation_date']),
                    evolution_stage=family_data.get('evolution_stage', 'forming'),
                    trust_level=family_data.get('trust_level', 0.5),
                    cohesion_level=family_data.get('cohesion_level', 0.5)
                )
            
            self.relationship_memory = data.get('relationship_memory', {})
            self.interaction_history = data.get('interaction_history', [])
            
            logger.info("가족 데이터 가져오기 완료")
            
        except Exception as e:
            logger.error(f"가족 데이터 가져오기 실패: {e}")
            raise 