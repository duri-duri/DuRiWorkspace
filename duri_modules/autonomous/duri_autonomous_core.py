import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from duri_brain.learning.auto_retrospector import AutoRetrospector
from duri_brain.learning.learning_loop_manager import LearningLoopManager

# 기존 시스템들 import
from duri_modules.autonomous.autonomous_question_generator import AutonomousQuestionGenerator
from duri_modules.autonomous.continuous_learner import AutonomousLearner
from duri_modules.autonomous.realtime_learner import RealtimeLearner
from duri_modules.autonomous.result_improver import ResultImprover
from duri_modules.autonomous.strategy_loop_runner import StrategyLoopRunner
from duri_modules.autonomous.unified_improvement_system import UnifiedImprovementSystem

logger = logging.getLogger(__name__)


@dataclass
class AutonomousLearningCycle:
    """자율 학습 사이클 결과"""

    cycle_id: str
    start_time: str
    end_time: str
    question_generated: bool
    learning_completed: bool
    improvement_applied: bool
    overall_score: float
    insights: List[str]
    next_actions: List[str]


class DuRiAutonomousCore:
    """DuRi 자율 학습 통합 핵심 시스템"""

    def __init__(self):
        # 기존 시스템들 초기화
        self.question_generator = AutonomousQuestionGenerator()
        self.result_improver = ResultImprover()
        self.strategy_runner = StrategyLoopRunner()
        self.unified_improver = UnifiedImprovementSystem()
        self.autonomous_learner = AutonomousLearner()
        self.realtime_learner = RealtimeLearner(self.autonomous_learner)

        # 기존 뇌 시스템들
        self.auto_retrospector = AutoRetrospector()
        self.learning_loop_manager = LearningLoopManager()
        # SelfEvolutionService는 db_session이 필요하므로 나중에 초기화
        self.self_evolution_service = None

        # 상태 관리
        self.is_active = False
        self.current_cycle = None
        self.learning_history = []

        logger.info("🧠 DuRi 자율 학습 통합 핵심 시스템 초기화 완료")

    async def start_autonomous_learning(self) -> bool:
        """자율 학습 시작"""
        try:
            self.is_active = True
            self.realtime_learner.start_realtime_learning()

            logger.info("🚀 DuRi 자율 학습 시스템 시작")
            return True

        except Exception as e:
            logger.error(f"❌ 자율 학습 시작 오류: {e}")
            return False

    async def stop_autonomous_learning(self) -> bool:
        """자율 학습 중지"""
        try:
            self.is_active = False
            self.realtime_learner.stop_realtime_learning()

            logger.info("🛑 DuRi 자율 학습 시스템 중지")
            return True

        except Exception as e:
            logger.error(f"❌ 자율 학습 중지 오류: {e}")
            return False

    async def execute_autonomous_learning_cycle(self, conversation_context: Dict[str, Any]) -> AutonomousLearningCycle:
        """완전한 자율 학습 사이클 실행"""
        try:
            cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = datetime.now().isoformat()

            logger.info(f"🔄 자율 학습 사이클 시작: {cycle_id}")

            # 1단계: 자율 질문 생성
            question_result = await self._generate_autonomous_question(conversation_context)

            # 2단계: 학습 실행
            learning_result = await self._execute_learning(question_result, conversation_context)

            # 3단계: 개선 적용
            improvement_result = await self._apply_improvements(learning_result, conversation_context)

            # 4단계: 메타 학습 업데이트
            meta_learning_result = await self._update_meta_learning(improvement_result)  # noqa: F841

            # 결과 생성
            end_time = datetime.now().isoformat()
            overall_score = self._calculate_cycle_score(question_result, learning_result, improvement_result)

            cycle_result = AutonomousLearningCycle(
                cycle_id=cycle_id,
                start_time=start_time,
                end_time=end_time,
                question_generated=question_result.get("success", False),
                learning_completed=learning_result.get("success", False),
                improvement_applied=improvement_result.get("success", False),
                overall_score=overall_score,
                insights=self._extract_insights(question_result, learning_result, improvement_result),
                next_actions=self._generate_next_actions(overall_score, improvement_result),
            )

            # 히스토리에 저장
            self.learning_history.append(cycle_result)

            logger.info(f"✅ 자율 학습 사이클 완료: {cycle_id} (점수: {overall_score:.3f})")

            return cycle_result

        except Exception as e:
            logger.error(f"❌ 자율 학습 사이클 오류: {e}")
            return None

    async def _generate_autonomous_question(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """자율 질문 생성"""
        try:
            # 학습 컨텍스트 준비
            learning_context = {
                "evaluation": context.get("evaluation", {}),
                "analysis": context.get("analysis", {}),
                "conversation": context.get("conversation", {}),
            }

            # 학습 세션 시작
            session = self.question_generator.start_learning_session(learning_context)

            if session:
                first_question = self.question_generator.get_next_question(session)

                return {
                    "success": True,
                    "session_id": session.session_id,
                    "question": first_question,
                    "total_questions": len(session.questions),
                    "learning_progress": session.learning_progress,
                }
            else:
                return {"success": False, "message": "학습 세션 시작 실패"}

        except Exception as e:
            logger.error(f"❌ 자율 질문 생성 오류: {e}")
            return {"success": False, "message": str(e)}

    async def _execute_learning(self, question_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """학습 실행"""
        try:
            if not question_result.get("success"):
                return {"success": False, "message": "질문 생성 실패"}

            # 자동 학습 시스템에 전달
            learning_metrics = {
                "question_id": question_result["question"].question_id,
                "question_text": question_result["question"].question_text,
                "category": question_result["question"].category,
                "difficulty": question_result["question"].difficulty,
                "context": context,
            }

            # 자동 학습 실행
            autonomous_result = self.autonomous_learner.process_learning_question(learning_metrics)

            # 실시간 학습에도 전달
            self.realtime_learner.add_conversation(
                question_result["question"].question_text,
                autonomous_result.get("response", "학습 처리 중..."),
            )

            return {
                "success": True,
                "autonomous_result": autonomous_result,
                "realtime_status": self.realtime_learner.get_realtime_status(),
            }

        except Exception as e:
            logger.error(f"❌ 학습 실행 오류: {e}")
            return {"success": False, "message": str(e)}

    async def _apply_improvements(self, learning_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """개선 적용"""
        try:
            if not learning_result.get("success"):
                return {"success": False, "message": "학습 실패"}

            # 개선 컨텍스트 준비
            improvement_context = {
                "learning_result": learning_result,
                "original_context": context,
                "evaluation": context.get("evaluation", {}),
            }

            # 결과 개선 실행
            improvement_result = self.result_improver.analyze_and_improve(improvement_context)

            # 전략 루프 실행
            strategy_result = self.strategy_runner.start_improvement_loop(improvement_context)

            # 통합 개선 시스템 실행
            unified_result = self.unified_improver.execute_comprehensive_improvement(
                improvement_context, improvement_context.get("categories", {})
            )

            return {
                "success": True,
                "improvement_result": improvement_result,
                "strategy_result": strategy_result,
                "unified_result": unified_result,
            }

        except Exception as e:
            logger.error(f"❌ 개선 적용 오류: {e}")
            return {"success": False, "message": str(e)}

    async def _update_meta_learning(self, improvement_result: Dict[str, Any]) -> Dict[str, Any]:
        """메타 학습 업데이트"""
        try:
            # 자동 성찰
            retrospection = self.auto_retrospector.reflect_on_learning_cycle(improvement_result)

            # 학습 루프 관리자 업데이트
            loop_update = self.learning_loop_manager.update_learning_strategy(retrospection)

            # 자기 진화 서비스 업데이트 (선택적)
            evolution_update = None
            if self.self_evolution_service:
                evolution_update = self.self_evolution_service.evolve_based_on_learning(improvement_result)

            return {
                "success": True,
                "retrospection": retrospection,
                "loop_update": loop_update,
                "evolution_update": evolution_update,
            }

        except Exception as e:
            logger.error(f"❌ 메타 학습 업데이트 오류: {e}")
            return {"success": False, "message": str(e)}

    def _calculate_cycle_score(
        self,
        question_result: Dict[str, Any],
        learning_result: Dict[str, Any],
        improvement_result: Dict[str, Any],
    ) -> float:
        """사이클 점수 계산"""
        scores = []

        # 질문 생성 점수
        if question_result.get("success"):
            scores.append(0.3)

        # 학습 완료 점수
        if learning_result.get("success"):
            scores.append(0.4)

        # 개선 적용 점수
        if improvement_result.get("success"):
            scores.append(0.3)

        return sum(scores) if scores else 0.0

    def _extract_insights(
        self,
        question_result: Dict[str, Any],
        learning_result: Dict[str, Any],
        improvement_result: Dict[str, Any],
    ) -> List[str]:
        """인사이트 추출"""
        insights = []

        if question_result.get("success"):
            insights.append("자율 질문 생성 성공")

        if learning_result.get("success"):
            insights.append("학습 프로세스 완료")

        if improvement_result.get("success"):
            insights.append("개선 적용 완료")

        return insights

    def _generate_next_actions(self, overall_score: float, improvement_result: Dict[str, Any]) -> List[str]:
        """다음 액션 생성"""
        actions = []

        if overall_score < 0.5:
            actions.append("기본 학습 강화 필요")
            actions.append("질문 생성 품질 개선")

        if overall_score >= 0.7:
            actions.append("고급 학습 주제 탐색")
            actions.append("복잡한 개선 전략 시도")

        return actions

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "is_active": self.is_active,
            "current_cycle": self.current_cycle,
            "total_cycles": len(self.learning_history),
            "autonomous_learner_status": self.autonomous_learner.get_status(),
            "realtime_learner_status": self.realtime_learner.get_realtime_status(),
            "question_generator_status": self.question_generator.get_system_status(),
            "recent_insights": (
                [cycle.insights for cycle in self.learning_history[-3:]] if self.learning_history else []
            ),
        }


# 전역 인스턴스
duri_autonomous_core = DuRiAutonomousCore()
