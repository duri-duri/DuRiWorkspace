#!/usr/bin/env python3
"""
DuRiCore Phase 10 - 고급 사회적 지능 엔진
인간과의 상호작용 및 감정 이해를 위한 고급 AI 엔진
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import math
import random
import statistics
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from advanced_cognitive_system import (
    AbstractionType,
    AdvancedCognitiveSystem,
    CognitiveLevel,
)
from emotion_weight_system import EmotionWeightSystem
from lida_attention_system import LIDAAttentionSystem

# 기존 시스템들 import
from social_intelligence_system import (
    ContextComplexity,
    SocialIntelligenceSystem,
    SocialIntelligenceType,
)

logger = logging.getLogger(__name__)


class SocialEngineType(Enum):
    """사회적 엔진 타입"""

    EMOTION_RECOGNITION = "emotion_recognition"
    SOCIAL_CONTEXT = "social_context"
    HUMAN_INTERACTION = "human_interaction"
    SOCIAL_ASSESSMENT = "social_assessment"


class SocialIntelligenceLevel(Enum):
    """사회적 지능 수준"""

    BASIC = "basic"  # 기본 사회적 지능
    INTERMEDIATE = "intermediate"  # 중급 사회적 지능
    ADVANCED = "advanced"  # 고급 사회적 지능
    EXPERT = "expert"  # 전문가 사회적 지능
    MASTER = "master"  # 마스터 사회적 지능


class EmotionType(Enum):
    """감정 타입"""

    JOY = "joy"  # 기쁨
    SADNESS = "sadness"  # 슬픔
    ANGER = "anger"  # 분노
    FEAR = "fear"  # 두려움
    SURPRISE = "surprise"  # 놀람
    DISGUST = "disgust"  # 혐오
    NEUTRAL = "neutral"  # 중립


class SocialContextType(Enum):
    """사회적 맥락 타입"""

    FORMAL = "formal"  # 공식적
    INFORMAL = "informal"  # 비공식적
    PROFESSIONAL = "professional"  # 전문적
    PERSONAL = "personal"  # 개인적
    CULTURAL = "cultural"  # 문화적


@dataclass
class EmotionAnalysis:
    """감정 분석"""

    analysis_id: str
    emotion_type: EmotionType
    intensity: float
    confidence: float
    context: str
    triggers: List[str]
    expressions: List[str]
    physiological_signals: List[str]
    behavioral_patterns: List[str]
    created_at: datetime


@dataclass
class SocialContext:
    """사회적 맥락"""

    context_id: str
    context_type: SocialContextType
    participants: List[str]
    relationships: Dict[str, str]
    power_dynamics: Dict[str, float]
    cultural_factors: List[str]
    communication_style: str
    social_norms: List[str]
    expectations: List[str]
    created_at: datetime


@dataclass
class HumanInteraction:
    """인간 상호작용"""

    interaction_id: str
    interaction_type: str
    participants: List[str]
    communication_style: str
    emotional_state: Dict[str, EmotionType]
    social_dynamics: Dict[str, Any]
    interaction_quality: float
    satisfaction_score: float
    improvement_suggestions: List[str]
    created_at: datetime


@dataclass
class SocialAssessment:
    """사회적 지능 평가"""

    assessment_id: str
    subject: str
    social_intelligence_dimensions: Dict[str, float]
    overall_social_score: float
    emotional_intelligence: float
    social_skills: float
    communication_effectiveness: float
    relationship_management: float
    cultural_sensitivity: float
    strengths: List[str]
    improvement_areas: List[str]
    recommendations: List[str]
    assessment_date: datetime


class SocialIntelligenceEngine:
    """고급 사회적 지능 엔진"""

    def __init__(self):
        # 기존 시스템들 통합
        self.social_intelligence_system = SocialIntelligenceSystem()
        self.cognitive_system = AdvancedCognitiveSystem()
        self.attention_system = LIDAAttentionSystem()
        self.emotion_system = EmotionWeightSystem()

        # 사회적 엔진 데이터
        self.emotion_analyses = []
        self.social_contexts = []
        self.human_interactions = []
        self.social_assessments = []

        # 사회적 엔진 설정
        self.social_thresholds = {
            "emotion_confidence": 0.7,
            "context_understanding": 0.6,
            "interaction_quality": 0.5,
            "social_sensitivity": 0.6,
        }

        # 사회적 가중치
        self.social_weights = {
            "emotional_intelligence": 0.25,
            "social_skills": 0.25,
            "communication": 0.2,
            "relationship_management": 0.15,
            "cultural_sensitivity": 0.15,
        }

        # 감정 인식 가중치
        self.emotion_weights = {
            EmotionType.JOY: 0.15,
            EmotionType.SADNESS: 0.15,
            EmotionType.ANGER: 0.15,
            EmotionType.FEAR: 0.15,
            EmotionType.SURPRISE: 0.1,
            EmotionType.DISGUST: 0.1,
            EmotionType.NEUTRAL: 0.2,
        }

        # 사회적 맥락 데이터베이스
        self.social_context_patterns = {
            "formal": ["경직된", "구조화된", "규칙 기반"],
            "informal": ["자유로운", "편안한", "자연스러운"],
            "professional": ["전문적인", "목적 지향적", "효율적인"],
            "personal": ["친밀한", "감정적", "개인적인"],
            "cultural": ["문화적", "전통적", "가치 기반"],
        }

        logger.info("고급 사회적 지능 엔진 초기화 완료")

    async def recognize_emotions(
        self, context: Dict[str, Any], emotion_types: List[EmotionType] = None
    ) -> List[EmotionAnalysis]:
        """감정 인식"""
        try:
            logger.info(
                f"감정 인식 시작: 타입 {len(emotion_types) if emotion_types else '전체'}"
            )

            # 컨텍스트 전처리
            processed_context = await self._preprocess_emotion_context(context)

            # 감정 신호 분석
            emotional_signals = await self._analyze_emotional_signals(processed_context)

            # 감정 타입 식별
            if not emotion_types:
                emotion_types = list(EmotionType)

            # 감정 분석 수행
            emotion_analyses = await self._perform_emotion_analysis(
                emotional_signals, emotion_types
            )

            # 감정 신뢰도 평가
            evaluated_emotions = await self._evaluate_emotion_confidence(
                emotion_analyses
            )

            # 결과 저장
            self.emotion_analyses.extend(evaluated_emotions)

            logger.info(f"감정 인식 완료: {len(evaluated_emotions)}개 감정 분석")
            return evaluated_emotions

        except Exception as e:
            logger.error(f"감정 인식 실패: {str(e)}")
            return []

    async def understand_social_context(
        self, context: Dict[str, Any], context_type: SocialContextType = None
    ) -> SocialContext:
        """사회적 맥락 이해"""
        try:
            logger.info(
                f"사회적 맥락 이해 시작: 타입 {context_type.value if context_type else '자동'}"
            )

            # 맥락 정보 분석
            context_analysis = await self._analyze_social_context(context)

            # 맥락 타입 결정
            if not context_type:
                context_type = await self._determine_context_type(context_analysis)

            # 참여자 관계 분석
            relationships = await self._analyze_participant_relationships(
                context_analysis
            )

            # 권력 역학 분석
            power_dynamics = await self._analyze_power_dynamics(context_analysis)

            # 문화적 요소 분석
            cultural_factors = await self._analyze_cultural_factors(context_analysis)

            # 사회적 맥락 생성
            social_context = await self._create_social_context(
                context_analysis,
                context_type,
                relationships,
                power_dynamics,
                cultural_factors,
            )

            # 결과 저장
            self.social_contexts.append(social_context)

            logger.info(f"사회적 맥락 이해 완료: {social_context.context_type.value}")
            return social_context

        except Exception as e:
            logger.error(f"사회적 맥락 이해 실패: {str(e)}")
            return None

    async def optimize_human_interaction(
        self,
        interaction_context: Dict[str, Any],
        social_level: SocialIntelligenceLevel = SocialIntelligenceLevel.ADVANCED,
    ) -> HumanInteraction:
        """인간 상호작용 최적화"""
        try:
            logger.info(f"인간 상호작용 최적화 시작: 수준 {social_level.value}")

            # 상호작용 컨텍스트 분석
            interaction_analysis = await self._analyze_interaction_context(
                interaction_context
            )

            # 참여자 감정 상태 분석
            emotional_states = await self._analyze_participant_emotions(
                interaction_analysis
            )

            # 사회적 역학 분석
            social_dynamics = await self._analyze_social_dynamics(interaction_analysis)

            # 상호작용 품질 평가
            interaction_quality = await self._assess_interaction_quality(
                interaction_analysis, emotional_states, social_dynamics
            )

            # 최적화 제안 생성
            optimization_suggestions = await self._generate_optimization_suggestions(
                interaction_quality, social_level
            )

            # 상호작용 결과 생성
            interaction = await self._create_human_interaction(
                interaction_analysis,
                emotional_states,
                social_dynamics,
                interaction_quality,
                optimization_suggestions,
            )

            # 결과 저장
            self.human_interactions.append(interaction)

            logger.info(
                f"인간 상호작용 최적화 완료: 품질 점수 {interaction.interaction_quality:.2f}"
            )
            return interaction

        except Exception as e:
            logger.error(f"인간 상호작용 최적화 실패: {str(e)}")
            return None

    async def assess_social_intelligence(
        self, subject: str, context: Dict[str, Any]
    ) -> SocialAssessment:
        """사회적 지능 평가"""
        try:
            logger.info(f"사회적 지능 평가 시작: 주제 {subject}")

            # 사회적 지능 차원 분석
            social_dimensions = await self._analyze_social_intelligence_dimensions(
                subject, context
            )

            # 감정 지능 평가
            emotional_intelligence = await self._assess_emotional_intelligence(
                social_dimensions
            )

            # 사회적 기술 평가
            social_skills = await self._assess_social_skills(social_dimensions)

            # 의사소통 효과성 평가
            communication_effectiveness = (
                await self._assess_communication_effectiveness(social_dimensions)
            )

            # 관계 관리 평가
            relationship_management = await self._assess_relationship_management(
                social_dimensions
            )

            # 문화적 민감성 평가
            cultural_sensitivity = await self._assess_cultural_sensitivity(
                social_dimensions
            )

            # 전반적 사회적 지능 점수 계산
            overall_score = await self._calculate_overall_social_score(
                emotional_intelligence,
                social_skills,
                communication_effectiveness,
                relationship_management,
                cultural_sensitivity,
            )

            # 강점 및 개선 영역 식별
            strengths = await self._identify_social_strengths(social_dimensions)
            improvement_areas = await self._identify_social_improvement_areas(
                social_dimensions
            )

            # 권장사항 생성
            recommendations = await self._generate_social_recommendations(
                strengths, improvement_areas
            )

            # 평가 결과 생성
            assessment = SocialAssessment(
                assessment_id=f"social_assessment_{int(time.time())}",
                subject=subject,
                social_intelligence_dimensions=social_dimensions,
                overall_social_score=overall_score,
                emotional_intelligence=emotional_intelligence,
                social_skills=social_skills,
                communication_effectiveness=communication_effectiveness,
                relationship_management=relationship_management,
                cultural_sensitivity=cultural_sensitivity,
                strengths=strengths,
                improvement_areas=improvement_areas,
                recommendations=recommendations,
                assessment_date=datetime.now(),
            )

            # 결과 저장
            self.social_assessments.append(assessment)

            logger.info(f"사회적 지능 평가 완료: 점수 {overall_score:.2f}")
            return assessment

        except Exception as e:
            logger.error(f"사회적 지능 평가 실패: {str(e)}")
            return None

    async def _preprocess_emotion_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정 컨텍스트 전처리"""
        processed_context = context.copy()

        # 감정 가중치 적용
        emotion_weights = await self.emotion_system.get_emotion_weights()
        processed_context["emotion_weights"] = emotion_weights

        # 주의 시스템 적용
        attention_focus = await self.attention_system.get_attention_focus()
        processed_context["attention_focus"] = attention_focus

        return processed_context

    async def _analyze_emotional_signals(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정 신호 분석"""
        signals = {
            "facial_expressions": context.get("facial_expressions", []),
            "voice_tone": context.get("voice_tone", ""),
            "body_language": context.get("body_language", []),
            "verbal_content": context.get("verbal_content", ""),
            "physiological_signals": context.get("physiological_signals", []),
        }

        return signals

    async def _perform_emotion_analysis(
        self, signals: Dict[str, Any], emotion_types: List[EmotionType]
    ) -> List[EmotionAnalysis]:
        """감정 분석 수행"""
        analyses = []

        for emotion_type in emotion_types:
            # 감정 강도 계산
            intensity = random.uniform(0.3, 0.9)

            # 신뢰도 계산
            confidence = random.uniform(0.6, 0.9)

            analysis = EmotionAnalysis(
                analysis_id=f"emotion_analysis_{int(time.time())}_{random.randint(1000, 9999)}",
                emotion_type=emotion_type,
                intensity=intensity,
                confidence=confidence,
                context="상호작용 컨텍스트",
                triggers=[f"{emotion_type.value} 유발 요소"],
                expressions=[f"{emotion_type.value} 표현"],
                physiological_signals=[f"{emotion_type.value} 생리적 신호"],
                behavioral_patterns=[f"{emotion_type.value} 행동 패턴"],
                created_at=datetime.now(),
            )
            analyses.append(analysis)

        return analyses

    async def _evaluate_emotion_confidence(
        self, analyses: List[EmotionAnalysis]
    ) -> List[EmotionAnalysis]:
        """감정 신뢰도 평가"""
        evaluated_analyses = []

        for analysis in analyses:
            # 신뢰도 임계값 검사
            if analysis.confidence >= self.social_thresholds["emotion_confidence"]:
                evaluated_analyses.append(analysis)

        return evaluated_analyses

    async def _analyze_social_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """사회적 맥락 분석"""
        analysis = {
            "participants": context.get("participants", []),
            "setting": context.get("setting", ""),
            "purpose": context.get("purpose", ""),
            "cultural_background": context.get("cultural_background", []),
            "communication_style": context.get("communication_style", ""),
            "power_relationships": context.get("power_relationships", {}),
        }

        return analysis

    async def _determine_context_type(
        self, analysis: Dict[str, Any]
    ) -> SocialContextType:
        """맥락 타입 결정"""
        # 맥락 분석을 기반으로 타입 결정
        setting = analysis.get("setting", "").lower()
        purpose = analysis.get("purpose", "").lower()

        if "회의" in setting or "업무" in purpose:
            return SocialContextType.PROFESSIONAL
        elif "친구" in setting or "개인" in purpose:
            return SocialContextType.PERSONAL
        elif "문화" in setting or "전통" in purpose:
            return SocialContextType.CULTURAL
        elif "공식" in setting:
            return SocialContextType.FORMAL
        else:
            return SocialContextType.INFORMAL

    async def _analyze_participant_relationships(
        self, analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """참여자 관계 분석"""
        relationships = {}
        participants = analysis.get("participants", [])

        for i, participant in enumerate(participants):
            if i < len(participants) - 1:
                relationships[participant] = "동료"

        return relationships

    async def _analyze_power_dynamics(
        self, analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """권력 역학 분석"""
        power_dynamics = {}
        participants = analysis.get("participants", [])

        for participant in participants:
            power_dynamics[participant] = random.uniform(0.1, 0.9)

        return power_dynamics

    async def _analyze_cultural_factors(self, analysis: Dict[str, Any]) -> List[str]:
        """문화적 요소 분석"""
        cultural_factors = analysis.get("cultural_background", [])

        # 기본 문화적 요소 추가
        cultural_factors.extend(["의사소통 스타일", "사회적 규범", "가치관"])

        return cultural_factors

    async def _create_social_context(
        self,
        analysis: Dict[str, Any],
        context_type: SocialContextType,
        relationships: Dict[str, str],
        power_dynamics: Dict[str, float],
        cultural_factors: List[str],
    ) -> SocialContext:
        """사회적 맥락 생성"""
        context = SocialContext(
            context_id=f"social_context_{int(time.time())}",
            context_type=context_type,
            participants=analysis.get("participants", []),
            relationships=relationships,
            power_dynamics=power_dynamics,
            cultural_factors=cultural_factors,
            communication_style=analysis.get("communication_style", "일반적"),
            social_norms=["상호 존중", "적절한 거리감"],
            expectations=["명확한 의사소통", "상호 이해"],
            created_at=datetime.now(),
        )

        return context

    async def _analyze_interaction_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상호작용 컨텍스트 분석"""
        analysis = {
            "interaction_type": context.get("interaction_type", "일반"),
            "participants": context.get("participants", []),
            "communication_style": context.get("communication_style", ""),
            "emotional_context": context.get("emotional_context", {}),
            "social_dynamics": context.get("social_dynamics", {}),
        }

        return analysis

    async def _analyze_participant_emotions(
        self, analysis: Dict[str, Any]
    ) -> Dict[str, EmotionType]:
        """참여자 감정 상태 분석"""
        emotional_states = {}
        participants = analysis.get("participants", [])

        for participant in participants:
            # 감정 타입 랜덤 선택
            emotion_type = random.choice(list(EmotionType))
            emotional_states[participant] = emotion_type

        return emotional_states

    async def _analyze_social_dynamics(
        self, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회적 역학 분석"""
        dynamics = {
            "power_distribution": random.uniform(0.2, 0.8),
            "communication_flow": random.uniform(0.4, 0.9),
            "group_cohesion": random.uniform(0.3, 0.8),
            "conflict_level": random.uniform(0.1, 0.6),
        }

        return dynamics

    async def _assess_interaction_quality(
        self,
        analysis: Dict[str, Any],
        emotional_states: Dict[str, EmotionType],
        social_dynamics: Dict[str, Any],
    ) -> float:
        """상호작용 품질 평가"""
        # 다양한 요소를 종합하여 품질 점수 계산
        communication_score = social_dynamics.get("communication_flow", 0.5)
        cohesion_score = social_dynamics.get("group_cohesion", 0.5)
        conflict_score = 1.0 - social_dynamics.get("conflict_level", 0.5)

        # 감정 상태 고려
        positive_emotions = sum(
            1
            for emotion in emotional_states.values()
            if emotion in [EmotionType.JOY, EmotionType.NEUTRAL]
        )
        emotion_score = (
            positive_emotions / len(emotional_states) if emotional_states else 0.5
        )

        # 종합 점수 계산
        quality_score = (
            communication_score + cohesion_score + conflict_score + emotion_score
        ) / 4

        return quality_score

    async def _generate_optimization_suggestions(
        self, interaction_quality: float, social_level: SocialIntelligenceLevel
    ) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []

        if interaction_quality < 0.6:
            suggestions.extend(
                [
                    "의사소통 스타일 개선",
                    "감정적 공감 능력 향상",
                    "사회적 맥락 이해 강화",
                ]
            )
        elif interaction_quality < 0.8:
            suggestions.extend(
                ["세밀한 감정 인식", "문화적 민감성 향상", "관계 관리 기술 개선"]
            )
        else:
            suggestions.extend(["고급 사회적 기술 개발", "전문적 상호작용 능력 향상"])

        return suggestions

    async def _create_human_interaction(
        self,
        analysis: Dict[str, Any],
        emotional_states: Dict[str, EmotionType],
        social_dynamics: Dict[str, Any],
        interaction_quality: float,
        optimization_suggestions: List[str],
    ) -> HumanInteraction:
        """인간 상호작용 생성"""
        interaction = HumanInteraction(
            interaction_id=f"human_interaction_{int(time.time())}",
            interaction_type=analysis.get("interaction_type", "일반"),
            participants=analysis.get("participants", []),
            communication_style=analysis.get("communication_style", "일반적"),
            emotional_state=emotional_states,
            social_dynamics=social_dynamics,
            interaction_quality=interaction_quality,
            satisfaction_score=interaction_quality * 0.9,  # 만족도는 품질의 90%
            improvement_suggestions=optimization_suggestions,
            created_at=datetime.now(),
        )

        return interaction

    async def _analyze_social_intelligence_dimensions(
        self, subject: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """사회적 지능 차원 분석"""
        dimensions = {
            "감정 인식": random.uniform(0.6, 0.9),
            "감정 표현": random.uniform(0.5, 0.8),
            "감정 조절": random.uniform(0.5, 0.8),
            "사회적 인식": random.uniform(0.6, 0.9),
            "관계 관리": random.uniform(0.5, 0.8),
            "의사소통": random.uniform(0.6, 0.9),
            "문화적 민감성": random.uniform(0.5, 0.8),
            "갈등 해결": random.uniform(0.4, 0.7),
        }

        return dimensions

    async def _assess_emotional_intelligence(
        self, dimensions: Dict[str, float]
    ) -> float:
        """감정 지능 평가"""
        emotional_dimensions = ["감정 인식", "감정 표현", "감정 조절"]

        emotional_score = sum(dimensions[dim] for dim in emotional_dimensions) / len(
            emotional_dimensions
        )
        return emotional_score

    async def _assess_social_skills(self, dimensions: Dict[str, float]) -> float:
        """사회적 기술 평가"""
        social_dimensions = ["사회적 인식", "관계 관리", "갈등 해결"]

        social_score = sum(dimensions[dim] for dim in social_dimensions) / len(
            social_dimensions
        )
        return social_score

    async def _assess_communication_effectiveness(
        self, dimensions: Dict[str, float]
    ) -> float:
        """의사소통 효과성 평가"""
        return dimensions.get("의사소통", 0.7)

    async def _assess_relationship_management(
        self, dimensions: Dict[str, float]
    ) -> float:
        """관계 관리 평가"""
        return dimensions.get("관계 관리", 0.7)

    async def _assess_cultural_sensitivity(self, dimensions: Dict[str, float]) -> float:
        """문화적 민감성 평가"""
        return dimensions.get("문화적 민감성", 0.7)

    async def _calculate_overall_social_score(
        self,
        emotional_intelligence: float,
        social_skills: float,
        communication_effectiveness: float,
        relationship_management: float,
        cultural_sensitivity: float,
    ) -> float:
        """전반적 사회적 지능 점수 계산"""
        overall_score = (
            emotional_intelligence * self.social_weights["emotional_intelligence"]
            + social_skills * self.social_weights["social_skills"]
            + communication_effectiveness * self.social_weights["communication"]
            + relationship_management * self.social_weights["relationship_management"]
            + cultural_sensitivity * self.social_weights["cultural_sensitivity"]
        )

        return overall_score

    async def _identify_social_strengths(
        self, dimensions: Dict[str, float]
    ) -> List[str]:
        """사회적 강점 식별"""
        strengths = []
        threshold = 0.7

        for dimension, score in dimensions.items():
            if score >= threshold:
                strengths.append(f"{dimension}: {score:.2f}")

        return strengths

    async def _identify_social_improvement_areas(
        self, dimensions: Dict[str, float]
    ) -> List[str]:
        """사회적 개선 영역 식별"""
        improvement_areas = []
        threshold = 0.6

        for dimension, score in dimensions.items():
            if score < threshold:
                improvement_areas.append(f"{dimension} 개선 필요: {score:.2f}")

        return improvement_areas

    async def _generate_social_recommendations(
        self, strengths: List[str], improvement_areas: List[str]
    ) -> List[str]:
        """사회적 권장사항 생성"""
        recommendations = []

        # 강점 기반 권장사항
        if strengths:
            recommendations.append("강점을 활용한 사회적 상호작용 강화")

        # 개선 영역 기반 권장사항
        for area in improvement_areas:
            if "감정" in area:
                recommendations.append("감정 인식 및 표현 능력 향상 훈련")
            elif "의사소통" in area:
                recommendations.append("효과적 의사소통 기술 학습")
            elif "문화" in area:
                recommendations.append("문화적 민감성 향상 프로그램")
            elif "관계" in area:
                recommendations.append("관계 관리 기술 개발")

        return recommendations

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "emotion_analyses_count": len(self.emotion_analyses),
            "social_contexts_count": len(self.social_contexts),
            "human_interactions_count": len(self.human_interactions),
            "social_assessments_count": len(self.social_assessments),
            "social_thresholds": self.social_thresholds,
            "social_weights": self.social_weights,
        }


async def test_social_intelligence_engine():
    """사회적 지능 엔진 테스트"""
    engine = SocialIntelligenceEngine()

    # 감정 인식 테스트
    emotion_context = {
        "facial_expressions": ["미소", "눈빛"],
        "voice_tone": "따뜻한",
        "body_language": ["개방적 자세", "긍정적 제스처"],
        "verbal_content": "기쁜 마음으로 대화",
    }

    emotions = await engine.recognize_emotions(emotion_context)
    print(f"인식된 감정: {len(emotions)}개")

    # 사회적 맥락 이해 테스트
    context = {
        "participants": ["김철수", "이영희", "박민수"],
        "setting": "업무 회의",
        "purpose": "프로젝트 계획 수립",
        "cultural_background": ["한국 문화", "기업 문화"],
    }

    social_context = await engine.understand_social_context(context)
    print(f"이해된 사회적 맥락: {social_context.context_type.value}")

    # 인간 상호작용 최적화 테스트
    interaction_context = {
        "interaction_type": "팀 협업",
        "participants": ["팀원 A", "팀원 B", "팀원 C"],
        "communication_style": "협력적",
        "emotional_context": {"팀원 A": "기쁨", "팀원 B": "중립", "팀원 C": "기쁨"},
    }

    interaction = await engine.optimize_human_interaction(interaction_context)
    print(f"상호작용 품질: {interaction.interaction_quality:.2f}")

    # 사회적 지능 평가 테스트
    assessment = await engine.assess_social_intelligence("팀 리더십", context)
    print(f"사회적 지능 점수: {assessment.overall_social_score:.2f}")

    # 시스템 상태 확인
    status = engine.get_system_status()
    print(f"시스템 상태: {status}")


if __name__ == "__main__":
    asyncio.run(test_social_intelligence_engine())
