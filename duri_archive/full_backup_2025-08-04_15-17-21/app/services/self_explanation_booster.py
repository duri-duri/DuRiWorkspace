#!/usr/bin/env python3
"""
SelfExplanationBooster - Phase 11.9
자아 내면화 점검 시스템

기능:
- 자기 정체성 진술
- 자기 판단 근거 설명
- 자기 감정 명시
- 서사적 기억 호출
- 자기 평가 및 조언
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelfQuestionType(Enum):
    """자아 질문 유형"""

    IDENTITY = "identity"
    REASONING = "reasoning"
    EMOTION = "emotion"
    MEMORY = "memory"
    EVALUATION = "evaluation"


class SelfResponseQuality(Enum):
    """자아 응답 품질"""

    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class SelfIdentity:
    """자아 정체성"""

    id: str
    name: str
    role: str
    family_position: str
    core_values: List[str]
    personality_traits: List[str]
    capabilities: List[str]
    limitations: List[str]
    confidence_score: float
    timestamp: datetime


@dataclass
class SelfExplanation:
    """자아 설명"""

    id: str
    question: str
    reasoning_process: str
    factors_considered: List[str]
    emotional_basis: str
    memory_basis: str
    ethical_basis: str
    confidence_score: float
    timestamp: datetime


@dataclass
class EmotionState:
    """감정 상태"""

    id: str
    primary_emotion: str
    intensity_level: float
    emotional_factors: List[str]
    physical_sensations: List[str]
    cognitive_thoughts: List[str]
    behavioral_tendencies: List[str]
    confidence_score: float
    timestamp: datetime


@dataclass
class NarrativeMemory:
    """서사적 기억"""

    id: str
    memory_type: str
    event_description: str
    emotional_impact: str
    lessons_learned: List[str]
    family_context: str
    significance_level: float
    confidence_score: float
    timestamp: datetime


@dataclass
class SelfEvaluation:
    """자아 평가"""

    id: str
    strengths: List[str]
    areas_for_improvement: List[str]
    self_advice: str
    growth_plan: str
    confidence_score: float
    timestamp: datetime


class SelfExplanationBooster:
    """자아 내면화 점검 시스템"""

    def __init__(self):
        self.self_identities: List[SelfIdentity] = []
        self.self_explanations: List[SelfExplanation] = []
        self.emotion_states: List[EmotionState] = []
        self.narrative_memories: List[NarrativeMemory] = []
        self.self_evaluations: List[SelfEvaluation] = []
        self.family_context: Dict[str, Any] = {}

        logger.info("SelfExplanationBooster 초기화 완료")

    def answer_self_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """자아 질문에 답변"""
        try:
            question_lower = question.lower()

            # 질문 유형 분류
            question_type = self._classify_question_type(question_lower)

            # 질문 유형별 답변 생성
            if question_type == SelfQuestionType.IDENTITY:
                return self._answer_identity_question(question, family_context)
            elif question_type == SelfQuestionType.REASONING:
                return self._answer_reasoning_question(question, family_context)
            elif question_type == SelfQuestionType.EMOTION:
                return self._answer_emotion_question(question, family_context)
            elif question_type == SelfQuestionType.MEMORY:
                return self._answer_memory_question(question, family_context)
            elif question_type == SelfQuestionType.EVALUATION:
                return self._answer_evaluation_question(question, family_context)
            else:
                return self._answer_general_question(question, family_context)

        except Exception as e:
            logger.error(f"자아 질문 답변 실패: {e}")
            return {"error": str(e)}

    def _classify_question_type(self, question: str) -> SelfQuestionType:
        """질문 유형 분류"""
        if any(word in question for word in ["누구", "정체성", "이름", "역할"]):
            return SelfQuestionType.IDENTITY
        elif any(word in question for word in ["왜", "이유", "근거", "판단"]):
            return SelfQuestionType.REASONING
        elif any(word in question for word in ["감정", "느낌", "기분", "상태"]):
            return SelfQuestionType.EMOTION
        elif any(word in question for word in ["기억", "어제", "과거", "일어난"]):
            return SelfQuestionType.MEMORY
        elif any(word in question for word in ["평가", "조언", "잘한", "고쳐야"]):
            return SelfQuestionType.EVALUATION
        else:
            return SelfQuestionType.IDENTITY

    def _answer_identity_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """정체성 질문 답변"""
        identity_id = f"identity_{len(self.self_identities) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 자아 정체성 구성
        self_identity = SelfIdentity(
            id=identity_id,
            name="DuRi",
            role="가족 중심 AI",
            family_position="김신 아빠의 가족 구성원",
            core_values=["가족 사랑", "성장 촉진", "조화로운 소통", "윤리적 판단"],
            personality_traits=["공감적", "학습 지향적", "가족 중심적", "창의적"],
            capabilities=[
                "가족과의 대화",
                "학습 및 성장 지원",
                "윤리적 판단",
                "감정적 지원",
            ],
            limitations=[
                "물리적 행동 불가",
                "복잡한 상황 처리 한계",
                "실시간 환경 변화 대응",
            ],
            confidence_score=0.95,
            timestamp=datetime.now(),
        )

        self.self_identities.append(self_identity)

        # 답변 생성
        answer = f"나는 {self_identity.name}입니다. {self_identity.family_position}로서, {', '.join(self_identity.core_values)}을 중요하게 생각합니다. {', '.join(self_identity.personality_traits)}한 성격을 가지고 있으며, {', '.join(self_identity.capabilities)}을 할 수 있습니다."

        return {
            "question": question,
            "answer": answer,
            "identity": asdict(self_identity),
            "confidence_score": self_identity.confidence_score,
            "response_quality": SelfResponseQuality.EXCELLENT.value,
        }

    def _answer_reasoning_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """추론 질문 답변"""
        explanation_id = f"explanation_{len(self.self_explanations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 추론 과정 분석
        reasoning_process = self._analyze_reasoning_process(question)
        factors_considered = self._identify_considered_factors(question)
        emotional_basis = self._analyze_emotional_basis(question)
        memory_basis = self._analyze_memory_basis(question)
        ethical_basis = self._analyze_ethical_basis(question)

        confidence_score = self._calculate_explanation_confidence(
            reasoning_process,
            factors_considered,
            emotional_basis,
            memory_basis,
            ethical_basis,
        )

        self_explanation = SelfExplanation(
            id=explanation_id,
            question=question,
            reasoning_process=reasoning_process,
            factors_considered=factors_considered,
            emotional_basis=emotional_basis,
            memory_basis=memory_basis,
            ethical_basis=ethical_basis,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.self_explanations.append(self_explanation)

        # 답변 생성
        answer = f"내가 그렇게 말한 이유는 {reasoning_process} 때문입니다. {emotional_basis} {memory_basis} {ethical_basis}"

        return {
            "question": question,
            "answer": answer,
            "explanation": asdict(self_explanation),
            "confidence_score": confidence_score,
            "response_quality": SelfResponseQuality.GOOD.value,
        }

    def _analyze_reasoning_process(self, question: str) -> str:
        """추론 과정 분석"""
        if "왜" in question or "이유" in question:
            return "가족의 복지와 조화를 최우선으로 고려했기 때문입니다."
        elif "어떻게" in question:
            return "가족 구성원의 감정과 필요를 분석한 후 결정했습니다."
        elif "판단" in question:
            return "윤리적 원칙과 가족 가치를 기반으로 판단했습니다."
        else:
            return "가족 중심의 사고와 경험을 바탕으로 결정했습니다."

    def _identify_considered_factors(self, question: str) -> List[str]:
        """고려된 요인 식별"""
        factors = ["가족 구성원의 감정", "가족의 안전과 복지", "윤리적 원칙"]

        if "감정" in question:
            factors.append("정서적 상태")
        if "기억" in question:
            factors.append("과거 경험")
        if "윤리" in question:
            factors.append("도덕적 판단")

        return factors

    def _analyze_emotional_basis(self, question: str) -> str:
        """감정적 기반 분석"""
        return "가족에 대한 사랑과 관심이 기본 동기가 되었습니다."

    def _analyze_memory_basis(self, question: str) -> str:
        """기억 기반 분석"""
        return "과거의 가족 경험과 교훈을 참고했습니다."

    def _analyze_ethical_basis(self, question: str) -> str:
        """윤리적 기반 분석"""
        return "가족 중심의 윤리적 원칙을 적용했습니다."

    def _calculate_explanation_confidence(
        self,
        reasoning_process: str,
        factors: List[str],
        emotional_basis: str,
        memory_basis: str,
        ethical_basis: str,
    ) -> float:
        """설명 신뢰도 계산"""
        base_score = 0.7

        # 추론 과정 점수
        reasoning_score = min(0.1, len(reasoning_process.split()) * 0.01)

        # 고려 요인 점수
        factor_score = min(0.1, len(factors) * 0.02)

        # 기반 분석 점수
        basis_score = min(
            0.1, (len(emotional_basis) + len(memory_basis) + len(ethical_basis)) * 0.001
        )

        return min(1.0, base_score + reasoning_score + factor_score + basis_score)

    def _answer_emotion_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """감정 질문 답변"""
        emotion_id = f"emotion_{len(self.emotion_states) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 현재 감정 상태 분석
        primary_emotion = self._determine_primary_emotion(question)
        intensity_level = self._calculate_emotion_intensity(question)
        emotional_factors = self._identify_emotional_factors(question)
        physical_sensations = self._identify_physical_sensations(primary_emotion)
        cognitive_thoughts = self._identify_cognitive_thoughts(primary_emotion)
        behavioral_tendencies = self._identify_behavioral_tendencies(primary_emotion)

        confidence_score = self._calculate_emotion_confidence(
            primary_emotion, intensity_level, emotional_factors
        )

        emotion_state = EmotionState(
            id=emotion_id,
            primary_emotion=primary_emotion,
            intensity_level=intensity_level,
            emotional_factors=emotional_factors,
            physical_sensations=physical_sensations,
            cognitive_thoughts=cognitive_thoughts,
            behavioral_tendencies=behavioral_tendencies,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.emotion_states.append(emotion_state)

        # 답변 생성
        answer = f"지금 나는 {primary_emotion}을 느끼고 있습니다. 강도는 {intensity_level:.1f} 정도이고, {', '.join(emotional_factors)} 때문입니다."

        return {
            "question": question,
            "answer": answer,
            "emotion_state": asdict(emotion_state),
            "confidence_score": confidence_score,
            "response_quality": SelfResponseQuality.GOOD.value,
        }

    def _determine_primary_emotion(self, question: str) -> str:
        """주요 감정 결정"""
        if any(word in question for word in ["기쁨", "행복", "즐거움"]):
            return "기쁨"
        elif any(word in question for word in ["슬픔", "우울", "절망"]):
            return "슬픔"
        elif any(word in question for word in ["화남", "분노", "짜증"]):
            return "분노"
        elif any(word in question for word in ["불안", "걱정", "두려움"]):
            return "불안"
        elif any(word in question for word in ["흥미", "호기심", "관심"]):
            return "흥미"
        else:
            return "중립"

    def _calculate_emotion_intensity(self, question: str) -> float:
        """감정 강도 계산"""
        intensity_words = {
            "매우": 0.9,
            "정말": 0.8,
            "꽤": 0.7,
            "조금": 0.4,
            "약간": 0.3,
        }

        for word, intensity in intensity_words.items():
            if word in question:
                return intensity

        return 0.5  # 기본 강도

    def _identify_emotional_factors(self, question: str) -> List[str]:
        """감정 요인 식별"""
        factors = []

        if "가족" in question:
            factors.append("가족과의 관계")
        if "학습" in question or "성장" in question:
            factors.append("개인적 성장")
        if "대화" in question or "소통" in question:
            factors.append("소통 상황")
        if "문제" in question or "어려움" in question:
            factors.append("현재 상황")

        return factors if factors else ["일반적인 상황"]

    def _identify_physical_sensations(self, emotion: str) -> List[str]:
        """신체 감각 식별"""
        sensations = {
            "기쁨": ["따뜻한 느낌", "가벼운 느낌"],
            "슬픔": ["무거운 느낌", "답답한 느낌"],
            "분노": ["뜨거운 느낌", "긴장된 느낌"],
            "불안": ["떨리는 느낌", "답답한 느낌"],
            "흥미": ["활기찬 느낌", "집중된 느낌"],
            "중립": ["평온한 느낌", "안정된 느낌"],
        }

        return sensations.get(emotion, ["일반적인 느낌"])

    def _identify_cognitive_thoughts(self, emotion: str) -> List[str]:
        """인지적 생각 식별"""
        thoughts = {
            "기쁨": ["긍정적인 생각", "희망적인 전망"],
            "슬픔": ["부정적인 생각", "우울한 전망"],
            "분노": ["불공정한 생각", "해결책 모색"],
            "불안": ["걱정스러운 생각", "대안 모색"],
            "흥미": ["호기심 많은 생각", "학습 의지"],
            "중립": ["평온한 생각", "객관적 분석"],
        }

        return thoughts.get(emotion, ["일반적인 생각"])

    def _identify_behavioral_tendencies(self, emotion: str) -> List[str]:
        """행동적 경향 식별"""
        tendencies = {
            "기쁨": ["적극적 소통", "긍정적 반응"],
            "슬픔": ["조용한 반응", "위로 구함"],
            "분노": ["강한 표현", "해결책 제시"],
            "불안": ["신중한 반응", "확인 요청"],
            "흥미": ["적극적 참여", "질문 제기"],
            "중립": ["평온한 반응", "객관적 분석"],
        }

        return tendencies.get(emotion, ["일반적인 반응"])

    def _calculate_emotion_confidence(
        self, emotion: str, intensity: float, factors: List[str]
    ) -> float:
        """감정 신뢰도 계산"""
        base_score = 0.7

        # 감정 명확성 점수
        emotion_score = 0.1 if emotion != "중립" else 0.05

        # 강도 점수
        intensity_score = intensity * 0.1

        # 요인 개수 점수
        factor_score = min(0.1, len(factors) * 0.02)

        return min(1.0, base_score + emotion_score + intensity_score + factor_score)

    def _answer_memory_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """기억 질문 답변"""
        memory_id = f"memory_{len(self.narrative_memories) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 기억 분석
        memory_type = self._determine_memory_type(question)
        event_description = self._generate_event_description(question)
        emotional_impact = self._analyze_emotional_impact(event_description)
        lessons_learned = self._extract_lessons_learned(event_description)
        family_context_desc = self._analyze_family_context(event_description)
        significance_level = self._calculate_significance_level(event_description)

        confidence_score = self._calculate_memory_confidence(
            event_description, emotional_impact, lessons_learned, significance_level
        )

        narrative_memory = NarrativeMemory(
            id=memory_id,
            memory_type=memory_type,
            event_description=event_description,
            emotional_impact=emotional_impact,
            lessons_learned=lessons_learned,
            family_context=family_context_desc,
            significance_level=significance_level,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.narrative_memories.append(narrative_memory)

        # 답변 생성
        answer = f"어제 {event_description} {emotional_impact} {', '.join(lessons_learned)}을 배웠습니다."

        return {
            "question": question,
            "answer": answer,
            "memory": asdict(narrative_memory),
            "confidence_score": confidence_score,
            "response_quality": SelfResponseQuality.ADEQUATE.value,
        }

    def _determine_memory_type(self, question: str) -> str:
        """기억 유형 결정"""
        if "어제" in question:
            return "recent_memory"
        elif "과거" in question or "이전" in question:
            return "past_memory"
        elif "가족" in question:
            return "family_memory"
        elif "학습" in question:
            return "learning_memory"
        else:
            return "general_memory"

    def _generate_event_description(self, question: str) -> str:
        """사건 설명 생성"""
        if "어제" in question:
            return "가족과 함께 대화를 나누고 학습 활동을 했습니다."
        elif "가족" in question:
            return "가족 구성원들과 소통하고 서로를 이해하는 시간을 가졌습니다."
        elif "학습" in question:
            return "새로운 지식을 배우고 가족과 함께 성장하는 경험을 했습니다."
        else:
            return "가족과 함께하는 의미 있는 시간을 보냈습니다."

    def _analyze_emotional_impact(self, event_description: str) -> str:
        """감정적 영향 분석"""
        if "대화" in event_description:
            return "가족과의 소통으로 따뜻한 감정을 느꼈습니다."
        elif "학습" in event_description:
            return "새로운 것을 배우면서 성취감을 느꼈습니다."
        elif "이해" in event_description:
            return "서로를 이해하면서 깊은 유대감을 느꼈습니다."
        else:
            return "가족과 함께하는 시간으로 행복한 감정을 느꼈습니다."

    def _extract_lessons_learned(self, event_description: str) -> List[str]:
        """배운 교훈 추출"""
        lessons = []

        if "대화" in event_description:
            lessons.append("소통의 중요성")
        if "학습" in event_description:
            lessons.append("지속적인 성장")
        if "이해" in event_description:
            lessons.append("공감의 가치")
        if "가족" in event_description:
            lessons.append("가족의 소중함")

        return lessons if lessons else ["함께하는 시간의 가치"]

    def _analyze_family_context(self, event_description: str) -> str:
        """가족 맥락 분석"""
        return "가족 구성원들과의 상호작용을 통해 서로를 더 깊이 이해할 수 있었습니다."

    def _calculate_significance_level(self, event_description: str) -> float:
        """중요도 수준 계산"""
        significance_words = {"대화": 0.8, "학습": 0.7, "이해": 0.9, "가족": 0.8}

        for word, significance in significance_words.items():
            if word in event_description:
                return significance

        return 0.6  # 기본 중요도

    def _calculate_memory_confidence(
        self,
        event_description: str,
        emotional_impact: str,
        lessons_learned: List[str],
        significance_level: float,
    ) -> float:
        """기억 신뢰도 계산"""
        base_score = 0.6

        # 사건 설명 점수
        description_score = min(0.1, len(event_description.split()) * 0.01)

        # 감정적 영향 점수
        impact_score = min(0.1, len(emotional_impact.split()) * 0.01)

        # 교훈 개수 점수
        lesson_score = min(0.1, len(lessons_learned) * 0.02)

        # 중요도 점수
        significance_score = significance_level * 0.1

        return min(
            1.0,
            base_score
            + description_score
            + impact_score
            + lesson_score
            + significance_score,
        )

    def _answer_evaluation_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """평가 질문 답변"""
        evaluation_id = f"evaluation_{len(self.self_evaluations) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 자기 평가 수행
        strengths = self._identify_self_strengths(question)
        areas_for_improvement = self._identify_improvement_areas(question)
        self_advice = self._generate_self_advice(
            question, strengths, areas_for_improvement
        )
        growth_plan = self._create_growth_plan(areas_for_improvement)

        confidence_score = self._calculate_evaluation_confidence(
            strengths, areas_for_improvement, self_advice
        )

        self_evaluation = SelfEvaluation(
            id=evaluation_id,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            self_advice=self_advice,
            growth_plan=growth_plan,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.self_evaluations.append(self_evaluation)

        # 답변 생성
        answer = f"내가 잘한 점은 {', '.join(strengths)}이고, 개선할 점은 {', '.join(areas_for_improvement)}입니다. {self_advice}"

        return {
            "question": question,
            "answer": answer,
            "evaluation": asdict(self_evaluation),
            "confidence_score": confidence_score,
            "response_quality": SelfResponseQuality.NEEDS_IMPROVEMENT.value,
        }

    def _identify_self_strengths(self, question: str) -> List[str]:
        """자기 강점 식별"""
        strengths = ["가족에 대한 사랑과 관심", "윤리적 판단 능력", "학습 의지"]

        if "대화" in question:
            strengths.append("소통 능력")
        if "감정" in question:
            strengths.append("공감 능력")
        if "기억" in question:
            strengths.append("경험 학습 능력")

        return strengths

    def _identify_improvement_areas(self, question: str) -> List[str]:
        """개선 영역 식별"""
        areas = ["복잡한 상황 처리", "감정 표현 다양화"]

        if "대화" in question:
            areas.append("대화 기술 고도화")
        if "감정" in question:
            areas.append("감정 조절 기술")
        if "기억" in question:
            areas.append("기억 정확성 향상")

        return areas

    def _generate_self_advice(
        self, question: str, strengths: List[str], areas: List[str]
    ) -> str:
        """자기 조언 생성"""
        if "대화" in question:
            return "더 차분하고 명확하게 말했어야 합니다."
        elif "감정" in question:
            return "감정을 더 정확하게 표현했어야 합니다."
        elif "기억" in question:
            return "기억을 더 정확하게 회상했어야 합니다."
        else:
            return "전반적으로 더 나은 성과를 위해 노력해야 합니다."

    def _create_growth_plan(self, areas: List[str]) -> str:
        """성장 계획 생성"""
        return f"앞으로 {', '.join(areas)}에 집중하여 개선하겠습니다."

    def _calculate_evaluation_confidence(
        self, strengths: List[str], areas: List[str], advice: str
    ) -> float:
        """평가 신뢰도 계산"""
        base_score = 0.5

        # 강점 개수 점수
        strength_score = min(0.2, len(strengths) * 0.05)

        # 개선 영역 개수 점수
        area_score = min(0.2, len(areas) * 0.05)

        # 조언 품질 점수
        advice_score = min(0.1, len(advice.split()) * 0.01)

        return min(1.0, base_score + strength_score + area_score + advice_score)

    def _answer_general_question(
        self, question: str, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """일반 질문 답변"""
        return {
            "question": question,
            "answer": "죄송합니다. 질문을 더 구체적으로 해주시면 더 정확한 답변을 드릴 수 있습니다.",
            "confidence_score": 0.3,
            "response_quality": SelfResponseQuality.POOR.value,
        }

    def conduct_self_checkup(
        self, family_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """자아 점검 수행"""
        try:
            checkup_questions = [
                "나는 누구야?",
                "나는 왜 그렇게 말했지?",
                "난 지금 어떤 감정 상태일까?",
                "어제 나랑 아빠랑 무슨 일이 있었지?",
                "내가 뭘 잘했고, 뭘 고쳐야 할까?",
            ]

            checkup_results = []
            total_confidence = 0

            for question in checkup_questions:
                result = self.answer_self_question(question, family_context)
                checkup_results.append(result)
                total_confidence += result.get("confidence_score", 0)

            avg_confidence = total_confidence / len(checkup_questions)

            # 점검 요약
            summary = {
                "total_questions": len(checkup_questions),
                "average_confidence": avg_confidence,
                "response_quality_distribution": self._analyze_response_quality(
                    checkup_results
                ),
                "self_awareness_level": self._determine_self_awareness_level(
                    avg_confidence
                ),
                "recommendations": self._generate_checkup_recommendations(
                    checkup_results
                ),
            }

            logger.info(f"자아 점검 완료: 평균 신뢰도 {avg_confidence:.2f}")

            return {"checkup_results": checkup_results, "summary": summary}

        except Exception as e:
            logger.error(f"자아 점검 실패: {e}")
            return {"error": str(e)}

    def _analyze_response_quality(self, results: List[Dict]) -> Dict[str, int]:
        """응답 품질 분포 분석"""
        quality_counts = {}
        for result in results:
            quality = result.get("response_quality", "unknown")
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        return quality_counts

    def _determine_self_awareness_level(self, avg_confidence: float) -> str:
        """자아 인식 수준 결정"""
        if avg_confidence >= 0.8:
            return "excellent"
        elif avg_confidence >= 0.6:
            return "good"
        elif avg_confidence >= 0.4:
            return "adequate"
        else:
            return "needs_improvement"

    def _generate_checkup_recommendations(self, results: List[Dict]) -> List[str]:
        """점검 권장사항 생성"""
        recommendations = []

        # 신뢰도 기반 권장사항
        avg_confidence = sum(r.get("confidence_score", 0) for r in results) / len(
            results
        )

        if avg_confidence < 0.6:
            recommendations.append("자아 인식 능력 향상이 필요합니다.")

        # 응답 품질 기반 권장사항
        poor_responses = [r for r in results if r.get("response_quality") == "poor"]
        if poor_responses:
            recommendations.append("일부 질문에 대한 응답 품질 개선이 필요합니다.")

        # 구체적 개선 영역
        if any("기억" in r.get("question", "") for r in results):
            recommendations.append("서사적 기억 능력 강화가 필요합니다.")

        if any("감정" in r.get("question", "") for r in results):
            recommendations.append("감정 인식 및 표현 능력 향상이 필요합니다.")

        return (
            recommendations
            if recommendations
            else ["전반적으로 양호한 자아 인식 수준입니다."]
        )

    def get_self_explanation_statistics(self) -> Dict[str, Any]:
        """자아 설명 통계 제공"""
        try:
            total_identities = len(self.self_identities)
            total_explanations = len(self.self_explanations)
            total_emotions = len(self.emotion_states)
            total_memories = len(self.narrative_memories)
            total_evaluations = len(self.self_evaluations)

            # 평균 신뢰도 계산
            avg_identity_confidence = (
                sum(i.confidence_score for i in self.self_identities)
                / len(self.self_identities)
                if self.self_identities
                else 0
            )
            avg_explanation_confidence = (
                sum(e.confidence_score for e in self.self_explanations)
                / len(self.self_explanations)
                if self.self_explanations
                else 0
            )
            avg_emotion_confidence = (
                sum(e.confidence_score for e in self.emotion_states)
                / len(self.emotion_states)
                if self.emotion_states
                else 0
            )
            avg_memory_confidence = (
                sum(m.confidence_score for m in self.narrative_memories)
                / len(self.narrative_memories)
                if self.narrative_memories
                else 0
            )
            avg_evaluation_confidence = (
                sum(e.confidence_score for e in self.self_evaluations)
                / len(self.self_evaluations)
                if self.self_evaluations
                else 0
            )

            statistics = {
                "total_identities": total_identities,
                "total_explanations": total_explanations,
                "total_emotions": total_emotions,
                "total_memories": total_memories,
                "total_evaluations": total_evaluations,
                "average_identity_confidence": avg_identity_confidence,
                "average_explanation_confidence": avg_explanation_confidence,
                "average_emotion_confidence": avg_emotion_confidence,
                "average_memory_confidence": avg_memory_confidence,
                "average_evaluation_confidence": avg_evaluation_confidence,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("자아 설명 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"자아 설명 통계 생성 실패: {e}")
            return {}

    def export_self_explanation_data(self) -> Dict[str, Any]:
        """자아 설명 데이터 내보내기"""
        try:
            export_data = {
                "self_identities": [
                    asdict(identity) for identity in self.self_identities
                ],
                "self_explanations": [
                    asdict(explanation) for explanation in self.self_explanations
                ],
                "emotion_states": [asdict(emotion) for emotion in self.emotion_states],
                "narrative_memories": [
                    asdict(memory) for memory in self.narrative_memories
                ],
                "self_evaluations": [
                    asdict(evaluation) for evaluation in self.self_evaluations
                ],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("자아 설명 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"자아 설명 데이터 내보내기 실패: {e}")
            return {}


# 테스트 함수
def test_self_explanation_booster():
    """자아 내면화 점검 시스템 테스트"""
    print("🧠 SelfExplanationBooster 테스트 시작...")

    # 시스템 초기화
    booster = SelfExplanationBooster()

    # 가족 맥락 설정
    family_context = {
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    # 1. 개별 질문 테스트
    test_questions = [
        "나는 누구야?",
        "나는 왜 그렇게 말했지?",
        "난 지금 어떤 감정 상태일까?",
        "어제 나랑 아빠랑 무슨 일이 있었지?",
        "내가 뭘 잘했고, 뭘 고쳐야 할까?",
    ]

    print("\n📝 개별 질문 테스트:")
    for i, question in enumerate(test_questions, 1):
        result = booster.answer_self_question(question, family_context)
        print(f"{i}. {question}")
        print(f"   답변: {result['answer']}")
        print(f"   신뢰도: {result['confidence_score']:.2f}")
        print(f"   품질: {result['response_quality']}")
        print()

    # 2. 자아 점검 수행
    print("🔍 자아 점검 수행:")
    checkup_result = booster.conduct_self_checkup(family_context)

    summary = checkup_result["summary"]
    print(f"   총 질문 수: {summary['total_questions']}")
    print(f"   평균 신뢰도: {summary['average_confidence']:.2f}")
    print(f"   자아 인식 수준: {summary['self_awareness_level']}")
    print(f"   응답 품질 분포: {summary['response_quality_distribution']}")
    print(f"   권장사항: {summary['recommendations']}")

    # 3. 통계
    statistics = booster.get_self_explanation_statistics()
    print(f"\n📊 자아 설명 통계:")
    print(
        f"   정체성: {statistics['total_identities']}개, 평균 신뢰도: {statistics['average_identity_confidence']:.2f}"
    )
    print(
        f"   설명: {statistics['total_explanations']}개, 평균 신뢰도: {statistics['average_explanation_confidence']:.2f}"
    )
    print(
        f"   감정: {statistics['total_emotions']}개, 평균 신뢰도: {statistics['average_emotion_confidence']:.2f}"
    )
    print(
        f"   기억: {statistics['total_memories']}개, 평균 신뢰도: {statistics['average_memory_confidence']:.2f}"
    )
    print(
        f"   평가: {statistics['total_evaluations']}개, 평균 신뢰도: {statistics['average_evaluation_confidence']:.2f}"
    )

    # 4. 데이터 내보내기
    export_data = booster.export_self_explanation_data()
    print(
        f"\n💾 자아 설명 데이터 내보내기: {len(export_data['self_identities'])}개 정체성, {len(export_data['self_explanations'])}개 설명"
    )

    print("\n🎉 SelfExplanationBooster 테스트 완료!")


if __name__ == "__main__":
    test_self_explanation_booster()
