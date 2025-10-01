#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 사회적 지능 시스템 - 관계 유형 전략 패턴

이 모듈은 다양한 관계 유형을 전략 패턴으로 처리하는 시스템입니다.
각 관계 유형별로 독립적인 전략 객체를 통해 일관된 처리를 제공합니다.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from social_intelligence_system import (
    InteractionType,
    RelationshipType,
    SocialContext,
    SocialContextType,
)

logger = logging.getLogger(__name__)


@dataclass
class RelationshipContext:
    """관계 처리 컨텍스트"""

    participants: List[str]
    context_type: SocialContextType
    interaction_type: InteractionType
    emotional_atmosphere: Dict[str, float]
    power_dynamics: Dict[str, float]
    cultural_context: Dict[str, Any]
    goals: List[str]
    constraints: List[str]


class RelationshipStrategy(ABC):
    """관계 유형 처리 전략 기본 클래스"""

    @abstractmethod
    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """관계 유형별 처리 로직"""
        pass

    @abstractmethod
    def get_communication_style(self, context: RelationshipContext) -> str:
        """의사소통 스타일 결정"""
        pass

    @abstractmethod
    def get_trust_level(self, context: RelationshipContext) -> float:
        """신뢰도 수준 결정"""
        pass

    @abstractmethod
    def get_intimacy_level(self, context: RelationshipContext) -> float:
        """친밀도 수준 결정"""
        pass


class OneOnOneStrategy(RelationshipStrategy):
    """1:1 관계 유형 처리 전략"""

    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """1:1 관계 전용 처리"""
        try:
            # 개별 신뢰 기반 관계 분석
            trust_level = self.get_trust_level(context)
            intimacy_level = self.get_intimacy_level(context)

            # 1:1 관계의 특별한 특성들
            characteristics = {
                "trust_based": True,
                "individual_attention": True,
                "personalized_interaction": True,
                "confidentiality": True,
                "direct_communication": True,
            }

            communication_style = self.get_communication_style(context)

            return {
                "relationship_type": "one_on_one",
                "trust_level": trust_level,
                "intimacy_level": intimacy_level,
                "communication_style": communication_style,
                "characteristics": characteristics,
                "recommendations": [
                    "개별적인 관심과 집중 제공",
                    "신뢰 기반의 개방적 소통",
                    "개인화된 응답과 피드백",
                    "직접적이고 명확한 의사소통",
                ],
            }
        except Exception as e:
            logger.warning(f"1:1 관계 처리 중 오류: {e}")
            return self._get_default_result()

    def get_communication_style(self, context: RelationshipContext) -> str:
        """1:1 관계 의사소통 스타일"""
        if context.context_type == SocialContextType.FORMAL:
            return "professional_personal"
        elif context.context_type == SocialContextType.INFORMAL:
            return "casual_personal"
        else:
            return "personal"

    def get_trust_level(self, context: RelationshipContext) -> float:
        """1:1 관계 신뢰도"""
        trust_level = 0.7  # 기본 신뢰도

        for participant in context.participants:
            if "user" in participant.lower():
                trust_level = 0.8
            elif "duri" in participant.lower():
                trust_level = 0.9

        return trust_level

    def get_intimacy_level(self, context: RelationshipContext) -> float:
        """1:1 관계 친밀도"""
        intimacy_level = 0.6  # 기본 친밀도

        for participant in context.participants:
            if "user" in participant.lower():
                intimacy_level = 0.7
            elif "duri" in participant.lower():
                intimacy_level = 0.8

        return intimacy_level

    def _get_default_result(self) -> Dict[str, Any]:
        """기본 결과 반환"""
        return {
            "relationship_type": "one_on_one",
            "trust_level": 0.5,
            "intimacy_level": 0.5,
            "communication_style": "personal",
            "characteristics": {"trust_based": True, "individual_attention": True},
            "recommendations": ["기본적인 1:1 상호작용 제공"],
        }


class FriendStrategy(RelationshipStrategy):
    """친구 관계 유형 처리 전략"""

    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """친구 관계 전용 처리"""
        trust_level = self.get_trust_level(context)
        intimacy_level = self.get_intimacy_level(context)

        characteristics = {
            "casual_interaction": True,
            "shared_interests": True,
            "mutual_support": True,
            "informal_communication": True,
        }

        communication_style = self.get_communication_style(context)

        return {
            "relationship_type": "friend",
            "trust_level": trust_level,
            "intimacy_level": intimacy_level,
            "communication_style": communication_style,
            "characteristics": characteristics,
            "recommendations": [
                "친근하고 편안한 분위기 조성",
                "공통 관심사 기반 대화",
                "상호 지원과 격려",
                "자연스러운 소통",
            ],
        }

    def get_communication_style(self, context: RelationshipContext) -> str:
        return "casual"

    def get_trust_level(self, context: RelationshipContext) -> float:
        return 0.8

    def get_intimacy_level(self, context: RelationshipContext) -> float:
        return 0.7


