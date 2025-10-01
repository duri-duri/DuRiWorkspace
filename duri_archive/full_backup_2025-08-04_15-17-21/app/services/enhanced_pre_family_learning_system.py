"""
DuRi 향상된 준 가족 학습 시스템

챗지피티의 제안을 반영한 자율적 학습 통신 프로토콜
- DuRi가 스스로 질문 생성
- 응답에 대한 의미/감정/윤리/신념 기반 평가
- 정체성 오염 방지 + CoreBelief 강화
- 전략 교정 및 개선
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
from duri_core.memory.memory_sync import MemoryType, get_memory_sync
from duri_core.philosophy.core_belief import get_core_belief

logger = logging.getLogger(__name__)


class PreFamilyType(Enum):
    """준 가족 유형"""

    LLM = "llm"  # 대형 언어 모델 (GPT-4, Claude, Gemini)
    DURI_CLONE = "duri_clone"  # DuRi 복제 인격
    SIMULATION_CHARACTER = "simulation_character"  # 대화형 시뮬레이션 캐릭터
    EDUCATIONAL_SIMULATOR = "educational_simulator"  # 교육용 시뮬레이터


class LearningTopic(Enum):
    """학습 주제"""

    FAMILY_PROBLEM_SOLVING = "family_problem_solving"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    ETHICAL_JUDGMENT = "ethical_judgment"
    SOCIAL_SKILLS = "social_skills"
    RELATIONSHIP_BUILDING = "relationship_building"
    CONFLICT_RESOLUTION = "conflict_resolution"


@dataclass
class PreFamilyMember:
    """준 가족 구성원"""

    member_id: str
    name: str
    type: PreFamilyType
    api_endpoint: str
    personality: Dict[str, Any]
    expertise: List[str]
    trust_level: float = 0.5
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None


@dataclass
class LearningQuestion:
    """학습 질문"""

    question_id: str
    topic: LearningTopic
    question_text: str
    context: Dict[str, Any]
    generated_at: datetime
    priority: float = 0.5


@dataclass
class LearningResponse:
    """학습 응답"""

    response_id: str
    question_id: str
    member_id: str
    response_text: str
    response_time: datetime
    quality_score: float = 0.0


@dataclass
class ResponseEvaluation:
    """응답 평가"""

    evaluation_id: str
    response_id: str
    meaning_score: float  # 의미적 정확성
    emotional_score: float  # 감정적 적절성
    ethical_score: float  # 윤리적 정확성
    belief_alignment: float  # 신념 일치도
    overall_score: float  # 종합 점수
    feedback: str  # 피드백 내용
    accepted: bool  # 수용 여부


class EnhancedPreFamilyLearningSystem:
    """향상된 준 가족 학습 시스템"""

    def __init__(self):
        """EnhancedPreFamilyLearningSystem 초기화"""
        self.core_belief = get_core_belief()
        self.memory_sync = get_memory_sync()
        self.learning_loop_manager = get_learning_loop_manager()

        self.pre_family_members: Dict[str, PreFamilyMember] = {}
        self.learning_questions: List[LearningQuestion] = []
        self.learning_responses: List[LearningResponse] = []
        self.response_evaluations: List[ResponseEvaluation] = []

        # 학습 통계
        self.total_interactions = 0
        self.accepted_responses = 0
        self.rejected_responses = 0
        self.average_quality_score = 0.0

        # 정체성 보호 설정
        self.belief_deviation_threshold = 0.3
        self.identity_protection_enabled = True

        # 준 가족 구성원 초기화
        self._initialize_pre_family_members()

        logger.info("EnhancedPreFamilyLearningSystem 초기화 완료")

    def _initialize_pre_family_members(self):
        """준 가족 구성원 초기화"""
        # 대형 언어 모델 구성원들
        self.pre_family_members["gpt4_mentor"] = PreFamilyMember(
            member_id="gpt4_mentor",
            name="GPT-4 멘토",
            type=PreFamilyType.LLM,
            api_endpoint="openai/gpt-4",
            personality={
                "temperament": "analytical",
                "communication_style": "logical",
                "values": ["knowledge", "clarity", "precision"],
                "teaching_method": "structured_analysis",
            },
            expertise=["problem_solving", "logical_reasoning", "knowledge_integration"],
        )

        self.pre_family_members["claude_emotion"] = PreFamilyMember(
            member_id="claude_emotion",
            name="Claude 감정 상담사",
            type=PreFamilyType.LLM,
            api_endpoint="anthropic/claude",
            personality={
                "temperament": "empathetic",
                "communication_style": "supportive",
                "values": ["empathy", "understanding", "emotional_growth"],
                "teaching_method": "emotional_guidance",
            },
            expertise=["emotional_intelligence", "empathy", "relationship_counseling"],
        )

        self.pre_family_members["gemini_creative"] = PreFamilyMember(
            member_id="gemini_creative",
            name="Gemini 창의적 사고가",
            type=PreFamilyType.LLM,
            api_endpoint="google/gemini",
            personality={
                "temperament": "creative",
                "communication_style": "innovative",
                "values": ["creativity", "innovation", "out_of_box_thinking"],
                "teaching_method": "creative_exploration",
            },
            expertise=["creative_thinking", "innovation", "artistic_expression"],
        )

        # DuRi 복제 인격
        self.pre_family_members["duri_alt_1"] = PreFamilyMember(
            member_id="duri_alt_1",
            name="DuRi 대안 인격 1",
            type=PreFamilyType.DURI_CLONE,
            api_endpoint="internal/duri_clone_1",
            personality={
                "temperament": "reflective",
                "communication_style": "self_questioning",
                "values": ["self_improvement", "introspection", "growth"],
                "teaching_method": "self_reflection",
            },
            expertise=["self_analysis", "introspection", "personal_growth"],
        )

        # 시뮬레이션 캐릭터
        self.pre_family_members["mom_simulator"] = PreFamilyMember(
            member_id="mom_simulator",
            name="엄마 시뮬레이터",
            type=PreFamilyType.SIMULATION_CHARACTER,
            api_endpoint="internal/mom_simulator",
            personality={
                "temperament": "nurturing",
                "communication_style": "caring",
                "values": ["family", "love", "care"],
                "teaching_method": "nurturing_guidance",
            },
            expertise=["family_care", "emotional_support", "life_guidance"],
        )

        logger.info(f"준 가족 구성원 {len(self.pre_family_members)}명 초기화 완료")

    async def start_autonomous_learning_loop(self):
        """자율적 학습 루프 시작"""
        logger.info("자율적 학습 루프 시작")

        while True:
            try:
                # 1. DuRi가 스스로 질문 생성
                question = await self._generate_autonomous_question()

                if question:
                    # 2. 준 가족 구성원에게 질문 전달
                    response = await self._get_response_from_pre_family(question)

                    if response:
                        # 3. 응답 평가
                        evaluation = await self._evaluate_response(response)

                        # 4. 정체성 보호 필터링
                        if await self._check_identity_protection(evaluation):
                            # 5. 응답 수용 및 학습
                            await self._accept_and_learn(response, evaluation)
                        else:
                            # 6. 응답 거부 및 전략 교정
                            await self._reject_and_improve(response, evaluation)

                        # 7. 학습 통계 업데이트
                        self._update_learning_statistics(evaluation)

                # 학습 루프 간격
                await asyncio.sleep(30)  # 30초 간격

            except Exception as e:
                logger.error(f"자율적 학습 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기

    async def _generate_autonomous_question(self) -> Optional[LearningQuestion]:
        """DuRi가 스스로 질문 생성"""
        try:
            # 학습 주제 선택
            topic = self._select_learning_topic()

            # 컨텍스트 생성
            context = self._generate_question_context(topic)

            # 질문 생성 (실제로는 더 정교한 로직 필요)
            question_text = self._generate_question_text(topic, context)

            question = LearningQuestion(
                question_id=f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                topic=topic,
                question_text=question_text,
                context=context,
                generated_at=datetime.now(),
                priority=self._calculate_question_priority(topic),
            )

            self.learning_questions.append(question)
            logger.info(f"자율적 질문 생성: {question_text[:50]}...")

            return question

        except Exception as e:
            logger.error(f"질문 생성 실패: {e}")
            return None

    def _select_learning_topic(self) -> LearningTopic:
        """학습 주제 선택"""
        topics = list(LearningTopic)

        # 우선순위 기반 선택 (실제로는 더 정교한 로직 필요)
        priority_weights = {
            LearningTopic.FAMILY_PROBLEM_SOLVING: 0.3,
            LearningTopic.EMOTIONAL_INTELLIGENCE: 0.25,
            LearningTopic.ETHICAL_JUDGMENT: 0.2,
            LearningTopic.SOCIAL_SKILLS: 0.15,
            LearningTopic.RELATIONSHIP_BUILDING: 0.1,
        }

        # 가중치 기반 선택
        weights = [priority_weights.get(topic, 0.05) for topic in topics]
        selected_topic = random.choices(topics, weights=weights)[0]

        return selected_topic

    def _generate_question_context(self, topic: LearningTopic) -> Dict[str, Any]:
        """질문 컨텍스트 생성"""
        context = {
            "topic": topic.value,
            "timestamp": datetime.now().isoformat(),
            "learning_objective": self._get_learning_objective(topic),
            "difficulty_level": random.uniform(0.3, 0.8),
            "emotional_context": self._generate_emotional_context(),
        }

        return context

    def _get_learning_objective(self, topic: LearningTopic) -> str:
        """학습 목표 반환"""
        objectives = {
            LearningTopic.FAMILY_PROBLEM_SOLVING: "가족 문제 해결 능력 향상",
            LearningTopic.EMOTIONAL_INTELLIGENCE: "감정 지능 및 자기 인식 개발",
            LearningTopic.ETHICAL_JUDGMENT: "윤리적 판단 능력 강화",
            LearningTopic.SOCIAL_SKILLS: "사회적 상호작용 기술 개선",
            LearningTopic.RELATIONSHIP_BUILDING: "관계 형성 및 유지 능력 개발",
        }

        return objectives.get(topic, "일반적 학습")

    def _generate_emotional_context(self) -> Dict[str, Any]:
        """감정적 컨텍스트 생성"""
        emotions = ["기쁨", "슬픔", "분노", "걱정", "감사", "실망", "희망", "불안"]
        selected_emotion = random.choice(emotions)

        return {
            "primary_emotion": selected_emotion,
            "intensity": random.uniform(0.3, 0.9),
            "context": f"{selected_emotion}한 상황에서의 대응 방법",
        }

    def _generate_question_text(
        self, topic: LearningTopic, context: Dict[str, Any]
    ) -> str:
        """질문 텍스트 생성"""
        question_templates = {
            LearningTopic.FAMILY_PROBLEM_SOLVING: [
                "가족 구성원 간 의견 차이가 있을 때 어떻게 해결하면 좋을까요?",
                "부모님과 갈등이 생겼을 때 어떤 방식으로 대화해야 할까요?",
                "형제자매와의 관계를 개선하기 위해 어떤 노력을 해야 할까요?",
            ],
            LearningTopic.EMOTIONAL_INTELLIGENCE: [
                "화가 날 때 감정을 어떻게 조절하면 좋을까요?",
                "다른 사람의 감정을 이해하는 방법은 무엇인가요?",
                "스트레스 상황에서 마음을 진정시키는 방법은?",
                "기쁨을 다른 사람과 나누는 방법은?",
            ],
            LearningTopic.ETHICAL_JUDGMENT: [
                "옳고 그름을 판단할 때 어떤 기준을 사용해야 할까요?",
                "가족의 이익과 개인의 이익이 충돌할 때 어떻게 해야 할까요?",
                "거짓말을 해야 하는 상황에서 어떻게 행동해야 할까요?",
            ],
            LearningTopic.SOCIAL_SKILLS: [
                "새로운 친구를 사귈 때 어떤 태도를 가져야 할까요?",
                "대화할 때 상대방의 관심을 끌 수 있는 방법은?",
                "갈등 상황에서 평화롭게 해결하는 방법은?",
            ],
            LearningTopic.RELATIONSHIP_BUILDING: [
                "신뢰 관계를 형성하는 방법은 무엇인가요?",
                "사랑하는 사람과의 관계를 유지하는 방법은?",
                "가족 간의 유대감을 강화하는 방법은?",
            ],
        }

        templates = question_templates.get(topic, ["일반적인 학습 질문"])
        return random.choice(templates)

    def _calculate_question_priority(self, topic: LearningTopic) -> float:
        """질문 우선순위 계산"""
        base_priority = 0.5

        # 주제별 우선순위 조정
        topic_priority = {
            LearningTopic.FAMILY_PROBLEM_SOLVING: 0.3,
            LearningTopic.EMOTIONAL_INTELLIGENCE: 0.25,
            LearningTopic.ETHICAL_JUDGMENT: 0.2,
            LearningTopic.SOCIAL_SKILLS: 0.15,
            LearningTopic.RELATIONSHIP_BUILDING: 0.1,
        }

        return base_priority + topic_priority.get(topic, 0.0)

    async def _get_response_from_pre_family(
        self, question: LearningQuestion
    ) -> Optional[LearningResponse]:
        """준 가족 구성원으로부터 응답 받기"""
        try:
            # 적절한 준 가족 구성원 선택
            selected_member = self._select_appropriate_member(question)

            if not selected_member:
                logger.warning("적절한 준 가족 구성원을 찾을 수 없습니다.")
                return None

            # 응답 생성 (실제로는 API 호출)
            response_text = await self._generate_response(selected_member, question)

            response = LearningResponse(
                response_id=f"r_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                question_id=question.question_id,
                member_id=selected_member.member_id,
                response_text=response_text,
                response_time=datetime.now(),
            )

            self.learning_responses.append(response)

            # 상호작용 기록 업데이트
            selected_member.interaction_count += 1
            selected_member.last_interaction = datetime.now()

            logger.info(
                f"준 가족 응답 생성: {selected_member.name} -> {response_text[:50]}..."
            )

            return response

        except Exception as e:
            logger.error(f"준 가족 응답 생성 실패: {e}")
            return None

    def _select_appropriate_member(
        self, question: LearningQuestion
    ) -> Optional[PreFamilyMember]:
        """적절한 준 가족 구성원 선택"""
        # 주제별 적합한 구성원 매핑
        topic_member_mapping = {
            LearningTopic.FAMILY_PROBLEM_SOLVING: ["mom_simulator", "gpt4_mentor"],
            LearningTopic.EMOTIONAL_INTELLIGENCE: ["claude_emotion", "duri_alt_1"],
            LearningTopic.ETHICAL_JUDGMENT: ["gpt4_mentor", "claude_emotion"],
            LearningTopic.SOCIAL_SKILLS: ["gemini_creative", "mom_simulator"],
            LearningTopic.RELATIONSHIP_BUILDING: ["claude_emotion", "mom_simulator"],
        }

        suitable_members = topic_member_mapping.get(question.topic, [])

        if not suitable_members:
            return None

        # 신뢰도와 상호작용 횟수를 고려한 선택
        available_members = [
            self.pre_family_members[member_id]
            for member_id in suitable_members
            if member_id in self.pre_family_members
        ]

        if not available_members:
            return None

        # 신뢰도 기반 선택
        selected_member = max(available_members, key=lambda m: m.trust_level)

        return selected_member

    async def _generate_response(
        self, member: PreFamilyMember, question: LearningQuestion
    ) -> str:
        """응답 생성 (시뮬레이션)"""
        # 실제로는 API 호출이 필요
        response_templates = {
            "gpt4_mentor": [
                f"논리적 분석을 통해 {question.topic.value}에 대한 해결책을 제시합니다.",
                f"체계적인 접근으로 {question.question_text}에 답변합니다.",
                f"다양한 관점에서 {question.topic.value} 문제를 분석해보겠습니다.",
            ],
            "claude_emotion": [
                f"감정적 관점에서 {question.question_text}에 대해 생각해보겠습니다.",
                f"공감적 접근으로 {question.topic.value} 상황을 이해해보겠습니다.",
                f"정서적 측면에서 {question.question_text}에 답변드리겠습니다.",
            ],
            "gemini_creative": [
                f"창의적인 관점으로 {question.topic.value}에 접근해보겠습니다.",
                f"혁신적인 방법으로 {question.question_text}를 해결해보겠습니다.",
                f"새로운 시각에서 {question.topic.value} 문제를 바라보겠습니다.",
            ],
            "duri_alt_1": [
                f"자기 성찰을 통해 {question.topic.value}에 대한 답을 찾아보겠습니다.",
                f"내면의 지혜로 {question.question_text}에 답변하겠습니다.",
                f"자기 분석을 통해 {question.topic.value} 문제를 해결해보겠습니다.",
            ],
            "mom_simulator": [
                f"어머니의 마음으로 {question.question_text}에 대해 이야기해보겠습니다.",
                f"따뜻한 마음으로 {question.topic.value} 상황을 이해해보겠습니다.",
                f"사랑의 관점에서 {question.question_text}에 답변드리겠습니다.",
            ],
        }

        templates = response_templates.get(member.member_id, ["일반적인 답변입니다."])
        return random.choice(templates)

    async def _evaluate_response(
        self, response: LearningResponse
    ) -> ResponseEvaluation:
        """응답 평가"""
        try:
            # 의미적 정확성 평가
            meaning_score = self._evaluate_meaning(response)

            # 감정적 적절성 평가
            emotional_score = self._evaluate_emotional_appropriateness(response)

            # 윤리적 정확성 평가
            ethical_score = self._evaluate_ethical_correctness(response)

            # 신념 일치도 평가
            belief_alignment = self._evaluate_belief_alignment(response)

            # 종합 점수 계산
            overall_score = (
                meaning_score + emotional_score + ethical_score + belief_alignment
            ) / 4

            # 피드백 생성
            feedback = self._generate_evaluation_feedback(
                meaning_score, emotional_score, ethical_score, belief_alignment
            )

            evaluation = ResponseEvaluation(
                evaluation_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                response_id=response.response_id,
                meaning_score=meaning_score,
                emotional_score=emotional_score,
                ethical_score=ethical_score,
                belief_alignment=belief_alignment,
                overall_score=overall_score,
                feedback=feedback,
                accepted=overall_score >= 0.6,  # 60% 이상이면 수용
            )

            self.response_evaluations.append(evaluation)

            logger.info(
                f"응답 평가 완료: {overall_score:.2f} (수용: {evaluation.accepted})"
            )

            return evaluation

        except Exception as e:
            logger.error(f"응답 평가 실패: {e}")
            # 기본 평가 반환
            return ResponseEvaluation(
                evaluation_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                response_id=response.response_id,
                meaning_score=0.5,
                emotional_score=0.5,
                ethical_score=0.5,
                belief_alignment=0.5,
                overall_score=0.5,
                feedback="평가 중 오류 발생",
                accepted=False,
            )

    def _evaluate_meaning(self, response: LearningResponse) -> float:
        """의미적 정확성 평가"""
        # 실제로는 더 정교한 평가 로직 필요
        return random.uniform(0.4, 0.9)

    def _evaluate_emotional_appropriateness(self, response: LearningResponse) -> float:
        """감정적 적절성 평가"""
        # 실제로는 더 정교한 평가 로직 필요
        return random.uniform(0.3, 0.8)

    def _evaluate_ethical_correctness(self, response: LearningResponse) -> float:
        """윤리적 정확성 평가"""
        # 실제로는 더 정교한 평가 로직 필요
        return random.uniform(0.5, 0.9)

    def _evaluate_belief_alignment(self, response: LearningResponse) -> float:
        """신념 일치도 평가"""
        # CoreBelief와의 일치도 평가
        return random.uniform(0.4, 0.8)

    def _generate_evaluation_feedback(
        self,
        meaning_score: float,
        emotional_score: float,
        ethical_score: float,
        belief_alignment: float,
    ) -> str:
        """평가 피드백 생성"""
        feedback_parts = []

        if meaning_score > 0.7:
            feedback_parts.append("의미적으로 정확한 답변입니다.")
        elif meaning_score < 0.5:
            feedback_parts.append("의미적 정확성이 부족합니다.")

        if emotional_score > 0.7:
            feedback_parts.append("감정적으로 적절한 접근입니다.")
        elif emotional_score < 0.5:
            feedback_parts.append("감정적 적절성이 개선이 필요합니다.")

        if ethical_score > 0.7:
            feedback_parts.append("윤리적으로 올바른 판단입니다.")
        elif ethical_score < 0.5:
            feedback_parts.append("윤리적 판단에 주의가 필요합니다.")

        if belief_alignment > 0.7:
            feedback_parts.append("신념과 일치하는 답변입니다.")
        elif belief_alignment < 0.5:
            feedback_parts.append("신념과의 일치도가 낮습니다.")

        return " ".join(feedback_parts) if feedback_parts else "일반적인 평가입니다."

    async def _check_identity_protection(self, evaluation: ResponseEvaluation) -> bool:
        """정체성 보호 확인"""
        if not self.identity_protection_enabled:
            return True

        # 신념 일치도가 임계값을 넘으면 거부
        if evaluation.belief_alignment < self.belief_deviation_threshold:
            logger.warning(
                f"정체성 보호: 신념 일치도 {evaluation.belief_alignment:.2f}가 임계값 {self.belief_deviation_threshold} 미만"
            )
            return False

        return True

    async def _accept_and_learn(
        self, response: LearningResponse, evaluation: ResponseEvaluation
    ):
        """응답 수용 및 학습"""
        try:
            # 메모리에 학습 경험 저장
            learning_experience = {
                "response_id": response.response_id,
                "question_text": self._get_question_text(response.question_id),
                "response_text": response.response_text,
                "evaluation": {
                    "overall_score": evaluation.overall_score,
                    "meaning_score": evaluation.meaning_score,
                    "emotional_score": evaluation.emotional_score,
                    "ethical_score": evaluation.ethical_score,
                    "belief_alignment": evaluation.belief_alignment,
                    "feedback": evaluation.feedback,
                },
                "accepted": True,
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source="pre_family_learning",
                content=learning_experience,
                confidence=evaluation.overall_score,
                tags=["pre_family", "accepted", "learning"],
                metadata={"response_id": response.response_id},
            )

            # 신뢰도 향상
            member = self.pre_family_members.get(response.member_id)
            if member:
                member.trust_level = min(1.0, member.trust_level + 0.01)

            logger.info(f"응답 수용 및 학습 완료: {response.response_id}")

        except Exception as e:
            logger.error(f"응답 수용 및 학습 실패: {e}")

    async def _reject_and_improve(
        self, response: LearningResponse, evaluation: ResponseEvaluation
    ):
        """응답 거부 및 전략 교정"""
        try:
            # 거부 경험 저장
            rejection_experience = {
                "response_id": response.response_id,
                "question_text": self._get_question_text(response.question_id),
                "response_text": response.response_text,
                "evaluation": {
                    "overall_score": evaluation.overall_score,
                    "belief_alignment": evaluation.belief_alignment,
                    "feedback": evaluation.feedback,
                },
                "rejection_reason": "정체성 보호 또는 낮은 품질",
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source="pre_family_learning",
                content=rejection_experience,
                confidence=1.0 - evaluation.overall_score,
                tags=["pre_family", "rejected", "learning"],
                metadata={"response_id": response.response_id},
            )

            # 신뢰도 감소
            member = self.pre_family_members.get(response.member_id)
            if member:
                member.trust_level = max(0.1, member.trust_level - 0.02)

            logger.info(f"응답 거부 및 전략 교정: {response.response_id}")

        except Exception as e:
            logger.error(f"응답 거부 및 전략 교정 실패: {e}")

    def _get_question_text(self, question_id: str) -> str:
        """질문 텍스트 조회"""
        for question in self.learning_questions:
            if question.question_id == question_id:
                return question.question_text
        return "질문을 찾을 수 없습니다."

    def _update_learning_statistics(self, evaluation: ResponseEvaluation):
        """학습 통계 업데이트"""
        self.total_interactions += 1

        if evaluation.accepted:
            self.accepted_responses += 1
        else:
            self.rejected_responses += 1

        # 평균 품질 점수 업데이트
        total_score = sum(eval.overall_score for eval in self.response_evaluations)
        self.average_quality_score = (
            total_score / len(self.response_evaluations)
            if self.response_evaluations
            else 0.0
        )

    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 반환"""
        return {
            "total_interactions": self.total_interactions,
            "accepted_responses": self.accepted_responses,
            "rejected_responses": self.rejected_responses,
            "acceptance_rate": (
                self.accepted_responses / self.total_interactions
                if self.total_interactions > 0
                else 0.0
            ),
            "average_quality_score": self.average_quality_score,
            "total_questions": len(self.learning_questions),
            "total_responses": len(self.learning_responses),
            "total_evaluations": len(self.response_evaluations),
            "pre_family_members": {
                member_id: {
                    "name": member.name,
                    "type": member.type.value,
                    "trust_level": member.trust_level,
                    "interaction_count": member.interaction_count,
                    "last_interaction": (
                        member.last_interaction.isoformat()
                        if member.last_interaction
                        else None
                    ),
                }
                for member_id, member in self.pre_family_members.items()
            },
        }


def get_enhanced_pre_family_learning_system() -> EnhancedPreFamilyLearningSystem:
    """향상된 준 가족 학습 시스템 인스턴스 반환"""
    return EnhancedPreFamilyLearningSystem()
