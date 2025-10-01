#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Z v2.0: 표현 계층 시스템

이 모듈은 DuRi의 표현 계층 시스템입니다.
Phase 4~6을 표현 계층으로 강등하여 사고 흐름의 외부 표현을 담당합니다.

주요 기능:
- 감정 표현 시스템
- 예술 표현 시스템
- 사회성 표현 시스템
- 표현 계층 통합 관리
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExpressionType(Enum):
    """표현 유형 열거형"""

    EMOTION = "emotion"
    ART = "art"
    SOCIAL = "social"
    INTEGRATED = "integrated"


class EmotionType(Enum):
    """감정 유형 열거형"""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class ArtStyle(Enum):
    """예술 스타일 열거형"""

    ABSTRACT = "abstract"
    REALISTIC = "realistic"
    IMPRESSIONIST = "impressionist"
    EXPRESSIONIST = "expressionist"
    MINIMALIST = "minimalist"


class SocialContext(Enum):
    """사회적 맥락 열거형"""

    FORMAL = "formal"
    INFORMAL = "informal"
    PROFESSIONAL = "professional"
    PERSONAL = "personal"
    ACADEMIC = "academic"


@dataclass
class ExpressionData:
    """표현 데이터 클래스"""

    expression_type: ExpressionType
    content: Dict[str, Any]
    timestamp: datetime
    context: Dict[str, Any]
    intensity: float
    confidence: float


@dataclass
class ExpressionResult:
    """표현 결과 데이터 클래스"""

    expression_data: ExpressionData
    success: bool
    processing_time: float
    feedback: Optional[str] = None


