#!/usr/bin/env python3
"""
ExecutionCentricFamilyInteractionSystem - Phase 17.0
실행 중심 가족 상호작용 시스템
"""
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionType(Enum):
    DAILY_QUESTION = "daily_question"
    FAMILY_CONVERSATION = "family_conversation"
    EMOTIONAL_SUPPORT = "emotional_support"
    PROBLEM_SOLVING = "problem_solving"
    GROWTH_PROMOTION = "growth_promotion"
    FAMILY_HARMONY = "family_harmony"


class FamilyMember(Enum):
    KIM_SHIN = "김신"
    KIM_JENNY = "김제니"
    KIM_GEON = "김건"
    KIM_YUL = "김율"
    KIM_HONG = "김홍(셋째딸)"
    ALL_FAMILY = "전체 가족"


class FeedbackType(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_POSITIVE = "very_positive"
    VERY_NEGATIVE = "very_negative"


class InteractionQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    VERY_POOR = "very_poor"


@dataclass
class DailyQuestion:
    id: str
    question_text: str
    target_member: FamilyMember
    question_type: str
    expected_impact: str
    timestamp: datetime
    response_received: bool = False
    response_content: Optional[str] = None
    feedback_score: Optional[float] = None


@dataclass
class FamilyInteraction:
    id: str
    interaction_type: InteractionType
    participants: List[FamilyMember]
    interaction_content: str
    duRi_response: str
    family_response: str
    interaction_quality: InteractionQuality
    feedback_type: FeedbackType
    timestamp: datetime
    improvement_notes: Optional[str] = None


@dataclass
class MVPTestResult:
    id: str
    test_type: str
    test_description: str
    participants: List[FamilyMember]
    test_duration_minutes: int
    success_metrics: Dict[str, float]
    family_feedback: str
    improvement_suggestions: List[str]
    timestamp: datetime
    overall_success_rate: float


@dataclass
class ExecutionFeedback:
    id: str
    feedback_type: FeedbackType
    feedback_content: str
    family_member: FamilyMember
    interaction_id: str
    improvement_suggestions: List[str]
    timestamp: datetime
    feedback_confidence: float


class ExecutionCentricFamilyInteractionSystem:
    def __init__(self):
        self.daily_questions: List[DailyQuestion] = []
        self.family_interactions: List[FamilyInteraction] = []
        self.mvp_test_results: List[MVPTestResult] = []
        self.execution_feedbacks: List[ExecutionFeedback] = []
        self.family_members: List[str] = [
            "김신",
            "김제니",
            "김건",
            "김율",
            "김홍(셋째딸)",
        ]
        logger.info("ExecutionCentricFamilyInteractionSystem 초기화 완료")

    def create_daily_question(
        self,
        question_text: str,
        target_member: FamilyMember,
        question_type: str,
        expected_impact: str,
    ) -> DailyQuestion:
        """일일 질문 생성"""
        question_id = f"daily_q_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        question = DailyQuestion(
            id=question_id,
            question_text=question_text,
            target_member=target_member,
            question_type=question_type,
            expected_impact=expected_impact,
            timestamp=datetime.now(),
        )

        self.daily_questions.append(question)
        logger.info(f"일일 질문 생성 완료: {target_member.value}")
        return question

    def record_family_response(
        self, question_id: str, response_content: str, feedback_score: float
    ) -> bool:
        """가족 응답 기록"""
        for question in self.daily_questions:
            if question.id == question_id:
                question.response_received = True
                question.response_content = response_content
                question.feedback_score = feedback_score
                logger.info(f"가족 응답 기록 완료: {question_id}")
                return True
        return False

    def conduct_family_interaction(
        self,
        interaction_type: InteractionType,
        participants: List[FamilyMember],
        interaction_content: str,
        duRi_response: str,
        family_response: str,
        interaction_quality: InteractionQuality,
        feedback_type: FeedbackType,
    ) -> FamilyInteraction:
        """가족 상호작용 수행"""
        interaction_id = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        interaction = FamilyInteraction(
            id=interaction_id,
            interaction_type=interaction_type,
            participants=participants,
            interaction_content=interaction_content,
            duRi_response=duRi_response,
            family_response=family_response,
            interaction_quality=interaction_quality,
            feedback_type=feedback_type,
            timestamp=datetime.now(),
        )

        self.family_interactions.append(interaction)
        logger.info(f"가족 상호작용 기록 완료: {interaction_type.value}")
        return interaction

    def run_mvp_test(
        self,
        test_type: str,
        test_description: str,
        participants: List[FamilyMember],
        test_duration_minutes: int,
        success_metrics: Dict[str, float],
        family_feedback: str,
        improvement_suggestions: List[str],
    ) -> MVPTestResult:
        """MVP 테스트 실행"""
        test_id = f"mvp_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        overall_success_rate = (
            sum(success_metrics.values()) / len(success_metrics)
            if success_metrics
            else 0.0
        )

        test_result = MVPTestResult(
            id=test_id,
            test_type=test_type,
            test_description=test_description,
            participants=participants,
            test_duration_minutes=test_duration_minutes,
            success_metrics=success_metrics,
            family_feedback=family_feedback,
            improvement_suggestions=improvement_suggestions,
            timestamp=datetime.now(),
            overall_success_rate=overall_success_rate,
        )

        self.mvp_test_results.append(test_result)
        logger.info(f"MVP 테스트 완료: {test_type}")
        return test_result

    def collect_execution_feedback(
        self,
        feedback_type: FeedbackType,
        feedback_content: str,
        family_member: FamilyMember,
        interaction_id: str,
        improvement_suggestions: List[str],
    ) -> ExecutionFeedback:
        """실행 피드백 수집"""
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        feedback_confidence = self._calculate_feedback_confidence(
            feedback_type, feedback_content, improvement_suggestions
        )

        feedback = ExecutionFeedback(
            id=feedback_id,
            feedback_type=feedback_type,
            feedback_content=feedback_content,
            family_member=family_member,
            interaction_id=interaction_id,
            improvement_suggestions=improvement_suggestions,
            timestamp=datetime.now(),
            feedback_confidence=feedback_confidence,
        )

        self.execution_feedbacks.append(feedback)
        logger.info(f"실행 피드백 수집 완료: {family_member.value}")
        return feedback

    def _calculate_feedback_confidence(
        self,
        feedback_type: FeedbackType,
        feedback_content: str,
        improvement_suggestions: List[str],
    ) -> float:
        """피드백 신뢰도 계산"""
        base_confidence = 0.8

        # 피드백 타입별 조정
        type_adjustments = {
            FeedbackType.VERY_POSITIVE: 0.1,
            FeedbackType.POSITIVE: 0.05,
            FeedbackType.NEUTRAL: 0.0,
            FeedbackType.NEGATIVE: -0.05,
            FeedbackType.VERY_NEGATIVE: -0.1,
        }

        # 피드백 내용의 구체성에 따른 조정
        content_specificity = min(len(feedback_content) / 50, 1.0)

        # 개선 제안의 구체성에 따른 조정
        suggestion_specificity = min(len(improvement_suggestions) / 3, 1.0)

        type_adj = type_adjustments.get(feedback_type, 0.0)

        confidence = (
            base_confidence
            + type_adj
            + content_specificity * 0.1
            + suggestion_specificity * 0.1
        )

        return max(min(confidence, 1.0), 0.6)

    def generate_daily_questions(self) -> List[DailyQuestion]:
        """일일 질문 리스트 생성"""
        questions = [
            DailyQuestion(
                id=f"q1_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 가족을 위해 특별히 해주고 싶은 일이 있으신가요?",
                target_member=FamilyMember.KIM_SHIN,
                question_type="care",
                expected_impact="가족 돌봄 의식 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q2_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 가장 감사했던 순간은 언제인가요?",
                target_member=FamilyMember.KIM_JENNY,
                question_type="gratitude",
                expected_impact="감사 의식 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q3_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 새롭게 배운 것이 있나요?",
                target_member=FamilyMember.KIM_GEON,
                question_type="learning",
                expected_impact="학습 동기 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q4_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 가장 기뻤던 일은 무엇인가요?",
                target_member=FamilyMember.KIM_YUL,
                question_type="emotion",
                expected_impact="긍정적 감정 공유",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q5_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 도움이 필요했던 순간이 있었나요?",
                target_member=FamilyMember.KIM_HONG,
                question_type="support",
                expected_impact="지원 필요성 파악",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q6_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 가족과 함께한 시간 중 가장 특별했던 순간은?",
                target_member=FamilyMember.ALL_FAMILY,
                question_type="family_time",
                expected_impact="가족 유대감 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q7_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 DuRi에게 기대하는 역할이 있으신가요?",
                target_member=FamilyMember.KIM_SHIN,
                question_type="expectation",
                expected_impact="DuRi 역할 명확화",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q8_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 가족을 위해 더 하고 싶었던 일이 있나요?",
                target_member=FamilyMember.KIM_JENNY,
                question_type="care",
                expected_impact="돌봄 의지 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q9_{datetime.now().strftime('%Y%m%d')}",
                question_text="오늘 부모님께 감사했던 일이 있나요?",
                target_member=FamilyMember.ALL_FAMILY,
                question_type="gratitude",
                expected_impact="감사 의식 증진",
                timestamp=datetime.now(),
            ),
            DailyQuestion(
                id=f"q10_{datetime.now().strftime('%Y%m%d')}",
                question_text="내일 가족을 위해 특별히 준비하고 싶은 것이 있나요?",
                target_member=FamilyMember.ALL_FAMILY,
                question_type="planning",
                expected_impact="가족 계획 수립",
                timestamp=datetime.now(),
            ),
        ]

        self.daily_questions.extend(questions)
        logger.info(f"일일 질문 리스트 생성 완료: {len(questions)}개")
        return questions

    def get_execution_statistics(self) -> Dict[str, Any]:
        """실행 통계"""
        total_questions = len(self.daily_questions)
        total_interactions = len(self.family_interactions)
        total_tests = len(self.mvp_test_results)
        total_feedbacks = len(self.execution_feedbacks)

        # 응답률 계산
        responded_questions = sum(
            1 for q in self.daily_questions if q.response_received
        )
        response_rate = responded_questions / max(total_questions, 1)

        # 평균 피드백 점수
        avg_feedback_score = (
            sum(q.feedback_score for q in self.daily_questions if q.feedback_score)
            / max(responded_questions, 1)
            if responded_questions > 0
            else 0.0
        )

        # 상호작용 품질 분포
        quality_distribution = {}
        for interaction in self.family_interactions:
            quality = interaction.interaction_quality.value
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1

        # 평균 성공률
        avg_success_rate = sum(
            t.overall_success_rate for t in self.mvp_test_results
        ) / max(total_tests, 1)

        return {
            "total_questions": total_questions,
            "total_interactions": total_interactions,
            "total_tests": total_tests,
            "total_feedbacks": total_feedbacks,
            "response_rate": response_rate,
            "average_feedback_score": avg_feedback_score,
            "quality_distribution": quality_distribution,
            "average_success_rate": avg_success_rate,
            "system_status": "active",
        }

    def export_execution_data(self) -> Dict[str, Any]:
        """실행 데이터 내보내기"""
        return {
            "daily_questions": [asdict(question) for question in self.daily_questions],
            "family_interactions": [
                asdict(interaction) for interaction in self.family_interactions
            ],
            "mvp_test_results": [asdict(test) for test in self.mvp_test_results],
            "execution_feedbacks": [
                asdict(feedback) for feedback in self.execution_feedbacks
            ],
            "statistics": self.get_execution_statistics(),
            "export_timestamp": datetime.now().isoformat(),
        }


