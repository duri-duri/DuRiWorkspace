from dataclasses import dataclass
from datetime import datetime
import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LearningQuestion:
    """학습 질문"""

    question_id: str
    question_text: str
    category: str  # 'concept', 'application', 'improvement', 'integration'
    difficulty: str  # 'easy', 'medium', 'hard'
    context: Dict[str, Any]
    expected_learning_value: float
    priority: str  # 'low', 'medium', 'high'
    generated_at: str


@dataclass
class LearningSession:
    """학습 세션"""

    session_id: str
    start_time: str
    questions: List[LearningQuestion]
    current_question_index: int
    learning_progress: float
    session_status: str  # 'active', 'completed', 'paused'


class AutonomousQuestionGenerator:
    """자율 질문 생성 시스템"""

    def __init__(self):
        self.learning_history = []
        self.question_templates = self._initialize_question_templates()
        self.learning_patterns = {}
        self.session_counter = 0

        logger.info("🧠 자율 질문 생성 시스템 초기화 완료")

    def _initialize_question_templates(self) -> Dict[str, List[str]]:
        """질문 템플릿 초기화"""
        return {
            "concept": [
                "{}의 핵심 개념은 무엇인가요?",
                "{}와 {}의 차이점은 무엇인가요?",
                "{}가 작동하는 원리는 무엇인가요?",
                "{}의 장단점은 무엇인가요?",
                "{}를 언제 사용해야 하나요?",
            ],
            "application": [
                "{}를 실제로 어떻게 구현하나요?",
                "{}에서 발생할 수 있는 문제점은 무엇인가요?",
                "{}를 개선하는 방법은 무엇인가요?",
                "{}와 함께 사용할 수 있는 도구는 무엇인가요?",
                "{}의 성능을 최적화하는 방법은 무엇인가요?",
            ],
            "improvement": [
                "{}의 어떤 부분을 개선할 수 있을까요?",
                "{}에서 더 나은 결과를 얻으려면 어떻게 해야 하나요?",
                "{}의 한계점은 무엇이고 어떻게 극복할 수 있을까요?",
                "{}를 더 효율적으로 만드는 방법은 무엇인가요?",
                "{}에서 사용자 경험을 개선하는 방법은 무엇인가요?",
            ],
            "integration": [
                "{}와 {}를 어떻게 통합할 수 있을까요?",
                "{}를 기존 시스템에 어떻게 적용할 수 있을까요?",
                "{}와 다른 기술들을 어떻게 조합할 수 있을까요?",
                "{}를 확장 가능한 구조로 만들려면 어떻게 해야 하나요?",
                "{}를 다른 프로젝트에 재사용하려면 어떻게 해야 하나요?",
            ],
        }

    def generate_learning_questions(
        self, learning_context: Dict[str, Any], num_questions: int = 5
    ) -> List[LearningQuestion]:
        """학습 질문 생성"""
        try:
            logger.info(f"🧠 자율 질문 생성 시작: {num_questions}개")

            questions = []
            available_topics = self._extract_learning_topics(learning_context)

            for i in range(num_questions):
                question = self._generate_single_question(
                    learning_context, available_topics, i
                )
                if question:
                    questions.append(question)

            logger.info(f"✅ 자율 질문 생성 완료: {len(questions)}개")
            return questions

        except Exception as e:
            logger.error(f"❌ 자율 질문 생성 오류: {e}")
            return []

    def _extract_learning_topics(self, learning_context: Dict[str, Any]) -> List[str]:
        """학습 컨텍스트에서 주제 추출"""
        topics = []

        # 평가 결과에서 주제 추출
        evaluation = learning_context.get("evaluation", {})
        if evaluation:
            # ChatGPT 평가에서 주제 추출
            chatgpt_eval = evaluation.get("chatgpt_evaluation", {})
            if chatgpt_eval:
                suggestions = chatgpt_eval.get("suggestions", [])
                for suggestion in suggestions:
                    if "코드" in suggestion or "구현" in suggestion:
                        topics.append("코딩")
                    if "설명" in suggestion or "이해" in suggestion:
                        topics.append("개념")
                    if "개선" in suggestion or "최적화" in suggestion:
                        topics.append("개선")

            # 자기성찰에서 주제 추출
            self_reflection = evaluation.get("self_reflection", {})
            if self_reflection:
                improvement_proposal = self_reflection.get("improvement_proposal", {})
                specific_improvements = improvement_proposal.get(
                    "specific_improvements", []
                )
                for improvement in specific_improvements:
                    if "코드" in improvement or "구현" in improvement:
                        topics.append("코딩")
                    if "구조" in improvement or "설명" in improvement:
                        topics.append("구조")
                    if "개선" in improvement:
                        topics.append("개선")

        # 분석 결과에서 주제 추출
        analysis = learning_context.get("analysis", {})
        if analysis:
            meaning = analysis.get("meaning", {})
            topic = meaning.get("topic", "일반")
            topics.append(topic)

        # 중복 제거 및 기본 주제 추가
        unique_topics = list(set(topics))
        if not unique_topics:
            unique_topics = ["DuRi", "자율학습", "개선"]

        return unique_topics

    def _generate_single_question(
        self,
        learning_context: Dict[str, Any],
        available_topics: List[str],
        question_index: int,
    ) -> Optional[LearningQuestion]:
        """단일 질문 생성"""
        try:
            # 질문 카테고리 선택
            categories = ["concept", "application", "improvement", "integration"]
            category = categories[question_index % len(categories)]

            # 주제 선택
            topic = random.choice(available_topics) if available_topics else "DuRi"

            # 난이도 결정
            difficulty = self._determine_difficulty(learning_context, question_index)

            # 질문 템플릿 선택 및 생성
            templates = self.question_templates.get(category, [])
            if templates:
                template = random.choice(templates)
                # 템플릿에 따라 다른 처리
                if template.count("{}") == 1:
                    question_text = template.format(topic)
                elif template.count("{}") == 2:
                    # 두 개의 주제가 필요한 경우
                    if len(available_topics) >= 2:
                        topic2 = random.choice(
                            [t for t in available_topics if t != topic]
                        )
                        question_text = template.format(topic, topic2)
                    else:
                        # 두 번째 주제가 없으면 기본값 사용
                        question_text = template.format(topic, "다른 기술")
                else:
                    question_text = template.format(topic)
            else:
                question_text = f"{topic}에 대해 더 자세히 설명해주세요."

            # 예상 학습 가치 계산
            expected_learning_value = self._calculate_learning_value(
                category, difficulty
            )

            # 우선순위 결정
            priority = self._determine_priority(learning_context, question_index)

            question = LearningQuestion(
                question_id=f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{question_index}",
                question_text=question_text,
                category=category,
                difficulty=difficulty,
                context=learning_context,
                expected_learning_value=expected_learning_value,
                priority=priority,
                generated_at=datetime.now().isoformat(),
            )

            return question

        except Exception as e:
            logger.error(f"❌ 단일 질문 생성 오류: {e}")
            return None

    def _determine_difficulty(
        self, learning_context: Dict[str, Any], question_index: int
    ) -> str:
        """난이도 결정"""
        # 학습 히스토리 기반 난이도 조정
        if len(self.learning_history) < 3:
            return "easy"
        elif len(self.learning_history) < 10:
            return "medium"
        else:
            return "hard"

    def _calculate_learning_value(self, category: str, difficulty: str) -> float:
        """학습 가치 계산"""
        base_values = {
            "concept": 0.3,
            "application": 0.5,
            "improvement": 0.7,
            "integration": 0.8,
        }

        difficulty_multipliers = {"easy": 0.8, "medium": 1.0, "hard": 1.2}

        base_value = base_values.get(category, 0.5)
        multiplier = difficulty_multipliers.get(difficulty, 1.0)

        return round(base_value * multiplier, 3)

    def _determine_priority(
        self, learning_context: Dict[str, Any], question_index: int
    ) -> str:
        """우선순위 결정"""
        # 첫 번째 질문은 높은 우선순위
        if question_index == 0:
            return "high"
        # 마지막 질문들도 높은 우선순위
        elif question_index >= 3:
            return "high"
        else:
            return "medium"

    def start_learning_session(
        self, learning_context: Dict[str, Any]
    ) -> LearningSession:
        """학습 세션 시작"""
        try:
            self.session_counter += 1
            session_id = f"session_{self.session_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 질문 생성
            questions = self.generate_learning_questions(
                learning_context, num_questions=5
            )

            session = LearningSession(
                session_id=session_id,
                start_time=datetime.now().isoformat(),
                questions=questions,
                current_question_index=0,
                learning_progress=0.0,
                session_status="active",
            )

            logger.info(f"📚 학습 세션 시작: {session_id} (질문 {len(questions)}개)")
            return session

        except Exception as e:
            logger.error(f"❌ 학습 세션 시작 오류: {e}")
            return None

    def get_next_question(self, session: LearningSession) -> Optional[LearningQuestion]:
        """다음 질문 가져오기"""
        try:
            if session.current_question_index < len(session.questions):
                question = session.questions[session.current_question_index]
                session.current_question_index += 1

                # 진행도 업데이트
                session.learning_progress = session.current_question_index / len(
                    session.questions
                )

                logger.info(f"📝 다음 질문: {question.question_text[:50]}...")
                return question
            else:
                # 모든 질문 완료
                session.session_status = "completed"
                session.learning_progress = 1.0
                logger.info(f"✅ 학습 세션 완료: {session.session_id}")
                return None

        except Exception as e:
            logger.error(f"❌ 다음 질문 가져오기 오류: {e}")
            return None

    def update_learning_patterns(
        self, session: LearningSession, question_result: Dict[str, Any]
    ):
        """학습 패턴 업데이트"""
        try:
            # 질문 결과 분석
            question_id = question_result.get("question_id")
            success = question_result.get("success", False)
            learning_value = question_result.get("learning_value", 0.0)

            # 패턴 저장
            pattern = {
                "question_id": question_id,
                "success": success,
                "learning_value": learning_value,
                "timestamp": datetime.now().isoformat(),
            }

            if session.session_id not in self.learning_patterns:
                self.learning_patterns[session.session_id] = []

            self.learning_patterns[session.session_id].append(pattern)

            logger.info(
                f"📊 학습 패턴 업데이트: {session.session_id} - 성공: {success}, 가치: {learning_value}"
            )

        except Exception as e:
            logger.error(f"❌ 학습 패턴 업데이트 오류: {e}")

    def get_learning_insights(self) -> Dict[str, Any]:
        """학습 인사이트 생성"""
        try:
            total_sessions = len(self.learning_patterns)
            total_questions = sum(
                len(patterns) for patterns in self.learning_patterns.values()
            )

            if total_questions == 0:
                return {"message": "아직 학습 데이터가 없습니다"}

            # 성공률 계산
            successful_questions = sum(
                sum(1 for pattern in patterns if pattern.get("success", False))
                for patterns in self.learning_patterns.values()
            )

            success_rate = successful_questions / total_questions

            # 평균 학습 가치
            total_learning_value = sum(
                sum(pattern.get("learning_value", 0.0) for pattern in patterns)
                for patterns in self.learning_patterns.values()
            )

            avg_learning_value = total_learning_value / total_questions

            # 추천 사항 생성
            recommendations = []
            if success_rate < 0.5:
                recommendations.append("기본 개념부터 다시 학습해보세요")
            elif success_rate < 0.8:
                recommendations.append("실용적 적용에 더 집중해보세요")
            else:
                recommendations.append("고급 통합 문제에 도전해보세요")

            return {
                "total_sessions": total_sessions,
                "total_questions": total_questions,
                "success_rate": round(success_rate, 3),
                "avg_learning_value": round(avg_learning_value, 3),
                "recommendations": recommendations,
                "learning_patterns": self.learning_patterns,
            }

        except Exception as e:
            logger.error(f"❌ 학습 인사이트 생성 오류: {e}")
            return {"error": str(e)}

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "total_sessions": len(self.learning_patterns),
            "question_templates": {
                category: len(templates)
                for category, templates in self.question_templates.items()
            },
            "learning_insights": self.get_learning_insights(),
        }


# 전역 인스턴스 생성
autonomous_question_generator = AutonomousQuestionGenerator()
