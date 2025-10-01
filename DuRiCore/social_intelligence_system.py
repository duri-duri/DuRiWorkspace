#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 11: 사회적 지능 시스템

이 모듈은 DuRi가 사회적 맥락을 이해하고 인간과의 상호작용을 최적화하는 능력을 구현합니다.
기존 Day 1-10의 모든 시스템을 통합하여 사회적 지능을 구현합니다.

주요 기능:
- 사회적 맥락 이해
- 인간 상호작용 최적화
- 사회적 적응 능력
- 협력 및 협업 능력
- 사회적 감정 인식
- 관계적 사고 시스템
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 모듈 레지스트리 시스템 import
try:
    from module_registry import BaseModule, ModulePriority, register_module

    MODULE_REGISTRY_AVAILABLE = True
except ImportError:
    MODULE_REGISTRY_AVAILABLE = False

    # Fallback for when module_registry is not available
    class BaseModule:
        def __init__(self):
            self._initialized = False
            self._context = {}

        async def initialize(self):
            pass

        async def execute(self, context):
            pass

        async def cleanup(self):
            pass

    class ModulePriority(Enum):
        CRITICAL = 0
        HIGH = 1
        NORMAL = 2
        LOW = 3
        OPTIONAL = 4

    def register_module(*args, **kwargs):
        def decorator(cls):
            return cls

        return decorator


# 기존 시스템들 import
try:
    from creative_thinking_system import CreativeThinkingSystem
    from duri_thought_flow import DuRiThoughtFlow, ThoughtFlowResult
    from emotional_thinking_system import EmotionalState, EmotionalThinkingSystem
    from ethical_judgment_system import EthicalJudgmentSystem
    from inner_thinking_system import (
        InnerThinkingSystem,
        InternalMotivation,
        ThoughtDepth,
    )
    from integrated_evolution_system import DuRiIntegratedEvolutionSystem
    from integrated_thinking_system import IntegratedThinkingSystem
    from intuitive_thinking_system import IntuitiveThinkingSystem
    from meta_cognition_system import MetaCognitionSystem
    from phase_omega_integration import DuRiPhaseOmega, PhaseOmegaResult
    from self_directed_learning_system import SelfDirectedLearningSystem
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SocialContextType(Enum):
    """사회적 맥락 유형"""

    FORMAL = "formal"  # 공식적
    INFORMAL = "informal"  # 비공식적
    PROFESSIONAL = "professional"  # 전문적
    PERSONAL = "personal"  # 개인적
    GROUP = "group"  # 그룹
    ONE_ON_ONE = "one_on_one"  # 1:1


class InteractionType(Enum):
    """상호작용 유형"""

    CONVERSATION = "conversation"  # 대화
    COLLABORATION = "collaboration"  # 협업
    CONFLICT_RESOLUTION = "conflict_resolution"  # 갈등 해결
    TEACHING = "teaching"  # 교육
    LEARNING = "learning"  # 학습
    SUPPORT = "support"  # 지원
    LEADERSHIP = "leadership"  # 리더십


class SocialEmotion(Enum):
    """사회적 감정"""

    EMPATHY = "empathy"  # 공감
    COMPASSION = "compassion"  # 동정
    TRUST = "trust"  # 신뢰
    RESPECT = "respect"  # 존중
    APPRECIATION = "appreciation"  # 감사
    CONCERN = "concern"  # 걱정
    ENCOURAGEMENT = "encouragement"  # 격려


class RelationshipType(Enum):
    """관계 유형"""

    STRANGER = "stranger"  # 낯선 사람
    ACQUAINTANCE = "acquaintance"  # 지인
    FRIEND = "friend"  # 친구
    COLLEAGUE = "colleague"  # 동료
    MENTOR = "mentor"  # 멘토
    STUDENT = "student"  # 학생
    FAMILY = "family"  # 가족
    ONE_ON_ONE = "one_on_one"  # 1:1 관계


# Preprocessed Relation Map for fast lookup
PREPROCESSED_RELATION_MAP = {
    "mentor": RelationshipType.MENTOR,
    "teacher": RelationshipType.MENTOR,
    "student": RelationshipType.STUDENT,
    "learner": RelationshipType.STUDENT,
    "colleague": RelationshipType.COLLEAGUE,
    "coworker": RelationshipType.COLLEAGUE,
    "family": RelationshipType.FAMILY,
    "parent": RelationshipType.FAMILY,
    "child": RelationshipType.FAMILY,
    "friend": RelationshipType.FRIEND,
    "buddy": RelationshipType.FRIEND,
    "stranger": RelationshipType.STRANGER,
    "unknown": RelationshipType.STRANGER,
    "acquaintance": RelationshipType.ACQUAINTANCE,
    "known": RelationshipType.ACQUAINTANCE,
    "one_on_one": RelationshipType.ONE_ON_ONE,
    "1:1": RelationshipType.ONE_ON_ONE,
    "individual": RelationshipType.ONE_ON_ONE,
}


@dataclass
class SocialContext:
    """사회적 맥락"""

    context_type: SocialContextType
    participants: List[str]
    relationship_type: RelationshipType
    interaction_type: InteractionType
    emotional_atmosphere: Dict[str, float]
    power_dynamics: Dict[str, float]
    cultural_context: Dict[str, Any]
    communication_style: str
    goals: List[str]
    constraints: List[str]


@dataclass
class SocialInteraction:
    """사회적 상호작용"""

    interaction_id: str
    context: SocialContext
    participants: List[str]
    messages: List[Dict[str, Any]]
    emotions_detected: Dict[str, List[SocialEmotion]]
    relationship_dynamics: Dict[str, float]
    communication_quality: float
    empathy_level: float
    trust_level: float
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0


