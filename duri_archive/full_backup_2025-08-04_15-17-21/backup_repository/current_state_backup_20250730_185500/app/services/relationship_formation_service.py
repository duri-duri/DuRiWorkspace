"""
Phase 10: 관계 형성 시스템 (FamilyRelationshipFormationSystem)
가족 구성원과의 상호작용 학습, 관계 패턴 인식 및 적응, 가족 내 역할과 책임 이해
"""

import json
import logging
import math
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """상호작용 유형 정의"""

    CONVERSATION = "conversation"
    ACTIVITY = "activity"
    SUPPORT = "support"
    CONFLICT = "conflict"
    CELEBRATION = "celebration"
    LEARNING = "learning"
    EMOTIONAL_SUPPORT = "emotional_support"
    PRACTICAL_HELP = "practical_help"
    FAMILY_INTERACTION = "family_interaction"
    EMOTIONAL = "emotional"
    DAILY_LIFE = "daily_life"


class RelationshipQuality(Enum):
    """관계 품질 정의"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CONFLICTED = "conflicted"


class RoleExpectation(Enum):
    """역할 기대 정의"""

    LEADER = "leader"
    SUPPORTER = "supporter"
    LEARNER = "learner"
    CAREGIVER = "caregiver"
    MENTOR = "mentor"
    FRIEND = "friend"


@dataclass
class Interaction:
    """상호작용 데이터 구조"""

    id: str
    participants: List[str]
    interaction_type: InteractionType
    duration_minutes: int
    emotional_impact: float  # -1.0 to 1.0
    satisfaction_level: float  # 0.0 to 1.0
    communication_quality: float  # 0.0 to 1.0
    mutual_understanding: float  # 0.0 to 1.0
    context: Dict[str, Any]
    timestamp: datetime
    location: str
    weather: Optional[str] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RelationshipPattern:
    """관계 패턴 데이터 구조"""

    id: str
    participant_pair: Tuple[str, str]
    pattern_type: str
    frequency: int
    average_quality: float
    common_interactions: List[str]
    emotional_trend: str  # improving, stable, declining
    trust_level: float
    communication_style: str
    conflict_resolution_style: str
    support_pattern: str


@dataclass
class RoleUnderstanding:
    """역할 이해 데이터 구조"""

    member_id: str
    role: RoleExpectation
    responsibilities: List[str]
    expectations: List[str]
    performance_score: float  # 0.0 to 1.0
    satisfaction_score: float  # 0.0 to 1.0
    adaptation_level: float  # 0.0 to 1.0
    last_updated: datetime


class FamilyRelationshipFormationSystem:
    """
    가족 관계 형성 시스템
    가족 구성원과의 상호작용 학습, 관계 패턴 인식 및 적응, 가족 내 역할과 책임 이해
    """

    def __init__(self):
        self.interactions: List[Interaction] = []
        self.relationship_patterns: List[RelationshipPattern] = []
        self.role_understandings: Dict[str, RoleUnderstanding] = {}
        self.trust_metrics: Dict[str, Dict[str, float]] = {}
        self.communication_patterns: Dict[str, Dict[str, Any]] = {}
        self.conflict_history: List[Dict] = []
        self.support_network: Dict[str, List[str]] = {}

        logger.info("FamilyRelationshipFormationSystem 초기화 완료")

    def record_interaction(self, interaction_data: Dict) -> Interaction:
        """
        새로운 상호작용 기록
        """
        try:
            interaction = Interaction(
                id=str(uuid.uuid4()),
                participants=interaction_data["participants"],
                interaction_type=InteractionType(interaction_data["interaction_type"]),
                duration_minutes=interaction_data.get("duration_minutes", 0),
                emotional_impact=interaction_data["emotional_impact"],
                satisfaction_level=interaction_data["satisfaction_level"],
                communication_quality=interaction_data["communication_quality"],
                mutual_understanding=interaction_data["mutual_understanding"],
                context=interaction_data.get("context", {}),
                timestamp=datetime.now(),
                location=interaction_data.get("location", "unknown"),
                weather=interaction_data.get("weather"),
                mood_before=interaction_data.get("mood_before"),
                mood_after=interaction_data.get("mood_after"),
            )

            self.interactions.append(interaction)

            # 관계 패턴 업데이트
            self._update_relationship_patterns(interaction)

            # 신뢰도 메트릭 업데이트
            self._update_trust_metrics(interaction)

            # 의사소통 패턴 업데이트
            self._update_communication_patterns(interaction)

            # 지원 네트워크 업데이트
            self._update_support_network(interaction)

            logger.info(f"상호작용 기록 완료: {interaction.interaction_type.value}")
            return interaction

        except Exception as e:
            logger.error(f"상호작용 기록 실패: {e}")
            raise

    def analyze_relationship_health(self, member_id: str) -> Dict:
        """
        특정 구성원의 관계 건강도 분석
        """
        try:
            # 해당 구성원과의 모든 상호작용
            member_interactions = [
                i for i in self.interactions if member_id in i.participants
            ]

            if not member_interactions:
                return {"overall_health": 0.0, "relationships": {}, "insights": []}

            # 각 관계별 분석
            relationships = {}
            for interaction in member_interactions:
                other_participants = [
                    p for p in interaction.participants if p != member_id
                ]
                for other_id in other_participants:
                    if other_id not in relationships:
                        relationships[other_id] = {
                            "interactions": [],
                            "total_emotional_impact": 0.0,
                            "total_satisfaction": 0.0,
                            "total_communication_quality": 0.0,
                            "interaction_count": 0,
                        }

                    relationships[other_id]["interactions"].append(interaction)
                    relationships[other_id][
                        "total_emotional_impact"
                    ] += interaction.emotional_impact
                    relationships[other_id][
                        "total_satisfaction"
                    ] += interaction.satisfaction_level
                    relationships[other_id][
                        "total_communication_quality"
                    ] += interaction.communication_quality
                    relationships[other_id]["interaction_count"] += 1

            # 평균 계산
            for other_id, data in relationships.items():
                count = data["interaction_count"]
                data["avg_emotional_impact"] = data["total_emotional_impact"] / count
                data["avg_satisfaction"] = data["total_satisfaction"] / count
                data["avg_communication_quality"] = (
                    data["total_communication_quality"] / count
                )
                data["relationship_health"] = (
                    data["avg_emotional_impact"]
                    + data["avg_satisfaction"]
                    + data["avg_communication_quality"]
                ) / 3

            # 전체 건강도 계산
            overall_health = sum(
                data["relationship_health"] for data in relationships.values()
            ) / len(relationships)

            # 통찰력 생성
            insights = self._generate_relationship_insights(member_id, relationships)

            return {
                "overall_health": overall_health,
                "relationships": relationships,
                "insights": insights,
            }

        except Exception as e:
            logger.error(f"관계 건강도 분석 실패: {e}")
            raise

    def understand_family_role(
        self, member_id: str, role_data: Dict
    ) -> RoleUnderstanding:
        """
        가족 내 역할 이해 및 적응
        """
        try:
            role_understanding = RoleUnderstanding(
                member_id=member_id,
                role=RoleExpectation(role_data["role"]),
                responsibilities=role_data.get("responsibilities", []),
                expectations=role_data.get("expectations", []),
                performance_score=role_data.get("performance_score", 0.5),
                satisfaction_score=role_data.get("satisfaction_score", 0.5),
                adaptation_level=role_data.get("adaptation_level", 0.3),
                last_updated=datetime.now(),
            )

            self.role_understandings[member_id] = role_understanding

            # 역할 적응도 업데이트
            self._update_role_adaptation(member_id, role_understanding)

            logger.info(
                f"역할 이해 업데이트: {member_id} - {role_understanding.role.value}"
            )
            return role_understanding

        except Exception as e:
            logger.error(f"역할 이해 실패: {e}")
            raise

    def get_relationship_insights(self) -> Dict:
        """
        전체 관계 통찰력 제공
        """
        try:
            insights = {
                "overall_relationship_health": self._calculate_overall_relationship_health(),
                "communication_patterns": self._analyze_communication_patterns(),
                "conflict_resolution_patterns": self._analyze_conflict_patterns(),
                "support_network_analysis": self._analyze_support_network(),
                "trust_distribution": self._get_trust_distribution(),
                "role_effectiveness": self._analyze_role_effectiveness(),
                "relationship_evolution": self._analyze_relationship_evolution(),
            }

            return insights

        except Exception as e:
            logger.error(f"관계 통찰력 생성 실패: {e}")
            raise

    def suggest_relationship_improvements(self, member_id: str) -> List[Dict]:
        """
        관계 개선 제안
        """
        try:
            suggestions = []

            # 관계 건강도 분석
            health_analysis = self.analyze_relationship_health(member_id)

            for other_id, relationship_data in health_analysis["relationships"].items():
                if relationship_data["relationship_health"] < 0.6:  # 개선 필요
                    suggestion = self._generate_improvement_suggestion(
                        member_id, other_id, relationship_data
                    )
                    suggestions.append(suggestion)

            # 역할 적응도 개선 제안
            if member_id in self.role_understandings:
                role_suggestions = self._generate_role_improvement_suggestions(
                    member_id
                )
                suggestions.extend(role_suggestions)

            return suggestions

        except Exception as e:
            logger.error(f"관계 개선 제안 생성 실패: {e}")
            raise

    def _update_relationship_patterns(self, interaction: Interaction):
        """관계 패턴 업데이트"""
        if len(interaction.participants) != 2:
            return  # 2명 간의 상호작용만 분석

        participant_pair = tuple(sorted(interaction.participants))

        # 기존 패턴 찾기
        existing_pattern = None
        for pattern in self.relationship_patterns:
            if pattern.participant_pair == participant_pair:
                existing_pattern = pattern
                break

        if existing_pattern:
            # 기존 패턴 업데이트
            existing_pattern.frequency += 1
            total_quality = (
                interaction.emotional_impact
                + interaction.satisfaction_level
                + interaction.communication_quality
            ) / 3
            existing_pattern.average_quality = (
                existing_pattern.average_quality * (existing_pattern.frequency - 1)
                + total_quality
            ) / existing_pattern.frequency

            if (
                interaction.interaction_type.value
                not in existing_pattern.common_interactions
            ):
                existing_pattern.common_interactions.append(
                    interaction.interaction_type.value
                )

            # 감정적 트렌드 업데이트
            if total_quality > existing_pattern.average_quality + 0.1:
                existing_pattern.emotional_trend = "improving"
            elif total_quality < existing_pattern.average_quality - 0.1:
                existing_pattern.emotional_trend = "declining"
            else:
                existing_pattern.emotional_trend = "stable"

        else:
            # 새로운 패턴 생성
            new_pattern = RelationshipPattern(
                id=str(uuid.uuid4()),
                participant_pair=participant_pair,
                pattern_type="forming",
                frequency=1,
                average_quality=(
                    interaction.emotional_impact
                    + interaction.satisfaction_level
                    + interaction.communication_quality
                )
                / 3,
                common_interactions=[interaction.interaction_type.value],
                emotional_trend="stable",
                trust_level=0.5,
                communication_style="developing",
                conflict_resolution_style="unknown",
                support_pattern="developing",
            )
            self.relationship_patterns.append(new_pattern)

    def _update_trust_metrics(self, interaction: Interaction):
        """신뢰도 메트릭 업데이트"""
        if len(interaction.participants) != 2:
            return

        for participant in interaction.participants:
            if participant not in self.trust_metrics:
                self.trust_metrics[participant] = {}

            other_participant = [
                p for p in interaction.participants if p != participant
            ][0]

            # 신뢰도 계산 (의사소통 품질, 상호 이해도, 만족도 기반)
            trust_score = (
                interaction.communication_quality
                + interaction.mutual_understanding
                + interaction.satisfaction_level
            ) / 3

            # 기존 신뢰도와 새로운 신뢰도 결합
            if other_participant in self.trust_metrics[participant]:
                current_trust = self.trust_metrics[participant][other_participant]
                # 가중 평균 (새로운 상호작용에 더 높은 가중치)
                new_trust = current_trust * 0.7 + trust_score * 0.3
            else:
                new_trust = trust_score

            self.trust_metrics[participant][other_participant] = new_trust

    def _update_communication_patterns(self, interaction: Interaction):
        """의사소통 패턴 업데이트"""
        for participant in interaction.participants:
            if participant not in self.communication_patterns:
                self.communication_patterns[participant] = {
                    "preferred_interaction_types": {},
                    "communication_quality_trend": [],
                    "emotional_expression_style": "developing",
                    "conflict_handling_style": "unknown",
                }

            # 선호하는 상호작용 유형 업데이트
            interaction_type = interaction.interaction_type.value
            if (
                interaction_type
                not in self.communication_patterns[participant][
                    "preferred_interaction_types"
                ]
            ):
                self.communication_patterns[participant]["preferred_interaction_types"][
                    interaction_type
                ] = 0
            self.communication_patterns[participant]["preferred_interaction_types"][
                interaction_type
            ] += 1

            # 의사소통 품질 트렌드 업데이트
            self.communication_patterns[participant][
                "communication_quality_trend"
            ].append(
                {
                    "timestamp": interaction.timestamp,
                    "quality": interaction.communication_quality,
                }
            )

    def _update_support_network(self, interaction: Interaction):
        """지원 네트워크 업데이트"""
        if interaction.interaction_type in [
            InteractionType.SUPPORT,
            InteractionType.EMOTIONAL_SUPPORT,
            InteractionType.PRACTICAL_HELP,
        ]:
            for participant in interaction.participants:
                if participant not in self.support_network:
                    self.support_network[participant] = []

                other_participants = [
                    p for p in interaction.participants if p != participant
                ]
                for other_participant in other_participants:
                    if other_participant not in self.support_network[participant]:
                        self.support_network[participant].append(other_participant)

    def _update_role_adaptation(
        self, member_id: str, role_understanding: RoleUnderstanding
    ):
        """역할 적응도 업데이트"""
        # 최근 상호작용을 기반으로 적응도 계산
        recent_interactions = [
            i
            for i in self.interactions
            if member_id in i.participants
            and i.timestamp >= datetime.now() - timedelta(days=30)
        ]

        if recent_interactions:
            # 역할 수행 점수 계산
            role_performance = sum(
                i.satisfaction_level for i in recent_interactions
            ) / len(recent_interactions)
            role_understanding.performance_score = role_performance

            # 적응도 업데이트 (성능과 만족도의 조합)
            adaptation_score = (
                role_performance + role_understanding.satisfaction_score
            ) / 2
            role_understanding.adaptation_level = min(1.0, adaptation_score)

    def _generate_relationship_insights(
        self, member_id: str, relationships: Dict
    ) -> List[str]:
        """관계 통찰력 생성"""
        insights = []

        # 강한 관계 식별
        strong_relationships = [
            other_id
            for other_id, data in relationships.items()
            if data["relationship_health"] > 0.8
        ]
        if strong_relationships:
            insights.append(
                f"강한 관계를 가진 구성원: {', '.join(strong_relationships)}"
            )

        # 개선이 필요한 관계 식별
        weak_relationships = [
            other_id
            for other_id, data in relationships.items()
            if data["relationship_health"] < 0.5
        ]
        if weak_relationships:
            insights.append(f"개선이 필요한 관계: {', '.join(weak_relationships)}")

        # 의사소통 패턴 분석
        if member_id in self.communication_patterns:
            preferred_types = self.communication_patterns[member_id][
                "preferred_interaction_types"
            ]
            if preferred_types:
                top_type = max(preferred_types.items(), key=lambda x: x[1])
                insights.append(f"선호하는 상호작용 유형: {top_type[0]}")

        return insights

    def _calculate_overall_relationship_health(self) -> float:
        """전체 관계 건강도 계산"""
        if not self.relationship_patterns:
            return 0.0

        total_health = sum(
            pattern.average_quality for pattern in self.relationship_patterns
        )
        return total_health / len(self.relationship_patterns)

    def _analyze_communication_patterns(self) -> Dict:
        """의사소통 패턴 분석"""
        analysis = {
            "total_members": len(self.communication_patterns),
            "communication_styles": {},
            "preferred_interaction_types": {},
            "quality_trends": {},
        }

        for member_id, patterns in self.communication_patterns.items():
            # 의사소통 스타일 분류
            style = patterns["emotional_expression_style"]
            if style not in analysis["communication_styles"]:
                analysis["communication_styles"][style] = 0
            analysis["communication_styles"][style] += 1

            # 선호하는 상호작용 유형
            for interaction_type, count in patterns[
                "preferred_interaction_types"
            ].items():
                if interaction_type not in analysis["preferred_interaction_types"]:
                    analysis["preferred_interaction_types"][interaction_type] = 0
                analysis["preferred_interaction_types"][interaction_type] += count

        return analysis

    def _analyze_conflict_patterns(self) -> Dict:
        """갈등 해결 패턴 분석"""
        conflict_interactions = [
            i
            for i in self.interactions
            if i.interaction_type == InteractionType.CONFLICT
        ]

        analysis = {
            "total_conflicts": len(conflict_interactions),
            "resolution_success_rate": 0.0,
            "common_conflict_topics": [],
            "resolution_styles": {},
        }

        if conflict_interactions:
            # 해결 성공률 계산 (감정적 영향이 개선된 경우)
            resolved_conflicts = [
                i for i in conflict_interactions if i.mood_after and i.mood_before
            ]
            if resolved_conflicts:
                successful_resolutions = [
                    i
                    for i in resolved_conflicts
                    if self._is_mood_improved(i.mood_before, i.mood_after)
                ]
                analysis["resolution_success_rate"] = len(successful_resolutions) / len(
                    resolved_conflicts
                )

        return analysis

    def _analyze_support_network(self) -> Dict:
        """지원 네트워크 분석"""
        analysis = {
            "total_members": len(self.support_network),
            "average_support_connections": 0.0,
            "most_supportive_member": None,
            "support_network_density": 0.0,
        }

        if self.support_network:
            total_connections = sum(
                len(connections) for connections in self.support_network.values()
            )
            analysis["average_support_connections"] = total_connections / len(
                self.support_network
            )

            # 가장 지원적인 구성원
            most_supportive = max(self.support_network.items(), key=lambda x: len(x[1]))
            analysis["most_supportive_member"] = most_supportive[0]

            # 네트워크 밀도 계산
            total_possible_connections = len(self.support_network) * (
                len(self.support_network) - 1
            )
            if total_possible_connections > 0:
                analysis["support_network_density"] = (
                    total_connections / total_possible_connections
                )

        return analysis

    def _get_trust_distribution(self) -> Dict:
        """신뢰도 분포"""
        if not self.trust_metrics:
            return {"high": 0, "medium": 0, "low": 0}

        high_trust = 0
        medium_trust = 0
        low_trust = 0

        for member_trusts in self.trust_metrics.values():
            for trust_level in member_trusts.values():
                if trust_level >= 0.7:
                    high_trust += 1
                elif trust_level >= 0.4:
                    medium_trust += 1
                else:
                    low_trust += 1

        return {"high": high_trust, "medium": medium_trust, "low": low_trust}

    def _analyze_role_effectiveness(self) -> Dict:
        """역할 효과성 분석"""
        analysis = {
            "total_roles": len(self.role_understandings),
            "average_performance": 0.0,
            "average_satisfaction": 0.0,
            "average_adaptation": 0.0,
            "role_distribution": {},
        }

        if self.role_understandings:
            total_performance = sum(
                role.performance_score for role in self.role_understandings.values()
            )
            total_satisfaction = sum(
                role.satisfaction_score for role in self.role_understandings.values()
            )
            total_adaptation = sum(
                role.adaptation_level for role in self.role_understandings.values()
            )

            analysis["average_performance"] = total_performance / len(
                self.role_understandings
            )
            analysis["average_satisfaction"] = total_satisfaction / len(
                self.role_understandings
            )
            analysis["average_adaptation"] = total_adaptation / len(
                self.role_understandings
            )

            # 역할 분포
            for role_understanding in self.role_understandings.values():
                role_type = role_understanding.role.value
                if role_type not in analysis["role_distribution"]:
                    analysis["role_distribution"][role_type] = 0
                analysis["role_distribution"][role_type] += 1

        return analysis

    def _analyze_relationship_evolution(self) -> Dict:
        """관계 진화 분석"""
        if not self.relationship_patterns:
            return {"evolution_stage": "forming", "trend": "stable"}

        improving_patterns = [
            p for p in self.relationship_patterns if p.emotional_trend == "improving"
        ]
        declining_patterns = [
            p for p in self.relationship_patterns if p.emotional_trend == "declining"
        ]
        stable_patterns = [
            p for p in self.relationship_patterns if p.emotional_trend == "stable"
        ]

        total_patterns = len(self.relationship_patterns)

        evolution_data = {
            "improving_ratio": len(improving_patterns) / total_patterns,
            "declining_ratio": len(declining_patterns) / total_patterns,
            "stable_ratio": len(stable_patterns) / total_patterns,
            "average_trust": sum(p.trust_level for p in self.relationship_patterns)
            / total_patterns,
        }

        # 진화 단계 결정
        if evolution_data["improving_ratio"] > 0.6:
            evolution_stage = "growing"
        elif evolution_data["declining_ratio"] > 0.4:
            evolution_stage = "challenging"
        else:
            evolution_stage = "stable"

        evolution_data["evolution_stage"] = evolution_stage

        return evolution_data

    def _generate_improvement_suggestion(
        self, member_id: str, other_id: str, relationship_data: Dict
    ) -> Dict:
        """개선 제안 생성"""
        suggestion = {
            "type": "relationship_improvement",
            "target_member": other_id,
            "current_health": relationship_data["relationship_health"],
            "suggestions": [],
        }

        # 의사소통 품질 개선 제안
        if relationship_data["avg_communication_quality"] < 0.6:
            suggestion["suggestions"].append(
                {
                    "area": "communication",
                    "action": "더 자주 대화하고 서로의 관점을 이해하려 노력하세요",
                    "priority": "high",
                }
            )

        # 감정적 연결 개선 제안
        if relationship_data["avg_emotional_impact"] < 0.5:
            suggestion["suggestions"].append(
                {
                    "area": "emotional_connection",
                    "action": "함께하는 활동을 늘리고 감정을 공유하세요",
                    "priority": "medium",
                }
            )

        # 만족도 개선 제안
        if relationship_data["avg_satisfaction"] < 0.6:
            suggestion["suggestions"].append(
                {
                    "area": "satisfaction",
                    "action": "서로의 기대를 명확히 하고 공통 관심사를 찾아보세요",
                    "priority": "medium",
                }
            )

        return suggestion

    def _generate_role_improvement_suggestions(self, member_id: str) -> List[Dict]:
        """역할 개선 제안 생성"""
        suggestions = []
        role_understanding = self.role_understandings[member_id]

        # 성능 개선 제안
        if role_understanding.performance_score < 0.6:
            suggestions.append(
                {
                    "type": "role_performance_improvement",
                    "area": "performance",
                    "action": f"{role_understanding.role.value} 역할을 더 효과적으로 수행하기 위해 관련 기술을 개발하세요",
                    "priority": "high",
                }
            )

        # 만족도 개선 제안
        if role_understanding.satisfaction_score < 0.5:
            suggestions.append(
                {
                    "type": "role_satisfaction_improvement",
                    "area": "satisfaction",
                    "action": "역할에 대한 만족도를 높이기 위해 개인적 성장과 가족 기여의 균형을 찾아보세요",
                    "priority": "medium",
                }
            )

        # 적응도 개선 제안
        if role_understanding.adaptation_level < 0.4:
            suggestions.append(
                {
                    "type": "role_adaptation_improvement",
                    "area": "adaptation",
                    "action": "역할에 더 잘 적응하기 위해 점진적으로 책임을 늘려가며 경험을 쌓으세요",
                    "priority": "high",
                }
            )

        return suggestions

    def _is_mood_improved(self, mood_before: str, mood_after: str) -> bool:
        """기분 개선 여부 판단"""
        mood_scores = {
            "very_happy": 5,
            "happy": 4,
            "neutral": 3,
            "sad": 2,
            "very_sad": 1,
        }

        before_score = mood_scores.get(mood_before.lower(), 3)
        after_score = mood_scores.get(mood_after.lower(), 3)

        return after_score > before_score

    def export_relationship_data(self) -> Dict:
        """관계 데이터 내보내기"""
        return {
            "interactions": [asdict(interaction) for interaction in self.interactions],
            "relationship_patterns": [
                asdict(pattern) for pattern in self.relationship_patterns
            ],
            "role_understandings": {
                member_id: asdict(understanding)
                for member_id, understanding in self.role_understandings.items()
            },
            "trust_metrics": self.trust_metrics,
            "communication_patterns": self.communication_patterns,
            "support_network": self.support_network,
            "insights": self.get_relationship_insights(),
        }

    def import_relationship_data(self, data: Dict):
        """관계 데이터 가져오기"""
        try:
            # 상호작용 데이터 복원
            self.interactions = []
            for interaction_data in data.get("interactions", []):
                interaction_data["timestamp"] = datetime.fromisoformat(
                    interaction_data["timestamp"]
                )
                interaction_data["interaction_type"] = InteractionType(
                    interaction_data["interaction_type"]
                )
                self.interactions.append(Interaction(**interaction_data))

            # 관계 패턴 데이터 복원
            self.relationship_patterns = []
            for pattern_data in data.get("relationship_patterns", []):
                pattern_data["participant_pair"] = tuple(
                    pattern_data["participant_pair"]
                )
                self.relationship_patterns.append(RelationshipPattern(**pattern_data))

            # 역할 이해 데이터 복원
            self.role_understandings = {}
            for member_id, understanding_data in data.get(
                "role_understandings", {}
            ).items():
                understanding_data["last_updated"] = datetime.fromisoformat(
                    understanding_data["last_updated"]
                )
                understanding_data["role"] = RoleExpectation(understanding_data["role"])
                self.role_understandings[member_id] = RoleUnderstanding(
                    **understanding_data
                )

            # 기타 데이터 복원
            self.trust_metrics = data.get("trust_metrics", {})
            self.communication_patterns = data.get("communication_patterns", {})
            self.support_network = data.get("support_network", {})

            logger.info("관계 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"관계 데이터 가져오기 실패: {e}")
            raise
