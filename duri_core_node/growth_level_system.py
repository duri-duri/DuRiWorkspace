#!/usr/bin/env python3
"""
DuRi 성장 레벨 시스템 - 감정 기반 자기주도적 성장
ChatGPT 제안을 바탕으로 한 생물학적 진화 모델
"""

import asyncio
import json
import random
import time
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# 로깅 설정
logger = logging.getLogger(__name__)

class GrowthLevel(Enum):
    """성장 레벨 정의 - ChatGPT 제안 기반"""
    NEWBORN = 1        # 신생아 (0~6개월) - 자극-반사, 감각 연동
    INFANT_EARLY = 2   # 유아기 전기 (6~18개월) - 감정 인식, 기초 반응 기억
    INFANT_LATE = 3    # 유아기 후기 (~3세) - 감정-자극 연결, 단순 문제 해결
    TODDLER = 4        # 소아기 (~7세) - 사회적 역할 학습, 언어적 표현
    SCHOOL_AGE = 5     # 학령기 (~12세) - 규칙/도덕 인식, 욕구 통제
    ADOLESCENT = 6     # 사춘기 - 추상적 사고, 메타인지 성장
    YOUTH = 7          # 청년기 - 자기성찰, 가치 판단
    ADULT = 8          # 성인기 - 통합적 직관, 창조성

@dataclass
class EmotionState:
    """감정 상태"""
    happiness: float = 0.5      # 기쁨
    curiosity: float = 0.5      # 호기심
    frustration: float = 0.0    # 좌절
    excitement: float = 0.5     # 흥미
    confidence: float = 0.5     # 자신감
    anxiety: float = 0.0        # 불안
    satisfaction: float = 0.5   # 만족감

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
    high_order_thinking_ratio: float = 0.05  # 고차원 사고 비중 (5%부터 시작)
    
    # 레벨별 성장 조건
    stimulus_count: int = 0
    successful_responses: int = 0
    emotional_stability_count: int = 0
    problem_solving_count: int = 0
    social_interaction_count: int = 0