class ColleagueStrategy(RelationshipStrategy):
    """동료 관계 유형 처리 전략"""

    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """동료 관계 전용 처리"""
        trust_level = self.get_trust_level(context)
        intimacy_level = self.get_intimacy_level(context)

        characteristics = {
            "professional_interaction": True,
            "collaborative_work": True,
            "respectful_communication": True,
            "goal_oriented": True,
        }

        communication_style = self.get_communication_style(context)

        return {
            "relationship_type": "colleague",
            "trust_level": trust_level,
            "intimacy_level": intimacy_level,
            "communication_style": communication_style,
            "characteristics": characteristics,
            "recommendations": [
                "전문적이고 존중하는 소통",
                "협력적 작업 환경 조성",
                "목표 지향적 상호작용",
                "적절한 경계 유지",
            ],
        }

    def get_communication_style(self, context: RelationshipContext) -> str:
        return "professional"

    def get_trust_level(self, context: RelationshipContext) -> float:
        return 0.6

    def get_intimacy_level(self, context: RelationshipContext) -> float:
        return 0.4


class MentorStrategy(RelationshipStrategy):
    """멘토 관계 유형 처리 전략"""

    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """멘토 관계 전용 처리"""
        trust_level = self.get_trust_level(context)
        intimacy_level = self.get_intimacy_level(context)

        characteristics = {
            "guidance_oriented": True,
            "supportive_teaching": True,
            "experience_sharing": True,
            "developmental_focus": True,
        }

        communication_style = self.get_communication_style(context)

        return {
            "relationship_type": "mentor",
            "trust_level": trust_level,
            "intimacy_level": intimacy_level,
            "communication_style": communication_style,
            "characteristics": characteristics,
            "recommendations": [
                "지도와 조언 제공",
                "지지적이고 격려하는 소통",
                "경험 공유와 학습",
                "개발과 성장에 집중",
            ],
        }

    def get_communication_style(self, context: RelationshipContext) -> str:
        return "supportive"

    def get_trust_level(self, context: RelationshipContext) -> float:
        return 0.8

    def get_intimacy_level(self, context: RelationshipContext) -> float:
        return 0.6


class DefaultStrategy(RelationshipStrategy):
    """기본 관계 유형 처리 전략"""

    def handle(self, context: RelationshipContext) -> Dict[str, Any]:
        """기본 관계 처리"""
        return {
            "relationship_type": "default",
            "trust_level": 0.5,
            "intimacy_level": 0.5,
            "communication_style": "professional",
            "characteristics": {"standard_interaction": True},
            "recommendations": ["표준적인 상호작용 제공"],
        }

    def get_communication_style(self, context: RelationshipContext) -> str:
        return "professional"

    def get_trust_level(self, context: RelationshipContext) -> float:
        return 0.5

    def get_intimacy_level(self, context: RelationshipContext) -> float:
        return 0.5


# 관계 유형별 전략 핸들러 딕셔너리
RELATIONSHIP_HANDLERS = {
    RelationshipType.ONE_ON_ONE: OneOnOneStrategy(),
    RelationshipType.FRIEND: FriendStrategy(),
    RelationshipType.COLLEAGUE: ColleagueStrategy(),
    RelationshipType.MENTOR: MentorStrategy(),
    RelationshipType.STUDENT: MentorStrategy(),  # 멘토 전략 재사용
    RelationshipType.FAMILY: FriendStrategy(),  # 친구 전략 재사용
    RelationshipType.STRANGER: DefaultStrategy(),
    RelationshipType.ACQUAINTANCE: DefaultStrategy(),
}


def get_relationship_strategy(
    relationship_type: RelationshipType,
) -> RelationshipStrategy:
    """관계 유형에 따른 전략 반환"""
    return RELATIONSHIP_HANDLERS.get(relationship_type, DefaultStrategy())


def handle_relationship(
    context: RelationshipContext, relationship_type: RelationshipType
) -> Dict[str, Any]:
    """관계 유형별 처리 실행"""
    strategy = get_relationship_strategy(relationship_type)
    return strategy.handle(context)