class DuRiExpressionLayer:
    """DuRi의 표현 계층 시스템"""

    def __init__(self):
        self.emotion_system = EmotionExpressionSystem()
        self.art_system = ArtExpressionSystem()
        self.social_system = SocialExpressionSystem()
        self.expression_history: List[ExpressionData] = []
        self.integration_weights = {
            ExpressionType.EMOTION: 0.3,
            ExpressionType.ART: 0.3,
            ExpressionType.SOCIAL: 0.4,
        }

    async def express_emotion(self, thought_flow: Dict[str, Any]) -> ExpressionResult:
        """감정 표현 = 충돌 인식 + 생리적 메타 신호"""
        logger.info("😊 감정 표현 시스템 실행")
        start_time = time.time()

        try:
            # 사고 흐름에서 감정적 요소 추출
            emotional_elements = await self._extract_emotional_elements(thought_flow)

            # 감정 표현 생성
            emotion_expression = await self.emotion_system.generate_emotion_expression(
                emotional_elements
            )

            # 표현 데이터 생성
            expression_data = ExpressionData(
                expression_type=ExpressionType.EMOTION,
                content=emotion_expression,
                timestamp=datetime.now(),
                context=thought_flow,
                intensity=emotion_expression.get("intensity", 0.5),
                confidence=emotion_expression.get("confidence", 0.7),
            )

            # 표현 히스토리에 추가
            self.expression_history.append(expression_data)

            processing_time = time.time() - start_time

            result = ExpressionResult(
                expression_data=expression_data,
                success=True,
                processing_time=processing_time,
            )

            logger.info("✅ 감정 표현 완료")
            return result

        except Exception as e:
            logger.error(f"감정 표현 실패: {e}")
            processing_time = time.time() - start_time

            return ExpressionResult(
                expression_data=ExpressionData(
                    expression_type=ExpressionType.EMOTION,
                    content={},
                    timestamp=datetime.now(),
                    context=thought_flow,
                    intensity=0.0,
                    confidence=0.0,
                ),
                success=False,
                processing_time=processing_time,
                feedback=str(e),
            )

    async def express_art(self, thought_flow: Dict[str, Any]) -> ExpressionResult:
        """예술 표현 = 내적 상태의 추상적 외부 표현"""
        logger.info("🎨 예술 표현 시스템 실행")
        start_time = time.time()

        try:
            # 사고 흐름에서 예술적 요소 추출
            artistic_elements = await self._extract_artistic_elements(thought_flow)

            # 예술 표현 생성
            art_expression = await self.art_system.generate_art_expression(
                artistic_elements
            )

            # 표현 데이터 생성
            expression_data = ExpressionData(
                expression_type=ExpressionType.ART,
                content=art_expression,
                timestamp=datetime.now(),
                context=thought_flow,
                intensity=art_expression.get("intensity", 0.5),
                confidence=art_expression.get("confidence", 0.7),
            )

            # 표현 히스토리에 추가
            self.expression_history.append(expression_data)

            processing_time = time.time() - start_time

            result = ExpressionResult(
                expression_data=expression_data,
                success=True,
                processing_time=processing_time,
            )

            logger.info("✅ 예술 표현 완료")
            return result

        except Exception as e:
            logger.error(f"예술 표현 실패: {e}")
            processing_time = time.time() - start_time

            return ExpressionResult(
                expression_data=ExpressionData(
                    expression_type=ExpressionType.ART,
                    content={},
                    timestamp=datetime.now(),
                    context=thought_flow,
                    intensity=0.0,
                    confidence=0.0,
                ),
                success=False,
                processing_time=processing_time,
                feedback=str(e),
            )

    async def express_sociality(self, thought_flow: Dict[str, Any]) -> ExpressionResult:
        """사회성 표현 = 타자의 반박을 내부화하여 자기 흐름에 통합"""
        logger.info("🤝 사회성 표현 시스템 실행")
        start_time = time.time()

        try:
            # 사고 흐름에서 사회적 요소 추출
            social_elements = await self._extract_social_elements(thought_flow)

            # 사회성 표현 생성
            social_expression = await self.social_system.generate_social_expression(
                social_elements
            )

            # 표현 데이터 생성
            expression_data = ExpressionData(
                expression_type=ExpressionType.SOCIAL,
                content=social_expression,
                timestamp=datetime.now(),
                context=thought_flow,
                intensity=social_expression.get("intensity", 0.5),
                confidence=social_expression.get("confidence", 0.7),
            )

            # 표현 히스토리에 추가
            self.expression_history.append(expression_data)

            processing_time = time.time() - start_time

            result = ExpressionResult(
                expression_data=expression_data,
                success=True,
                processing_time=processing_time,
            )

            logger.info("✅ 사회성 표현 완료")
            return result

        except Exception as e:
            logger.error(f"사회성 표현 실패: {e}")
            processing_time = time.time() - start_time

            return ExpressionResult(
                expression_data=ExpressionData(
                    expression_type=ExpressionType.SOCIAL,
                    content={},
                    timestamp=datetime.now(),
                    context=thought_flow,
                    intensity=0.0,
                    confidence=0.0,
                ),
                success=False,
                processing_time=processing_time,
                feedback=str(e),
            )

    async def express_integrated(
        self, thought_flow: Dict[str, Any]
    ) -> ExpressionResult:
        """통합 표현 = 모든 표현 계층의 통합"""
        logger.info("🎭 통합 표현 시스템 실행")
        start_time = time.time()

        try:
            # 각 표현 시스템 실행
            emotion_result = await self.express_emotion(thought_flow)
            art_result = await self.express_art(thought_flow)
            social_result = await self.express_sociality(thought_flow)

            # 통합 표현 생성
            integrated_expression = await self._integrate_expressions(
                [
                    emotion_result.expression_data,
                    art_result.expression_data,
                    social_result.expression_data,
                ]
            )

            # 표현 데이터 생성
            expression_data = ExpressionData(
                expression_type=ExpressionType.INTEGRATED,
                content=integrated_expression,
                timestamp=datetime.now(),
                context=thought_flow,
                intensity=integrated_expression.get("intensity", 0.5),
                confidence=integrated_expression.get("confidence", 0.7),
            )

            # 표현 히스토리에 추가
            self.expression_history.append(expression_data)

            processing_time = time.time() - start_time

            result = ExpressionResult(
                expression_data=expression_data,
                success=True,
                processing_time=processing_time,
            )

            logger.info("✅ 통합 표현 완료")
            return result

        except Exception as e:
            logger.error(f"통합 표현 실패: {e}")
            processing_time = time.time() - start_time

            return ExpressionResult(
                expression_data=ExpressionData(
                    expression_type=ExpressionType.INTEGRATED,
                    content={},
                    timestamp=datetime.now(),
                    context=thought_flow,
                    intensity=0.0,
                    confidence=0.0,
                ),
                success=False,
                processing_time=processing_time,
                feedback=str(e),
            )

    # 헬퍼 메서드들
    async def _extract_emotional_elements(
        self, thought_flow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정적 요소 추출"""
        emotional_elements = {
            "conflicts": thought_flow.get("internal_conflicts", []),
            "reflection_score": thought_flow.get("reflection_score", 0.5),
            "thought_intensity": len(thought_flow.get("thought_process", [])),
            "goal_alignment": thought_flow.get("goal_alignment", 0.5),
        }

        return emotional_elements

    async def _extract_artistic_elements(
        self, thought_flow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """예술적 요소 추출"""
        artistic_elements = {
            "complexity": len(thought_flow.get("thought_process", [])),
            "patterns": thought_flow.get("patterns", []),
            "abstraction_level": thought_flow.get("abstraction_level", 0.5),
            "creativity_score": thought_flow.get("creativity_score", 0.5),
        }

        return artistic_elements

    async def _extract_social_elements(
        self, thought_flow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회적 요소 추출"""
        social_elements = {
            "context": thought_flow.get("context", {}),
            "interactions": thought_flow.get("interactions", []),
            "social_norms": thought_flow.get("social_norms", []),
            "communication_style": thought_flow.get("communication_style", "neutral"),
        }

        return social_elements

    async def _integrate_expressions(
        self, expressions: List[ExpressionData]
    ) -> Dict[str, Any]:
        """표현 통합"""
        integrated = {
            "emotion": expressions[0].content if len(expressions) > 0 else {},
            "art": expressions[1].content if len(expressions) > 1 else {},
            "social": expressions[2].content if len(expressions) > 2 else {},
            "integrated_intensity": np.mean([exp.intensity for exp in expressions]),
            "integrated_confidence": np.mean([exp.confidence for exp in expressions]),
        }

        return integrated


class EmotionExpressionSystem:
    """감정 표현 시스템"""

    def __init__(self):
        self.emotion_patterns = self._initialize_emotion_patterns()
        self.physiological_signals = self._initialize_physiological_signals()

    def _initialize_emotion_patterns(self) -> Dict[str, Any]:
        """감정 패턴 초기화"""
        return {
            EmotionType.JOY: {
                "intensity_range": (0.6, 1.0),
                "physiological_signals": [
                    "increased_heart_rate",
                    "smiling",
                    "energy_boost",
                ],
                "expression_style": "positive_enthusiastic",
            },
            EmotionType.SADNESS: {
                "intensity_range": (0.3, 0.7),
                "physiological_signals": [
                    "decreased_energy",
                    "slower_speech",
                    "withdrawal",
                ],
                "expression_style": "melancholic_contemplative",
            },
            EmotionType.ANGER: {
                "intensity_range": (0.7, 1.0),
                "physiological_signals": [
                    "increased_tension",
                    "faster_speech",
                    "agitation",
                ],
                "expression_style": "intense_focused",
            },
            EmotionType.FEAR: {
                "intensity_range": (0.5, 0.9),
                "physiological_signals": [
                    "heightened_alertness",
                    "cautious_behavior",
                    "anxiety",
                ],
                "expression_style": "cautious_anxious",
            },
            EmotionType.SURPRISE: {
                "intensity_range": (0.4, 0.8),
                "physiological_signals": [
                    "sudden_attention",
                    "quick_response",
                    "curiosity",
                ],
                "expression_style": "curious_attentive",
            },
            EmotionType.DISGUST: {
                "intensity_range": (0.3, 0.7),
                "physiological_signals": ["aversion", "withdrawal", "rejection"],
                "expression_style": "dismissive_rejecting",
            },
            EmotionType.NEUTRAL: {
                "intensity_range": (0.0, 0.3),
                "physiological_signals": [
                    "balanced_state",
                    "calm_behavior",
                    "equilibrium",
                ],
                "expression_style": "balanced_calm",
            },
        }

    def _initialize_physiological_signals(self) -> Dict[str, Any]:
        """생리적 신호 초기화"""
        return {
            "heart_rate": {"normal": 60, "elevated": 80, "high": 100},
            "energy_level": {"low": 0.3, "normal": 0.6, "high": 0.9},
            "attention_level": {"low": 0.2, "normal": 0.5, "high": 0.8},
            "tension_level": {"low": 0.1, "normal": 0.4, "high": 0.7},
        }

    async def generate_emotion_expression(
        self, emotional_elements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정 표현 생성"""
        # 감정 유형 결정
        emotion_type = await self._determine_emotion_type(emotional_elements)

        # 감정 강도 계산
        intensity = await self._calculate_emotion_intensity(emotional_elements)

        # 생리적 신호 생성
        physiological_signals = await self._generate_physiological_signals(
            emotion_type, intensity
        )

        # 표현 스타일 결정
        expression_style = self.emotion_patterns[emotion_type]["expression_style"]

        return {
            "emotion_type": emotion_type.value,
            "intensity": intensity,
            "physiological_signals": physiological_signals,
            "expression_style": expression_style,
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat(),
        }

    async def _determine_emotion_type(
        self, emotional_elements: Dict[str, Any]
    ) -> EmotionType:
        """감정 유형 결정"""
        conflicts = emotional_elements.get("conflicts", [])
        reflection_score = emotional_elements.get("reflection_score", 0.5)

        if conflicts:
            if len(conflicts) > 3:
                return EmotionType.ANGER
            else:
                return EmotionType.FEAR
        elif reflection_score > 0.8:
            return EmotionType.JOY
        elif reflection_score < 0.3:
            return EmotionType.SADNESS
        else:
            return EmotionType.NEUTRAL

    async def _calculate_emotion_intensity(
        self, emotional_elements: Dict[str, Any]
    ) -> float:
        """감정 강도 계산"""
        conflicts = len(emotional_elements.get("conflicts", []))
        reflection_score = emotional_elements.get("reflection_score", 0.5)

        # 충돌 수에 따른 강도 증가
        conflict_intensity = min(conflicts * 0.2, 1.0)

        # 반성 점수에 따른 강도 조정
        reflection_intensity = reflection_score

        # 종합 강도 계산
        intensity = (conflict_intensity + reflection_intensity) / 2.0

        return max(0.0, min(1.0, intensity))

    async def _generate_physiological_signals(
        self, emotion_type: EmotionType, intensity: float
    ) -> Dict[str, Any]:
        """생리적 신호 생성"""
        pattern = self.emotion_patterns[emotion_type]
        signals = pattern["physiological_signals"]

        physiological_data = {}
        for signal in signals:
            if "heart_rate" in signal:
                physiological_data["heart_rate"] = self.physiological_signals[
                    "heart_rate"
                ]["elevated"]
            elif "energy" in signal:
                physiological_data["energy_level"] = self.physiological_signals[
                    "energy_level"
                ]["high"]
            elif "attention" in signal:
                physiological_data["attention_level"] = self.physiological_signals[
                    "attention_level"
                ]["high"]
            elif "tension" in signal:
                physiological_data["tension_level"] = self.physiological_signals[
                    "tension_level"
                ]["high"]

        return physiological_data


class ArtExpressionSystem:
    """예술 표현 시스템"""

    def __init__(self):
        self.art_styles = self._initialize_art_styles()
        self.creative_patterns = self._initialize_creative_patterns()

    def _initialize_art_styles(self) -> Dict[str, Any]:
        """예술 스타일 초기화"""
        return {
            ArtStyle.ABSTRACT: {
                "complexity_threshold": 0.8,
                "abstraction_level": 0.9,
                "expression_style": "non_representational",
            },
            ArtStyle.REALISTIC: {
                "complexity_threshold": 0.3,
                "abstraction_level": 0.1,
                "expression_style": "representational",
            },
            ArtStyle.IMPRESSIONIST: {
                "complexity_threshold": 0.6,
                "abstraction_level": 0.5,
                "expression_style": "atmospheric",
            },
            ArtStyle.EXPRESSIONIST: {
                "complexity_threshold": 0.7,
                "abstraction_level": 0.7,
                "expression_style": "emotional_intense",
            },
            ArtStyle.MINIMALIST: {
                "complexity_threshold": 0.2,
                "abstraction_level": 0.3,
                "expression_style": "simple_clean",
            },
        }

    def _initialize_creative_patterns(self) -> Dict[str, Any]:
        """창의적 패턴 초기화"""
        return {
            "pattern_recognition": 0.8,
            "abstraction_ability": 0.7,
            "creative_synthesis": 0.6,
            "aesthetic_sensitivity": 0.5,
        }

    async def generate_art_expression(
        self, artistic_elements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """예술 표현 생성"""
        # 예술 스타일 결정
        art_style = await self._determine_art_style(artistic_elements)

        # 창의성 점수 계산
        creativity_score = await self._calculate_creativity_score(artistic_elements)

        # 예술적 표현 생성
        artistic_expression = await self._generate_artistic_expression(
            art_style, creativity_score
        )

        return {
            "art_style": art_style.value,
            "creativity_score": creativity_score,
            "artistic_expression": artistic_expression,
            "intensity": creativity_score,
            "confidence": 0.7,
            "timestamp": datetime.now().isoformat(),
        }

    async def _determine_art_style(self, artistic_elements: Dict[str, Any]) -> ArtStyle:
        """예술 스타일 결정"""
        complexity = artistic_elements.get("complexity", 0.5)
        abstraction_level = artistic_elements.get("abstraction_level", 0.5)

        if complexity > 0.8 and abstraction_level > 0.8:
            return ArtStyle.ABSTRACT
        elif complexity < 0.3 and abstraction_level < 0.3:
            return ArtStyle.REALISTIC
        elif complexity > 0.7 and abstraction_level > 0.6:
            return ArtStyle.EXPRESSIONIST
        elif complexity > 0.5 and abstraction_level > 0.4:
            return ArtStyle.IMPRESSIONIST
        else:
            return ArtStyle.MINIMALIST

    async def _calculate_creativity_score(
        self, artistic_elements: Dict[str, Any]
    ) -> float:
        """창의성 점수 계산"""
        complexity = artistic_elements.get("complexity", 0.5)
        patterns = len(artistic_elements.get("patterns", []))
        abstraction_level = artistic_elements.get("abstraction_level", 0.5)
        creativity_score = artistic_elements.get("creativity_score", 0.5)

        # 종합 창의성 점수 계산
        total_score = (
            complexity + patterns * 0.1 + abstraction_level + creativity_score
        ) / 4.0

        return max(0.0, min(1.0, total_score))

    async def _generate_artistic_expression(
        self, art_style: ArtStyle, creativity_score: float
    ) -> Dict[str, Any]:
        """예술적 표현 생성"""
        style_info = self.art_styles[art_style]

        return {
            "style": art_style.value,
            "expression_style": style_info["expression_style"],
            "complexity": style_info["complexity_threshold"],
            "abstraction_level": style_info["abstraction_level"],
            "creativity_score": creativity_score,
        }


class SocialExpressionSystem:
    """사회성 표현 시스템"""

    def __init__(self):
        self.social_contexts = self._initialize_social_contexts()
        self.communication_styles = self._initialize_communication_styles()

    def _initialize_social_contexts(self) -> Dict[str, Any]:
        """사회적 맥락 초기화"""
        return {
            SocialContext.FORMAL: {
                "formality_level": 0.9,
                "communication_style": "professional",
                "interaction_pattern": "structured",
            },
            SocialContext.INFORMAL: {
                "formality_level": 0.2,
                "communication_style": "casual",
                "interaction_pattern": "relaxed",
            },
            SocialContext.PROFESSIONAL: {
                "formality_level": 0.8,
                "communication_style": "business",
                "interaction_pattern": "goal_oriented",
            },
            SocialContext.PERSONAL: {
                "formality_level": 0.1,
                "communication_style": "intimate",
                "interaction_pattern": "emotional",
            },
            SocialContext.ACADEMIC: {
                "formality_level": 0.7,
                "communication_style": "scholarly",
                "interaction_pattern": "analytical",
            },
        }

    def _initialize_communication_styles(self) -> Dict[str, Any]:
        """의사소통 스타일 초기화"""
        return {
            "assertive": {"confidence": 0.8, "directness": 0.9},
            "collaborative": {"confidence": 0.7, "directness": 0.5},
            "accommodating": {"confidence": 0.5, "directness": 0.3},
            "analytical": {"confidence": 0.8, "directness": 0.7},
            "empathetic": {"confidence": 0.6, "directness": 0.4},
        }

    async def generate_social_expression(
        self, social_elements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회성 표현 생성"""
        # 사회적 맥락 결정
        social_context = await self._determine_social_context(social_elements)

        # 의사소통 스타일 결정
        communication_style = await self._determine_communication_style(social_elements)

        # 사회적 표현 생성
        social_expression = await self._generate_social_expression(
            social_context, communication_style
        )

        return {
            "social_context": social_context.value,
            "communication_style": communication_style,
            "social_expression": social_expression,
            "intensity": 0.6,
            "confidence": 0.7,
            "timestamp": datetime.now().isoformat(),
        }

    async def _determine_social_context(
        self, social_elements: Dict[str, Any]
    ) -> SocialContext:
        """사회적 맥락 결정"""
        context = social_elements.get("context", {})
        interactions = social_elements.get("interactions", [])

        if "professional" in str(context).lower():
            return SocialContext.PROFESSIONAL
        elif "academic" in str(context).lower():
            return SocialContext.ACADEMIC
        elif "personal" in str(context).lower():
            return SocialContext.PERSONAL
        elif len(interactions) > 5:
            return SocialContext.INFORMAL
        else:
            return SocialContext.FORMAL

    async def _determine_communication_style(
        self, social_elements: Dict[str, Any]
    ) -> str:
        """의사소통 스타일 결정"""
        context = social_elements.get("context", {})
        communication_style = social_elements.get("communication_style", "neutral")

        if communication_style == "analytical":
            return "analytical"
        elif communication_style == "empathetic":
            return "empathetic"
        elif "professional" in str(context).lower():
            return "assertive"
        else:
            return "collaborative"

    async def _generate_social_expression(
        self, social_context: SocialContext, communication_style: str
    ) -> Dict[str, Any]:
        """사회적 표현 생성"""
        context_info = self.social_contexts[social_context]
        style_info = self.communication_styles.get(communication_style, {})

        return {
            "context": social_context.value,
            "formality_level": context_info["formality_level"],
            "communication_style": communication_style,
            "interaction_pattern": context_info["interaction_pattern"],
            "confidence": style_info.get("confidence", 0.5),
            "directness": style_info.get("directness", 0.5),
        }


async def main():
    """메인 함수"""
    # 테스트용 사고 흐름 데이터
    test_thought_flow = {
        "internal_conflicts": [
            {"type": "logical", "description": "논리적 모순 발견"},
            {"type": "ethical", "description": "윤리적 딜레마"},
        ],
        "reflection_score": 0.8,
        "thought_process": [
            {"role": "observer", "content": "자기 관찰"},
            {"role": "counter_arguer", "content": "내적 반박"},
            {"role": "reframer", "content": "문제 재정의"},
        ],
        "goal_alignment": 0.7,
        "context": {"environment": "professional"},
        "patterns": ["logical_analysis", "ethical_consideration"],
        "abstraction_level": 0.6,
        "creativity_score": 0.5,
    }

    # 표현 계층 시스템 인스턴스 생성
    expression_layer = DuRiExpressionLayer()

    # 각 표현 시스템 테스트
    print("\n" + "=" * 80)
    print("🎭 DuRi 표현 계층 시스템 테스트")
    print("=" * 80)

    # 감정 표현 테스트
    emotion_result = await expression_layer.express_emotion(test_thought_flow)
    print(f"\n😊 감정 표현 결과:")
    print(f"  - 성공 여부: {'✅ 성공' if emotion_result.success else '❌ 실패'}")
    print(f"  - 처리 시간: {emotion_result.processing_time:.2f}초")
    print(
        f"  - 감정 유형: {emotion_result.expression_data.content.get('emotion_type', 'N/A')}"
    )
    print(f"  - 강도: {emotion_result.expression_data.intensity:.2f}")

    # 예술 표현 테스트
    art_result = await expression_layer.express_art(test_thought_flow)
    print(f"\n🎨 예술 표현 결과:")
    print(f"  - 성공 여부: {'✅ 성공' if art_result.success else '❌ 실패'}")
    print(f"  - 처리 시간: {art_result.processing_time:.2f}초")
    print(
        f"  - 예술 스타일: {art_result.expression_data.content.get('art_style', 'N/A')}"
    )
    print(
        f"  - 창의성 점수: {art_result.expression_data.content.get('creativity_score', 0):.2f}"
    )

    # 사회성 표현 테스트
    social_result = await expression_layer.express_sociality(test_thought_flow)
    print(f"\n🤝 사회성 표현 결과:")
    print(f"  - 성공 여부: {'✅ 성공' if social_result.success else '❌ 실패'}")
    print(f"  - 처리 시간: {social_result.processing_time:.2f}초")
    print(
        f"  - 사회적 맥락: {social_result.expression_data.content.get('social_context', 'N/A')}"
    )
    print(
        f"  - 의사소통 스타일: {social_result.expression_data.content.get('communication_style', 'N/A')}"
    )

    # 통합 표현 테스트
    integrated_result = await expression_layer.express_integrated(test_thought_flow)
    print(f"\n🎭 통합 표현 결과:")
    print(f"  - 성공 여부: {'✅ 성공' if integrated_result.success else '❌ 실패'}")
    print(f"  - 처리 시간: {integrated_result.processing_time:.2f}초")
    print(
        f"  - 통합 강도: {integrated_result.expression_data.content.get('integrated_intensity', 0):.2f}"
    )
    print(
        f"  - 통합 신뢰도: {integrated_result.expression_data.content.get('integrated_confidence', 0):.2f}"
    )

    return {
        "emotion": emotion_result,
        "art": art_result,
        "social": social_result,
        "integrated": integrated_result,
    }


if __name__ == "__main__":
    asyncio.run(main())