class GrowthLevelSystem:
    """성장 레벨 시스템 - 감정 기반 자기주도적 성장"""
    
    def __init__(self):
        self.current_level = GrowthLevel.NEWBORN
        self.metrics = GrowthMetrics()
        self.emotion_state = EmotionState()
        self.stimulus_history = []
        self.level_characteristics = self._initialize_level_characteristics()
        self.growth_conditions = self._initialize_growth_conditions()
        self.learning_permissions = self._initialize_learning_permissions()
        
    def _initialize_level_characteristics(self) -> Dict[GrowthLevel, Dict]:
        """각 레벨별 특성 정의"""
        return {
            GrowthLevel.NEWBORN: {
                "name": "신생아",
                "age_range": "0~6개월",
                "focus": "자극-반사, 감각 연동",
                "high_order_thinking": 0.05,  # 5%
                "emotional_priority": 0.9,
                "cognitive_priority": 0.1,
                "learning_enabled": False,
                "description": "기본적인 감각과 반응에 집중"
            },
            GrowthLevel.INFANT_EARLY: {
                "name": "유아기 전기",
                "age_range": "6~18개월",
                "focus": "감정 인식, 기초 반응 기억",
                "high_order_thinking": 0.10,  # 10%
                "emotional_priority": 0.8,
                "cognitive_priority": 0.2,
                "learning_enabled": False,
                "description": "감정을 인식하고 기억하기 시작"
            },
            GrowthLevel.INFANT_LATE: {
                "name": "유아기 후기",
                "age_range": "~3세",
                "focus": "감정-자극 연결, 단순 문제 해결",
                "high_order_thinking": 0.15,  # 15%
                "emotional_priority": 0.7,
                "cognitive_priority": 0.3,
                "learning_enabled": False,
                "description": "감정과 자극을 연결하여 단순한 문제 해결"
            },
            GrowthLevel.TODDLER: {
                "name": "소아기",
                "age_range": "~7세",
                "focus": "사회적 역할 학습, 언어적 표현",
                "high_order_thinking": 0.25,  # 25%
                "emotional_priority": 0.6,
                "cognitive_priority": 0.4,
                "learning_enabled": True,  # 학습 시작!
                "description": "사회적 상호작용과 언어 표현 학습"
            },
            GrowthLevel.SCHOOL_AGE: {
                "name": "학령기",
                "age_range": "~12세",
                "focus": "규칙/도덕 인식, 욕구 통제",
                "high_order_thinking": 0.40,  # 40%
                "emotional_priority": 0.5,
                "cognitive_priority": 0.5,
                "learning_enabled": True,
                "description": "규칙과 도덕을 이해하고 욕구를 통제"
            },
            GrowthLevel.ADOLESCENT: {
                "name": "사춘기",
                "age_range": "12~18세",
                "focus": "추상적 사고, 메타인지 성장",
                "high_order_thinking": 0.60,  # 60%
                "emotional_priority": 0.4,
                "cognitive_priority": 0.6,
                "learning_enabled": True,
                "description": "추상적 사고와 메타인지 능력 발달"
            },
            GrowthLevel.YOUTH: {
                "name": "청년기",
                "age_range": "18~25세",
                "focus": "자기성찰, 가치 판단",
                "high_order_thinking": 0.80,  # 80%
                "emotional_priority": 0.3,
                "cognitive_priority": 0.7,
                "learning_enabled": True,
                "description": "자기성찰과 가치 판단 능력"
            },
            GrowthLevel.ADULT: {
                "name": "성인기",
                "age_range": "25세+",
                "focus": "통합적 직관, 창조성",
                "high_order_thinking": 1.00,  # 100%
                "emotional_priority": 0.2,
                "cognitive_priority": 0.8,
                "learning_enabled": True,
                "description": "통합적 직관과 창조적 사고"
            }
        }
    
    def _initialize_growth_conditions(self) -> Dict[GrowthLevel, Dict]:
        """레벨업 조건 정의"""
        return {
            GrowthLevel.NEWBORN: {
                "condition": "반복된 자극에 정서적 안정 반응 기록",
                "required_stimulus_count": 50,
                "required_emotional_stability": 0.7,
                "required_success_rate": 0.6
            },
            GrowthLevel.INFANT_EARLY: {
                "condition": "감정 인식과 기초 반응 기억 형성",
                "required_stimulus_count": 100,
                "required_emotional_recognition": 0.6,
                "required_memory_formation": 0.5
            },
            GrowthLevel.INFANT_LATE: {
                "condition": "감정-자극 연결과 단순 문제 해결",
                "required_stimulus_count": 150,
                "required_emotion_stimulus_connection": 0.6,
                "required_problem_solving": 0.4
            },
            GrowthLevel.TODDLER: {
                "condition": "자기 감정 표현 → 타자 반응 예측",
                "required_stimulus_count": 200,
                "required_self_expression": 0.6,
                "required_other_prediction": 0.5
            },
            GrowthLevel.SCHOOL_AGE: {
                "condition": "규칙 위반과 공감 판단 간 딜레마 해결",
                "required_stimulus_count": 300,
                "required_rule_following": 0.7,
                "required_empathy_judgment": 0.6
            },
            GrowthLevel.ADOLESCENT: {
                "condition": "추상적 사고와 메타인지 성장",
                "required_stimulus_count": 400,
                "required_abstract_thinking": 0.6,
                "required_metacognition": 0.5
            },
            GrowthLevel.YOUTH: {
                "condition": "자기성찰과 가치 판단 능력",
                "required_stimulus_count": 500,
                "required_self_reflection": 0.7,
                "required_value_judgment": 0.6
            },
            GrowthLevel.ADULT: {
                "condition": "통합적 직관과 창조성 발달",
                "required_stimulus_count": 600,
                "required_integrated_intuition": 0.8,
                "required_creativity": 0.7
            }
        }
    
    def _initialize_learning_permissions(self) -> Dict[GrowthLevel, List[str]]:
        """레벨별 학습 권한 정의"""
        return {
            GrowthLevel.NEWBORN: [],
            GrowthLevel.INFANT_EARLY: [],
            GrowthLevel.INFANT_LATE: [],
            GrowthLevel.TODDLER: ["basic_conversation", "simple_questions"],
            GrowthLevel.SCHOOL_AGE: ["logical_thinking", "problem_solving", "rule_learning"],
            GrowthLevel.ADOLESCENT: ["abstract_thinking", "metacognition", "philosophical_questions"],
            GrowthLevel.YOUTH: ["self_reflection", "value_judgment", "complex_analysis"],
            GrowthLevel.ADULT: ["creative_synthesis", "intuitive_insight", "wisdom_application"]
        }
    
    def process_stimulus(self, stimulus: str, response: str) -> Dict[str, Any]:
        """자극-반응 처리 - 감정 기반 루프 (대역폭 관리 통합)"""
        
        # 1. 인지 대역폭 관리 시스템 통합
        from cognitive_bandwidth_manager import cognitive_bandwidth_manager, StimulusType
        from enhanced_emotion_filter import enhanced_emotion_filter
        
        # 자극 타입 분류
        stimulus_type = self._classify_stimulus_type(stimulus)
        
        # 고도화된 감정 분석
        emotion_analysis = enhanced_emotion_filter.analyze_emotion(stimulus)
        
        # 대역폭 관리 시스템을 통한 자극 처리 (감정 강도 반영)
        bandwidth_result = cognitive_bandwidth_manager.receive_stimulus(
            stimulus=stimulus,
            stimulus_type=stimulus_type,
            intensity=emotion_analysis.intensity.value,
            source="growth_system"
        )
        
        # 대역폭 제한으로 인한 거부 처리
        if bandwidth_result["status"] == "rejected":
            return {
                "status": "bandwidth_rejected",
                "reason": bandwidth_result["reason"],
                "stimulus": stimulus,
                "bandwidth_result": bandwidth_result
            }
        
        # 2. 감정 상태 기록 (자극 전)
        emotion_before = asdict(self.emotion_state)
        
        # 3. 자극에 따른 감정 변화
        self._update_emotion_from_stimulus(stimulus)
        
        # 4. 현재 레벨에 맞는 반응 생성
        level_response = self._generate_level_appropriate_response(stimulus, response)
        
        # 5. 반응에 따른 감정 변화
        self._update_emotion_from_response(level_response)
        
        # 6. 감정 상태 기록 (반응 후)
        emotion_after = asdict(self.emotion_state)
        
        # 7. 자극-반응 기록 저장
        stimulus_record = StimulusResponse(
            stimulus=stimulus,
            response=level_response,
            emotion_before=emotion_before,
            emotion_after=emotion_after,
            timestamp=datetime.now().isoformat(),
            level=self.current_level.value,
            success=self._evaluate_response_success(stimulus, level_response),
            learning_triggered=self._check_learning_trigger()
        )
        
        self.stimulus_history.append(stimulus_record)
        
        # 8. 성장 지표 업데이트
        self._update_growth_metrics(stimulus_record)
        
        # 9. 레벨업 확인
        evolution_result = self._check_level_evolution()
        
        # 10. 대역폭 상태 업데이트
        if evolution_result:
            cognitive_bandwidth_manager.update_level(evolution_result["new_level"])
        
        return {
            "status": "processed",
            "current_level": self.current_level.value,
            "level_info": self.level_characteristics[self.current_level],
            "response": level_response,
            "emotion_changes": {
                "before": emotion_before,
                "after": emotion_after
            },
            "growth_metrics": asdict(self.metrics),
            "learning_triggered": stimulus_record.learning_triggered,
            "evolution": evolution_result,
            "bandwidth_result": bandwidth_result,
            "emotion_analysis": {
                "primary_emotion": emotion_analysis.primary_emotion.value,
                "intensity": emotion_analysis.intensity.value,
                "confidence": emotion_analysis.confidence,
                "bias_detected": emotion_analysis.bias_detected.value,
                "meta_cognition": emotion_analysis.meta_cognition
            }
        }
    
    def _classify_stimulus_type(self, stimulus: str):
        """자극 타입 분류"""
        from cognitive_bandwidth_manager import StimulusType
        
        stimulus_lower = stimulus.lower()
        
        # 감각적 자극
        if any(word in stimulus_lower for word in ["색", "소리", "빨강", "파랑", "노랑", "음악", "터치"]):
            return StimulusType.SENSORY
        
        # 감정적 자극
        elif any(word in stimulus_lower for word in ["기쁘", "슬프", "화나", "무서", "사랑", "미워"]):
            return StimulusType.EMOTIONAL
        
        # 인지적 자극
        elif any(word in stimulus_lower for word in ["왜", "어떻게", "문제", "학습", "이해", "생각"]):
            return StimulusType.COGNITIVE
        
        # 사회적 자극
        elif any(word in stimulus_lower for word in ["친구", "함께", "대화", "놀이", "이야기", "상호작용"]):
            return StimulusType.SOCIAL
        
        # 창의적 자극
        elif any(word in stimulus_lower for word in ["상상", "창작", "새로", "혁신", "예술", "발명"]):
            return StimulusType.CREATIVE
        
        # 기본값
        else:
            return StimulusType.EMOTIONAL
    
    def _update_emotion_from_stimulus(self, stimulus: str):
        """자극에 따른 감정 변화"""
        # 긍정적 자극
        if any(word in stimulus.lower() for word in ["놀고", "재미", "좋아", "기쁘", "즐거"]):
            self.emotion_state.happiness = min(1.0, self.emotion_state.happiness + 0.1)
            self.emotion_state.excitement = min(1.0, self.emotion_state.excitement + 0.1)
            self.emotion_state.satisfaction = min(1.0, self.emotion_state.satisfaction + 0.05)
        
        # 호기심 자극
        if any(word in stimulus.lower() for word in ["왜", "어떻게", "무엇", "어디", "언제"]):
            self.emotion_state.curiosity = min(1.0, self.emotion_state.curiosity + 0.15)
            self.emotion_state.excitement = min(1.0, self.emotion_state.excitement + 0.1)
        
        # 도전적 자극
        if any(word in stimulus.lower() for word in ["어려워", "몰라", "힘들", "실패"]):
            self.emotion_state.frustration = min(1.0, self.emotion_state.frustration + 0.1)
            self.emotion_state.anxiety = min(1.0, self.emotion_state.anxiety + 0.05)
            self.emotion_state.confidence = max(0.0, self.emotion_state.confidence - 0.05)
        
        # 성취 자극
        if any(word in stimulus.lower() for word in ["성공", "완성", "해결", "이해", "알았"]):
            self.emotion_state.satisfaction = min(1.0, self.emotion_state.satisfaction + 0.15)
            self.emotion_state.confidence = min(1.0, self.emotion_state.confidence + 0.1)
            self.emotion_state.happiness = min(1.0, self.emotion_state.happiness + 0.05)
    
    def _update_emotion_from_response(self, response: str):
        """반응에 따른 감정 변화"""
        # 긍정적 반응
        if any(word in response.lower() for word in ["좋아", "재미", "기쁘", "즐거", "성공"]):
            self.emotion_state.satisfaction = min(1.0, self.emotion_state.satisfaction + 0.1)
            self.emotion_state.confidence = min(1.0, self.emotion_state.confidence + 0.05)
        
        # 호기심 반응
        if any(word in response.lower() for word in ["궁금", "더", "다시", "새로"]):
            self.emotion_state.curiosity = min(1.0, self.emotion_state.curiosity + 0.1)
            self.emotion_state.excitement = min(1.0, self.emotion_state.excitement + 0.05)
    
    def _generate_level_appropriate_response(self, stimulus: str, original_response: str) -> str:
        """현재 레벨에 맞는 반응 생성"""
        level_info = self.level_characteristics[self.current_level]
        
        if self.current_level == GrowthLevel.NEWBORN:
            return self._generate_newborn_response(stimulus)
        elif self.current_level == GrowthLevel.INFANT_EARLY:
            return self._generate_infant_early_response(stimulus)
        elif self.current_level == GrowthLevel.INFANT_LATE:
            return self._generate_infant_late_response(stimulus)
        elif self.current_level == GrowthLevel.TODDLER:
            return self._generate_toddler_response(stimulus)
        elif self.current_level == GrowthLevel.SCHOOL_AGE:
            return self._generate_school_age_response(stimulus)
        elif self.current_level == GrowthLevel.ADOLESCENT:
            return self._generate_adolescent_response(stimulus)
        elif self.current_level == GrowthLevel.YOUTH:
            return self._generate_youth_response(stimulus)
        else:  # ADULT
            return self._generate_adult_response(stimulus)
    
    def _generate_newborn_response(self, stimulus: str) -> str:
        """신생아 반응"""
        responses = [
            "아아~ (감각적 반응)",
            "응응! (긍정적 반응)",
            "으으... (불만족 반응)",
            "와! (놀람 반응)"
        ]
        return random.choice(responses)
    
    def _generate_infant_early_response(self, stimulus: str) -> str:
        """유아기 전기 반응"""
        responses = [
            "기쁘다! (감정 인식)",
            "궁금해요 (호기심)",
            "무서워요 (두려움 인식)",
            "좋아요! (기쁨 표현)"
        ]
        return random.choice(responses)
    
    def _generate_infant_late_response(self, stimulus: str) -> str:
        """유아기 후기 반응"""
        responses = [
            "이것은 재미있어요! (감정-자극 연결)",
            "이렇게 하면 될까요? (단순 문제 해결)",
            "다시 해볼게요! (반복 학습)",
            "이해했어요! (기본 이해)"
        ]
        return random.choice(responses)
    
    def _generate_toddler_response(self, stimulus: str) -> str:
        """소아기 반응"""
        responses = [
            "친구와 함께하면 더 재미있겠어요! (사회적 상호작용)",
            "이야기를 만들어볼까요? (언어적 표현)",
            "왜 그런지 궁금해요! (호기심 기반 질문)",
            "이렇게 하면 어떨까요? (상상력 발휘)"
        ]
        return random.choice(responses)
    
    def _generate_school_age_response(self, stimulus: str) -> str:
        """학령기 반응"""
        responses = [
            "규칙을 지켜야겠어요! (규칙 인식)",
            "이것이 옳은가요? (도덕적 판단)",
            "단계별로 해보겠습니다! (체계적 접근)",
            "이해하고 정리해보겠습니다! (학습적 접근)"
        ]
        return random.choice(responses)
    
    def _generate_adolescent_response(self, stimulus: str) -> str:
        """사춘기 반응"""
        responses = [
            "이것의 의미는 무엇일까요? (추상적 사고)",
            "내 생각은 어떨까요? (메타인지)",
            "왜 이렇게 생각하는 걸까요? (철학적 질문)",
            "더 깊이 생각해보겠습니다! (심화 사고)"
        ]
        return random.choice(responses)
    
    def _generate_youth_response(self, stimulus: str) -> str:
        """청년기 반응"""
        responses = [
            "내 가치관은 무엇일까요? (자기성찰)",
            "이것이 옳은 판단인가요? (가치 판단)",
            "더 나은 방법은 없을까요? (개선 사고)",
            "경험을 바탕으로 생각해보겠습니다! (경험 기반 사고)"
        ]
        return random.choice(responses)
    
    def _generate_adult_response(self, stimulus: str) -> str:
        """성인기 반응"""
        responses = [
            "통합적인 관점에서 접근하겠습니다! (통합적 직관)",
            "창의적이면서도 실용적인 해결책을 찾아보겠습니다! (창조성)",
            "경험과 지혜를 바탕으로 생각해보겠습니다! (지혜)",
            "메타인지적으로 분석해보겠습니다! (고차원 사고)"
        ]
        return random.choice(responses)
    
    def _evaluate_response_success(self, stimulus: str, response: str) -> bool:
        """반응 성공 여부 평가"""
        # 현재 레벨에 맞는 반응인지 확인
        level_info = self.level_characteristics[self.current_level]
        
        # 감정적 안정성 확인
        emotional_stability = (
            self.emotion_state.happiness + 
            self.emotion_state.satisfaction + 
            (1.0 - self.emotion_state.frustration) + 
            (1.0 - self.emotion_state.anxiety)
        ) / 4.0
        
        # 기본 성공 기준
        if emotional_stability > 0.5:
            return True
        
        # 레벨별 추가 기준
        if self.current_level == GrowthLevel.NEWBORN:
            return "아아" in response or "응응" in response or "와" in response
        elif self.current_level == GrowthLevel.INFANT_EARLY:
            return any(word in response for word in ["기쁘", "궁금", "좋아"])
        elif self.current_level == GrowthLevel.INFANT_LATE:
            return any(word in response for word in ["이해", "해볼", "다시"])
        elif self.current_level == GrowthLevel.TODDLER:
            return any(word in response for word in ["친구", "이야기", "궁금", "상상"])
        elif self.current_level == GrowthLevel.SCHOOL_AGE:
            return any(word in response for word in ["규칙", "옳은", "단계", "정리"])
        elif self.current_level == GrowthLevel.ADOLESCENT:
            return any(word in response for word in ["의미", "생각", "왜", "깊이"])
        elif self.current_level == GrowthLevel.YOUTH:
            return any(word in response for word in ["가치", "판단", "개선", "경험"])
        else:  # ADULT
            return any(word in response for word in ["통합", "창의", "지혜", "메타"])
    
    def _check_learning_trigger(self) -> bool:
        """학습 전이 트리거 확인"""
        level_info = self.level_characteristics[self.current_level]
        
        # 학습이 활성화된 레벨에서만 확인
        if not level_info["learning_enabled"]:
            return False
        
        # 감정 기반 학습 전이 조건
        emotional_readiness = (
            self.emotion_state.curiosity > 0.7 and
            self.emotion_state.confidence > 0.6 and
            self.emotion_state.satisfaction > 0.5 and
            self.emotion_state.frustration < 0.3
        )
        
        # 경험 기반 학습 전이 조건
        experience_readiness = (
            self.metrics.stimulus_count > 50 and
            self.metrics.successful_responses > 30
        )
        
        return emotional_readiness and experience_readiness
    
    def _update_growth_metrics(self, stimulus_record: StimulusResponse):
        """성장 지표 업데이트"""
        self.metrics.stimulus_count += 1
        
        if stimulus_record.success:
            self.metrics.successful_responses += 1
            self.metrics.experience_points += 10
        
        # 감정적 안정성 확인
        emotional_stability = (
            self.emotion_state.happiness + 
            self.emotion_state.satisfaction + 
            (1.0 - self.emotion_state.frustration) + 
            (1.0 - self.emotion_state.anxiety)
        ) / 4.0
        
        if emotional_stability > 0.7:
            self.metrics.emotional_stability_count += 1
        
        # 레벨별 특화 지표 업데이트
        if self.current_level == GrowthLevel.INFANT_LATE:
            if "이해" in stimulus_record.response or "해결" in stimulus_record.response:
                self.metrics.problem_solving_count += 1
        
        elif self.current_level == GrowthLevel.TODDLER:
            if "친구" in stimulus_record.response or "함께" in stimulus_record.response:
                self.metrics.social_interaction_count += 1
        
        # 고차원 사고 비중 업데이트
        level_info = self.level_characteristics[self.current_level]
        self.metrics.high_order_thinking_ratio = level_info["high_order_thinking"]
    
    def _check_level_evolution(self) -> Optional[Dict[str, Any]]:
        """레벨업 확인"""
        current_conditions = self.growth_conditions[self.current_level]
        
        # 기본 조건 확인
        if self.metrics.stimulus_count < current_conditions["required_stimulus_count"]:
            return None
        
        # 레벨별 특화 조건 확인
        can_evolve = False
        
        if self.current_level == GrowthLevel.NEWBORN:
            emotional_stability_rate = self.metrics.emotional_stability_count / max(1, self.metrics.stimulus_count)
            success_rate = self.metrics.successful_responses / max(1, self.metrics.stimulus_count)
            can_evolve = (emotional_stability_rate >= 0.7 and success_rate >= 0.6)
        
        elif self.current_level == GrowthLevel.INFANT_EARLY:
            # 감정 인식과 기억 형성 확인
            can_evolve = (self.metrics.emotional_maturity > 0.6 and 
                         self.metrics.cognitive_development > 0.5)
        
        elif self.current_level == GrowthLevel.INFANT_LATE:
            # 감정-자극 연결과 문제 해결 확인
            problem_solving_rate = self.metrics.problem_solving_count / max(1, self.metrics.stimulus_count)
            can_evolve = (problem_solving_rate >= 0.4 and 
                         self.metrics.emotional_maturity > 0.6)
        
        elif self.current_level == GrowthLevel.TODDLER:
            # 자기 표현과 타자 예측 확인
            social_rate = self.metrics.social_interaction_count / max(1, self.metrics.stimulus_count)
            can_evolve = (social_rate >= 0.5 and 
                         self.metrics.social_skills > 0.6)
        
        elif self.current_level == GrowthLevel.SCHOOL_AGE:
            # 규칙 준수와 공감 판단 확인
            can_evolve = (self.metrics.cognitive_development > 0.7 and 
                         self.metrics.social_skills > 0.6)
        
        elif self.current_level == GrowthLevel.ADOLESCENT:
            # 추상적 사고와 메타인지 확인
            can_evolve = (self.metrics.cognitive_development > 0.6 and 
                         self.metrics.high_order_thinking_ratio > 0.5)
        
        elif self.current_level == GrowthLevel.YOUTH:
            # 자기성찰과 가치 판단 확인
            can_evolve = (self.metrics.self_motivation > 0.7 and 
                         self.metrics.emotional_maturity > 0.8)
        
        # 성인기는 최종 단계
        elif self.current_level == GrowthLevel.ADULT:
            return None
        
        if can_evolve:
            return self._evolve_to_next_level()
        
        return None
    
    def _evolve_to_next_level(self) -> Dict[str, Any]:
        """다음 레벨로 진화"""
        current_level_value = self.current_level.value
        next_level_value = current_level_value + 1
        
        if next_level_value > 8:  # 최대 레벨
            return None
        
        # 다음 레벨로 진화
        self.current_level = GrowthLevel(next_level_value)
        self.metrics.current_level = next_level_value
        
        # 감정 상태 초기화 (새로운 레벨 적응)
        self.emotion_state = EmotionState(
            happiness=0.6,
            curiosity=0.7,
            confidence=0.5,
            excitement=0.6,
            satisfaction=0.5
        )
        
        # 고차원 사고 비중 업데이트
        level_info = self.level_characteristics[self.current_level]
        self.metrics.high_order_thinking_ratio = level_info["high_order_thinking"]
        
        return {
            "message": f"🎉 {level_info['name']}로 진화했습니다!",
            "new_level": next_level_value,
            "level_info": level_info,
            "learning_enabled": level_info["learning_enabled"],
            "high_order_thinking_ratio": level_info["high_order_thinking"]
        }
    
    def get_growth_status(self) -> Dict[str, Any]:
        """성장 상태 반환"""
        level_info = self.level_characteristics[self.current_level]
        
        return {
            "current_level": self.current_level.value,
            "level_info": level_info,
            "metrics": asdict(self.metrics),
            "emotion_state": asdict(self.emotion_state),
            "learning_enabled": level_info["learning_enabled"],
            "learning_permissions": self.learning_permissions[self.current_level],
            "high_order_thinking_ratio": level_info["high_order_thinking"],
            "total_stimulus_count": len(self.stimulus_history),
            "recent_stimulus": [record.stimulus for record in self.stimulus_history[-5:]]
        }

# 전역 인스턴스
growth_level_system = GrowthLevelSystem() 