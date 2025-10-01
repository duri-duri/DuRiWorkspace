#!/usr/bin/env python3
"""
감정 가중치 시스템 - Phase 6.2.3
DuRi Phase 6.2.3 - 감정-판단 보정 가중치 모델

기능:
1. 감정이 판단과 행동에 미치는 영향 모델링
2. 감정-판단 보정 가중치 시스템
3. 감정 상태에 따른 의사결정 조정
4. 감정 기반 동기 시스템
"""

import asyncio
import json
import logging
import random
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EmotionType(Enum):
    """감정 유형"""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    EXCITEMENT = "excitement"
    ANXIETY = "anxiety"
    CONTENTMENT = "contentment"


class EmotionIntensity(Enum):
    """감정 강도"""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DecisionBias(Enum):
    """의사결정 편향"""

    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    RISK_AVERSE = "risk_averse"
    RISK_SEEKING = "risk_seeking"
    IMPULSIVE = "impulsive"
    CAUTIOUS = "cautious"
    NEUTRAL = "neutral"


@dataclass
class EmotionState:
    """감정 상태"""

    primary_emotion: EmotionType
    intensity: float  # 0.0 - 1.0
    secondary_emotions: List[EmotionType]
    emotional_stability: float  # 0.0 - 1.0
    decision_bias: DecisionBias
    created_at: datetime
    duration: float = 0.0  # 감정 지속 시간 (초)

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class EmotionWeight:
    """감정 가중치"""

    emotion_type: EmotionType
    judgment_weight: float  # 판단에 미치는 영향
    action_weight: float  # 행동에 미치는 영향
    confidence_modifier: float  # 신뢰도 수정자
    risk_tolerance_modifier: float  # 위험 감수도 수정자
    decision_speed_modifier: float  # 의사결정 속도 수정자


@dataclass
class EmotionalDecision:
    """감정적 의사결정"""

    original_decision: str
    emotional_adjustment: str
    final_decision: str
    emotion_influence: float
    confidence_change: float
    reasoning: str
    created_at: datetime


