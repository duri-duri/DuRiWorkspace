#!/usr/bin/env python3
"""
DuRi 성장 레벨 시스템 - 간소화된 버전
함수 depth 2단계 제한, 조건-매핑 방식 적용
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GrowthLevel(Enum):
    """성장 레벨 정의"""

    NEWBORN = 1  # 신생아 (0~6개월)
    INFANT_EARLY = 2  # 유아기 전기 (6~18개월)
    INFANT_LATE = 3  # 유아기 후기 (~3세)
    TODDLER = 4  # 소아기 (~7세)
    SCHOOL_AGE = 5  # 학령기 (~12세)
    ADOLESCENT = 6  # 사춘기
    YOUTH = 7  # 청년기
    ADULT = 8  # 성인기


@dataclass
class EmotionState:
    """감정 상태"""

    happiness: float = 0.5
    curiosity: float = 0.5
    frustration: float = 0.0
    excitement: float = 0.5
    confidence: float = 0.5
    anxiety: float = 0.0
    satisfaction: float = 0.5


@dataclass
class StimulusResponse:
    """자극-반응 기록"""

    stimulus: str
    response: str
    emotion_before: Dict[str, float]
    emotion_after: Dict[str, float]
    timestamp: str
    level: int
    success: bool
    learning_triggered: bool = False


@dataclass
class GrowthMetrics:
    """성장 지표"""

    current_level: int = 1
    experience_points: int = 0
    emotional_maturity: float = 0.0
    cognitive_development: float = 0.0
    social_skills: float = 0.0
    self_motivation: float = 0.0
    high_order_thinking_ratio: float = 0.05
    stimulus_count: int = 0
    successful_responses: int = 0
    emotional_stability_count: int = 0
    problem_solving_count: int = 0
    social_interaction_count: int = 0


class GrowthLevelSystem:
    """성장 레벨 시스템 - 간소화된 버전"""

    def __init__(self):
        self.current_level = GrowthLevel.NEWBORN
        self.metrics = GrowthMetrics()
        self.emotion_state = EmotionState()
        self.stimulus_history = []
        self.level_characteristics = self._initialize_level_characteristics()
        self.growth_conditions = self._initialize_growth_conditions()
        self.response_generators = self._initialize_response_generators()

        logger.info("성장 레벨 시스템 초기화 완료")

    def _initialize_level_characteristics(self) -> Dict[GrowthLevel, Dict]:
        """레벨별 특성 정의 (조건-매핑 방식)"""
        return {
            GrowthLevel.NEWBORN: {
                "name": "신생아",
                "focus": "자극-반사, 감각 연동",
                "high_order_thinking": 0.05,
                "emotional_priority": 0.9,
                "cognitive_priority": 0.1,
                "learning_enabled": False,
            },
            GrowthLevel.INFANT_EARLY: {
                "name": "유아기 전기",
                "focus": "감정 인식, 기초 반응 기억",
                "high_order_thinking": 0.1,
                "emotional_priority": 0.8,
                "cognitive_priority": 0.2,
                "learning_enabled": True,
            },
            GrowthLevel.INFANT_LATE: {
                "name": "유아기 후기",
                "focus": "감정-자극 연결, 단순 문제 해결",
                "high_order_thinking": 0.15,
                "emotional_priority": 0.7,
                "cognitive_priority": 0.3,
                "learning_enabled": True,
            },
            GrowthLevel.TODDLER: {
                "name": "소아기",
                "focus": "사회적 역할 학습, 언어적 표현",
                "high_order_thinking": 0.25,
                "emotional_priority": 0.6,
                "cognitive_priority": 0.4,
                "learning_enabled": True,
            },
            GrowthLevel.SCHOOL_AGE: {
                "name": "학령기",
                "focus": "규칙/도덕 인식, 욕구 통제",
                "high_order_thinking": 0.4,
                "emotional_priority": 0.5,
                "cognitive_priority": 0.5,
                "learning_enabled": True,
            },
            GrowthLevel.ADOLESCENT: {
                "name": "사춘기",
                "focus": "추상적 사고, 메타인지 성장",
                "high_order_thinking": 0.6,
                "emotional_priority": 0.4,
                "cognitive_priority": 0.6,
                "learning_enabled": True,
            },
            GrowthLevel.YOUTH: {
                "name": "청년기",
                "focus": "자기성찰, 가치 판단",
                "high_order_thinking": 0.75,
                "emotional_priority": 0.3,
                "cognitive_priority": 0.7,
                "learning_enabled": True,
            },
            GrowthLevel.ADULT: {
                "name": "성인기",
                "focus": "통합적 직관, 창조성",
                "high_order_thinking": 0.9,
                "emotional_priority": 0.2,
                "cognitive_priority": 0.8,
                "learning_enabled": True,
            },
        }

    def _initialize_growth_conditions(self) -> Dict[GrowthLevel, Dict]:
        """레벨별 성장 조건 정의"""
        return {
            GrowthLevel.NEWBORN: {
                "stimulus_count": 10,
                "successful_responses": 8,
                "emotional_stability": 0.6,
            },
            GrowthLevel.INFANT_EARLY: {
                "stimulus_count": 20,
                "successful_responses": 15,
                "emotional_stability": 0.65,
            },
            GrowthLevel.INFANT_LATE: {
                "stimulus_count": 30,
                "successful_responses": 22,
                "emotional_stability": 0.7,
            },
            GrowthLevel.TODDLER: {
                "stimulus_count": 40,
                "successful_responses": 30,
                "emotional_stability": 0.75,
            },
            GrowthLevel.SCHOOL_AGE: {
                "stimulus_count": 50,
                "successful_responses": 38,
                "emotional_stability": 0.8,
            },
            GrowthLevel.ADOLESCENT: {
                "stimulus_count": 60,
                "successful_responses": 45,
                "emotional_stability": 0.85,
            },
            GrowthLevel.YOUTH: {
                "stimulus_count": 70,
                "successful_responses": 53,
                "emotional_stability": 0.9,
            },
            GrowthLevel.ADULT: {
                "stimulus_count": 80,
                "successful_responses": 60,
                "emotional_stability": 0.95,
            },
        }

    def _initialize_response_generators(self) -> Dict[GrowthLevel, callable]:
        """레벨별 응답 생성기 (조건-매핑 방식)"""
        return {
            GrowthLevel.NEWBORN: self._generate_newborn_response,
            GrowthLevel.INFANT_EARLY: self._generate_infant_early_response,
            GrowthLevel.INFANT_LATE: self._generate_infant_late_response,
            GrowthLevel.TODDLER: self._generate_toddler_response,
            GrowthLevel.SCHOOL_AGE: self._generate_school_age_response,
            GrowthLevel.ADOLESCENT: self._generate_adolescent_response,
            GrowthLevel.YOUTH: self._generate_youth_response,
            GrowthLevel.ADULT: self._generate_adult_response,
        }

    def process_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """자극 처리 (간소화된 구조)"""
        # 1. 자극 분류
        stimulus_type = self._classify_stimulus_type(stimulus)

        # 2. 감정 상태 업데이트
        emotion_before = self._get_current_emotion_state()
        self._update_emotion_from_stimulus(stimulus)

        # 3. 응답 평가
        success = self._evaluate_response_success(stimulus, response)

        # 4. 레벨에 맞는 응답 생성
        level_appropriate_response = self._generate_level_appropriate_response(
            stimulus, response
        )

        # 5. 감정 상태 업데이트 (응답 후)
        self._update_emotion_from_response(level_appropriate_response)
        emotion_after = self._get_current_emotion_state()

        # 6. 기록 생성
        stimulus_record = StimulusResponse(
            stimulus=stimulus,
            response=level_appropriate_response,
            emotion_before=emotion_before,
            emotion_after=emotion_after,
            timestamp=datetime.now().isoformat(),
            level=self.current_level.value,
            success=success,
            learning_triggered=self._check_learning_trigger(),
        )

        self.stimulus_history.append(stimulus_record)

        # 7. 성장 지표 업데이트
        self._update_growth_metrics(stimulus_record)

        # 8. 레벨 진화 확인
        evolution_result = self._check_level_evolution()

        return {
            "processed_stimulus": stimulus_record,
            "level_appropriate_response": level_appropriate_response,
            "success": success,
            "evolution_result": evolution_result,
            "current_metrics": self.metrics,
        }

    def _classify_stimulus_type(self, stimulus: str) -> str:
        """자극 분류 (조건-매핑 방식)"""
        stimulus_types = {
            "emotional": ["기쁘", "슬프", "화나", "무서", "좋아", "싫어"],
            "cognitive": ["왜", "어떻게", "무엇", "언제", "어디", "누가"],
            "social": ["친구", "엄마", "아빠", "선생님", "같이", "함께"],
            "creative": ["상상", "꿈", "이야기", "그림", "노래", "춤"],
            "problem_solving": ["문제", "해결", "도움", "방법", "계획", "전략"],
        }

        for stimulus_type, keywords in stimulus_types.items():
            if any(keyword in stimulus for keyword in keywords):
                return stimulus_type

        return "general"

    def _update_emotion_from_stimulus(self, stimulus: str):
        """자극에 따른 감정 상태 업데이트"""
        # 간소화된 감정 업데이트 로직
        if "기쁘" in stimulus or "좋아" in stimulus:
            self.emotion_state.happiness += 0.1
            self.emotion_state.excitement += 0.1
        elif "슬프" in stimulus or "우울" in stimulus:
            self.emotion_state.happiness -= 0.1
            self.emotion_state.anxiety += 0.1
        elif "화나" in stimulus or "짜증" in stimulus:
            self.emotion_state.frustration += 0.1
            self.emotion_state.confidence -= 0.1

        # 값 범위 제한
        for attr in [
            "happiness",
            "curiosity",
            "frustration",
            "excitement",
            "confidence",
            "anxiety",
            "satisfaction",
        ]:
            value = getattr(self.emotion_state, attr)
            setattr(self.emotion_state, attr, max(0.0, min(1.0, value)))

    def _update_emotion_from_response(self, response: str):
        """응답에 따른 감정 상태 업데이트"""
        # 간소화된 응답 기반 감정 업데이트
        if "성공" in response or "완성" in response:
            self.emotion_state.satisfaction += 0.1
            self.emotion_state.confidence += 0.1
        elif "실패" in response or "어려워" in response:
            self.emotion_state.frustration += 0.1
            self.emotion_state.confidence -= 0.1

        # 값 범위 제한
        for attr in [
            "happiness",
            "curiosity",
            "frustration",
            "excitement",
            "confidence",
            "anxiety",
            "satisfaction",
        ]:
            value = getattr(self.emotion_state, attr)
            setattr(self.emotion_state, attr, max(0.0, min(1.0, value)))

    def _generate_level_appropriate_response(
        self, stimulus: str, original_response: str
    ) -> str:
        """레벨에 맞는 응답 생성"""
        response_generator = self.response_generators.get(self.current_level)
        if response_generator:
            return response_generator(stimulus)
        return original_response

    def _generate_newborn_response(self, stimulus: str) -> str:
        """신생아 응답 생성"""
        return "응응~"

    def _generate_infant_early_response(self, stimulus: str) -> str:
        """유아기 전기 응답 생성"""
        return "아~"

    def _generate_infant_late_response(self, stimulus: str) -> str:
        """유아기 후기 응답 생성"""
        return "그래요!"

    def _generate_toddler_response(self, stimulus: str) -> str:
        """소아기 응답 생성"""
        return "재미있어요!"

    def _generate_school_age_response(self, stimulus: str) -> str:
        """학령기 응답 생성"""
        return "알겠어요!"

    def _generate_adolescent_response(self, stimulus: str) -> str:
        """사춘기 응답 생성"""
        return "흥미롭네요."

    def _generate_youth_response(self, stimulus: str) -> str:
        """청년기 응답 생성"""
        return "깊이 생각해보겠습니다."

    def _generate_adult_response(self, stimulus: str) -> str:
        """성인기 응답 생성"""
        return "종합적으로 분석해보겠습니다."

    def _evaluate_response_success(self, stimulus: str, response: str) -> bool:
        """응답 성공 여부 평가"""
        # 간소화된 성공 평가
        positive_indicators = ["좋아", "재미있", "성공", "완성", "알겠", "그래"]
        negative_indicators = ["싫어", "어려워", "실패", "못하겠", "모르겠"]

        positive_count = sum(
            1 for indicator in positive_indicators if indicator in response
        )
        negative_count = sum(
            1 for indicator in negative_indicators if indicator in response
        )

        return positive_count > negative_count

    def _check_learning_trigger(self) -> bool:
        """학습 트리거 확인"""
        # 간소화된 학습 트리거
        return (
            self.emotion_state.curiosity > 0.7
            and self.emotion_state.confidence > 0.6
            and self.emotion_state.anxiety < 0.3
        )

    def _update_growth_metrics(self, stimulus_record: StimulusResponse):
        """성장 지표 업데이트"""
        self.metrics.stimulus_count += 1

        if stimulus_record.success:
            self.metrics.successful_responses += 1
            self.metrics.experience_points += 10

        # 감정 안정성 체크
        emotion_variance = sum(abs(v) for v in stimulus_record.emotion_after.values())
        if emotion_variance < 0.5:  # 안정적
            self.metrics.emotional_stability_count += 1

        # 레벨별 특성에 따른 지표 업데이트
        characteristics = self.level_characteristics[self.current_level]
        self.metrics.emotional_maturity += characteristics["emotional_priority"] * 0.01
        self.metrics.cognitive_development += (
            characteristics["cognitive_priority"] * 0.01
        )

    def _check_level_evolution(self) -> Optional[Dict[str, Any]]:
        """레벨 진화 확인"""
        if self.current_level == GrowthLevel.ADULT:
            return None

        conditions = self.growth_conditions[self.current_level]

        # 조건 확인
        stimulus_condition = self.metrics.stimulus_count >= conditions["stimulus_count"]
        success_condition = (
            self.metrics.successful_responses >= conditions["successful_responses"]
        )
        stability_condition = (
            self.metrics.emotional_stability_count / max(1, self.metrics.stimulus_count)
        ) >= conditions["emotional_stability"]

        if stimulus_condition and success_condition and stability_condition:
            return self._evolve_to_next_level()

        return None

    def _evolve_to_next_level(self) -> Dict[str, Any]:
        """다음 레벨로 진화"""
        current_level_value = self.current_level.value
        next_level_value = current_level_value + 1

        if next_level_value <= 8:
            self.current_level = GrowthLevel(next_level_value)
            self.metrics.current_level = next_level_value

            logger.info(f"레벨 진화: {self.current_level.name}")

            return {
                "evolved": True,
                "from_level": current_level_value,
                "to_level": next_level_value,
                "new_characteristics": self.level_characteristics[self.current_level],
            }

        return {"evolved": False, "reason": "max_level_reached"}

    def _get_current_emotion_state(self) -> Dict[str, float]:
        """현재 감정 상태 반환"""
        return {
            "happiness": self.emotion_state.happiness,
            "curiosity": self.emotion_state.curiosity,
            "frustration": self.emotion_state.frustration,
            "excitement": self.emotion_state.excitement,
            "confidence": self.emotion_state.confidence,
            "anxiety": self.emotion_state.anxiety,
            "satisfaction": self.emotion_state.satisfaction,
        }

    def get_growth_status(self) -> Dict[str, Any]:
        """성장 상태 반환"""
        return {
            "current_level": self.current_level.value,
            "level_name": self.current_level.name,
            "characteristics": self.level_characteristics[self.current_level],
            "metrics": self.metrics,
            "emotion_state": self._get_current_emotion_state(),
            "growth_conditions": self.growth_conditions[self.current_level],
        }