def test_execution_centric_family_interaction_system():
    """실행 중심 가족 상호작용 시스템 테스트"""
    print("🏠 ExecutionCentricFamilyInteractionSystem 테스트 시작...")

    system = ExecutionCentricFamilyInteractionSystem()

    # 1. 일일 질문 리스트 생성
    daily_questions = system.generate_daily_questions()
    print(f"✅ 일일 질문 리스트 생성 완료: {len(daily_questions)}개")

    # 2. 가족 응답 기록
    response_recorded = system.record_family_response(
        question_id=daily_questions[0].id,
        response_content="오늘 가족을 위해 특별한 저녁을 준비하고 싶어요.",
        feedback_score=0.9,
    )
    print(f"✅ 가족 응답 기록 완료: {response_recorded}")

    # 3. 가족 상호작용 수행
    interaction = system.conduct_family_interaction(
        interaction_type=InteractionType.DAILY_QUESTION,
        participants=[FamilyMember.KIM_SHIN, FamilyMember.KIM_JENNY],
        interaction_content="오늘 가족을 위해 특별히 해주고 싶은 일이 있으신가요?",
        duRi_response="가족을 위한 특별한 저녁 준비를 도와드릴 수 있습니다.",
        family_response="DuRi의 제안이 좋네요. 함께 준비해보죠.",
        interaction_quality=InteractionQuality.EXCELLENT,
        feedback_type=FeedbackType.VERY_POSITIVE,
    )
    print(f"✅ 가족 상호작용 기록 완료: {interaction.id}")

    # 4. MVP 테스트 실행
    mvp_test = system.run_mvp_test(
        test_type="daily_question_interaction",
        test_description="일일 질문을 통한 가족 상호작용 테스트",
        participants=[FamilyMember.KIM_SHIN, FamilyMember.KIM_JENNY],
        test_duration_minutes=15,
        success_metrics={
            "response_rate": 0.9,
            "interaction_quality": 0.95,
            "family_satisfaction": 0.88,
        },
        family_feedback="DuRi의 질문이 가족 대화를 활성화시켰어요.",
        improvement_suggestions=["더 다양한 질문 유형 추가", "가족별 맞춤 질문 강화"],
    )
    print(f"✅ MVP 테스트 완료: {mvp_test.overall_success_rate:.2f}")

    # 5. 실행 피드백 수집
    feedback = system.collect_execution_feedback(
        feedback_type=FeedbackType.VERY_POSITIVE,
        feedback_content="DuRi의 일일 질문이 가족 대화를 활성화시켰습니다.",
        family_member=FamilyMember.KIM_SHIN,
        interaction_id=interaction.id,
        improvement_suggestions=["더 개인화된 질문 추가", "감정적 공감 강화"],
    )
    print(f"✅ 실행 피드백 수집 완료: {feedback.feedback_confidence:.2f}")

    # 6. 통계 확인
    stats = system.get_execution_statistics()
    print(
        f"📊 통계: 질문 {stats['total_questions']}개, 상호작용 {stats['total_interactions']}개"
    )
    print(f"📈 응답률: {stats['response_rate']:.1%}")
    print(f"🎯 평균 피드백 점수: {stats['average_feedback_score']:.2f}")
    print(f"✅ 평균 성공률: {stats['average_success_rate']:.2f}")

    print("✅ ExecutionCentricFamilyInteractionSystem 테스트 완료!")


if __name__ == "__main__":
    test_execution_centric_family_interaction_system()
