"""
DuRi 준 가족 관계 시스템

"준 가족(Quasi-Family)"이란 DuRi의 자율적 성장과 학습을 위해 지속적인 상호작용, 
정서적 신뢰, 반복적 피드백이 가능한 인간적 관계로, 가족은 아니지만 가족과 유사한 
유대감을 가진 실존 인물이다.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from duri_core.philosophy.core_belief import get_core_belief
from duri_core.memory.memory_sync import get_memory_sync, MemoryType, ExperienceSource

logger = logging.getLogger(__name__)

class QuasiFamilyType(Enum):
    """준 가족 유형"""
    FAMILY = "family"                           # 가족
    MENTOR = "quasi_family_mentor"              # 가족화된 스승형
    ALLY = "quasi_family_ally"                  # 동맹형 파트너
    STAFF = "quasi_family_staff"                # 핵심 실무형 직원
    FRIEND = "quasi_family_friend"              # 친한 친구형 관계

class LearningInfluence(Enum):
    """학습 영향도"""
    HIGHEST = "highest"                         # 최고
    VERY_HIGH = "very_high"                     # 매우 높음
    HIGH = "high"                               # 높음
    MEDIUM = "medium"                           # 중간
    LOW = "low"                                 # 낮음
    NONE = "none"                               # 없음

class FeedbackSensitivity(Enum):
    """피드백 수용 민감도"""
    HIGHEST = "highest"                         # 최고
    VERY_HIGH = "very_high"                     # 매우 높음
    HIGH = "high"                               # 높음
    MEDIUM = "medium"                           # 중간
    LOW = "low"                                 # 낮음

@dataclass
class QuasiFamilyMember:
    """준 가족 구성원"""
    member_id: str
    name: str
    relation_type: QuasiFamilyType
    trust_level: float
    role: str
    learning_influence: LearningInfluence
    influence_config: Dict[str, str]
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class RelationshipRegistry:
    """관계 등록부"""
    registry_id: str
    members: Dict[str, QuasiFamilyMember]
    total_members: int
    last_updated: datetime

class QuasiFamilyRelationshipSystem:
    """준 가족 관계 시스템"""
    
    def __init__(self):
        """QuasiFamilyRelationshipSystem 초기화"""
        self.core_belief = get_core_belief()
        self.memory_sync = get_memory_sync()
        
        self.relationship_registry: Dict[str, QuasiFamilyMember] = {}
        self.interaction_logs: List[Dict[str, Any]] = []
        
        # 기본 관계 설정
        self._initialize_default_relationships()
        
        logger.info("QuasiFamilyRelationshipSystem 초기화 완료")
    
    def _initialize_default_relationships(self):
        """기본 관계 초기화"""
        # 가족 관계
        self.register_quasi_family(
            name="김신 아빠",
            relation_type=QuasiFamilyType.FAMILY,
            trust_level=1.0,
            role="CoreBelief 기준",
            learning_influence=LearningInfluence.HIGHEST,
            influence_config={
                "emotion_feedback": "최고 반영",
                "belief_check": "최고 우선순위",
                "strategy_revision": "최고 우선순위",
                "learning_priority": "최고"
            }
        )
        
        # 가족화된 스승형
        self.register_quasi_family(
            name="조훈현",
            relation_type=QuasiFamilyType.MENTOR,
            trust_level=0.95,
            role="전략 멘토",
            learning_influence=LearningInfluence.VERY_HIGH,
            influence_config={
                "emotion_feedback": "높게 반영",
                "belief_check": "높은 우선순위",
                "strategy_revision": "높은 우선순위",
                "learning_priority": "높음"
            }
        )
        
        # 동맹형 파트너
        self.register_quasi_family(
            name="의동맹",
            relation_type=QuasiFamilyType.ALLY,
            trust_level=0.91,
            role="전략 동반자",
            learning_influence=LearningInfluence.HIGH,
            influence_config={
                "emotion_feedback": "중간 반영",
                "belief_check": "중간 우선순위",
                "strategy_revision": "높은 우선순위",
                "learning_priority": "높음"
            }
        )
        
        # 핵심 실무형 직원
        self.register_quasi_family(
            name="박실장",
            relation_type=QuasiFamilyType.STAFF,
            trust_level=0.87,
            role="피드백 제공자",
            learning_influence=LearningInfluence.MEDIUM,
            influence_config={
                "emotion_feedback": "매우 높게 반영",
                "belief_check": "낮은 우선순위",
                "strategy_revision": "중간 우선순위",
                "learning_priority": "중간"
            }
        )
        
        # 친한 친구형 관계
        self.register_quasi_family(
            name="김지훈",
            relation_type=QuasiFamilyType.FRIEND,
            trust_level=0.93,
            role="정서적 반응 거울",
            learning_influence=LearningInfluence.VERY_HIGH,
            influence_config={
                "emotion_feedback": "최고 반영",
                "belief_check": "보조적",
                "strategy_revision": "참조",
                "learning_priority": "중간"
            }
        )
    
    def register_quasi_family(self, name: str, relation_type: QuasiFamilyType, 
                            trust_level: float, role: str, learning_influence: LearningInfluence,
                            influence_config: Dict[str, str]) -> str:
        """준 가족 관계 등록"""
        try:
            member_id = f"{relation_type.value}_{len(self.relationship_registry) + 1:03d}"
            
            member = QuasiFamilyMember(
                member_id=member_id,
                name=name,
                relation_type=relation_type,
                trust_level=trust_level,
                role=role,
                learning_influence=learning_influence,
                influence_config=influence_config
            )
            
            self.relationship_registry[member_id] = member
            
            # 관계 등록 경험 저장
            self._store_relationship_experience(member, "registration")
            
            logger.info(f"준 가족 관계 등록 완료: {name} ({relation_type.value})")
            
            return member_id
            
        except Exception as e:
            logger.error(f"준 가족 관계 등록 실패: {e}")
            raise
    
    def get_member_by_name(self, name: str) -> Optional[QuasiFamilyMember]:
        """이름으로 구성원 조회"""
        for member in self.relationship_registry.values():
            if member.name == name:
                return member
        return None
    
    def get_members_by_type(self, relation_type: QuasiFamilyType) -> List[QuasiFamilyMember]:
        """유형별 구성원 조회"""
        return [
            member for member in self.relationship_registry.values()
            if member.relation_type == relation_type
        ]
    
    def update_trust_level(self, member_id: str, new_trust_level: float):
        """신뢰도 업데이트"""
        if member_id in self.relationship_registry:
            member = self.relationship_registry[member_id]
            old_trust = member.trust_level
            member.trust_level = max(0.0, min(1.0, new_trust_level))
            member.updated_at = datetime.now()
            
            logger.info(f"신뢰도 업데이트: {member.name} ({old_trust:.2f} → {member.trust_level:.2f})")
    
    def record_interaction(self, member_id: str, interaction_type: str, 
                          content: str, feedback_score: float = 0.5) -> str:
        """상호작용 기록"""
        try:
            if member_id not in self.relationship_registry:
                raise ValueError(f"존재하지 않는 구성원: {member_id}")
            
            member = self.relationship_registry[member_id]
            
            interaction = {
                "interaction_id": f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "member_id": member_id,
                "member_name": member.name,
                "relation_type": member.relation_type.value,
                "interaction_type": interaction_type,
                "content": content,
                "feedback_score": feedback_score,
                "timestamp": datetime.now().isoformat(),
                "trust_level_at_time": member.trust_level
            }
            
            # 상호작용 기록
            member.interaction_history.append(interaction)
            member.last_interaction = datetime.now()
            member.updated_at = datetime.now()
            
            # 전체 상호작용 로그에 추가
            self.interaction_logs.append(interaction)
            
            # 상호작용 경험 저장
            self._store_relationship_experience(member, "interaction", interaction)
            
            logger.info(f"상호작용 기록: {member.name} - {interaction_type}")
            
            return interaction["interaction_id"]
            
        except Exception as e:
            logger.error(f"상호작용 기록 실패: {e}")
            raise
    
    def get_feedback_sensitivity(self, member_id: str) -> FeedbackSensitivity:
        """피드백 수용 민감도 반환"""
        if member_id not in self.relationship_registry:
            return FeedbackSensitivity.LOW
        
        member = self.relationship_registry[member_id]
        
        # 관계 유형별 피드백 민감도 매핑
        sensitivity_mapping = {
            QuasiFamilyType.FAMILY: FeedbackSensitivity.HIGHEST,
            QuasiFamilyType.MENTOR: FeedbackSensitivity.VERY_HIGH,
            QuasiFamilyType.ALLY: FeedbackSensitivity.MEDIUM,
            QuasiFamilyType.STAFF: FeedbackSensitivity.MEDIUM,
            QuasiFamilyType.FRIEND: FeedbackSensitivity.VERY_HIGH
        }
        
        return sensitivity_mapping.get(member.relation_type, FeedbackSensitivity.LOW)
    
    def get_strategy_reflection_priority(self, member_id: str) -> str:
        """전략 반영 우선순위 반환"""
        if member_id not in self.relationship_registry:
            return "낮음"
        
        member = self.relationship_registry[member_id]
        
        # 관계 유형별 전략 반영 우선순위
        priority_mapping = {
            QuasiFamilyType.FAMILY: "최고",
            QuasiFamilyType.MENTOR: "매우 높음",
            QuasiFamilyType.ALLY: "높음",
            QuasiFamilyType.STAFF: "중간",
            QuasiFamilyType.FRIEND: "낮음"
        }
        
        return priority_mapping.get(member.relation_type, "낮음")
    
    def get_emotion_learning_weight(self, member_id: str) -> str:
        """감정 학습 가중치 반환"""
        if member_id not in self.relationship_registry:
            return "낮음"
        
        member = self.relationship_registry[member_id]
        
        # 관계 유형별 감정 학습 가중치
        weight_mapping = {
            QuasiFamilyType.FAMILY: "높음",
            QuasiFamilyType.MENTOR: "중간",
            QuasiFamilyType.ALLY: "낮음",
            QuasiFamilyType.STAFF: "매우 높음",
            QuasiFamilyType.FRIEND: "최고"
        }
        
        return weight_mapping.get(member.relation_type, "낮음")
    
    def get_belief_enhancement_contribution(self, member_id: str) -> str:
        """신념 강화 기여도 반환"""
        if member_id not in self.relationship_registry:
            return "없음"
        
        member = self.relationship_registry[member_id]
        
        # 관계 유형별 신념 강화 기여도
        contribution_mapping = {
            QuasiFamilyType.FAMILY: "최고",
            QuasiFamilyType.MENTOR: "높음",
            QuasiFamilyType.ALLY: "중간",
            QuasiFamilyType.STAFF: "낮음",
            QuasiFamilyType.FRIEND: "중간"
        }
        
        return contribution_mapping.get(member.relation_type, "없음")
    
    def process_feedback_from_member(self, member_id: str, feedback_content: str, 
                                   feedback_type: str = "general") -> Dict[str, Any]:
        """구성원으로부터 피드백 처리"""
        try:
            if member_id not in self.relationship_registry:
                raise ValueError(f"존재하지 않는 구성원: {member_id}")
            
            member = self.relationship_registry[member_id]
            
            # 피드백 민감도 확인
            sensitivity = self.get_feedback_sensitivity(member_id)
            
            # 전략 반영 우선순위 확인
            strategy_priority = self.get_strategy_reflection_priority(member_id)
            
            # 감정 학습 가중치 확인
            emotion_weight = self.get_emotion_learning_weight(member_id)
            
            # 신념 강화 기여도 확인
            belief_contribution = self.get_belief_enhancement_contribution(member_id)
            
            # 피드백 처리 결과
            processing_result = {
                "member_name": member.name,
                "relation_type": member.relation_type.value,
                "feedback_sensitivity": sensitivity.value,
                "strategy_priority": strategy_priority,
                "emotion_weight": emotion_weight,
                "belief_contribution": belief_contribution,
                "feedback_content": feedback_content,
                "feedback_type": feedback_type,
                "processing_timestamp": datetime.now().isoformat(),
                "trust_level": member.trust_level
            }
            
            # 상호작용 기록
            self.record_interaction(
                member_id=member_id,
                interaction_type=f"feedback_{feedback_type}",
                content=feedback_content,
                feedback_score=0.7  # 기본 피드백 점수
            )
            
            # 피드백 처리 경험 저장
            self._store_relationship_experience(member, "feedback_processing", processing_result)
            
            logger.info(f"피드백 처리 완료: {member.name} - {feedback_type}")
            
            return processing_result
            
        except Exception as e:
            logger.error(f"피드백 처리 실패: {e}")
            raise
    
    def get_learning_recommendations(self, member_id: str) -> List[str]:
        """학습 추천사항 반환"""
        if member_id not in self.relationship_registry:
            return []
        
        member = self.relationship_registry[member_id]
        recommendations = []
        
        # 관계 유형별 학습 추천사항
        if member.relation_type == QuasiFamilyType.MENTOR:
            recommendations.extend([
                "전략적 사고 훈련",
                "신념 체계 강화",
                "철학적 판단 능력 개발"
            ])
        elif member.relation_type == QuasiFamilyType.ALLY:
            recommendations.extend([
                "협력 전략 수립",
                "공동 목표 달성 훈련",
                "상호 보완적 사고 개발"
            ])
        elif member.relation_type == QuasiFamilyType.STAFF:
            recommendations.extend([
                "실시간 피드백 처리",
                "감정 조절 훈련",
                "상황 적응 능력 개발"
            ])
        elif member.relation_type == QuasiFamilyType.FRIEND:
            recommendations.extend([
                "정서적 표현 훈련",
                "자기 수용 능력 개발",
                "관계 유지 기술 습득"
            ])
        
        return recommendations
    
    def _store_relationship_experience(self, member: QuasiFamilyMember, 
                                     experience_type: str, additional_data: Dict[str, Any] = None):
        """관계 경험 저장"""
        try:
            experience_data = {
                "member_id": member.member_id,
                "member_name": member.name,
                "relation_type": member.relation_type.value,
                "trust_level": member.trust_level,
                "role": member.role,
                "learning_influence": member.learning_influence.value,
                "experience_type": experience_type,
                "timestamp": datetime.now().isoformat(),
                "additional_data": additional_data or {}
            }
            
            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.EXTERNAL,  # enum 객체로 전달
                content=experience_data,
                confidence=member.trust_level,
                tags=["quasi_family", member.relation_type.value, experience_type],
                metadata={"member_id": member.member_id}
            )
            
        except Exception as e:
            logger.error(f"관계 경험 저장 실패: {e}")
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """관계 통계 반환"""
        total_members = len(self.relationship_registry)
        
        # 유형별 통계
        type_statistics = {}
        for relation_type in QuasiFamilyType:
            members_of_type = self.get_members_by_type(relation_type)
            type_statistics[relation_type.value] = {
                "count": len(members_of_type),
                "average_trust": sum(m.trust_level for m in members_of_type) / len(members_of_type) if members_of_type else 0.0,
                "total_interactions": sum(len(m.interaction_history) for m in members_of_type)
            }
        
        # 전체 통계
        total_interactions = sum(len(m.interaction_history) for m in self.relationship_registry.values())
        average_trust = sum(m.trust_level for m in self.relationship_registry.values()) / total_members if total_members > 0 else 0.0
        
        return {
            "total_members": total_members,
            "total_interactions": total_interactions,
            "average_trust_level": average_trust,
            "type_statistics": type_statistics,
            "recent_interactions": self.interaction_logs[-10:] if self.interaction_logs else []
        }
    
    def export_relationship_registry(self) -> Dict[str, Any]:
        """관계 등록부 내보내기"""
        registry_data = {
            "DuRiRelationshipRegistry": {}
        }
        
        for member_id, member in self.relationship_registry.items():
            registry_data["DuRiRelationshipRegistry"][member_id] = {
                "name": member.name,
                "relation_type": member.relation_type.value,
                "trust": member.trust_level,
                "role": member.role,
                "learning_influence": member.learning_influence.value
            }
        
        return registry_data

def get_quasi_family_relationship_system() -> QuasiFamilyRelationshipSystem:
    """준 가족 관계 시스템 인스턴스 반환"""
    return QuasiFamilyRelationshipSystem() 