class EmotionWeightSystem:
    """감정 가중치 시스템 - Phase 6.2.3"""

    def __init__(self):
        self.current_emotion_state = EmotionState(
            primary_emotion=EmotionType.NEUTRAL,
            intensity=0.5,
            secondary_emotions=[],
            emotional_stability=0.7,
            decision_bias=DecisionBias.NEUTRAL,
            created_at=datetime.now(),
        )

        # 감정 가중치 매핑 (Phase 6.2.3 핵심)
        self.emotion_weights = {
            EmotionType.JOY: EmotionWeight(
                emotion_type=EmotionType.JOY,
                judgment_weight=0.1,  # 긍정적 영향
                action_weight=0.15,  # 행동 촉진
                confidence_modifier=0.05,  # 신뢰도 증가
                risk_tolerance_modifier=0.1,  # 위험 감수도 증가
                decision_speed_modifier=0.1,  # 의사결정 속도 증가
            ),
            EmotionType.SADNESS: EmotionWeight(
                emotion_type=EmotionType.SADNESS,
                judgment_weight=-0.1,  # 부정적 영향
                action_weight=-0.1,  # 행동 억제
                confidence_modifier=-0.05,  # 신뢰도 감소
                risk_tolerance_modifier=-0.1,  # 위험 감수도 감소
                decision_speed_modifier=-0.05,  # 의사결정 속도 감소
            ),
            EmotionType.ANGER: EmotionWeight(
                emotion_type=EmotionType.ANGER,
                judgment_weight=-0.15,  # 강한 부정적 영향
                action_weight=0.2,  # 행동 촉진 (공격적)
                confidence_modifier=0.1,  # 신뢰도 증가 (과신)
                risk_tolerance_modifier=0.2,  # 위험 감수도 증가
                decision_speed_modifier=0.15,  # 의사결정 속도 증가
            ),
            EmotionType.FEAR: EmotionWeight(
                emotion_type=EmotionType.FEAR,
                judgment_weight=-0.1,  # 부정적 영향
                action_weight=-0.15,  # 행동 억제
                confidence_modifier=-0.1,  # 신뢰도 감소
                risk_tolerance_modifier=-0.2,  # 위험 감수도 감소
                decision_speed_modifier=-0.1,  # 의사결정 속도 감소
            ),
            EmotionType.EXCITEMENT: EmotionWeight(
                emotion_type=EmotionType.EXCITEMENT,
                judgment_weight=0.05,  # 약간의 긍정적 영향
                action_weight=0.1,  # 행동 촉진
                confidence_modifier=0.05,  # 신뢰도 증가
                risk_tolerance_modifier=0.1,  # 위험 감수도 증가
                decision_speed_modifier=0.1,  # 의사결정 속도 증가
            ),
            EmotionType.ANXIETY: EmotionWeight(
                emotion_type=EmotionType.ANXIETY,
                judgment_weight=-0.05,  # 약간의 부정적 영향
                action_weight=-0.05,  # 행동 억제
                confidence_modifier=-0.05,  # 신뢰도 감소
                risk_tolerance_modifier=-0.1,  # 위험 감수도 감소
                decision_speed_modifier=-0.05,  # 의사결정 속도 감소
            ),
            EmotionType.CONTENTMENT: EmotionWeight(
                emotion_type=EmotionType.CONTENTMENT,
                judgment_weight=0.05,  # 약간의 긍정적 영향
                action_weight=0.05,  # 행동 촉진
                confidence_modifier=0.05,  # 신뢰도 증가
                risk_tolerance_modifier=0.05,  # 위험 감수도 증가
                decision_speed_modifier=0.05,  # 의사결정 속도 증가
            ),
            EmotionType.NEUTRAL: EmotionWeight(
                emotion_type=EmotionType.NEUTRAL,
                judgment_weight=0.0,  # 영향 없음
                action_weight=0.0,  # 영향 없음
                confidence_modifier=0.0,  # 영향 없음
                risk_tolerance_modifier=0.0,  # 영향 없음
                decision_speed_modifier=0.0,  # 영향 없음
            ),
        }

        # 감정 히스토리
        self.emotion_history: List[EmotionState] = []
        self.decision_history: List[EmotionalDecision] = []

        # 성능 메트릭
        self.performance_metrics = {
            "total_decisions": 0,
            "emotion_adjusted_decisions": 0,
            "average_emotion_influence": 0.0,
            "decision_bias_changes": 0,
            "emotional_stability_score": 0.7,
        }

        logger.info("🧠 감정 가중치 시스템 초기화 완료 (Phase 6.2.3)")

    async def update_emotion_state(
        self,
        emotion_type: EmotionType,
        intensity: float,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """감정 상태 업데이트"""
        try:
            # 이전 감정 상태를 히스토리에 저장
            if self.current_emotion_state.primary_emotion != EmotionType.NEUTRAL:
                self.emotion_history.append(self.current_emotion_state)

            # 새로운 감정 상태 생성
            secondary_emotions = self._determine_secondary_emotions(
                emotion_type, context
            )
            decision_bias = self._determine_decision_bias(emotion_type, intensity)
            emotional_stability = self._calculate_emotional_stability()

            self.current_emotion_state = EmotionState(
                primary_emotion=emotion_type,
                intensity=intensity,
                secondary_emotions=secondary_emotions,
                emotional_stability=emotional_stability,
                decision_bias=decision_bias,
                created_at=datetime.now(),
            )

            logger.info(
                f"😊 감정 상태 업데이트: {emotion_type.value} (강도: {intensity:.2f})"
            )

            return {
                "success": True,
                "emotion_state": asdict(self.current_emotion_state),
                "decision_bias": decision_bias.value,
                "emotional_stability": emotional_stability,
            }

        except Exception as e:
            logger.error(f"감정 상태 업데이트 실패: {e}")
            return {"success": False, "error": str(e)}

    def _determine_secondary_emotions(
        self, primary_emotion: EmotionType, context: Dict[str, Any]
    ) -> List[EmotionType]:
        """보조 감정 결정"""
        secondary_emotions = []

        if primary_emotion == EmotionType.JOY:
            if context and context.get("achievement", False):
                secondary_emotions.append(EmotionType.EXCITEMENT)
        elif primary_emotion == EmotionType.ANGER:
            if context and context.get("frustration", False):
                secondary_emotions.append(EmotionType.FEAR)
        elif primary_emotion == EmotionType.FEAR:
            if context and context.get("uncertainty", False):
                secondary_emotions.append(EmotionType.ANXIETY)

        return secondary_emotions

    def _determine_decision_bias(
        self, emotion_type: EmotionType, intensity: float
    ) -> DecisionBias:
        """의사결정 편향 결정"""
        if emotion_type == EmotionType.JOY:
            return DecisionBias.OPTIMISTIC if intensity > 0.7 else DecisionBias.NEUTRAL
        elif emotion_type == EmotionType.SADNESS:
            return (
                DecisionBias.PESSIMISTIC if intensity > 0.7 else DecisionBias.CAUTIOUS
            )
        elif emotion_type == EmotionType.ANGER:
            return (
                DecisionBias.IMPULSIVE if intensity > 0.7 else DecisionBias.RISK_SEEKING
            )
        elif emotion_type == EmotionType.FEAR:
            return (
                DecisionBias.RISK_AVERSE if intensity > 0.7 else DecisionBias.CAUTIOUS
            )
        elif emotion_type == EmotionType.EXCITEMENT:
            return DecisionBias.OPTIMISTIC
        elif emotion_type == EmotionType.ANXIETY:
            return DecisionBias.RISK_AVERSE
        else:
            return DecisionBias.NEUTRAL

    def _calculate_emotional_stability(self) -> float:
        """감정 안정성 계산"""
        if len(self.emotion_history) < 2:
            return 0.7  # 기본값

        # 최근 감정 변화 분석
        recent_emotions = self.emotion_history[-5:]  # 최근 5개
        emotion_changes = 0

        for i in range(1, len(recent_emotions)):
            if (
                recent_emotions[i].primary_emotion
                != recent_emotions[i - 1].primary_emotion
            ):
                emotion_changes += 1

        # 안정성 점수 계산 (변화가 적을수록 안정적)
        stability_score = max(0.0, 1.0 - (emotion_changes / len(recent_emotions)))
        return stability_score

    async def apply_emotion_to_judgment(
        self, original_judgment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """판단에 감정 가중치 적용"""
        try:
            self.performance_metrics["total_decisions"] += 1

            # 현재 감정 상태의 가중치 가져오기
            emotion_weight = self.emotion_weights.get(
                self.current_emotion_state.primary_emotion,
                self.emotion_weights[EmotionType.NEUTRAL],
            )

            # 원본 판단 정보
            original_decision = original_judgment.get("decision", "")
            original_confidence = original_judgment.get("confidence", 0.5)
            original_reasoning = original_judgment.get("reasoning", "")

            # 감정 영향 계산
            emotion_influence = self._calculate_emotion_influence(emotion_weight)

            # 판단 조정
            adjusted_decision = self._adjust_decision(original_decision, emotion_weight)
            adjusted_confidence = self._adjust_confidence(
                original_confidence, emotion_weight
            )
            adjusted_reasoning = self._adjust_reasoning(
                original_reasoning, emotion_weight
            )

            # 감정적 의사결정 기록
            emotional_decision = EmotionalDecision(
                original_decision=original_decision,
                emotional_adjustment=adjusted_decision,
                final_decision=adjusted_decision,
                emotion_influence=emotion_influence,
                confidence_change=adjusted_confidence - original_confidence,
                reasoning=adjusted_reasoning,
                created_at=datetime.now(),
            )

            self.decision_history.append(emotional_decision)

            # 성능 메트릭 업데이트
            self.performance_metrics["emotion_adjusted_decisions"] += 1
            self.performance_metrics["average_emotion_influence"] = sum(
                d.emotion_influence for d in self.decision_history
            ) / len(self.decision_history)

            logger.info(
                f"🧠 감정 가중치 적용: {self.current_emotion_state.primary_emotion.value} "
                f"(영향: {emotion_influence:.3f})"
            )

            return {
                "success": True,
                "original_judgment": original_judgment,
                "emotion_adjusted_judgment": {
                    "decision": adjusted_decision,
                    "confidence": adjusted_confidence,
                    "reasoning": adjusted_reasoning,
                    "emotion_influence": emotion_influence,
                    "decision_bias": self.current_emotion_state.decision_bias.value,
                },
                "emotion_state": asdict(self.current_emotion_state),
            }

        except Exception as e:
            logger.error(f"감정 가중치 적용 실패: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_emotion_influence(self, emotion_weight: EmotionWeight) -> float:
        """감정 영향 계산"""
        # 기본 감정 영향
        base_influence = emotion_weight.judgment_weight

        # 강도에 따른 조정
        intensity_factor = self.current_emotion_state.intensity

        # 안정성에 따른 조정
        stability_factor = self.current_emotion_state.emotional_stability

        # 최종 영향 계산
        total_influence = base_influence * intensity_factor * stability_factor

        return max(-0.3, min(0.3, total_influence))  # -30% ~ +30% 범위 제한

    def _adjust_decision(
        self, original_decision: str, emotion_weight: EmotionWeight
    ) -> str:
        """의사결정 조정"""
        # 감정에 따른 의사결정 조정 로직
        if emotion_weight.emotion_type == EmotionType.JOY:
            if "wait" in original_decision.lower():
                return "proceed"  # 기다리기 → 진행
            elif "reject" in original_decision.lower():
                return "consider"  # 거부 → 고려
        elif emotion_weight.emotion_type == EmotionType.ANGER:
            if "wait" in original_decision.lower():
                return "act_now"  # 기다리기 → 즉시 행동
            elif "consider" in original_decision.lower():
                return "decide"  # 고려 → 결정
        elif emotion_weight.emotion_type == EmotionType.FEAR:
            if "proceed" in original_decision.lower():
                return "wait"  # 진행 → 기다리기
            elif "act_now" in original_decision.lower():
                return "consider"  # 즉시 행동 → 고려

        return original_decision

    def _adjust_confidence(
        self, original_confidence: float, emotion_weight: EmotionWeight
    ) -> float:
        """신뢰도 조정"""
        confidence_modifier = emotion_weight.confidence_modifier
        intensity_factor = self.current_emotion_state.intensity

        adjusted_confidence = original_confidence + (
            confidence_modifier * intensity_factor
        )
        return max(0.1, min(1.0, adjusted_confidence))

    def _adjust_reasoning(
        self, original_reasoning: str, emotion_weight: EmotionWeight
    ) -> str:
        """추론 조정"""
        emotion_name = emotion_weight.emotion_type.value

        if emotion_weight.emotion_type == EmotionType.JOY:
            return f"{original_reasoning} (긍정적 감정 상태에서 판단)"
        elif emotion_weight.emotion_type == EmotionType.ANGER:
            return f"{original_reasoning} (분노 상태에서 판단 - 신중히 검토 필요)"
        elif emotion_weight.emotion_type == EmotionType.FEAR:
            return f"{original_reasoning} (두려움 상태에서 판단 - 보수적 접근)"
        elif emotion_weight.emotion_type == EmotionType.SADNESS:
            return f"{original_reasoning} (슬픔 상태에서 판단 - 객관성 유지 필요)"
        else:
            return f"{original_reasoning} (감정 상태: {emotion_name})"

    async def apply_emotion_to_action(
        self, original_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """행동에 감정 가중치 적용"""
        try:
            emotion_weight = self.emotion_weights.get(
                self.current_emotion_state.primary_emotion,
                self.emotion_weights[EmotionType.NEUTRAL],
            )

            # 원본 행동 정보
            original_action_type = original_action.get("action_type", "")
            original_speed = original_action.get("speed", "normal")
            original_aggressiveness = original_action.get("aggressiveness", "normal")

            # 행동 조정
            adjusted_speed = self._adjust_action_speed(original_speed, emotion_weight)
            adjusted_aggressiveness = self._adjust_aggressiveness(
                original_aggressiveness, emotion_weight
            )

            return {
                "success": True,
                "original_action": original_action,
                "emotion_adjusted_action": {
                    "action_type": original_action_type,
                    "speed": adjusted_speed,
                    "aggressiveness": adjusted_aggressiveness,
                    "emotion_influence": emotion_weight.action_weight,
                    "decision_bias": self.current_emotion_state.decision_bias.value,
                },
            }

        except Exception as e:
            logger.error(f"행동 감정 가중치 적용 실패: {e}")
            return {"success": False, "error": str(e)}

    def _adjust_action_speed(
        self, original_speed: str, emotion_weight: EmotionWeight
    ) -> str:
        """행동 속도 조정"""
        speed_modifier = emotion_weight.decision_speed_modifier

        if speed_modifier > 0.05:  # 빠른 의사결정
            if original_speed == "slow":
                return "normal"
            elif original_speed == "normal":
                return "fast"
        elif speed_modifier < -0.05:  # 느린 의사결정
            if original_speed == "fast":
                return "normal"
            elif original_speed == "normal":
                return "slow"

        return original_speed

    def _adjust_aggressiveness(
        self, original_aggressiveness: str, emotion_weight: EmotionWeight
    ) -> str:
        """공격성 조정"""
        if emotion_weight.emotion_type == EmotionType.ANGER:
            if original_aggressiveness == "passive":
                return "normal"
            elif original_aggressiveness == "normal":
                return "aggressive"
        elif emotion_weight.emotion_type == EmotionType.FEAR:
            if original_aggressiveness == "aggressive":
                return "normal"
            elif original_aggressiveness == "normal":
                return "passive"

        return original_aggressiveness

    async def get_emotion_analysis(self) -> Dict[str, Any]:
        """감정 분석 리포트"""
        return {
            "current_emotion": asdict(self.current_emotion_state),
            "emotion_history_count": len(self.emotion_history),
            "decision_history_count": len(self.decision_history),
            "performance_metrics": self.performance_metrics,
            "emotional_stability": self.current_emotion_state.emotional_stability,
            "decision_bias": self.current_emotion_state.decision_bias.value,
            "recent_emotions": [
                {
                    "emotion": e.primary_emotion.value,
                    "intensity": e.intensity,
                    "duration": e.duration,
                    "created_at": e.created_at.isoformat(),
                }
                for e in self.emotion_history[-5:]  # 최근 5개
            ],
        }

    async def integrate_with_system(
        self, system_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 시스템과 연동"""
        # 시스템 컨텍스트에서 감정 정보 추출
        if "emotion" in system_context:
            emotion_data = system_context["emotion"]
            emotion_type = EmotionType(emotion_data.get("type", "neutral"))
            intensity = emotion_data.get("intensity", 0.5)

            await self.update_emotion_state(emotion_type, intensity, emotion_data)

        # 판단에 감정 가중치 적용
        if "judgment_request" in system_context:
            judgment_result = await self.apply_emotion_to_judgment(
                system_context["judgment_request"]
            )
            return {
                "emotion_system_result": judgment_result,
                "emotion_state": asdict(self.current_emotion_state),
                "performance_metrics": self.performance_metrics,
            }

        return {
            "emotion_state": asdict(self.current_emotion_state),
            "performance_metrics": self.performance_metrics,
        }

    async def get_emotion_weights(self) -> Dict[str, float]:
        """감정 가중치 반환"""
        try:
            # 현재 감정 상태에 따른 가중치 계산
            current_emotion = self.current_emotion_state.primary_emotion
            intensity = self.current_emotion_state.intensity

            # 기본 가중치 설정
            weights = {
                "joy": 0.1,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.1,
                "disgust": 0.1,
                "neutral": 0.2,
                "excitement": 0.1,
                "anxiety": 0.1,
                "contentment": 0.1,
            }

            # 현재 감정에 따른 가중치 조정
            emotion_key = current_emotion.value
            if emotion_key in weights:
                weights[emotion_key] = min(0.5, weights[emotion_key] + intensity * 0.3)

            return weights

        except Exception as e:
            logger.error(f"감정 가중치 반환 실패: {str(e)}")
            return {
                "neutral": 0.2,
                "joy": 0.1,
                "sadness": 0.1,
                "anger": 0.1,
                "fear": 0.1,
                "surprise": 0.1,
                "disgust": 0.1,
                "excitement": 0.1,
                "anxiety": 0.1,
                "contentment": 0.1,
            }

    async def analyze_emotion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """감정 분석 - 고급 AI 통합 시스템용 인터페이스"""
        try:
            # 컨텍스트에서 감정 정보 추출
            emotion_info = self._extract_emotion_from_context(context)

            # 감정 상태 업데이트
            await self.update_emotion_state(
                emotion_info["emotion_type"], emotion_info["intensity"], context
            )

            # 감정 분석 결과 생성
            emotion_analysis = await self.get_emotion_analysis()

            return {
                "emotion_vector": {
                    "primary_emotion": self.current_emotion_state.primary_emotion.value,
                    "intensity": self.current_emotion_state.intensity,
                    "secondary_emotions": [
                        e.value for e in self.current_emotion_state.secondary_emotions
                    ],
                    "decision_bias": self.current_emotion_state.decision_bias.value,
                    "emotional_stability": self.current_emotion_state.emotional_stability,
                },
                "emotion_analysis": emotion_analysis,
                "current_emotion_state": asdict(self.current_emotion_state),
            }
        except Exception as e:
            logger.error(f"감정 분석 중 오류: {e}")
            return {
                "emotion_vector": {
                    "primary_emotion": "neutral",
                    "intensity": 0.5,
                    "secondary_emotions": [],
                    "decision_bias": "neutral",
                    "emotional_stability": 0.7,
                },
                "emotion_analysis": {},
                "current_emotion_state": asdict(self.current_emotion_state),
            }

    def _extract_emotion_from_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트에서 감정 정보 추출"""
        # 기본 감정 정보
        emotion_info = {"emotion_type": EmotionType.NEUTRAL, "intensity": 0.5}

        # 컨텍스트 키워드 기반 감정 추출
        context_text = str(context).lower()

        # 긍정적 감정 키워드
        positive_keywords = [
            "success",
            "achievement",
            "opportunity",
            "growth",
            "improvement",
            "innovation",
        ]
        if any(keyword in context_text for keyword in positive_keywords):
            emotion_info["emotion_type"] = EmotionType.JOY
            emotion_info["intensity"] = 0.7

        # 부정적 감정 키워드
        negative_keywords = [
            "problem",
            "risk",
            "failure",
            "threat",
            "conflict",
            "difficulty",
        ]
        if any(keyword in context_text for keyword in negative_keywords):
            emotion_info["emotion_type"] = EmotionType.ANXIETY
            emotion_info["intensity"] = 0.6

        # 긴급한 상황
        urgent_keywords = ["urgent", "critical", "emergency", "deadline", "pressure"]
        if any(keyword in context_text for keyword in urgent_keywords):
            emotion_info["emotion_type"] = EmotionType.FEAR
            emotion_info["intensity"] = 0.8

        # 창의적 상황
        creative_keywords = [
            "creative",
            "innovation",
            "new",
            "breakthrough",
            "invention",
        ]
        if any(keyword in context_text for keyword in creative_keywords):
            emotion_info["emotion_type"] = EmotionType.EXCITEMENT
            emotion_info["intensity"] = 0.6

        return emotion_info


# 테스트 함수
async def test_emotion_weight_system():
    """감정 가중치 시스템 테스트"""
    logger.info("🧪 감정 가중치 시스템 테스트 시작")

    emotion_system = EmotionWeightSystem()

    # 감정 상태 업데이트 테스트
    logger.info("😊 감정 상태 업데이트 테스트")
    emotions_to_test = [
        (EmotionType.JOY, 0.8),
        (EmotionType.ANGER, 0.7),
        (EmotionType.FEAR, 0.6),
        (EmotionType.SADNESS, 0.5),
        (EmotionType.EXCITEMENT, 0.9),
    ]

    for emotion_type, intensity in emotions_to_test:
        result = await emotion_system.update_emotion_state(emotion_type, intensity)
        logger.info(f"   감정 업데이트: {emotion_type.value} (강도: {intensity})")

    # 판단에 감정 가중치 적용 테스트
    logger.info("🧠 판단 감정 가중치 테스트")
    test_judgments = [
        {"decision": "wait", "confidence": 0.7, "reasoning": "상황을 더 관찰해야 함"},
        {
            "decision": "proceed",
            "confidence": 0.8,
            "reasoning": "이미 충분한 정보가 있음",
        },
        {"decision": "reject", "confidence": 0.6, "reasoning": "위험도가 너무 높음"},
    ]

    for judgment in test_judgments:
        result = await emotion_system.apply_emotion_to_judgment(judgment)
        if result.get("success"):
            adjusted = result["emotion_adjusted_judgment"]
            logger.info(
                f"   원본: {judgment['decision']} → 조정: {adjusted['decision']}"
            )
            logger.info(
                f"   신뢰도: {judgment['confidence']:.2f} → {adjusted['confidence']:.2f}"
            )

    # 감정 분석 리포트
    analysis = await emotion_system.get_emotion_analysis()
    logger.info(f"📊 감정 분석:")
    logger.info(f"   현재 감정: {analysis['current_emotion']['primary_emotion']}")
    logger.info(f"   감정 안정성: {analysis['emotional_stability']:.2f}")
    logger.info(f"   의사결정 편향: {analysis['decision_bias']}")
    logger.info(
        f"   평균 감정 영향: {analysis['performance_metrics']['average_emotion_influence']:.3f}"
    )

    return analysis


if __name__ == "__main__":
    asyncio.run(test_emotion_weight_system())
