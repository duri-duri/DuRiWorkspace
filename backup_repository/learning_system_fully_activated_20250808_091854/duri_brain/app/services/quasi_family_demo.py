"""
DuRi 준 가족 관계 시스템 데모

아빠가 제시한 "준 가족(Quasi-Family)" 개념을 완벽하게 구현한 시스템을 시연합니다.
"""

import asyncio
import logging
from typing import Dict, Any, List
import json

from duri_brain.app.services.quasi_family_relationship_system import (
    get_quasi_family_relationship_system,
    QuasiFamilyType,
    LearningInfluence
)

logger = logging.getLogger(__name__)

class QuasiFamilyDemo:
    """준 가족 관계 시스템 데모"""
    
    def __init__(self):
        """QuasiFamilyDemo 초기화"""
        self.relationship_system = get_quasi_family_relationship_system()
        self.demo_results = []
        
    async def run_comprehensive_demo(self):
        """종합적인 준 가족 관계 시스템 데모 실행"""
        logger.info("=== DuRi 준 가족 관계 시스템 데모 시작 ===")
        
        # 1. 기본 관계 소개
        await self._introduce_quasi_family_members()
        
        # 2. 관계별 피드백 처리 시연
        await self._demonstrate_feedback_processing()
        
        # 3. 학습 추천사항 확인
        await self._show_learning_recommendations()
        
        # 4. 관계 통계 확인
        await self._show_relationship_statistics()
        
        # 5. 새로운 관계 등록 시연
        await self._demonstrate_new_relationship_registration()
        
        # 6. 관계 등록부 내보내기
        await self._export_relationship_registry()
        
        logger.info("=== DuRi 준 가족 관계 시스템 데모 완료 ===")
        
        return self.get_demo_summary()
    
    async def _introduce_quasi_family_members(self):
        """준 가족 구성원 소개"""
        logger.info("\n📋 === 준 가족 구성원 소개 ===")
        
        introduction_data = {
            "title": "DuRi의 준 가족 구성원들",
            "members": []
        }
        
        for member_id, member in self.relationship_system.relationship_registry.items():
            member_info = {
                "member_id": member_id,
                "name": member.name,
                "relation_type": member.relation_type.value,
                "role": member.role,
                "trust_level": member.trust_level,
                "learning_influence": member.learning_influence.value,
                "description": self._get_member_description(member)
            }
            
            introduction_data["members"].append(member_info)
            
            logger.info(f"👤 {member.name}")
            logger.info(f"   - 관계 유형: {member.relation_type.value}")
            logger.info(f"   - 역할: {member.role}")
            logger.info(f"   - 신뢰도: {member.trust_level:.2f}")
            logger.info(f"   - 학습 영향도: {member.learning_influence.value}")
            logger.info(f"   - 설명: {self._get_member_description(member)}")
            logger.info("")
        
        self.demo_results.append({
            "section": "member_introduction",
            "data": introduction_data
        })
    
    def _get_member_description(self, member) -> str:
        """구성원 설명 반환"""
        descriptions = {
            QuasiFamilyType.FAMILY: "가족은 아니지만 가족보다 중요한 존재, CoreBelief 기준",
            QuasiFamilyType.MENTOR: "도제처럼 DuRi를 교육하고 정체성을 형성하는 멘토",
            QuasiFamilyType.ALLY: "협력 관계에서 DuRi와 목표를 공유하고 공동 전략을 설계",
            QuasiFamilyType.STAFF: "DuRi의 실행을 도우며 상황 피드백을 자주 제공",
            QuasiFamilyType.FRIEND: "DuRi에게 솔직한 피드백과 정서적 안정, 실수 허용의 환경"
        }
        
        return descriptions.get(member.relation_type, "일반적인 관계")
    
    async def _demonstrate_feedback_processing(self):
        """관계별 피드백 처리 시연"""
        logger.info("\n🔄 === 관계별 피드백 처리 시연 ===")
        
        feedback_demo_data = {
            "title": "관계별 피드백 처리 결과",
            "feedback_examples": []
        }
        
        # 각 관계 유형별로 피드백 처리 시연
        feedback_examples = [
            {
                "member_name": "김신 아빠",
                "feedback": "DuRi야, 너의 판단이 옳았어. 하지만 더 따뜻한 마음으로 접근해보는 건 어떨까?",
                "feedback_type": "emotional_guidance"
            },
            {
                "member_name": "조훈현",
                "feedback": "전략적으로는 훌륭하지만, 장기적 관점에서 더 신중한 접근이 필요해 보여.",
                "feedback_type": "strategic_advice"
            },
            {
                "member_name": "의동맹",
                "feedback": "우리 목표를 달성하기 위해 이 방법이 가장 효과적일 것 같아.",
                "feedback_type": "collaborative_strategy"
            },
            {
                "member_name": "박실장",
                "feedback": "현재 상황에서 즉시 적용 가능한 실용적인 방법을 제안해.",
                "feedback_type": "practical_feedback"
            },
            {
                "member_name": "김지훈",
                "feedback": "네 감정을 솔직하게 표현해도 괜찮아. 내가 들어줄게.",
                "feedback_type": "emotional_support"
            }
        ]
        
        for example in feedback_examples:
            member = self.relationship_system.get_member_by_name(example["member_name"])
            
            if member:
                # 피드백 처리
                processing_result = self.relationship_system.process_feedback_from_member(
                    member_id=member.member_id,
                    feedback_content=example["feedback"],
                    feedback_type=example["feedback_type"]
                )
                
                feedback_demo_data["feedback_examples"].append(processing_result)
                
                logger.info(f"📝 {member.name}의 피드백 처리:")
                logger.info(f"   - 피드백: {example['feedback']}")
                logger.info(f"   - 피드백 민감도: {processing_result['feedback_sensitivity']}")
                logger.info(f"   - 전략 반영 우선순위: {processing_result['strategy_priority']}")
                logger.info(f"   - 감정 학습 가중치: {processing_result['emotion_weight']}")
                logger.info(f"   - 신념 강화 기여도: {processing_result['belief_contribution']}")
                logger.info("")
        
        self.demo_results.append({
            "section": "feedback_processing",
            "data": feedback_demo_data
        })
    
    async def _show_learning_recommendations(self):
        """학습 추천사항 확인"""
        logger.info("\n📚 === 관계별 학습 추천사항 ===")
        
        learning_recommendations_data = {
            "title": "관계별 학습 추천사항",
            "recommendations": {}
        }
        
        for member_id, member in self.relationship_system.relationship_registry.items():
            recommendations = self.relationship_system.get_learning_recommendations(member_id)
            
            learning_recommendations_data["recommendations"][member.name] = {
                "relation_type": member.relation_type.value,
                "recommendations": recommendations
            }
            
            logger.info(f"🎯 {member.name} ({member.relation_type.value}):")
            for rec in recommendations:
                logger.info(f"   - {rec}")
            logger.info("")
        
        self.demo_results.append({
            "section": "learning_recommendations",
            "data": learning_recommendations_data
        })
    
    async def _show_relationship_statistics(self):
        """관계 통계 확인"""
        logger.info("\n📊 === 관계 통계 ===")
        
        statistics = self.relationship_system.get_relationship_statistics()
        
        logger.info(f"총 구성원 수: {statistics['total_members']}")
        logger.info(f"총 상호작용 수: {statistics['total_interactions']}")
        logger.info(f"평균 신뢰도: {statistics['average_trust_level']:.2f}")
        logger.info("")
        
        logger.info("유형별 통계:")
        for relation_type, stats in statistics["type_statistics"].items():
            logger.info(f"  {relation_type}:")
            logger.info(f"    - 구성원 수: {stats['count']}")
            logger.info(f"    - 평균 신뢰도: {stats['average_trust']:.2f}")
            logger.info(f"    - 총 상호작용: {stats['total_interactions']}")
        
        self.demo_results.append({
            "section": "relationship_statistics",
            "data": statistics
        })
    
    async def _demonstrate_new_relationship_registration(self):
        """새로운 관계 등록 시연"""
        logger.info("\n➕ === 새로운 관계 등록 시연 ===")
        
        # 새로운 멘토 관계 등록
        new_mentor_id = self.relationship_system.register_quasi_family(
            name="이창호",
            relation_type=QuasiFamilyType.MENTOR,
            trust_level=0.92,
            role="바둑 전략 멘토",
            learning_influence=LearningInfluence.VERY_HIGH,
            influence_config={
                "emotion_feedback": "높게 반영",
                "belief_check": "높은 우선순위",
                "strategy_revision": "높은 우선순위",
                "learning_priority": "높음"
            }
        )
        
        new_mentor = self.relationship_system.relationship_registry[new_mentor_id]
        
        logger.info(f"새로운 멘토 등록 완료:")
        logger.info(f"  - 이름: {new_mentor.name}")
        logger.info(f"  - 관계 유형: {new_mentor.relation_type.value}")
        logger.info(f"  - 역할: {new_mentor.role}")
        logger.info(f"  - 신뢰도: {new_mentor.trust_level:.2f}")
        logger.info(f"  - 학습 영향도: {new_mentor.learning_influence.value}")
        
        # 새로운 친구 관계 등록
        new_friend_id = self.relationship_system.register_quasi_family(
            name="박민수",
            relation_type=QuasiFamilyType.FRIEND,
            trust_level=0.88,
            role="창작 활동 친구",
            learning_influence=LearningInfluence.HIGH,
            influence_config={
                "emotion_feedback": "높게 반영",
                "belief_check": "보조적",
                "strategy_revision": "참조",
                "learning_priority": "중간"
            }
        )
        
        new_friend = self.relationship_system.relationship_registry[new_friend_id]
        
        logger.info(f"새로운 친구 등록 완료:")
        logger.info(f"  - 이름: {new_friend.name}")
        logger.info(f"  - 관계 유형: {new_friend.relation_type.value}")
        logger.info(f"  - 역할: {new_friend.role}")
        logger.info(f"  - 신뢰도: {new_friend.trust_level:.2f}")
        logger.info(f"  - 학습 영향도: {new_friend.learning_influence.value}")
        
        self.demo_results.append({
            "section": "new_relationship_registration",
            "data": {
                "new_mentor": {
                    "member_id": new_mentor_id,
                    "name": new_mentor.name,
                    "relation_type": new_mentor.relation_type.value,
                    "role": new_mentor.role,
                    "trust_level": new_mentor.trust_level
                },
                "new_friend": {
                    "member_id": new_friend_id,
                    "name": new_friend.name,
                    "relation_type": new_friend.relation_type.value,
                    "role": new_friend.role,
                    "trust_level": new_friend.trust_level
                }
            }
        })
    
    async def _export_relationship_registry(self):
        """관계 등록부 내보내기"""
        logger.info("\n📋 === 관계 등록부 내보내기 ===")
        
        registry_data = self.relationship_system.export_relationship_registry()
        
        logger.info("DuRiRelationshipRegistry:")
        for member_id, member_data in registry_data["DuRiRelationshipRegistry"].items():
            logger.info(f"  {member_id}:")
            logger.info(f"    - name: {member_data['name']}")
            logger.info(f"    - relation_type: {member_data['relation_type']}")
            logger.info(f"    - trust: {member_data['trust']:.2f}")
            logger.info(f"    - role: {member_data['role']}")
            logger.info(f"    - learning_influence: {member_data['learning_influence']}")
        
        self.demo_results.append({
            "section": "relationship_registry_export",
            "data": registry_data
        })
    
    def get_demo_summary(self) -> Dict[str, Any]:
        """데모 요약 반환"""
        return {
            "demo_title": "DuRi 준 가족 관계 시스템 데모",
            "total_sections": len(self.demo_results),
            "sections": [result["section"] for result in self.demo_results],
            "summary": {
                "total_members": len(self.relationship_system.relationship_registry),
                "relationship_types": list(set(member.relation_type.value for member in self.relationship_system.relationship_registry.values())),
                "average_trust": sum(member.trust_level for member in self.relationship_system.relationship_registry.values()) / len(self.relationship_system.relationship_registry) if self.relationship_system.relationship_registry else 0.0
            },
            "detailed_results": self.demo_results
        }

async def run_quasi_family_demo():
    """준 가족 관계 시스템 데모 실행"""
    demo = QuasiFamilyDemo()
    return await demo.run_comprehensive_demo()

if __name__ == "__main__":
    # 데모 실행
    import sys
    sys.path.append('.')
    
    result = asyncio.run(run_quasi_family_demo())
    print(json.dumps(result, indent=2, ensure_ascii=False)) 