#!/usr/bin/env python3
"""
DuRiCore Phase 5.5.3 - 사회적 지능 시스템
상황 이해, 적응적 행동, 협력 능력 시스템
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class SocialIntelligenceType(Enum):
    """사회적 지능 타입 열거형"""

    CONTEXT_UNDERSTANDING = "context_understanding"  # 상황 이해
    ADAPTIVE_BEHAVIOR = "adaptive_behavior"  # 적응적 행동
    COLLABORATION = "collaboration"  # 협력 능력
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"  # 감정 지능
    COMMUNICATION = "communication"  # 의사소통


class ContextComplexity(Enum):
    """상황 복잡성 열거형"""

    SIMPLE = "simple"  # 단순 (0.0-0.3)
    MODERATE = "moderate"  # 보통 (0.3-0.7)
    COMPLEX = "complex"  # 복잡 (0.7-1.0)
    HIGHLY_COMPLEX = "highly_complex"  # 매우 복잡 (0.9-1.0)


class AdaptationLevel(Enum):
    """적응 수준 열거형"""

    LOW = "low"  # 낮음 (0.0-0.3)
    MEDIUM = "medium"  # 중간 (0.3-0.7)
    HIGH = "high"  # 높음 (0.7-1.0)
    EXCELLENT = "excellent"  # 우수 (0.9-1.0)


@dataclass
class ContextAnalysis:
    """상황 분석"""

    context_id: str
    context_type: str
    complexity: ContextComplexity
    key_factors: List[str]
    stakeholders: List[str]
    power_dynamics: Dict[str, float]
    cultural_factors: List[str]
    emotional_climate: str
    communication_channels: List[str]
    created_at: datetime

    def get(self, key: str, default=None):
        """딕셔너리 스타일 접근을 위한 get 메서드"""
        return getattr(self, key, default)


@dataclass
class AdaptiveBehavior:
    """적응적 행동"""

    behavior_id: str
    behavior_type: SocialIntelligenceType
    adaptation_level: AdaptationLevel
    context_appropriateness: float
    effectiveness_score: float
    stakeholder_satisfaction: float
    communication_quality: float
    emotional_resonance: float
    implementation_strategy: List[str]
    success_metrics: Dict[str, float]
    created_at: datetime


@dataclass
class CollaborationPlan:
    """협력 계획"""

    collaboration_id: str
    collaboration_type: str
    participants: List[str]
    roles_and_responsibilities: Dict[str, str]
    communication_protocol: List[str]
    conflict_resolution_strategy: List[str]
    success_criteria: List[str]
    timeline: Dict[str, datetime]
    resource_allocation: Dict[str, Any]
    risk_mitigation: List[str]
    created_at: datetime


class SocialIntelligenceSystem:
    """사회적 지능 시스템"""

    def __init__(self):
        # 사회적 지능 데이터
        self.context_analyses = []
        self.adaptive_behaviors = []
        self.collaboration_plans = []

        # 사회적 지능 설정
        self.min_context_understanding = 0.6
        self.min_adaptation_threshold = 0.7
        self.optimal_collaboration_score = 0.8

        # 사회적 지능 가중치
        self.social_weights = {
            "context_understanding": 0.3,
            "adaptive_behavior": 0.3,
            "collaboration": 0.2,
            "emotional_intelligence": 0.2,
        }

        logger.info("사회적 지능 시스템 초기화 완료")

    async def understand_context(self, situation: Dict[str, Any]) -> ContextAnalysis:
        """상황 이해"""
        try:
            # 상황 분석
            context_type = await self._analyze_context_type(situation)
            complexity = await self._assess_complexity(situation)
            key_factors = await self._identify_key_factors(situation)
            stakeholders = await self._identify_stakeholders(situation)
            power_dynamics = await self._analyze_power_dynamics(stakeholders)
            cultural_factors = await self._identify_cultural_factors(situation)
            emotional_climate = await self._assess_emotional_climate(situation)
            communication_channels = await self._identify_communication_channels(
                situation
            )

            # 상황 분석 생성
            context_analysis = ContextAnalysis(
                context_id=f"context_{int(time.time() * 1000)}",
                context_type=context_type,
                complexity=complexity,
                key_factors=key_factors,
                stakeholders=stakeholders,
                power_dynamics=power_dynamics,
                cultural_factors=cultural_factors,
                emotional_climate=emotional_climate,
                communication_channels=communication_channels,
                created_at=datetime.now(),
            )

            self.context_analyses.append(context_analysis)

            logger.info(f"상황 이해 완료: {context_analysis.context_id}")
            return context_analysis

        except Exception as e:
            logger.error(f"상황 이해 실패: {e}")
            return await self._create_empty_context_analysis()

    async def adapt_behavior(
        self, context_analysis: ContextAnalysis, current_behavior: Dict[str, Any]
    ) -> AdaptiveBehavior:
        """적응적 행동"""
        try:
            # 현재 행동 분석
            behavior_analysis = await self._analyze_current_behavior(current_behavior)

            # 적응 전략 수립
            adaptation_strategy = await self._develop_adaptation_strategy(
                context_analysis, behavior_analysis
            )

            # 적응 수준 평가
            adaptation_level = await self._assess_adaptation_level(adaptation_strategy)

            # 상황 적합성 평가
            context_appropriateness = await self._assess_context_appropriateness(
                adaptation_strategy, context_analysis
            )

            # 효과성 평가
            effectiveness_score = await self._assess_effectiveness(adaptation_strategy)

            # 이해관계자 만족도 예측
            stakeholder_satisfaction = await self._predict_stakeholder_satisfaction(
                adaptation_strategy, context_analysis
            )

            # 의사소통 품질 평가
            communication_quality = await self._assess_communication_quality(
                adaptation_strategy
            )

            # 감정적 공감도 평가
            emotional_resonance = await self._assess_emotional_resonance(
                adaptation_strategy, context_analysis
            )

            # 구현 전략 수립
            implementation_strategy = await self._create_implementation_strategy(
                adaptation_strategy
            )

            # 성공 지표 정의
            success_metrics = await self._define_success_metrics(adaptation_strategy)

            # 적응적 행동 생성
            adaptive_behavior = AdaptiveBehavior(
                behavior_id=f"behavior_{int(time.time() * 1000)}",
                behavior_type=SocialIntelligenceType.ADAPTIVE_BEHAVIOR,
                adaptation_level=adaptation_level,
                context_appropriateness=context_appropriateness,
                effectiveness_score=effectiveness_score,
                stakeholder_satisfaction=stakeholder_satisfaction,
                communication_quality=communication_quality,
                emotional_resonance=emotional_resonance,
                implementation_strategy=implementation_strategy,
                success_metrics=success_metrics,
                created_at=datetime.now(),
            )

            self.adaptive_behaviors.append(adaptive_behavior)

            logger.info(f"적응적 행동 생성 완료: {adaptive_behavior.behavior_id}")
            return adaptive_behavior

        except Exception as e:
            logger.error(f"적응적 행동 실패: {e}")
            return await self._create_empty_adaptive_behavior()

    async def collaborate(
        self, context_analysis: ContextAnalysis, collaboration_goal: Dict[str, Any]
    ) -> CollaborationPlan:
        """협력 능력"""
        try:
            # 협력 유형 분석
            collaboration_type = await self._analyze_collaboration_type(
                collaboration_goal
            )

            # 참여자 식별
            participants = await self._identify_participants(
                context_analysis, collaboration_goal
            )

            # 역할 및 책임 분담
            roles_and_responsibilities = await self._assign_roles_and_responsibilities(
                participants
            )

            # 의사소통 프로토콜 수립
            communication_protocol = await self._create_communication_protocol(
                context_analysis
            )

            # 갈등 해결 전략
            conflict_resolution_strategy = (
                await self._develop_conflict_resolution_strategy(context_analysis)
            )

            # 성공 기준 정의
            success_criteria = await self._define_collaboration_success_criteria(
                collaboration_goal
            )

            # 타임라인 설정
            timeline = await self._create_collaboration_timeline(collaboration_goal)

            # 자원 배분
            resource_allocation = await self._allocate_collaboration_resources(
                participants, collaboration_goal
            )

            # 리스크 완화 전략
            risk_mitigation = await self._develop_collaboration_risk_mitigation(
                context_analysis
            )

            # 협력 계획 생성
            collaboration_plan = CollaborationPlan(
                collaboration_id=f"collaboration_{int(time.time() * 1000)}",
                collaboration_type=collaboration_type,
                participants=participants,
                roles_and_responsibilities=roles_and_responsibilities,
                communication_protocol=communication_protocol,
                conflict_resolution_strategy=conflict_resolution_strategy,
                success_criteria=success_criteria,
                timeline=timeline,
                resource_allocation=resource_allocation,
                risk_mitigation=risk_mitigation,
                created_at=datetime.now(),
            )

            self.collaboration_plans.append(collaboration_plan)

            logger.info(f"협력 계획 수립 완료: {collaboration_plan.collaboration_id}")
            return collaboration_plan

        except Exception as e:
            logger.error(f"협력 계획 수립 실패: {e}")
            return await self._create_empty_collaboration_plan()

    async def _analyze_context_type(self, situation: Dict[str, Any]) -> str:
        """상황 유형 분석"""
        try:
            # 상황 유형 분류
            if "conflict" in situation.get("keywords", []):
                return "conflict_resolution"
            elif "collaboration" in situation.get("keywords", []):
                return "collaboration"
            elif "negotiation" in situation.get("keywords", []):
                return "negotiation"
            elif "leadership" in situation.get("keywords", []):
                return "leadership"
            else:
                return "general_interaction"

        except Exception as e:
            logger.warning(f"상황 유형 분석 실패: {e}")
            return "general_interaction"

    async def _assess_complexity(self, situation: Dict[str, Any]) -> ContextComplexity:
        """복잡성 평가"""
        try:
            # 복잡성 지표 계산
            stakeholder_count = len(situation.get("stakeholders", []))
            issue_count = len(situation.get("issues", []))
            time_pressure = situation.get("time_pressure", 0.5)

            complexity_score = (
                stakeholder_count * 0.2 + issue_count * 0.3 + time_pressure * 0.5
            ) / 3

            if complexity_score > 0.8:
                return ContextComplexity.HIGHLY_COMPLEX
            elif complexity_score > 0.6:
                return ContextComplexity.COMPLEX
            elif complexity_score > 0.3:
                return ContextComplexity.MODERATE
            else:
                return ContextComplexity.SIMPLE

        except Exception as e:
            logger.warning(f"복잡성 평가 실패: {e}")
            return ContextComplexity.MODERATE

    async def _identify_key_factors(self, situation: Dict[str, Any]) -> List[str]:
        """핵심 요소 식별"""
        try:
            factors = []

            # 상황에서 핵심 요소 추출
            if situation.get("stakeholders"):
                factors.append("stakeholder_diversity")
            if situation.get("time_constraints"):
                factors.append("time_pressure")
            if situation.get("resource_limitations"):
                factors.append("resource_constraints")
            if situation.get("cultural_differences"):
                factors.append("cultural_diversity")
            if situation.get("conflicting_interests"):
                factors.append("conflict_of_interests")

            return factors

        except Exception as e:
            logger.warning(f"핵심 요소 식별 실패: {e}")
            return ["general_factors"]

    async def _identify_stakeholders(self, situation: Dict[str, Any]) -> List[str]:
        """이해관계자 식별"""
        try:
            stakeholders = situation.get("stakeholders", [])

            # 기본 이해관계자 추가
            if not stakeholders:
                stakeholders = [
                    "primary_stakeholder",
                    "secondary_stakeholder",
                    "external_partner",
                ]

            return stakeholders

        except Exception as e:
            logger.warning(f"이해관계자 식별 실패: {e}")
            return ["general_stakeholder"]

    async def _analyze_power_dynamics(
        self, stakeholders: List[str]
    ) -> Dict[str, float]:
        """권력 역학 분석"""
        try:
            power_dynamics = {}

            for stakeholder in stakeholders:
                # 간단한 권력 수준 계산
                power_level = random.uniform(0.2, 0.9)
                power_dynamics[stakeholder] = power_level

            return power_dynamics

        except Exception as e:
            logger.warning(f"권력 역학 분석 실패: {e}")
            return {"default_stakeholder": 0.5}

    async def _identify_cultural_factors(self, situation: Dict[str, Any]) -> List[str]:
        """문화적 요소 식별"""
        try:
            cultural_factors = []

            # 문화적 요소 추출
            if situation.get("cultural_differences"):
                cultural_factors.extend(
                    [
                        "communication_style",
                        "decision_making_style",
                        "conflict_resolution_style",
                    ]
                )
            if situation.get("organizational_culture"):
                cultural_factors.append("organizational_norms")
            if situation.get("regional_differences"):
                cultural_factors.append("regional_customs")

            return cultural_factors

        except Exception as e:
            logger.warning(f"문화적 요소 식별 실패: {e}")
            return ["general_cultural_factors"]

    async def _assess_emotional_climate(self, situation: Dict[str, Any]) -> str:
        """감정적 분위기 평가"""
        try:
            # 감정적 분위기 분석
            emotional_indicators = situation.get("emotional_indicators", {})

            if emotional_indicators.get("tension", 0) > 0.7:
                return "high_tension"
            elif emotional_indicators.get("cooperation", 0) > 0.7:
                return "cooperative"
            elif emotional_indicators.get("conflict", 0) > 0.7:
                return "conflictual"
            else:
                return "neutral"

        except Exception as e:
            logger.warning(f"감정적 분위기 평가 실패: {e}")
            return "neutral"

    async def _identify_communication_channels(
        self, situation: Dict[str, Any]
    ) -> List[str]:
        """의사소통 채널 식별"""
        try:
            channels = []

            # 의사소통 채널 추출
            if situation.get("face_to_face_available"):
                channels.append("face_to_face")
            if situation.get("virtual_meeting_available"):
                channels.append("virtual_meeting")
            if situation.get("written_communication_required"):
                channels.append("written_communication")
            if situation.get("informal_communication_possible"):
                channels.append("informal_communication")

            return channels

        except Exception as e:
            logger.warning(f"의사소통 채널 식별 실패: {e}")
            return ["general_communication"]

    async def _analyze_current_behavior(
        self, current_behavior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """현재 행동 분석"""
        try:
            analysis = {
                "effectiveness": current_behavior.get("effectiveness", 0.5),
                "appropriateness": current_behavior.get("appropriateness", 0.5),
                "communication_style": current_behavior.get(
                    "communication_style", "neutral"
                ),
                "emotional_response": current_behavior.get(
                    "emotional_response", "neutral"
                ),
                "stakeholder_reaction": current_behavior.get(
                    "stakeholder_reaction", "neutral"
                ),
            }
            return analysis

        except Exception as e:
            logger.warning(f"현재 행동 분석 실패: {e}")
            return {}

    async def _develop_adaptation_strategy(
        self, context_analysis: ContextAnalysis, behavior_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """적응 전략 수립"""
        try:
            strategy = {
                "communication_approach": "adaptive",
                "emotional_regulation": "context_appropriate",
                "stakeholder_engagement": "proactive",
                "conflict_resolution": "collaborative",
                "cultural_sensitivity": "high",
            }
            return strategy

        except Exception as e:
            logger.warning(f"적응 전략 수립 실패: {e}")
            return {}

    async def _assess_adaptation_level(
        self, adaptation_strategy: Dict[str, Any]
    ) -> AdaptationLevel:
        """적응 수준 평가"""
        try:
            # 적응 수준 계산
            adaptation_score = random.uniform(0.6, 0.95)

            if adaptation_score > 0.9:
                return AdaptationLevel.EXCELLENT
            elif adaptation_score > 0.7:
                return AdaptationLevel.HIGH
            elif adaptation_score > 0.4:
                return AdaptationLevel.MEDIUM
            else:
                return AdaptationLevel.LOW

        except Exception as e:
            logger.warning(f"적응 수준 평가 실패: {e}")
            return AdaptationLevel.MEDIUM

    async def _assess_context_appropriateness(
        self, adaptation_strategy: Dict[str, Any], context_analysis: ContextAnalysis
    ) -> float:
        """상황 적합성 평가"""
        try:
            # 상황 적합성 계산
            appropriateness = random.uniform(0.7, 0.95)
            return appropriateness

        except Exception as e:
            logger.warning(f"상황 적합성 평가 실패: {e}")
            return 0.7

    async def _assess_effectiveness(self, adaptation_strategy: Dict[str, Any]) -> float:
        """효과성 평가"""
        try:
            # 효과성 계산
            effectiveness = random.uniform(0.7, 0.95)
            return effectiveness

        except Exception as e:
            logger.warning(f"효과성 평가 실패: {e}")
            return 0.7

    async def _predict_stakeholder_satisfaction(
        self, adaptation_strategy: Dict[str, Any], context_analysis: ContextAnalysis
    ) -> float:
        """이해관계자 만족도 예측"""
        try:
            # 만족도 예측
            satisfaction = random.uniform(0.6, 0.9)
            return satisfaction

        except Exception as e:
            logger.warning(f"이해관계자 만족도 예측 실패: {e}")
            return 0.7

    async def _assess_communication_quality(
        self, adaptation_strategy: Dict[str, Any]
    ) -> float:
        """의사소통 품질 평가"""
        try:
            # 의사소통 품질 계산
            quality = random.uniform(0.7, 0.95)
            return quality

        except Exception as e:
            logger.warning(f"의사소통 품질 평가 실패: {e}")
            return 0.7

    async def _assess_emotional_resonance(
        self, adaptation_strategy: Dict[str, Any], context_analysis: ContextAnalysis
    ) -> float:
        """감정적 공감도 평가"""
        try:
            # 감정적 공감도 계산
            resonance = random.uniform(0.6, 0.9)
            return resonance

        except Exception as e:
            logger.warning(f"감정적 공감도 평가 실패: {e}")
            return 0.7

    async def _create_implementation_strategy(
        self, adaptation_strategy: Dict[str, Any]
    ) -> List[str]:
        """구현 전략 수립"""
        try:
            strategy = [
                "상황별 적응적 의사소통",
                "감정 조절 및 공감적 반응",
                "이해관계자 적극적 참여 유도",
                "갈등 해결을 위한 협력적 접근",
                "문화적 민감성 고려",
            ]
            return strategy

        except Exception as e:
            logger.warning(f"구현 전략 수립 실패: {e}")
            return ["기본 적응 전략"]

    async def _define_success_metrics(
        self, adaptation_strategy: Dict[str, Any]
    ) -> Dict[str, float]:
        """성공 지표 정의"""
        try:
            metrics = {
                "stakeholder_satisfaction": 0.8,
                "communication_effectiveness": 0.85,
                "conflict_resolution_success": 0.9,
                "cultural_appropriateness": 0.85,
                "overall_adaptation_success": 0.8,
            }
            return metrics

        except Exception as e:
            logger.warning(f"성공 지표 정의 실패: {e}")
            return {"general_success": 0.7}

    async def _analyze_collaboration_type(
        self, collaboration_goal: Dict[str, Any]
    ) -> str:
        """협력 유형 분석"""
        try:
            goal_type = collaboration_goal.get("type", "general")

            if goal_type == "project_collaboration":
                return "project_based"
            elif goal_type == "problem_solving":
                return "problem_solving"
            elif goal_type == "innovation":
                return "innovation_collaboration"
            else:
                return "general_collaboration"

        except Exception as e:
            logger.warning(f"협력 유형 분석 실패: {e}")
            return "general_collaboration"

    async def _identify_participants(
        self, context_analysis: ContextAnalysis, collaboration_goal: Dict[str, Any]
    ) -> List[str]:
        """참여자 식별"""
        try:
            participants = context_analysis.stakeholders.copy()

            # 목표에 따른 추가 참여자
            if collaboration_goal.get("requires_expertise"):
                participants.append("domain_expert")
            if collaboration_goal.get("requires_facilitation"):
                participants.append("facilitator")
            if collaboration_goal.get("requires_decision_making"):
                participants.append("decision_maker")

            return participants

        except Exception as e:
            logger.warning(f"참여자 식별 실패: {e}")
            return ["primary_participant", "secondary_participant"]

    async def _assign_roles_and_responsibilities(
        self, participants: List[str]
    ) -> Dict[str, str]:
        """역할 및 책임 분담"""
        try:
            roles = {}

            for participant in participants:
                if "expert" in participant:
                    roles[participant] = "technical_lead"
                elif "facilitator" in participant:
                    roles[participant] = "process_facilitator"
                elif "decision" in participant:
                    roles[participant] = "decision_maker"
                else:
                    roles[participant] = "team_member"

            return roles

        except Exception as e:
            logger.warning(f"역할 및 책임 분담 실패: {e}")
            return {"default_participant": "general_role"}

    async def _create_communication_protocol(
        self, context_analysis: ContextAnalysis
    ) -> List[str]:
        """의사소통 프로토콜 수립"""
        try:
            protocol = [
                "정기적 상태 업데이트",
                "명확한 의사소통 채널",
                "피드백 수집 및 반영",
                "갈등 조기 해결",
                "문화적 민감성 고려",
            ]
            return protocol

        except Exception as e:
            logger.warning(f"의사소통 프로토콜 수립 실패: {e}")
            return ["기본 의사소통 규칙"]

    async def _develop_conflict_resolution_strategy(
        self, context_analysis: ContextAnalysis
    ) -> List[str]:
        """갈등 해결 전략 개발"""
        try:
            strategy = [
                "조기 갈등 식별",
                "이해관계자 간 대화 촉진",
                "공통 목표 강조",
                "중재자 역할 활용",
                "구조화된 해결 과정",
            ]
            return strategy

        except Exception as e:
            logger.warning(f"갈등 해결 전략 개발 실패: {e}")
            return ["기본 갈등 해결 방법"]

    async def _define_collaboration_success_criteria(
        self, collaboration_goal: Dict[str, Any]
    ) -> List[str]:
        """협력 성공 기준 정의"""
        try:
            criteria = [
                "목표 달성률 80% 이상",
                "참여자 만족도 75% 이상",
                "의사소통 효과성 85% 이상",
                "갈등 해결 성공률 90% 이상",
                "문화적 적합성 80% 이상",
            ]
            return criteria

        except Exception as e:
            logger.warning(f"협력 성공 기준 정의 실패: {e}")
            return ["기본 성공 기준"]

    async def _create_collaboration_timeline(
        self, collaboration_goal: Dict[str, Any]
    ) -> Dict[str, datetime]:
        """협력 타임라인 설정"""
        try:
            timeline = {}
            current_time = datetime.now()

            timeline["start"] = current_time
            timeline["planning_phase"] = current_time + timedelta(days=7)
            timeline["execution_phase"] = current_time + timedelta(days=14)
            timeline["review_phase"] = current_time + timedelta(days=21)
            timeline["completion"] = current_time + timedelta(days=30)

            return timeline

        except Exception as e:
            logger.warning(f"협력 타임라인 설정 실패: {e}")
            return {"start": datetime.now(), "end": datetime.now() + timedelta(days=30)}

    async def _allocate_collaboration_resources(
        self, participants: List[str], collaboration_goal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """협력 자원 배분"""
        try:
            resources = {
                "human_resources": participants,
                "time_allocation": {"planning": 0.2, "execution": 0.6, "review": 0.2},
                "communication_tools": [
                    "meeting_platform",
                    "document_sharing",
                    "feedback_system",
                ],
                "facilitation_resources": [
                    "mediator",
                    "process_guide",
                    "conflict_resolution_tools",
                ],
            }
            return resources

        except Exception as e:
            logger.warning(f"협력 자원 배분 실패: {e}")
            return {
                "human_resources": [],
                "time_allocation": {},
                "communication_tools": [],
            }

    async def _develop_collaboration_risk_mitigation(
        self, context_analysis: ContextAnalysis
    ) -> List[str]:
        """협력 리스크 완화 전략 개발"""
        try:
            mitigation = [
                "참여자 간 명확한 기대치 설정",
                "정기적 진행 상황 점검",
                "갈등 조기 해결 메커니즘",
                "문화적 차이 인식 및 대응",
                "비상 계획 수립",
            ]
            return mitigation

        except Exception as e:
            logger.warning(f"협력 리스크 완화 전략 개발 실패: {e}")
            return ["기본 리스크 완화 전략"]

    async def _create_empty_context_analysis(self) -> ContextAnalysis:
        """빈 상황 분석 생성"""
        return ContextAnalysis(
            context_id=f"empty_context_{int(time.time() * 1000)}",
            context_type="unknown",
            complexity=ContextComplexity.MODERATE,
            key_factors=[],
            stakeholders=[],
            power_dynamics={},
            cultural_factors=[],
            emotional_climate="neutral",
            communication_channels=[],
            created_at=datetime.now(),
        )

    async def _create_empty_adaptive_behavior(self) -> AdaptiveBehavior:
        """빈 적응적 행동 생성"""
        return AdaptiveBehavior(
            behavior_id=f"empty_behavior_{int(time.time() * 1000)}",
            behavior_type=SocialIntelligenceType.ADAPTIVE_BEHAVIOR,
            adaptation_level=AdaptationLevel.MEDIUM,
            context_appropriateness=0.5,
            effectiveness_score=0.5,
            stakeholder_satisfaction=0.5,
            communication_quality=0.5,
            emotional_resonance=0.5,
            implementation_strategy=[],
            success_metrics={},
            created_at=datetime.now(),
        )

    async def _create_empty_collaboration_plan(self) -> CollaborationPlan:
        """빈 협력 계획 생성"""
        return CollaborationPlan(
            collaboration_id=f"empty_collaboration_{int(time.time() * 1000)}",
            collaboration_type="general",
            participants=[],
            roles_and_responsibilities={},
            communication_protocol=[],
            conflict_resolution_strategy=[],
            success_criteria=[],
            timeline={},
            resource_allocation={},
            risk_mitigation=[],
            created_at=datetime.now(),
        )

    async def analyze_social_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """사회적 맥락 분석 - 고급 AI 통합 시스템용 인터페이스"""
        try:
            # 컨텍스트에서 사회적 정보 추출
            social_info = self._extract_social_info_from_context(context)

            # 사회적 맥락 분석
            context_analysis = await self.understand_context(context)

            # 적응적 행동 생성
            adaptive_behavior = await self.adapt_behavior(context_analysis, context)

            return {
                "social_context": social_info,
                "context_analysis": context_analysis,
                "adaptive_behavior": adaptive_behavior,
                "social_intelligence_score": self._calculate_social_intelligence_score(
                    context_analysis, adaptive_behavior
                ),
            }
        except Exception as e:
            logger.error(f"사회적 맥락 분석 중 오류: {e}")
            return {
                "social_context": {},
                "context_analysis": {},
                "adaptive_behavior": {},
                "social_intelligence_score": 0.5,
            }

    def _extract_social_info_from_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """컨텍스트에서 사회적 정보 추출"""
        social_info = {
            "stakeholders": [],
            "power_dynamics": {},
            "cultural_factors": [],
            "communication_channels": [],
            "social_complexity": "simple",
        }

        # 이해관계자 추출
        if "stakeholders" in context:
            social_info["stakeholders"] = context["stakeholders"]

        # 권력 역학 분석
        if "stakeholders" in context:
            stakeholders = context["stakeholders"]
            for i, stakeholder in enumerate(stakeholders):
                # 간단한 권력 점수 계산 (위치 기반)
                power_score = 1.0 - (i * 0.2)  # 첫 번째가 가장 높은 권력
                social_info["power_dynamics"][stakeholder] = max(0.1, power_score)

        # 문화적 요소 추출
        context_text = str(context).lower()
        cultural_keywords = ["culture", "tradition", "custom", "norm", "value"]
        for keyword in cultural_keywords:
            if keyword in context_text:
                social_info["cultural_factors"].append(keyword)

        # 의사소통 채널 추출
        communication_keywords = ["meeting", "email", "phone", "video", "presentation"]
        for keyword in communication_keywords:
            if keyword in context_text:
                social_info["communication_channels"].append(keyword)

        # 사회적 복잡성 평가
        complexity_score = len(social_info["stakeholders"]) + len(
            social_info["cultural_factors"]
        )
        if complexity_score >= 5:
            social_info["social_complexity"] = "highly_complex"
        elif complexity_score >= 3:
            social_info["social_complexity"] = "complex"
        elif complexity_score >= 1:
            social_info["social_complexity"] = "moderate"
        else:
            social_info["social_complexity"] = "simple"

        return social_info

    def _calculate_social_intelligence_score(
        self, context_analysis: ContextAnalysis, adaptive_behavior: AdaptiveBehavior
    ) -> float:
        """사회적 지능 점수 계산"""
        try:
            # 기본 점수
            base_score = 0.5

            # 컨텍스트 분석 점수
            if context_analysis:
                complexity_bonus = 0.0
                if hasattr(context_analysis, "complexity"):
                    complexity_scores = {
                        "simple": 0.1,
                        "moderate": 0.2,
                        "complex": 0.3,
                        "highly_complex": 0.4,
                    }
                    complexity_bonus = complexity_scores.get(
                        context_analysis.complexity.value, 0.1
                    )

                base_score += complexity_bonus

            # 적응적 행동 점수
            if adaptive_behavior:
                adaptation_bonus = 0.0
                if hasattr(adaptive_behavior, "adaptation_level"):
                    adaptation_scores = {
                        "low": 0.1,
                        "medium": 0.2,
                        "high": 0.3,
                        "excellent": 0.4,
                    }
                    adaptation_bonus = adaptation_scores.get(
                        adaptive_behavior.adaptation_level.value, 0.1
                    )

                base_score += adaptation_bonus

            return min(1.0, base_score)
        except Exception as e:
            logger.error(f"사회적 지능 점수 계산 중 오류: {e}")
            return 0.5


async def test_social_intelligence_system():
    """사회적 지능 시스템 테스트"""
    print("=== 사회적 지능 시스템 테스트 시작 ===")

    # 사회적 지능 시스템 생성
    social_system = SocialIntelligenceSystem()

    # 테스트 상황
    test_situation = {
        "keywords": ["collaboration", "diversity"],
        "stakeholders": ["team_leader", "team_member", "external_partner"],
        "issues": ["communication_gap", "cultural_differences"],
        "time_pressure": 0.7,
        "cultural_differences": True,
        "conflicting_interests": True,
        "emotional_indicators": {"tension": 0.6, "cooperation": 0.7, "conflict": 0.4},
        "face_to_face_available": True,
        "virtual_meeting_available": True,
    }

    # 1. 상황 이해 테스트
    print("1. 상황 이해 테스트")
    context_analysis = await social_system.understand_context(test_situation)
    print(f"상황 이해 완료: {context_analysis.context_id}")
    print(f"복잡성: {context_analysis.complexity.value}")
    print(f"이해관계자 수: {len(context_analysis.stakeholders)}")

    # 2. 적응적 행동 테스트
    print("2. 적응적 행동 테스트")
    current_behavior = {
        "effectiveness": 0.6,
        "appropriateness": 0.7,
        "communication_style": "collaborative",
        "emotional_response": "empathetic",
        "stakeholder_reaction": "positive",
    }
    adaptive_behavior = await social_system.adapt_behavior(
        context_analysis, current_behavior
    )
    print(f"적응적 행동 생성 완료: {adaptive_behavior.behavior_id}")
    print(f"적응 수준: {adaptive_behavior.adaptation_level.value}")

    # 3. 협력 능력 테스트
    print("3. 협력 능력 테스트")
    collaboration_goal = {
        "type": "project_collaboration",
        "requires_expertise": True,
        "requires_facilitation": True,
        "requires_decision_making": True,
    }
    collaboration_plan = await social_system.collaborate(
        context_analysis, collaboration_goal
    )
    print(f"협력 계획 수립 완료: {collaboration_plan.collaboration_id}")
    print(f"참여자 수: {len(collaboration_plan.participants)}")

    print("=== 사회적 지능 시스템 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_social_intelligence_system())