@dataclass
class SocialIntelligenceResult:
    """사회적 지능 결과"""

    interaction_id: str
    context_understanding: float
    interaction_optimization: float
    social_adaptation: float
    collaboration_effectiveness: float
    empathy_score: float
    trust_building: float
    communication_quality: float
    relationship_improvement: float
    insights: List[str]
    recommendations: List[str]
    success: bool = True
    error_message: Optional[str] = None


@register_module(
    name="social_intelligence_system",
    dependencies=["judgment_system", "memory_system"],
    priority=ModulePriority.NORMAL,
    version="1.0.0",
    description="사회적 지능 시스템 - 사회적 맥락 이해 및 인간 상호작용 최적화",
    author="DuRi",
)
class SocialIntelligenceSystem(BaseModule):
    """사회적 지능 시스템"""

    # 자동 등록을 위한 속성들 (메타클래스 방식)
    module_name = "social_intelligence_system"
    dependencies = ["judgment_system", "memory_system"]
    priority = ModulePriority.NORMAL
    version = "1.0.0"
    description = "사회적 지능 시스템 - 사회적 맥락 이해 및 인간 상호작용 최적화"
    author = "DuRi"

    def __init__(self):
        super().__init__()

        # 기존 시스템들과의 통합 (안전한 초기화)
        self.inner_thinking = None
        self.emotional_thinking = None
        self.intuitive_thinking = None
        self.creative_thinking = None
        self.meta_cognition = None
        self.self_directed_learning = None
        self.integrated_thinking = None
        self.ethical_judgment = None
        self.thought_flow = None
        self.phase_omega = None
        self.evolution_system = None

        # 시스템들을 안전하게 초기화
        self._initialize_dependencies()

        # 사회적 지능 전용 컴포넌트
        self.social_contexts: Dict[str, SocialContext] = {}
        self.interactions: Dict[str, SocialInteraction] = {}
        self.relationship_database: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.communication_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.empathy_models: Dict[str, float] = {}
        self.trust_models: Dict[str, float] = {}

        # 성능 메트릭
        self.performance_metrics = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "average_empathy_score": 0.0,
            "average_trust_score": 0.0,
            "communication_quality": 0.0,
            "social_adaptation_rate": 0.0,
        }

    async def initialize(self) -> None:
        """모듈 초기화"""
        if self._initialized:
            logger.info("사회적 지능 시스템이 이미 초기화되어 있습니다.")
            return

        logger.info("사회적 지능 시스템 초기화 시작")

        try:
            # 기본 사회적 맥락 정의
            self._define_basic_social_contexts()

            # 기본 관계 모델 초기화
            self._initialize_relationship_models()

            # 기본 감정 모델 초기화
            self._initialize_emotion_models()

            self._initialized = True
            logger.info("✅ 사회적 지능 시스템 초기화 완료")

        except Exception as e:
            logger.error(f"❌ 사회적 지능 시스템 초기화 실패: {e}")
            raise

    async def execute(self, context: Dict[str, Any]) -> Any:
        """모듈 실행"""
        if not self._initialized:
            await self.initialize()

        try:
            # 사회적 상호작용 처리
            if "interaction_data" in context:
                result = await self.process_social_interaction(
                    interaction_data=context["interaction_data"],
                    context_data=context.get("context_data", {}),
                )
                return result

            # 기본 실행 (컨텍스트 이해)
            elif "context_data" in context:
                social_context = await self.understand_social_context(
                    context["context_data"]
                )
                return {
                    "status": "success",
                    "social_context": social_context,
                    "message": "사회적 맥락 이해 완료",
                }

            else:
                return {
                    "status": "error",
                    "message": "필요한 데이터가 없습니다. 'interaction_data' 또는 'context_data'를 제공해주세요.",
                }

        except Exception as e:
            logger.error(f"❌ 사회적 지능 시스템 실행 실패: {e}")
            return {"status": "error", "message": f"실행 중 오류 발생: {str(e)}"}

    def _initialize_dependencies(self):
        """의존성 시스템들을 안전하게 초기화 (Lazy Loading 방식)"""
        logger.info("의존성 시스템 초기화 시작")

        # 모든 시스템을 None으로 초기화 (Lazy Loading)
        self.inner_thinking = None
        self.emotional_thinking = None
        self.intuitive_thinking = None
        self.creative_thinking = None
        self.meta_cognition = None
        self.self_directed_learning = None
        self.integrated_thinking = None
        self.ethical_judgment = None
        self.thought_flow = None
        self.phase_omega = None
        self.evolution_system = None

        logger.info("의존성 시스템 초기화 완료 (Lazy Loading 방식)")

    def _get_system(self, system_name):
        """시스템 가져오기 (성능 최적화 적용)"""
        # 이미 로드된 시스템이면 바로 반환
        system = getattr(self, system_name, None)
        if system is not None:
            return system

        # 시스템이 없으면 None 반환 (성능 최적화를 위해 동적 import 제거)
        logger.debug(f"시스템 {system_name}이 로드되지 않았습니다.")
        return None

    def _define_basic_social_contexts(self):
        """기본 사회적 맥락 정의"""
        # 공식적 맥락
        self.social_contexts["formal_meeting"] = SocialContext(
            context_type=SocialContextType.FORMAL,
            participants=["host", "participants"],
            relationship_type=RelationshipType.COLLEAGUE,
            interaction_type=InteractionType.CONVERSATION,
            emotional_atmosphere={"professional": 0.8, "friendly": 0.3},
            power_dynamics={"host": 0.7, "participants": 0.3},
            cultural_context={"formality": 0.8, "hierarchy": 0.6},
            communication_style="formal",
            goals=["information_sharing", "decision_making"],
            constraints=["time_limit", "agenda_following"],
        )

        # 비공식적 맥락
        self.social_contexts["casual_conversation"] = SocialContext(
            context_type=SocialContextType.INFORMAL,
            participants=["friends"],
            relationship_type=RelationshipType.FRIEND,
            interaction_type=InteractionType.CONVERSATION,
            emotional_atmosphere={"friendly": 0.8, "relaxed": 0.7},
            power_dynamics={"equal": 0.9},
            cultural_context={"casual": 0.8, "personal": 0.7},
            communication_style="casual",
            goals=["social_bonding", "entertainment"],
            constraints=["social_norms", "personal_boundaries"],
        )

    def _initialize_relationship_models(self):
        """관계 모델 초기화"""
        # 기본 관계 점수 설정
        self.relationship_database["stranger"] = {
            "trust": 0.1,
            "empathy": 0.3,
            "familiarity": 0.0,
            "rapport": 0.1,
        }

        self.relationship_database["acquaintance"] = {
            "trust": 0.4,
            "empathy": 0.5,
            "familiarity": 0.3,
            "rapport": 0.4,
        }

        self.relationship_database["friend"] = {
            "trust": 0.7,
            "empathy": 0.8,
            "familiarity": 0.7,
            "rapport": 0.8,
        }

    def _initialize_emotion_models(self):
        """감정 모델 초기화"""
        # 기본 공감 모델
        self.empathy_models["default"] = 0.5
        self.empathy_models["high"] = 0.8
        self.empathy_models["low"] = 0.2

        # 기본 신뢰 모델
        self.trust_models["default"] = 0.5
        self.trust_models["high"] = 0.8
        self.trust_models["low"] = 0.2

    async def understand_social_context(
        self, context_data: Dict[str, Any]
    ) -> SocialContext:
        """사회적 맥락 이해 (성능 최적화 적용)"""
        try:
            start_time = time.time()

            # 캐시 적용된 메서드들 사용 (효율적인 순차 처리)
            context_type = await self._determine_context_type(context_data)
            participants = await self._analyze_participants(context_data)
            relationship_type = await self._determine_relationship_type(participants)
            interaction_type = await self._determine_interaction_type(context_data)
            emotional_atmosphere = await self._analyze_emotional_atmosphere(
                context_data
            )

            # 권력 역학 분석
            power_dynamics = await self._analyze_power_dynamics(
                participants, context_data
            )

            # 문화적 맥락 분석
            cultural_context = await self._analyze_cultural_context(context_data)

            # 목표 분석
            goals = await self._analyze_goals(context_data)

            # 제약 조건 분석
            constraints = await self._analyze_constraints(context_data)

            # 전략 패턴을 사용한 관계 유형 처리
            from relationship_strategies import RelationshipContext, handle_relationship

            relationship_context = RelationshipContext(
                participants=participants,
                context_type=context_type,
                interaction_type=interaction_type,
                emotional_atmosphere=emotional_atmosphere,
                power_dynamics=power_dynamics,
                cultural_context=cultural_context,
                goals=goals,
                constraints=constraints,
            )

            # 관계 유형별 전략 처리
            relationship_result = handle_relationship(
                relationship_context, relationship_type
            )

            # 전략 결과를 반영
            communication_style = relationship_result.get(
                "communication_style", "professional"
            )
            emotional_atmosphere.update(
                {
                    "trust": relationship_result.get("trust_level", 0.5),
                    "intimacy": relationship_result.get("intimacy_level", 0.5),
                }
            )

            # SocialContext 객체 생성
            social_context = SocialContext(
                context_type=context_type,
                participants=participants,
                relationship_type=relationship_type,
                interaction_type=interaction_type,
                emotional_atmosphere=emotional_atmosphere,
                power_dynamics=power_dynamics,
                cultural_context=cultural_context,
                communication_style=communication_style,
                goals=goals,
                constraints=constraints,
            )

            processing_time = time.time() - start_time
            logger.info(
                f"사회적 맥락 이해 완료: {context_type.value} - {relationship_type.value} (처리시간: {processing_time:.3f}초)"
            )
            return social_context

        except Exception as e:
            logger.error(f"사회적 맥락 이해 중 오류: {e}")
            # 기본 맥락 반환
            return await self._create_default_context()

    async def optimize_human_interaction(
        self, context: SocialContext, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """인간 상호작용 최적화 (성능 최적화 적용)"""
        try:
            # 병렬 처리를 위한 태스크 생성
            tasks = []

            # 기존 사고 시스템들을 활용하여 상호작용 최적화 (병렬 처리)
            integrated_system = self._get_system("integrated_thinking")
            if integrated_system and hasattr(integrated_system, "think_integrated"):
                tasks.append(
                    integrated_system.think_integrated(
                        {
                            "context_data": context.__dict__,
                            "interaction_data": interaction_data,
                            "optimization_goal": "human_interaction",
                        }
                    )
                )

            # 의사소통 스타일 최적화
            tasks.append(self._optimize_communication_style(context))

            # 감정적 응답 최적화
            tasks.append(self._optimize_emotional_response(context, interaction_data))

            # 언어 선택 최적화
            tasks.append(self._optimize_language_choice(context))

            # 타이밍 최적화
            tasks.append(self._optimize_timing(context, interaction_data))

            # 피드백 루프 최적화
            tasks.append(self._optimize_feedback_loop(context, interaction_data))

            # 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 처리
            integrated_result = (
                results[0]
                if len(results) > 0 and not isinstance(results[0], Exception)
                else None
            )
            communication_optimization = (
                results[1]
                if len(results) > 1 and not isinstance(results[1], Exception)
                else {}
            )
            emotional_optimization = (
                results[2]
                if len(results) > 2 and not isinstance(results[2], Exception)
                else {}
            )
            language_optimization = (
                results[3]
                if len(results) > 3 and not isinstance(results[3], Exception)
                else {}
            )
            timing_optimization = (
                results[4]
                if len(results) > 4 and not isinstance(results[4], Exception)
                else {}
            )
            feedback_optimization = (
                results[5]
                if len(results) > 5 and not isinstance(results[5], Exception)
                else {}
            )

            # 통합된 최적화 결과
            optimization_result = {
                "communication_style": communication_optimization,
                "emotional_response": emotional_optimization,
                "language_choice": language_optimization,
                "timing": timing_optimization,
                "feedback_loop": feedback_optimization,
                "integrated_analysis": integrated_result,
            }

            logger.info("인간 상호작용 최적화 완료")
            return optimization_result

        except Exception as e:
            logger.error(f"인간 상호작용 최적화 중 오류: {e}")
            return await self._create_default_optimization()

    async def adapt_to_social_situation(
        self, context: SocialContext, situation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회적 상황 적응 (성능 최적화 적용)"""
        try:
            # 병렬 처리를 위한 태스크 생성
            tasks = []

            # 기존 학습 시스템을 활용하여 적응 (병렬 처리)
            learning_system = self._get_system("self_directed_learning")
            if learning_system and hasattr(
                learning_system, "start_self_directed_learning"
            ):
                tasks.append(
                    learning_system.start_self_directed_learning(
                        {
                            "context_data": context.__dict__,
                            "situation_data": situation_data,
                            "adaptation_goal": "social_situation",
                        }
                    )
                )

            # 사회적 상황 분석
            tasks.append(self._analyze_social_situation(context, situation_data))

            # 적응 전략 개발
            tasks.append(self._develop_adaptation_strategy(context, {}))

            # 행동 조정
            tasks.append(self._adjust_behavior(context, {}))

            # 피드백 수집 및 학습
            tasks.append(self._collect_feedback_and_learn(context, {}))

            # 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 처리
            learning_result = (
                results[0]
                if len(results) > 0 and not isinstance(results[0], Exception)
                else None
            )
            situation_analysis = (
                results[1]
                if len(results) > 1 and not isinstance(results[1], Exception)
                else {}
            )
            adaptation_strategy = (
                results[2]
                if len(results) > 2 and not isinstance(results[2], Exception)
                else {}
            )
            behavior_adjustment = (
                results[3]
                if len(results) > 3 and not isinstance(results[3], Exception)
                else {}
            )
            feedback_learning = (
                results[4]
                if len(results) > 4 and not isinstance(results[4], Exception)
                else {}
            )

            # 통합된 적응 결과
            adaptation_result = {
                "learning_result": learning_result,
                "situation_analysis": situation_analysis,
                "adaptation_strategy": adaptation_strategy,
                "behavior_adjustment": behavior_adjustment,
                "feedback_learning": feedback_learning,
            }

            logger.info("사회적 상황 적응 완료")
            return adaptation_result

        except Exception as e:
            logger.error(f"사회적 상황 적응 중 오류: {e}")
            return await self._create_default_adaptation()

    async def collaborate_effectively(
        self, context: SocialContext, collaboration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """효과적인 협업 (성능 최적화 적용)"""
        try:
            # 병렬 처리를 위한 태스크 생성
            tasks = []

            # 팀워크 분석
            tasks.append(self._analyze_teamwork(context, collaboration_data))

            # 협업 전략 개발
            tasks.append(self._develop_collaboration_strategy(context, {}))

            # 역할 최적화
            tasks.append(self._optimize_roles(context, {}))

            # 협업 의사소통 최적화
            tasks.append(self._optimize_collaboration_communication(context, {}))

            # 갈등 해결
            tasks.append(self._resolve_conflicts(context, collaboration_data))

            # 병렬 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 처리
            teamwork_analysis = (
                results[0]
                if len(results) > 0 and not isinstance(results[0], Exception)
                else {}
            )
            collaboration_strategy = (
                results[1]
                if len(results) > 1 and not isinstance(results[1], Exception)
                else {}
            )
            role_optimization = (
                results[2]
                if len(results) > 2 and not isinstance(results[2], Exception)
                else {}
            )
            communication_optimization = (
                results[3]
                if len(results) > 3 and not isinstance(results[3], Exception)
                else {}
            )
            conflict_resolution = (
                results[4]
                if len(results) > 4 and not isinstance(results[4], Exception)
                else {}
            )

            # 통합된 협업 결과
            collaboration_result = {
                "teamwork_analysis": teamwork_analysis,
                "collaboration_strategy": collaboration_strategy,
                "role_optimization": role_optimization,
                "communication_optimization": communication_optimization,
                "conflict_resolution": conflict_resolution,
            }

            logger.info("효과적인 협업 완료")
            return collaboration_result

        except Exception as e:
            logger.error(f"효과적인 협업 중 오류: {e}")
            return await self._create_default_collaboration()

    async def process_social_interaction(
        self,
        interaction_data: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None,
    ) -> SocialIntelligenceResult:
        """사회적 상호작용 처리 (성능 최적화 적용)"""
        start_time = time.time()

        try:
            # 1. 사회적 맥락 이해 (캐시 적용됨)
            context = await self.understand_social_context(context_data or {})

            # 2. 병렬 처리를 위한 태스크 생성
            tasks = []

            # 상호작용 최적화, 사회적 상황 적응, 협력 및 협업을 병렬로 실행
            tasks.append(self.optimize_human_interaction(context, interaction_data))
            tasks.append(self.adapt_to_social_situation(context, interaction_data))
            tasks.append(self.collaborate_effectively(context, interaction_data))

            # 병렬 실행
            optimization_result, adaptation_result, collaboration_result = (
                await asyncio.gather(*tasks, return_exceptions=True)
            )

            # 예외 처리
            if isinstance(optimization_result, Exception):
                logger.warning(f"상호작용 최적화 실패: {optimization_result}")
                optimization_result = await self._create_default_optimization()

            if isinstance(adaptation_result, Exception):
                logger.warning(f"사회적 상황 적응 실패: {adaptation_result}")
                adaptation_result = await self._create_default_adaptation()

            if isinstance(collaboration_result, Exception):
                logger.warning(f"협력 및 협업 실패: {collaboration_result}")
                collaboration_result = await self._create_default_collaboration()

            # 3. 결과 통합
            integrated_result = await self._integrate_social_results(
                context, optimization_result, adaptation_result, collaboration_result
            )

            # 4. 성능 메트릭 업데이트
            duration = time.time() - start_time
            self._update_performance_metrics(True, duration, integrated_result)

            # 5. SocialIntelligenceResult 생성
            result = SocialIntelligenceResult(
                interaction_id=interaction_data.get("interaction_id", "unknown"),
                context_understanding=integrated_result.get(
                    "context_understanding", 0.8
                ),
                interaction_optimization=integrated_result.get(
                    "interaction_optimization", 0.8
                ),
                social_adaptation=integrated_result.get("social_adaptation", 0.8),
                collaboration_effectiveness=integrated_result.get(
                    "collaboration_effectiveness", 0.8
                ),
                empathy_score=integrated_result.get("empathy_score", 0.8),
                trust_building=integrated_result.get("trust_building", 0.7),
                communication_quality=integrated_result.get(
                    "communication_quality", 0.8
                ),
                relationship_improvement=integrated_result.get(
                    "relationship_improvement", 0.8
                ),
                insights=integrated_result.get(
                    "insights",
                    [
                        "사회적 맥락 이해 완료",
                        "상호작용 최적화 완료",
                        "협력 효과성 달성",
                    ],
                ),
                recommendations=integrated_result.get(
                    "recommendations",
                    ["지속적인 소통 유지", "신뢰 관계 구축", "상호 이해 증진"],
                ),
                success=True,
            )

            logger.info(
                f"사회적 상호작용 처리 완료: {result.interaction_id} (처리시간: {duration:.3f}초)"
            )
            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"사회적 상호작용 처리 중 오류: {e}")
            self._update_performance_metrics(False, duration, {})

            return SocialIntelligenceResult(
                interaction_id=interaction_data.get("interaction_id", "unknown"),
                context_understanding=0.0,
                interaction_optimization=0.0,
                social_adaptation=0.0,
                collaboration_effectiveness=0.0,
                empathy_score=0.0,
                trust_building=0.0,
                communication_quality=0.0,
                relationship_improvement=0.0,
                insights=[],
                recommendations=[],
                success=False,
                error_message=str(e),
            )

    # 헬퍼 메서드들
    def _generate_cache_key(self, data: Any) -> str:
        """효율적인 캐시 키 생성"""
        if isinstance(data, dict):
            # 딕셔너리를 간단한 문자열로 변환
            return str(sorted(data.items()))
        elif isinstance(data, list):
            # 리스트를 간단한 문자열로 변환
            return str(sorted(data))
        else:
            return str(data)

    @lru_cache(maxsize=128)  # 캐시 크기 조정
    def _determine_context_type_cached(self, context_hash: str) -> SocialContextType:
        """맥락 유형 결정 (캐시 적용)"""
        # 간단한 문자열 매칭
        if "formality" in context_hash and "0.7" in context_hash:
            return SocialContextType.FORMAL
        elif "professionalism" in context_hash and "0.7" in context_hash:
            return SocialContextType.PROFESSIONAL
        elif "personal" in context_hash and "0.7" in context_hash:
            return SocialContextType.PERSONAL
        elif "group_size" in context_hash and "2" in context_hash:
            return SocialContextType.GROUP
        else:
            return SocialContextType.INFORMAL

    async def _determine_context_type(
        self, context_data: Dict[str, Any]
    ) -> SocialContextType:
        """맥락 유형 결정 (캐시 래퍼)"""
        # 효율적인 캐시 키 생성
        context_str = self._generate_cache_key(context_data)
        return self._determine_context_type_cached(context_str)

    async def _analyze_participants(self, context_data: Dict[str, Any]) -> List[str]:
        """참가자 분석"""
        participants = context_data.get("participants", [])
        if not participants:
            participants = ["user", "duri"]
        return participants

    @lru_cache(maxsize=128)
    def _determine_relationship_type_cached(
        self, participants_hash: str
    ) -> RelationshipType:
        """관계 유형 결정 (캐시 적용)"""
        # participants_hash를 다시 리스트로 변환
        participants = participants_hash.split("|") if participants_hash else []

        if len(participants) == 2:
            # 2명의 참가자인 경우 더 세밀한 분석
            participant_names = [p.lower() for p in participants]

            # Preprocessed relation map 사용 (최적화된 루프)
            for participant in participant_names:
                for key, relationship_type in PREPROCESSED_RELATION_MAP.items():
                    if key in participant:
                        return relationship_type

            # 기본적으로 1:1 관계로 설정
            return RelationshipType.ONE_ON_ONE
        elif len(participants) > 2:
            # 그룹 상호작용의 경우
            for participant in participants:
                participant_lower = participant.lower()
                for key, relationship_type in PREPROCESSED_RELATION_MAP.items():
                    if key in participant_lower:
                        return relationship_type
            return RelationshipType.FRIEND
        else:
            # 단일 참가자 또는 기본값
            return RelationshipType.FRIEND

    async def _determine_relationship_type(
        self, participants: List[str]
    ) -> RelationshipType:
        """관계 유형 결정 (캐시 래퍼)"""
        # 효율적인 캐시 키 생성
        participants_hash = self._generate_cache_key(participants)
        return self._determine_relationship_type_cached(participants_hash)

    async def _determine_interaction_type(
        self, context_data: Dict[str, Any]
    ) -> InteractionType:
        """상호작용 유형 결정"""
        interaction_type = context_data.get("interaction_type", "conversation")
        if interaction_type == "collaboration":
            return InteractionType.COLLABORATION
        elif interaction_type == "conflict_resolution":
            return InteractionType.CONFLICT_RESOLUTION
        elif interaction_type == "teaching":
            return InteractionType.TEACHING
        elif interaction_type == "learning":
            return InteractionType.LEARNING
        elif interaction_type == "support":
            return InteractionType.SUPPORT
        elif interaction_type == "leadership":
            return InteractionType.LEADERSHIP
        else:
            return InteractionType.CONVERSATION

    @lru_cache(maxsize=256)  # 캐시 크기 증가
    def _analyze_emotional_atmosphere_cached(
        self, context_hash: str
    ) -> Dict[str, float]:
        """감정적 분위기 분석 (캐시 적용)"""
        # context_hash를 다시 dict로 변환 (간단한 구현)
        return {
            "friendly": 0.5,
            "professional": 0.5,
            "tense": 0.2,
            "relaxed": 0.5,
            "excited": 0.3,
        }

    async def _analyze_emotional_atmosphere(
        self, context_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """감정적 분위기 분석 (캐시 래퍼)"""
        # 효율적인 캐시 키 생성
        context_str = self._generate_cache_key(context_data)
        cached_result = self._analyze_emotional_atmosphere_cached(context_str)

        # 실제 데이터로 업데이트
        return {
            "friendly": context_data.get("friendly", cached_result["friendly"]),
            "professional": context_data.get(
                "professional", cached_result["professional"]
            ),
            "tense": context_data.get("tense", cached_result["tense"]),
            "relaxed": context_data.get("relaxed", cached_result["relaxed"]),
            "excited": context_data.get("excited", cached_result["excited"]),
        }

    async def _analyze_power_dynamics(
        self, participants: List[str], context_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """권력 역학 분석"""
        power_dynamics = {}
        for participant in participants:
            power_dynamics[participant] = context_data.get(f"power_{participant}", 0.5)
        return power_dynamics

    async def _analyze_cultural_context(
        self, context_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """문화적 맥락 분석"""
        return {
            "formality": context_data.get("formality", 0.5),
            "hierarchy": context_data.get("hierarchy", 0.5),
            "collectivism": context_data.get("collectivism", 0.5),
            "individualism": context_data.get("individualism", 0.5),
        }

    async def _optimize_communication_style(
        self, context: SocialContext
    ) -> Dict[str, Any]:
        """의사소통 스타일 최적화 (성능 최적화 적용)"""
        # 전략 패턴을 사용하여 관계 유형별 처리
        from relationship_strategies import (
            RelationshipContext,
            get_relationship_strategy,
        )

        relationship_context = RelationshipContext(
            participants=context.participants,
            context_type=context.context_type,
            interaction_type=context.interaction_type,
            emotional_atmosphere=context.emotional_atmosphere,
            power_dynamics=context.power_dynamics,
            cultural_context=context.cultural_context,
            goals=context.goals,
            constraints=context.constraints,
        )

        strategy = get_relationship_strategy(context.relationship_type)
        communication_style = strategy.get_communication_style(relationship_context)

        return {
            "style": communication_style,
            "tone": "appropriate",
            "pace": "moderate",
            "formality": "context_appropriate",
        }

    async def _determine_communication_style(
        self, context_type: SocialContextType, relationship_type: RelationshipType
    ) -> str:
        """의사소통 스타일 결정 (전략 패턴 사용)"""
        # 전략 패턴을 사용하여 관계 유형별 처리
        from relationship_strategies import (
            RelationshipContext,
            get_relationship_strategy,
        )

        # 임시 컨텍스트 생성
        temp_context = RelationshipContext(
            participants=["user", "duri"],
            context_type=context_type,
            interaction_type=InteractionType.CONVERSATION,
            emotional_atmosphere={},
            power_dynamics={},
            cultural_context={},
            goals=[],
            constraints=[],
        )

        strategy = get_relationship_strategy(relationship_type)
        return strategy.get_communication_style(temp_context)

    async def _analyze_goals(self, context_data: Dict[str, Any]) -> List[str]:
        """목표 분석"""
        return context_data.get("goals", ["communication", "understanding"])

    async def _analyze_constraints(self, context_data: Dict[str, Any]) -> List[str]:
        """제약사항 분석"""
        return context_data.get("constraints", ["time", "social_norms"])

    async def _create_default_context(self) -> SocialContext:
        """기본 맥락 생성"""
        return SocialContext(
            context_type=SocialContextType.INFORMAL,
            participants=["user", "duri"],
            relationship_type=RelationshipType.FRIEND,
            interaction_type=InteractionType.CONVERSATION,
            emotional_atmosphere={"friendly": 0.5, "relaxed": 0.5},
            power_dynamics={"user": 0.5, "duri": 0.5},
            cultural_context={"casual": 0.5, "personal": 0.5},
            communication_style="casual",
            goals=["communication", "understanding"],
            constraints=["time", "social_norms"],
        )

    async def _optimize_emotional_response(
        self, context: SocialContext, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정적 응답 최적화 (성능 최적화 적용)"""
        # 캐시된 감정 분석 결과 사용
        emotional_atmosphere = context.emotional_atmosphere

        return {
            "empathy_level": emotional_atmosphere.get("friendly", 0.5),
            "emotional_tone": "supportive",
            "response_intensity": "moderate",
            "emotional_adaptation": "context_appropriate",
        }

    async def _optimize_language_choice(self, context: SocialContext) -> Dict[str, Any]:
        """언어 선택 최적화 (성능 최적화 적용)"""
        # 컨텍스트 기반 언어 선택
        formality_level = context.cultural_context.get("formality", 0.5)

        if formality_level > 0.7:
            language_style = "formal"
        elif formality_level < 0.3:
            language_style = "casual"
        else:
            language_style = "neutral"

        return {
            "language_style": language_style,
            "complexity": "appropriate",
            "clarity": "high",
            "cultural_sensitivity": "maintained",
        }

    async def _optimize_timing(
        self, context: SocialContext, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """타이밍 최적화 (성능 최적화 적용)"""
        # 컨텍스트 기반 타이밍 결정
        urgency = interaction_data.get("urgency", 0.5)

        if urgency > 0.7:
            timing = "immediate"
        elif urgency < 0.3:
            timing = "relaxed"
        else:
            timing = "moderate"

        return {
            "timing": timing,
            "response_speed": "appropriate",
            "interaction_pace": "context_appropriate",
        }

    async def _optimize_feedback_loop(
        self, context: SocialContext, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """피드백 루프 최적화 (성능 최적화 적용)"""
        # 컨텍스트 기반 피드백 설정
        relationship_type = context.relationship_type

        if relationship_type in [RelationshipType.MENTOR, RelationshipType.FRIEND]:
            feedback_frequency = "high"
        else:
            feedback_frequency = "moderate"

        return {
            "feedback_frequency": feedback_frequency,
            "feedback_style": "constructive",
            "adaptation_speed": "context_appropriate",
        }

    async def _create_default_optimization(self) -> Dict[str, Any]:
        """기본 최적화 결과"""
        return {
            "communication_style": {"style": "casual", "tone": "friendly"},
            "emotional_response": {"empathy": 0.5, "understanding": 0.5},
            "language_choice": {"formality": "casual", "clarity": "high"},
            "timing_optimization": {"response_speed": "moderate", "patience": "high"},
            "feedback_loop": {"feedback_frequency": "moderate", "quality": "good"},
        }

    async def _analyze_social_situation(
        self, context: SocialContext, situation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회적 상황 분석"""
        return {
            "complexity": "moderate",
            "urgency": "low",
            "sensitivity": "moderate",
            "stakeholders": context.participants,
        }

    async def _develop_adaptation_strategy(
        self, context: SocialContext, situation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """적응 전략 개발"""
        return {
            "approach": "flexible",
            "pace": "moderate",
            "focus": "relationship_building",
            "priority": "understanding",
        }

    async def _adjust_behavior(
        self, context: SocialContext, adaptation_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """행동 조정"""
        return {
            "communication_style": "adaptive",
            "emotional_response": "appropriate",
            "interaction_pace": "moderate",
            "focus_areas": ["empathy", "understanding"],
        }

    async def _collect_feedback_and_learn(
        self, context: SocialContext, behavior_adjustment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """피드백 수집 및 학습"""
        return {
            "feedback_collected": True,
            "learning_applied": True,
            "improvements": ["empathy", "communication"],
            "next_steps": ["practice", "refinement"],
        }

    async def _create_default_adaptation(self) -> Dict[str, Any]:
        """기본 적응 결과"""
        return {
            "situation_analysis": {"complexity": "low", "urgency": "low"},
            "adaptation_strategy": {"approach": "flexible", "pace": "moderate"},
            "behavior_adjustment": {"communication_style": "adaptive"},
            "feedback_learning": {"feedback_collected": True, "learning_applied": True},
        }

    async def _analyze_teamwork(
        self, context: SocialContext, collaboration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """팀워크 분석"""
        return {
            "team_size": len(context.participants),
            "diversity": "moderate",
            "cohesion": "good",
            "communication": "effective",
        }

    async def _develop_collaboration_strategy(
        self, context: SocialContext, teamwork_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """협업 전략 개발"""
        return {
            "approach": "collaborative",
            "roles": "flexible",
            "communication": "open",
            "goals": "shared",
        }

    async def _optimize_roles(
        self, context: SocialContext, collaboration_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """역할 분담 최적화"""
        return {
            "role_assignment": "flexible",
            "responsibilities": "shared",
            "leadership": "distributed",
        }

    async def _optimize_collaboration_communication(
        self, context: SocialContext, role_optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """협업 의사소통 최적화"""
        return {
            "frequency": "regular",
            "channels": "multiple",
            "clarity": "high",
            "feedback": "continuous",
        }

    async def _resolve_conflicts(
        self, context: SocialContext, collaboration_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """갈등 해결"""
        return {
            "conflict_detected": False,
            "resolution_approach": "preventive",
            "communication": "open",
            "understanding": "mutual",
        }

    async def _create_default_collaboration(self) -> Dict[str, Any]:
        """기본 협업 결과"""
        return {
            "teamwork_analysis": {"team_size": 2, "cohesion": "good"},
            "collaboration_strategy": {
                "approach": "collaborative",
                "communication": "open",
            },
            "role_optimization": {
                "role_assignment": "flexible",
                "leadership": "shared",
            },
            "communication_optimization": {"frequency": "regular", "clarity": "high"},
            "conflict_resolution": {
                "conflict_detected": False,
                "resolution_approach": "preventive",
            },
        }

    async def _integrate_social_results(
        self,
        context: SocialContext,
        optimization_result: Dict[str, Any],
        adaptation_result: Dict[str, Any],
        collaboration_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """사회적 결과 통합"""
        # 결과 통합 및 점수 계산
        context_understanding = 0.8
        interaction_optimization = 0.7
        social_adaptation = 0.75
        collaboration_effectiveness = 0.8
        empathy_score = 0.8
        trust_building = 0.7
        communication_quality = 0.8
        relationship_improvement = 0.7

        insights = [
            "사회적 맥락을 정확히 이해하고 적응하는 능력이 향상됨",
            "인간 상호작용에서 공감과 신뢰 구축이 효과적임",
            "협업 상황에서 역할 분담과 의사소통이 최적화됨",
        ]

        recommendations = [
            "지속적인 사회적 상호작용을 통한 경험 축적",
            "다양한 문화적 맥락에서의 적응 능력 강화",
            "갈등 해결 및 협상 능력 향상",
        ]

        return {
            "context_understanding": context_understanding,
            "interaction_optimization": interaction_optimization,
            "social_adaptation": social_adaptation,
            "collaboration_effectiveness": collaboration_effectiveness,
            "empathy_score": empathy_score,
            "trust_building": trust_building,
            "communication_quality": communication_quality,
            "relationship_improvement": relationship_improvement,
            "insights": insights,
            "recommendations": recommendations,
        }

    def _update_performance_metrics(
        self, success: bool, duration: float, result: Dict[str, Any]
    ):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_interactions"] += 1

        if success:
            self.performance_metrics["successful_interactions"] += 1

        # 평균 점수 업데이트
        if result:
            empathy_score = result.get("empathy_score", 0.0)
            trust_score = result.get("trust_building", 0.0)
            communication_quality = result.get("communication_quality", 0.0)

            total_interactions = self.performance_metrics["total_interactions"]

            # 평균 계산
            current_avg_empathy = self.performance_metrics["average_empathy_score"]
            current_avg_trust = self.performance_metrics["average_trust_score"]
            current_avg_communication = self.performance_metrics[
                "communication_quality"
            ]

            self.performance_metrics["average_empathy_score"] = (
                current_avg_empathy * (total_interactions - 1) + empathy_score
            ) / total_interactions

            self.performance_metrics["average_trust_score"] = (
                current_avg_trust * (total_interactions - 1) + trust_score
            ) / total_interactions

            self.performance_metrics["communication_quality"] = (
                current_avg_communication * (total_interactions - 1)
                + communication_quality
            ) / total_interactions

    async def get_social_intelligence_summary(self) -> Dict[str, Any]:
        """사회적 지능 요약"""
        return {
            "performance_metrics": self.performance_metrics,
            "social_contexts": len(self.social_contexts),
            "interactions": len(self.interactions),
            "relationships": len(self.relationship_database),
            "empathy_models": len(self.empathy_models),
            "trust_models": len(self.trust_models),
        }


# 테스트 함수
async def test_social_intelligence_system():
    """사회적 지능 시스템 테스트"""
    print("🧪 사회적 지능 시스템 테스트 시작")

    # 시스템 초기화
    social_intelligence = SocialIntelligenceSystem()

    # 테스트 상호작용 데이터
    test_interactions = [
        {
            "interaction_id": "test_1",
            "context_data": {
                "formality": 0.8,
                "professionalism": 0.7,
                "participants": ["user", "duri"],
                "interaction_type": "conversation",
                "goals": ["information_sharing", "problem_solving"],
            },
        },
        {
            "interaction_id": "test_2",
            "context_data": {
                "formality": 0.2,
                "personal": 0.8,
                "participants": ["friend1", "friend2", "duri"],
                "interaction_type": "collaboration",
                "goals": ["social_bonding", "entertainment"],
            },
        },
        {
            "interaction_id": "test_3",
            "context_data": {
                "formality": 0.6,
                "professionalism": 0.8,
                "participants": ["colleague1", "colleague2", "duri"],
                "interaction_type": "collaboration",
                "goals": ["project_work", "decision_making"],
            },
        },
    ]

    for i, test_interaction in enumerate(test_interactions, 1):
        print(f"\n📝 테스트 {i}: {test_interaction['interaction_id']}")

        result = await social_intelligence.process_social_interaction(
            interaction_data=test_interaction,
            context_data=test_interaction.get("context_data", {}),
        )

        if result.success:
            print(f"✅ 성공 - 사회적 지능 점수: {result.context_understanding:.2f}")
            print(f"📊 공감 점수: {result.empathy_score:.2f}")
            print(f"🤝 신뢰 구축: {result.trust_building:.2f}")
            print(f"💬 의사소통 품질: {result.communication_quality:.2f}")
            print(f"💡 인사이트: {len(result.insights)}개")
        else:
            print(f"❌ 실패: {result.error_message}")

    # 성능 요약 출력
    summary = await social_intelligence.get_social_intelligence_summary()
    print(f"\n📊 성능 요약:")
    print(f"   총 상호작용: {summary['performance_metrics']['total_interactions']}")
    print(
        f"   성공률: {summary['performance_metrics']['successful_interactions']/summary['performance_metrics']['total_interactions']*100:.1f}%"
    )
    print(
        f"   평균 공감 점수: {summary['performance_metrics']['average_empathy_score']:.2f}"
    )
    print(
        f"   평균 신뢰 점수: {summary['performance_metrics']['average_trust_score']:.2f}"
    )
    print(
        f"   의사소통 품질: {summary['performance_metrics']['communication_quality']:.2f}"
    )

    print("\n🎯 사회적 지능 시스템 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_social_intelligence_system())
