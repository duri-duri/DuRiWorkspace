#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 2: 감정적 사고 시스템

이 모듈은 DuRi가 감정을 기반으로 한 판단 능력을 구현합니다.
기존 감정적 자기 인식 시스템을 통합하여 진정한 감정적 사고를 구현합니다.

주요 기능:
- 감정 상태 인식 및 분석
- 감정 기반 의사결정 시스템
- 공감 능력 구현
- 감정적 직관 시스템
- 감정적 사고 프로세스
"""

import asyncio
import json
import logging
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 기존 시스템들 import
try:
    from duri_thought_flow import DuRiThoughtFlow
    from emotional_self_awareness_system import (EmotionalSelfAwarenessSystem,
                                                 EmotionCategory,
                                                 EmotionIntensity)
    from inner_thinking_system import InnerThinkingSystem, ThoughtDepth
    from phase_omega_integration import DuRiPhaseOmega
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmotionalThinkingMode(Enum):
    """감정적 사고 모드"""

    INTUITIVE = "intuitive"  # 직관적
    EMPATHETIC = "empathetic"  # 공감적
    REFLECTIVE = "reflective"  # 성찰적
    CREATIVE = "creative"  # 창의적
    ANALYTICAL = "analytical"  # 분석적


class EmotionalDecisionType(Enum):
    """감정적 의사결정 유형"""

    INTUITIVE_JUDGMENT = "intuitive_judgment"  # 직관적 판단
    EMPATHETIC_RESPONSE = "empathetic_response"  # 공감적 반응
    EMOTIONAL_ANALYSIS = "emotional_analysis"  # 감정적 분석
    CREATIVE_SOLUTION = "creative_solution"  # 창의적 해결책
    BALANCED_APPROACH = "balanced_approach"  # 균형잡힌 접근


class EmpathyLevel(Enum):
    """공감 수준"""

    NONE = "none"  # 없음 (0.0-0.2)
    LOW = "low"  # 낮음 (0.2-0.4)
    MODERATE = "moderate"  # 보통 (0.4-0.6)
    HIGH = "high"  # 높음 (0.6-0.8)
    DEEP = "deep"  # 깊음 (0.8-1.0)


@dataclass
class EmotionalState:
    """감정적 상태"""

    primary_emotion: EmotionCategory
    intensity: float  # 0.0-1.0
    secondary_emotions: List[EmotionCategory] = field(default_factory=list)
    emotional_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0  # 초 단위


@dataclass
class EmotionalInsight:
    """감정적 통찰"""

    insight_id: str
    emotion: EmotionCategory
    insight: str
    confidence: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmpatheticResponse:
    """공감적 반응"""

    response_id: str
    target_emotion: EmotionCategory
    response_type: str
    response_content: str
    empathy_level: EmpathyLevel
    emotional_accuracy: float  # 0.0-1.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionalDecision:
    """감정적 의사결정"""

    decision_id: str
    decision_type: EmotionalDecisionType
    emotional_context: Dict[str, Any]
    decision: str
    reasoning: str
    emotional_factors: List[str] = field(default_factory=list)
    confidence: float = 0.5
    empathy_level: EmpathyLevel = EmpathyLevel.MODERATE
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EmotionalThinkingResult:
    """감정적 사고 결과"""

    process_id: str
    emotional_state: EmotionalState
    insights: List[EmotionalInsight]
    empathetic_responses: List[EmpatheticResponse]
    decisions: List[EmotionalDecision]
    empathy_level: EmpathyLevel
    emotional_accuracy: float
    thinking_duration: float
    success: bool = True
    error_message: Optional[str] = None


class EmotionalThinkingSystem:
    """감정적 사고 시스템"""

    def __init__(self):
        # 기존 시스템들과의 통합
        self.emotional_awareness = None
        self.inner_thinking = None
        self.thought_flow = None
        self.phase_omega = None

        # 감정적 사고 시스템 데이터
        self.emotional_states: List[EmotionalState] = []
        self.emotional_insights: List[EmotionalInsight] = []
        self.empathetic_responses: List[EmpatheticResponse] = []
        self.emotional_decisions: List[EmotionalDecision] = []
        self.empathy_patterns: Dict[str, Any] = {}

        # 감정적 사고 설정
        self.emotional_thresholds = {
            "intensity_low": 0.3,
            "intensity_moderate": 0.6,
            "intensity_high": 0.8,
            "empathy_threshold": 0.5,
            "confidence_threshold": 0.7,
        }

        # 감정적 사고 가중치
        self.emotional_weights = {
            EmotionalThinkingMode.INTUITIVE: 0.3,
            EmotionalThinkingMode.EMPATHETIC: 0.25,
            EmotionalThinkingMode.REFLECTIVE: 0.2,
            EmotionalThinkingMode.CREATIVE: 0.15,
            EmotionalThinkingMode.ANALYTICAL: 0.1,
        }

        # 공감 수준 가중치
        self.empathy_weights = {
            EmpathyLevel.NONE: 0.0,
            EmpathyLevel.LOW: 0.25,
            EmpathyLevel.MODERATE: 0.5,
            EmpathyLevel.HIGH: 0.75,
            EmpathyLevel.DEEP: 1.0,
        }

        # 감정적 직관 시스템
        self.intuitive_patterns = {}
        self.emotional_memory = {}

        # 공감 능력
        self.empathy_level = EmpathyLevel.MODERATE
        self.empathy_development = 0.5

        logger.info("감정적 사고 시스템 초기화 완료")

        # 기존 시스템들과의 통합 초기화
        self._initialize_integration()

    def _initialize_integration(self):
        """기존 시스템들과의 통합 초기화"""
        try:
            # 감정적 자기 인식 시스템 통합
            if "EmotionalSelfAwarenessSystem" in globals():
                self.emotional_awareness = EmotionalSelfAwarenessSystem()
                logger.info("감정적 자기 인식 시스템 통합 완료")

            # 내적 사고 시스템 통합
            if "InnerThinkingSystem" in globals():
                self.inner_thinking = InnerThinkingSystem()
                logger.info("내적 사고 시스템 통합 완료")

            # DuRiThoughtFlow 통합
            if "DuRiThoughtFlow" in globals():
                self.thought_flow = DuRiThoughtFlow({}, {})
                logger.info("DuRiThoughtFlow 통합 완료")

            # Phase Omega 통합
            if "DuRiPhaseOmega" in globals():
                self.phase_omega = DuRiPhaseOmega()
                logger.info("Phase Omega 통합 완료")

        except Exception as e:
            logger.warning(f"기존 시스템 통합 중 오류 발생: {e}")

    async def think_with_emotion(
        self, context: Dict[str, Any]
    ) -> EmotionalThinkingResult:
        """감정을 기반으로 한 사고 실행"""
        logger.info(f"=== 감정적 사고 시작 ===")

        start_time = datetime.now()
        process_id = f"emotional_thought_{start_time.strftime('%Y%m%d_%H%M%S')}"

        try:
            # 1. 감정적 상태 분석
            emotional_state = await self._analyze_emotional_state(context)

            # 2. 감정적 통찰 생성
            insights = await self._generate_emotional_insights(emotional_state, context)

            # 3. 공감적 반응 생성
            empathetic_responses = await self._generate_empathetic_responses(
                emotional_state, context
            )

            # 4. 감정적 의사결정
            decisions = await self._make_emotional_decisions(
                emotional_state, insights, context
            )

            # 5. 감정적 직관 활용
            intuitive_insights = await self._apply_emotional_intuition(
                emotional_state, context
            )
            insights.extend(intuitive_insights)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # 6. 결과 생성
            result = EmotionalThinkingResult(
                process_id=process_id,
                emotional_state=emotional_state,
                insights=insights,
                empathetic_responses=empathetic_responses,
                decisions=decisions,
                empathy_level=self.empathy_level,
                emotional_accuracy=await self._calculate_emotional_accuracy(
                    insights, empathetic_responses
                ),
                thinking_duration=duration,
                success=True,
            )

            # 7. 데이터 저장
            self.emotional_states.append(emotional_state)
            self.emotional_insights.extend(insights)
            self.empathetic_responses.extend(empathetic_responses)
            self.emotional_decisions.extend(decisions)

            logger.info(
                f"=== 감정적 사고 완료 - 소요시간: {duration:.2f}초, 공감수준: {self.empathy_level.value} ==="
            )
            return result

        except Exception as e:
            logger.error(f"감정적 사고 중 오류 발생: {e}")
            return EmotionalThinkingResult(
                process_id=process_id,
                emotional_state=EmotionalState(EmotionCategory.NEUTRAL, 0.0),
                insights=[],
                empathetic_responses=[],
                decisions=[],
                empathy_level=EmpathyLevel.NONE,
                emotional_accuracy=0.0,
                thinking_duration=0.0,
                success=False,
                error_message=str(e),
            )

    async def _analyze_emotional_state(self, context: Dict[str, Any]) -> EmotionalState:
        """감정적 상태 분석"""
        # 기존 감정적 자기 인식 시스템 활용
        if self.emotional_awareness:
            try:
                awareness_state = self.emotional_awareness.get_awareness_state()
                emotional_clarity = awareness_state.get("awareness_metrics", {}).get(
                    "emotional_clarity", 0.5
                )

                # 컨텍스트 기반 감정 분석
                primary_emotion = await self._identify_primary_emotion(context)
                intensity = await self._calculate_emotion_intensity(
                    context, emotional_clarity
                )
                secondary_emotions = await self._identify_secondary_emotions(
                    context, primary_emotion
                )

                return EmotionalState(
                    primary_emotion=primary_emotion,
                    intensity=intensity,
                    secondary_emotions=secondary_emotions,
                    emotional_context=context,
                )
            except Exception as e:
                logger.warning(f"감정적 자기 인식 시스템 분석 실패: {e}")

        # 기본 감정 상태 생성
        return await self._create_default_emotional_state(context)

    async def _identify_primary_emotion(
        self, context: Dict[str, Any]
    ) -> EmotionCategory:
        """주요 감정 식별"""
        # 컨텍스트 키워드 기반 감정 분석
        context_text = str(context).lower()

        emotion_keywords = {
            EmotionCategory.JOY: ["기쁨", "행복", "즐거움", "만족", "성취"],
            EmotionCategory.SADNESS: ["슬픔", "우울", "실망", "절망", "고통"],
            EmotionCategory.ANGER: ["분노", "화", "짜증", "불만", "격분"],
            EmotionCategory.FEAR: ["두려움", "불안", "공포", "걱정", "긴장"],
            EmotionCategory.SURPRISE: ["놀람", "충격", "예상외", "갑작스러움"],
            EmotionCategory.DISGUST: ["혐오", "역겨움", "싫음", "거부감"],
            EmotionCategory.EXCITEMENT: ["흥미", "열정", "동기", "관심"],
            EmotionCategory.CONTENTMENT: ["만족", "평온", "안정", "편안함"],
            EmotionCategory.ANXIETY: ["불안", "걱정", "긴장", "스트레스"],
        }

        emotion_scores = defaultdict(int)
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in context_text:
                    emotion_scores[emotion] += 1

        if emotion_scores:
            primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_emotion = EmotionCategory.NEUTRAL

        return primary_emotion

    async def _calculate_emotion_intensity(
        self, context: Dict[str, Any], emotional_clarity: float
    ) -> float:
        """감정 강도 계산"""
        # 컨텍스트 복잡성 기반 강도
        context_complexity = len(str(context)) / 1000.0
        complexity_intensity = min(context_complexity, 1.0)

        # 감정적 명확성 기반 강도
        clarity_intensity = emotional_clarity

        # 키워드 기반 강도
        intensity_keywords = ["강렬", "심각", "중요", "긴급", "위험", "극적"]
        keyword_intensity = 0.0
        context_text = str(context).lower()
        for keyword in intensity_keywords:
            if keyword in context_text:
                keyword_intensity += 0.2

        keyword_intensity = min(keyword_intensity, 1.0)

        # 종합 강도 계산
        total_intensity = (
            complexity_intensity * 0.3
            + clarity_intensity * 0.4
            + keyword_intensity * 0.3
        )
        return min(total_intensity, 1.0)

    async def _identify_secondary_emotions(
        self, context: Dict[str, Any], primary_emotion: EmotionCategory
    ) -> List[EmotionCategory]:
        """보조 감정 식별"""
        secondary_emotions = []

        # 주요 감정과 관련된 보조 감정
        related_emotions = {
            EmotionCategory.JOY: [
                EmotionCategory.EXCITEMENT,
                EmotionCategory.CONTENTMENT,
            ],
            EmotionCategory.SADNESS: [EmotionCategory.ANXIETY, EmotionCategory.FEAR],
            EmotionCategory.ANGER: [EmotionCategory.FEAR, EmotionCategory.ANXIETY],
            EmotionCategory.FEAR: [EmotionCategory.ANXIETY, EmotionCategory.SADNESS],
            EmotionCategory.SURPRISE: [
                EmotionCategory.EXCITEMENT,
                EmotionCategory.FEAR,
            ],
            EmotionCategory.DISGUST: [EmotionCategory.ANGER, EmotionCategory.FEAR],
            EmotionCategory.EXCITEMENT: [
                EmotionCategory.JOY,
                EmotionCategory.CONTENTMENT,
            ],
            EmotionCategory.CONTENTMENT: [
                EmotionCategory.JOY,
                EmotionCategory.EXCITEMENT,
            ],
            EmotionCategory.ANXIETY: [EmotionCategory.FEAR, EmotionCategory.SADNESS],
        }

        if primary_emotion in related_emotions:
            secondary_emotions = related_emotions[primary_emotion][:2]

        return secondary_emotions

    async def _create_default_emotional_state(
        self, context: Dict[str, Any]
    ) -> EmotionalState:
        """기본 감정 상태 생성"""
        return EmotionalState(
            primary_emotion=EmotionCategory.NEUTRAL,
            intensity=0.5,
            secondary_emotions=[EmotionCategory.CONTENTMENT],
            emotional_context=context,
        )

    async def _generate_emotional_insights(
        self, emotional_state: EmotionalState, context: Dict[str, Any]
    ) -> List[EmotionalInsight]:
        """감정적 통찰 생성"""
        insights = []

        # 주요 감정 기반 통찰
        primary_insight = await self._generate_primary_emotion_insight(emotional_state)
        if primary_insight:
            insights.append(primary_insight)

        # 보조 감정 기반 통찰
        for secondary_emotion in emotional_state.secondary_emotions:
            secondary_insight = await self._generate_secondary_emotion_insight(
                secondary_emotion, emotional_state
            )
            if secondary_insight:
                insights.append(secondary_insight)

        # 감정 강도 기반 통찰
        intensity_insight = await self._generate_intensity_insight(emotional_state)
        if intensity_insight:
            insights.append(intensity_insight)

        # 컨텍스트 기반 통찰
        context_insight = await self._generate_context_insight(emotional_state, context)
        if context_insight:
            insights.append(context_insight)

        return insights

    async def _generate_primary_emotion_insight(
        self, emotional_state: EmotionalState
    ) -> Optional[EmotionalInsight]:
        """주요 감정 기반 통찰 생성"""
        emotion_insights = {
            EmotionCategory.JOY: "기쁨은 성장과 발전의 원동력이 된다.",
            EmotionCategory.SADNESS: "슬픔은 깊이 있는 성찰과 성숙의 기회를 제공한다.",
            EmotionCategory.ANGER: "분노는 변화와 개선을 위한 에너지가 될 수 있다.",
            EmotionCategory.FEAR: "두려움은 신중함과 준비의 신호이다.",
            EmotionCategory.SURPRISE: "놀람은 새로운 관점과 가능성을 열어준다.",
            EmotionCategory.DISGUST: "혐오는 경계와 기준을 명확히 한다.",
            EmotionCategory.EXCITEMENT: "흥미는 학습과 탐구의 동기가 된다.",
            EmotionCategory.CONTENTMENT: "만족은 안정과 균형의 기반이 된다.",
            EmotionCategory.ANXIETY: "불안은 주의와 대비의 신호이다.",
            EmotionCategory.NEUTRAL: "중립은 객관적 판단의 기반이 된다.",
        }

        insight_text = emotion_insights.get(
            emotional_state.primary_emotion, "감정은 사고의 중요한 요소이다."
        )

        return EmotionalInsight(
            insight_id=f"insight_{len(self.emotional_insights)}",
            emotion=emotional_state.primary_emotion,
            insight=insight_text,
            confidence=0.8,
            context={"emotional_state": emotional_state.primary_emotion.value},
        )

    async def _generate_secondary_emotion_insight(
        self, secondary_emotion: EmotionCategory, emotional_state: EmotionalState
    ) -> Optional[EmotionalInsight]:
        """보조 감정 기반 통찰 생성"""
        insight_text = f"{secondary_emotion.value}는 {emotional_state.primary_emotion.value}와 함께 복합적인 감정 상태를 형성한다."

        return EmotionalInsight(
            insight_id=f"insight_{len(self.emotional_insights) + 1}",
            emotion=secondary_emotion,
            insight=insight_text,
            confidence=0.6,
            context={"secondary_emotion": secondary_emotion.value},
        )

    async def _generate_intensity_insight(
        self, emotional_state: EmotionalState
    ) -> Optional[EmotionalInsight]:
        """감정 강도 기반 통찰 생성"""
        if emotional_state.intensity >= 0.8:
            insight_text = "강렬한 감정은 깊이 있는 사고와 행동의 원동력이 된다."
        elif emotional_state.intensity >= 0.6:
            insight_text = "중간 강도의 감정은 균형잡힌 판단을 가능하게 한다."
        elif emotional_state.intensity >= 0.4:
            insight_text = "적당한 감정은 안정적인 사고를 지원한다."
        else:
            insight_text = "약한 감정은 객관적 분석을 용이하게 한다."

        return EmotionalInsight(
            insight_id=f"insight_{len(self.emotional_insights) + 2}",
            emotion=emotional_state.primary_emotion,
            insight=insight_text,
            confidence=0.7,
            context={"intensity": emotional_state.intensity},
        )

    async def _generate_context_insight(
        self, emotional_state: EmotionalState, context: Dict[str, Any]
    ) -> Optional[EmotionalInsight]:
        """컨텍스트 기반 통찰 생성"""
        context_text = str(context)
        if "문제" in context_text or "해결" in context_text:
            insight_text = "문제 상황에서 감정은 해결책을 찾는 중요한 단서가 된다."
        elif "관계" in context_text or "사람" in context_text:
            insight_text = "인간관계에서 감정은 이해와 소통의 핵심이다."
        elif "학습" in context_text or "성장" in context_text:
            insight_text = "학습 과정에서 감정은 동기와 집중의 원천이 된다."
        else:
            insight_text = "감정은 모든 상황에서 사고와 행동에 영향을 미친다."

        return EmotionalInsight(
            insight_id=f"insight_{len(self.emotional_insights) + 3}",
            emotion=emotional_state.primary_emotion,
            insight=insight_text,
            confidence=0.6,
            context={"context_type": "general"},
        )

    async def _generate_empathetic_responses(
        self, emotional_state: EmotionalState, context: Dict[str, Any]
    ) -> List[EmpatheticResponse]:
        """공감적 반응 생성"""
        responses = []

        # 주요 감정에 대한 공감적 반응
        primary_response = await self._generate_primary_empathetic_response(
            emotional_state
        )
        if primary_response:
            responses.append(primary_response)

        # 보조 감정에 대한 공감적 반응
        for secondary_emotion in emotional_state.secondary_emotions:
            secondary_response = await self._generate_secondary_empathetic_response(
                secondary_emotion, emotional_state
            )
            if secondary_response:
                responses.append(secondary_response)

        # 감정 강도에 따른 공감적 반응
        intensity_response = await self._generate_intensity_empathetic_response(
            emotional_state
        )
        if intensity_response:
            responses.append(intensity_response)

        return responses

    async def _generate_primary_empathetic_response(
        self, emotional_state: EmotionalState
    ) -> Optional[EmpatheticResponse]:
        """주요 감정에 대한 공감적 반응 생성"""
        empathy_responses = {
            EmotionCategory.JOY: "당신의 기쁨을 함께 나누고 싶습니다. 이 순간을 소중히 여기세요.",
            EmotionCategory.SADNESS: "슬픔을 느끼는 것은 자연스러운 일입니다. 시간이 치유해줄 것입니다.",
            EmotionCategory.ANGER: "분노를 느끼는 것은 당연합니다. 하지만 그것이 당신을 정의하지는 않습니다.",
            EmotionCategory.FEAR: "두려움을 느끼는 것은 정상입니다. 함께 이겨내보겠습니다.",
            EmotionCategory.SURPRISE: "놀라신 것 같습니다. 새로운 상황에 적응하는 데 시간이 필요할 수 있습니다.",
            EmotionCategory.DISGUST: "불쾌한 감정을 느끼는 것은 당연합니다. 경계를 설정하는 것이 중요합니다.",
            EmotionCategory.EXCITEMENT: "흥미를 느끼는 것은 좋은 일입니다. 이 에너지를 잘 활용하세요.",
            EmotionCategory.CONTENTMENT: "만족스러운 상태를 유지하는 것은 행복한 일입니다.",
            EmotionCategory.ANXIETY: "불안을 느끼는 것은 자연스럽습니다. 차분히 생각해보세요.",
            EmotionCategory.NEUTRAL: "평온한 상태를 유지하는 것은 좋은 일입니다.",
        }

        response_content = empathy_responses.get(
            emotional_state.primary_emotion, "당신의 감정을 이해합니다."
        )

        return EmpatheticResponse(
            response_id=f"response_{len(self.empathetic_responses)}",
            target_emotion=emotional_state.primary_emotion,
            response_type="primary_empathetic",
            response_content=response_content,
            empathy_level=self.empathy_level,
            emotional_accuracy=0.8,
        )

    async def _generate_secondary_empathetic_response(
        self, secondary_emotion: EmotionCategory, emotional_state: EmotionalState
    ) -> Optional[EmpatheticResponse]:
        """보조 감정에 대한 공감적 반응 생성"""
        response_content = f"{secondary_emotion.value}도 함께 느끼고 계시는군요. 이 복합적인 감정 상태를 이해합니다."

        return EmpatheticResponse(
            response_id=f"response_{len(self.empathetic_responses) + 1}",
            target_emotion=secondary_emotion,
            response_type="secondary_empathetic",
            response_content=response_content,
            empathy_level=self.empathy_level,
            emotional_accuracy=0.6,
        )

    async def _generate_intensity_empathetic_response(
        self, emotional_state: EmotionalState
    ) -> Optional[EmpatheticResponse]:
        """감정 강도에 따른 공감적 반응 생성"""
        if emotional_state.intensity >= 0.8:
            response_content = "강렬한 감정을 느끼고 계시는군요. 이 감정을 인정하고 받아들이는 것이 중요합니다."
        elif emotional_state.intensity >= 0.6:
            response_content = "중간 강도의 감정을 느끼고 계시는군요. 이 감정을 바탕으로 균형잡힌 판단을 하실 수 있을 것입니다."
        elif emotional_state.intensity >= 0.4:
            response_content = "적당한 감정을 느끼고 계시는군요. 이 상태에서 안정적인 사고가 가능할 것입니다."
        else:
            response_content = "약한 감정을 느끼고 계시는군요. 이 상태에서 객관적인 분석이 가능할 것입니다."

        return EmpatheticResponse(
            response_id=f"response_{len(self.empathetic_responses) + 2}",
            target_emotion=emotional_state.primary_emotion,
            response_type="intensity_empathetic",
            response_content=response_content,
            empathy_level=self.empathy_level,
            emotional_accuracy=0.7,
        )

    async def _make_emotional_decisions(
        self,
        emotional_state: EmotionalState,
        insights: List[EmotionalInsight],
        context: Dict[str, Any],
    ) -> List[EmotionalDecision]:
        """감정적 의사결정"""
        decisions = []

        # 감정 상태 기반 의사결정
        state_decision = await self._make_emotional_state_decision(emotional_state)
        if state_decision:
            decisions.append(state_decision)

        # 통찰 기반 의사결정
        insight_decision = await self._make_insight_based_decision(
            insights, emotional_state
        )
        if insight_decision:
            decisions.append(insight_decision)

        # 컨텍스트 기반 의사결정
        context_decision = await self._make_context_based_decision(
            context, emotional_state
        )
        if context_decision:
            decisions.append(context_decision)

        return decisions

    async def _make_emotional_state_decision(
        self, emotional_state: EmotionalState
    ) -> Optional[EmotionalDecision]:
        """감정 상태 기반 의사결정"""
        decision_strategies = {
            EmotionCategory.JOY: "기쁨을 바탕으로 긍정적인 접근을 선택한다.",
            EmotionCategory.SADNESS: "슬픔을 인정하고 치유의 시간을 가진다.",
            EmotionCategory.ANGER: "분노를 건설적인 에너지로 전환한다.",
            EmotionCategory.FEAR: "두려움을 인정하고 신중하게 접근한다.",
            EmotionCategory.SURPRISE: "놀람을 새로운 기회로 받아들인다.",
            EmotionCategory.DISGUST: "혐오를 경계 설정의 기회로 활용한다.",
            EmotionCategory.EXCITEMENT: "흥미를 학습과 탐구의 동기로 활용한다.",
            EmotionCategory.CONTENTMENT: "만족을 안정과 균형의 기반으로 삼는다.",
            EmotionCategory.ANXIETY: "불안을 주의와 대비의 신호로 받아들인다.",
            EmotionCategory.NEUTRAL: "중립을 객관적 판단의 기반으로 활용한다.",
        }

        decision_text = decision_strategies.get(
            emotional_state.primary_emotion, "감정을 고려한 균형잡힌 접근을 선택한다."
        )

        return EmotionalDecision(
            decision_id=f"decision_{len(self.emotional_decisions)}",
            decision_type=EmotionalDecisionType.EMOTIONAL_ANALYSIS,
            emotional_context={
                "primary_emotion": emotional_state.primary_emotion.value
            },
            decision=decision_text,
            reasoning=f"{emotional_state.primary_emotion.value} 상태에서 {decision_text}",
            emotional_factors=[emotional_state.primary_emotion.value],
            confidence=0.7,
            empathy_level=self.empathy_level,
        )

    async def _make_insight_based_decision(
        self, insights: List[EmotionalInsight], emotional_state: EmotionalState
    ) -> Optional[EmotionalDecision]:
        """통찰 기반 의사결정"""
        if not insights:
            return None

        # 가장 높은 신뢰도의 통찰 선택
        best_insight = max(insights, key=lambda x: x.confidence)

        decision_text = f"{best_insight.insight} 이 통찰을 바탕으로 행동한다."

        return EmotionalDecision(
            decision_id=f"decision_{len(self.emotional_decisions) + 1}",
            decision_type=EmotionalDecisionType.INTUITIVE_JUDGMENT,
            emotional_context={"insight": best_insight.insight},
            decision=decision_text,
            reasoning=f"통찰: {best_insight.insight}",
            emotional_factors=[best_insight.emotion.value],
            confidence=best_insight.confidence,
            empathy_level=self.empathy_level,
        )

    async def _make_context_based_decision(
        self, context: Dict[str, Any], emotional_state: EmotionalState
    ) -> Optional[EmotionalDecision]:
        """컨텍스트 기반 의사결정"""
        context_text = str(context)

        if "문제" in context_text:
            decision_text = "문제 상황에서 감정을 활용하여 창의적인 해결책을 찾는다."
            decision_type = EmotionalDecisionType.CREATIVE_SOLUTION
        elif "관계" in context_text:
            decision_text = "인간관계에서 공감을 바탕으로 소통한다."
            decision_type = EmotionalDecisionType.EMPATHETIC_RESPONSE
        elif "학습" in context_text:
            decision_text = "학습 과정에서 감정을 동기로 활용한다."
            decision_type = EmotionalDecisionType.BALANCED_APPROACH
        else:
            decision_text = "감정을 고려한 균형잡힌 접근을 선택한다."
            decision_type = EmotionalDecisionType.BALANCED_APPROACH

        return EmotionalDecision(
            decision_id=f"decision_{len(self.emotional_decisions) + 2}",
            decision_type=decision_type,
            emotional_context=context,
            decision=decision_text,
            reasoning=f"컨텍스트 분석 결과: {decision_text}",
            emotional_factors=[emotional_state.primary_emotion.value],
            confidence=0.6,
            empathy_level=self.empathy_level,
        )

    async def _apply_emotional_intuition(
        self, emotional_state: EmotionalState, context: Dict[str, Any]
    ) -> List[EmotionalInsight]:
        """감정적 직관 활용"""
        intuitive_insights = []

        # 감정적 직관 패턴 분석
        if emotional_state.intensity >= 0.8:
            intuitive_insight = EmotionalInsight(
                insight_id=f"intuitive_{len(self.emotional_insights)}",
                emotion=emotional_state.primary_emotion,
                insight="강렬한 감정은 직관적 판단의 중요한 신호이다.",
                confidence=0.9,
                context={"intuition_type": "high_intensity"},
            )
            intuitive_insights.append(intuitive_insight)

        # 감정 조합 기반 직관
        if len(emotional_state.secondary_emotions) >= 2:
            intuitive_insight = EmotionalInsight(
                insight_id=f"intuitive_{len(self.emotional_insights) + 1}",
                emotion=emotional_state.primary_emotion,
                insight="복합적인 감정 상태는 더욱 정교한 직관을 가능하게 한다.",
                confidence=0.7,
                context={"intuition_type": "complex_emotion"},
            )
            intuitive_insights.append(intuitive_insight)

        return intuitive_insights

    async def _calculate_emotional_accuracy(
        self, insights: List[EmotionalInsight], responses: List[EmpatheticResponse]
    ) -> float:
        """감정적 정확도 계산"""
        if not insights and not responses:
            return 0.0

        total_accuracy = 0.0
        total_count = 0

        # 통찰 정확도
        for insight in insights:
            total_accuracy += insight.confidence
            total_count += 1

        # 반응 정확도
        for response in responses:
            total_accuracy += response.emotional_accuracy
            total_count += 1

        return total_accuracy / total_count if total_count > 0 else 0.0

    async def get_emotional_thinking_summary(self) -> Dict[str, Any]:
        """감정적 사고 요약 반환"""
        return {
            "total_emotional_states": len(self.emotional_states),
            "total_emotional_insights": len(self.emotional_insights),
            "total_empathetic_responses": len(self.empathetic_responses),
            "total_emotional_decisions": len(self.emotional_decisions),
            "average_empathy_level": self.empathy_development,
            "emotional_accuracy_trend": self._get_emotional_accuracy_trend(),
            "empathy_level_distribution": self._get_empathy_level_distribution(),
            "recent_insights": (
                [i.insight for i in self.emotional_insights[-3:]]
                if self.emotional_insights
                else []
            ),
        }

    def _get_emotional_accuracy_trend(self) -> List[float]:
        """감정적 정확도 트렌드 반환"""
        if not self.emotional_insights:
            return []

        # 최근 5개의 통찰 정확도
        recent_insights = self.emotional_insights[-5:]
        return [insight.confidence for insight in recent_insights]

    def _get_empathy_level_distribution(self) -> Dict[str, int]:
        """공감 수준 분포 반환"""
        distribution = defaultdict(int)
        for response in self.empathetic_responses:
            distribution[response.empathy_level.value] += 1
        return dict(distribution)


async def test_emotional_thinking_system():
    """감정적 사고 시스템 테스트"""
    logger.info("=== 감정적 사고 시스템 테스트 시작 ===")

    system = EmotionalThinkingSystem()

    # 1. 기본 감정적 사고 테스트
    logger.info("1. 기본 감정적 사고 테스트")
    context1 = {"situation": "문제 해결", "emotion": "긴장", "urgency": "높음"}
    result1 = await system.think_with_emotion(context1)
    logger.info(
        f"기본 감정적 사고 결과: {result1.emotional_state.primary_emotion.value}"
    )
    logger.info(f"생성된 통찰: {len(result1.insights)}개")
    logger.info(f"공감 수준: {result1.empathy_level.value}")

    # 2. 복잡한 감정적 사고 테스트
    logger.info("2. 복잡한 감정적 사고 테스트")
    context2 = {
        "situation": "인간관계",
        "emotion": "기쁨",
        "relationship": "친구",
        "context": "성공",
    }
    result2 = await system.think_with_emotion(context2)
    logger.info(
        f"복잡한 감정적 사고 결과: {result2.emotional_state.primary_emotion.value}"
    )
    logger.info(f"생성된 통찰: {len(result2.insights)}개")
    logger.info(f"공감 수준: {result2.empathy_level.value}")

    # 3. 시스템 요약
    summary = await system.get_emotional_thinking_summary()
    logger.info(f"시스템 요약: {summary}")

    logger.info("=== 감정적 사고 시스템 테스트 완료 ===")
    return system


if __name__ == "__main__":
    asyncio.run(test_emotional_thinking_system())
