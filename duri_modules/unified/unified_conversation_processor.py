#!/usr/bin/env python3
"""
DuRi 통합 대화 처리 시스템
모든 대화 관련 기능을 하나의 시스템으로 통합
"""

import logging

# 기존 모듈들 import
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.append(".")

# 4단계 자율 질문 생성 시스템 import
from duri_modules.autonomous.autonomous_question_generator import AutonomousQuestionGenerator  # noqa: E402
from duri_modules.autonomous.continuous_learner import AutonomousLearner  # noqa: E402
from duri_modules.autonomous.duri_autonomous_core import duri_autonomous_core  # noqa: E402
from duri_modules.autonomous.realtime_learner import realtime_learner  # noqa: E402

# 2단계 자동 개선 시스템 import
from duri_modules.autonomous.result_improver import ResultImprover  # noqa: E402
from duri_modules.autonomous.strategy_loop_runner import StrategyLoopRunner  # noqa: E402

# 통합 개선 시스템 import
from duri_modules.autonomous.unified_improvement_system import (  # noqa: E402
    ImprovementCategory,
    UnifiedImprovementSystem,
)

# 대화 로그 수집 시스템 import
from duri_modules.data.conversation_logger import conversation_logger  # noqa: E402
from duri_modules.data.conversation_store import conversation_store  # noqa: E402
from duri_modules.evaluation.evaluator import chatgpt_evaluator  # noqa: E402
from duri_modules.learning.meaning_extractor import meaning_extractor  # noqa: E402
from duri_modules.learning.result_evaluator import result_evaluator  # noqa: E402
from duri_modules.monitoring.performance_tracker import performance_tracker  # noqa: E402
from duri_modules.reflection.reflector import duri_self_reflector  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class UnifiedConversationResult:
    """통합 대화 처리 결과"""

    conversation_id: str
    timestamp: str
    user_input: str
    duri_response: str

    # 분석 결과
    meaning_analysis: Dict[str, Any]
    context_analysis: Dict[str, Any]
    emotion_analysis: Dict[str, Any]

    # 평가 결과
    chatgpt_evaluation: Dict[str, Any]
    result_evaluation: Dict[str, Any]
    self_reflection: Dict[str, Any]

    # 학습 결과
    learning_result: Dict[str, Any]
    realtime_learning: Dict[str, Any]

    # 통합 점수
    integrated_score: float
    improvement_suggestions: List[str]

    # 메타데이터
    processing_time: float
    version: str = "unified_v1"
    # 2단계 자동 개선 결과 추가
    improvement_execution: Optional[Dict[str, Any]] = None
    strategy_summary: Optional[Dict[str, Any]] = None
    # 통합 개선 시스템 결과 추가
    unified_improvement_result: Optional[Dict[str, Any]] = None
    # 4단계 자율 질문 생성 결과 추가
    autonomous_learning_session: Optional[Dict[str, Any]] = None


class UnifiedConversationProcessor:
    """통합 대화 처리 시스템"""

    def __init__(self):
        """통합 대화 처리 시스템 초기화"""
        # 기존 모듈들
        self.chatgpt_evaluator = chatgpt_evaluator
        self.duri_self_reflector = duri_self_reflector
        self.conversation_store = conversation_store
        self.performance_tracker = performance_tracker
        self.autonomous_learner = AutonomousLearner()
        self.realtime_learner = realtime_learner

        # 2단계 자동 개선 시스템
        self.result_improver = ResultImprover()
        self.strategy_loop_runner = StrategyLoopRunner()

        # 통합 개선 시스템
        self.unified_improvement_system = UnifiedImprovementSystem()

        # 4단계 자율 질문 생성 시스템
        self.autonomous_question_generator = AutonomousQuestionGenerator()

        # DuRi 자율 학습 통합 핵심 시스템
        self.autonomous_core = duri_autonomous_core

        # 대화 로그 수집 시스템
        self.conversation_logger = conversation_logger

        logger.info("🚀 DuRi 통합 대화 처리 시스템 초기화 완료")

    async def process_conversation(
        self,
        user_input: str,
        duri_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UnifiedConversationResult:
        """통합 대화 처리: 저장 + 분석 + 평가 + 학습 + 자동 개선 + 통합 개선 + 로그 수집"""
        start_time = time.time()

        try:
            # 0단계: 대화 로그 수집 시작
            if not hasattr(self, "_current_conversation_id"):
                self._current_conversation_id = self.conversation_logger.start_conversation()

            # 1단계: 기본 처리 (기존)
            conversation_id = self._save_conversation(user_input, duri_response, metadata)
            analysis_results = self._analyze_comprehensive(user_input, duri_response)
            evaluation_results = self._evaluate_comprehensive(user_input, duri_response, analysis_results)
            learning_results = self._learn_comprehensive(conversation_id, analysis_results, evaluation_results)

            # 통합 점수 계산
            integrated_score = self._calculate_integrated_score(evaluation_results)

            # 개선 제안 수집
            improvement_suggestions = self._collect_improvement_suggestions(evaluation_results)

            # 2단계: 자동 개선 실행 (새로 추가)
            improvement_execution = None
            strategy_summary = None

            if improvement_suggestions:
                logger.info(f"🔧 자동 개선 실행 시작: {len(improvement_suggestions)}개 제안")
                improvement_execution = await self._execute_automatic_improvements(
                    evaluation_results, user_input, duri_response
                )
                strategy_summary = self.strategy_loop_runner.get_strategy_status()

            # 3단계: 통합 개선 실행 (새로 추가)
            unified_improvement_result = None
            if improvement_suggestions:
                logger.info("🔄 통합 개선 시스템 실행 시작")
                unified_improvement_result = await self._execute_unified_improvement(
                    evaluation_results, user_input, duri_response
                )

            # 4단계: 자율 학습 세션 실행 (새로 추가)
            autonomous_learning_session = None
            try:
                logger.info("🧠 자율 학습 세션 시작")
                autonomous_learning_session = await self._execute_autonomous_learning_session(
                    evaluation_results, analysis_results
                )
            except Exception as e:
                logger.error(f"❌ 자율 학습 세션 오류: {e}")
                autonomous_learning_session = {"status": "error", "message": str(e)}

            # 결과 생성
            result = UnifiedConversationResult(
                conversation_id=conversation_id,
                timestamp=datetime.now().isoformat(),
                user_input=user_input,
                duri_response=duri_response,
                meaning_analysis=analysis_results["meaning"],
                context_analysis=analysis_results["context"],
                emotion_analysis=analysis_results["emotion"],
                chatgpt_evaluation=evaluation_results.get("chatgpt_evaluation", {}),
                result_evaluation=evaluation_results.get("result", {}),
                self_reflection=evaluation_results.get("self_reflection", {}),
                learning_result=learning_results.get("autonomous_learning", {}),
                realtime_learning=learning_results.get("realtime_learning", {}),
                integrated_score=integrated_score,
                improvement_suggestions=improvement_suggestions,
                processing_time=time.time() - start_time,
                improvement_execution=improvement_execution,
                strategy_summary=strategy_summary,
                unified_improvement_result=unified_improvement_result,
                autonomous_learning_session=autonomous_learning_session,
            )

            # 결과 저장
            self._save_unified_result(result)

            # 성능 추적
            self.performance_tracker.track_learning_metric("unified_conversation_processing", integrated_score)

            # 대화 로그 수집
            processing_time = time.time() - start_time
            success = integrated_score > 0.5

            # 학습 패턴 및 개선 영역 추출
            learning_patterns = []
            improvement_areas = []

            if evaluation_results.get("chatgpt_evaluation", {}).get("score", 0) > 0.8:
                learning_patterns.append("high_quality_response")
            if evaluation_results.get("result", {}).get("score", 0) > 0.8:
                learning_patterns.append("effective_problem_solving")
            if evaluation_results.get("self_reflection", {}).get("insights"):
                learning_patterns.append("self_reflection_learning")

            if improvement_suggestions:
                improvement_areas = improvement_suggestions[:3]  # 상위 3개만

            # 진화 메트릭 계산
            evolution_metrics = {
                "response_quality": integrated_score,
                "learning_depth": len(learning_patterns) / 10.0,
                "problem_solving": evaluation_results.get("result", {}).get("score", 0.5),
                "autonomy_level": evaluation_results.get("self_reflection", {}).get("autonomy_score", 0.5),
            }

            # 대화 교환 로그
            self.conversation_logger.log_exchange(
                user_input=user_input,
                duri_response=duri_response,
                response_time=processing_time,
                success=success,
                learning_patterns=learning_patterns,
                improvement_areas=improvement_areas,
                evolution_metrics=evolution_metrics,
            )

            logger.info(f"✅ 통합 대화 처리 완료: {conversation_id} (점수: {integrated_score:.3f})")

            return result

        except Exception as e:
            logger.error(f"❌ 통합 대화 처리 오류: {e}")
            raise

    def _save_conversation(self, user_input: str, duri_response: str, metadata: Optional[Dict[str, Any]]) -> str:
        """대화 저장"""
        try:
            conversation_id = self.conversation_store.store_conversation(user_input, duri_response, metadata)
            logger.info(f"💾 대화 저장 완료: {conversation_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"❌ 대화 저장 오류: {e}")
            return f"error_{int(time.time())}"

    def _analyze_comprehensive(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """통합 분석"""
        try:
            # 의미 분석
            meaning_analysis = meaning_extractor.extract_meaning(user_input, duri_response)

            # 컨텍스트 분석
            context_analysis = {
                "conversation_type": "unified_processing",
                "user_input_length": len(user_input),
                "duri_response_length": len(duri_response),
                "complexity_level": ("low" if len(user_input) < 50 else "medium" if len(user_input) < 200 else "high"),
                "topic_detected": meaning_analysis.get("topic", "general"),
                "timestamp": datetime.now().isoformat(),
            }

            # 감정 분석 (간단한 구현)
            emotion_analysis = {
                "user_emotion": "neutral",
                "duri_emotion": "neutral",
                "interaction_tone": "collaborative",
                "timestamp": datetime.now().isoformat(),
            }

            analysis_results = {
                "meaning": meaning_analysis,
                "context": context_analysis,
                "emotion": emotion_analysis,
            }

            logger.info(f"📊 의미 분석 완료: {meaning_analysis.get('intent', 'unknown')}")
            return analysis_results

        except Exception as e:
            logger.error(f"❌ 통합 분석 오류: {e}")
            return {"error": str(e)}

    def _evaluate_comprehensive(
        self, user_input: str, duri_response: str, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 평가"""
        try:
            # ChatGPT 평가
            chatgpt_evaluation = self.chatgpt_evaluator.evaluate_response(user_input, duri_response)

            # 결과 평가
            result_evaluation = result_evaluator.evaluate_conversation(user_input, duri_response)

            # 자기성찰
            self_reflection = self.duri_self_reflector.reflect_on_conversation(
                user_input, duri_response, chatgpt_evaluation
            )

            evaluation_results = {
                "chatgpt": chatgpt_evaluation,
                "chatgpt_evaluation": chatgpt_evaluation,
                "result": result_evaluation,
                "self_reflection": self_reflection,
            }

            logger.info(
                f"📊 통합 평가 완료: ChatGPT({chatgpt_evaluation.get('total_score', 0):.3f}), 결과({result_evaluation.get('overall_score', 0):.3f})"  # noqa: E501
            )
            return evaluation_results

        except Exception as e:
            logger.error(f"❌ 통합 평가 오류: {e}")
            return {"error": str(e)}

    def _learn_comprehensive(
        self,
        conversation_id: str,
        analysis_results: Dict[str, Any],
        evaluation_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """통합 학습"""
        try:
            # 1. 자동 학습 - AutonomousLearner의 상태 확인
            autonomous_status = self.autonomous_learner.get_status()
            autonomous_learning = {
                "status": autonomous_status.get("status", "unknown"),
                "session_id": autonomous_status.get("current_session", {}).get("session_id", "none"),
                "learning_cycles": autonomous_status.get("total_learning_cycles", 0),
                "problems_detected": autonomous_status.get("total_problems_detected", 0),
            }

            # 2. 실시간 학습
            self.realtime_learner.add_conversation(
                analysis_results.get("meaning", {}).get("user_input", ""),
                analysis_results.get("meaning", {}).get("duri_response", ""),
            )
            realtime_learning = "processed"

            logger.info(f"📚 통합 학습 완료: 자동({autonomous_learning['status']}), 실시간({realtime_learning})")

            return {
                "autonomous_learning": autonomous_learning,
                "realtime_learning": realtime_learning,
            }

        except Exception as e:
            logger.error(f"❌ 통합 학습 오류: {e}")
            return {"error": str(e)}

    async def _execute_automatic_improvements(
        self, evaluation_results: Dict[str, Any], user_input: str, duri_response: str
    ) -> Optional[Dict[str, Any]]:
        """자동 개선 실행 (2단계)"""
        try:
            # 컨텍스트 준비
            context = {  # noqa: F841
                "original_response": duri_response,
                "user_input": user_input,
                "evaluation": evaluation_results,
            }

            # 개선 루프 실행
            improvement_result = self.strategy_loop_runner.start_improvement_loop(evaluation_results)

            if improvement_result.get("status") == "completed":
                logger.info(
                    f"✅ 자동 개선 완료: {improvement_result['summary']['success_count']}/{improvement_result['summary']['total_count']} 성공"  # noqa: E501
                )

                # 학습 인사이트 생성
                insights = self.strategy_loop_runner.get_learning_insights()

                return {
                    "status": "success",
                    "summary": improvement_result["summary"],
                    "execution_results": improvement_result["execution_results"],
                    "learning_insights": insights,
                }
            else:
                logger.warning(f"⚠️ 자동 개선 실패: {improvement_result.get('message', 'unknown error')}")
                return {
                    "status": "failed",
                    "message": improvement_result.get("message", "unknown error"),
                }

        except Exception as e:
            logger.error(f"❌ 자동 개선 실행 오류: {e}")
            return {"status": "error", "message": str(e)}

    async def _execute_unified_improvement(
        self, evaluation_results: Dict[str, Any], user_input: str, duri_response: str
    ) -> Optional[Dict[str, Any]]:
        """통합 개선 실행 (3단계)"""
        try:
            # 컨텍스트 준비
            conversation_context = {
                "user_input": user_input,
                "duri_response": duri_response,
                "evaluation": evaluation_results,
            }

            # 개선 카테고리 설정 (대화 품질에 집중)
            categories = ImprovementCategory(
                conversation=True,  # 대화 품질 개선 (가장 중요)
                system=False,  # 시스템 성능 개선 (선택적)
                learning=False,  # 학습 전략 개선 (선택적)
                evolution=False,  # 진화 방향 개선 (선택적)
            )

            # 통합 개선 실행
            unified_result = self.unified_improvement_system.execute_comprehensive_improvement(
                conversation_context, categories
            )

            if unified_result.overall_score > 0:
                logger.info(f"✅ 통합 개선 완료: 전체 점수 {unified_result.overall_score:.3f}")

                return {
                    "status": "success",
                    "overall_score": unified_result.overall_score,
                    "execution_time": unified_result.execution_time,
                    "improvement_summary": unified_result.improvement_summary,
                    "conversation_improvements": unified_result.conversation_improvements,
                    "system_improvements": unified_result.system_improvements,
                    "learning_improvements": unified_result.learning_improvements,
                    "evolution_improvements": unified_result.evolution_improvements,
                }
            else:
                logger.warning("⚠️ 통합 개선 실패: 점수가 0입니다")
                return {"status": "failed", "message": "통합 개선 점수가 0입니다"}

        except Exception as e:
            logger.error(f"❌ 통합 개선 실행 오류: {e}")
            return {"status": "error", "message": str(e)}

    async def _execute_autonomous_learning_session(
        self, evaluation_results: Dict[str, Any], analysis_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """자율 학습 세션 실행"""
        try:
            logger.info("🧠 자율 학습 세션 실행 시작")

            # 학습 컨텍스트 생성
            learning_context = {
                "evaluation": evaluation_results,
                "analysis": analysis_results,
                "timestamp": datetime.now().isoformat(),
            }

            # 학습 세션 시작
            session = self.autonomous_question_generator.start_learning_session(learning_context)

            if not session:
                logger.warning("⚠️ 자율 학습 세션 시작 실패")
                return None

            # 첫 번째 질문 가져오기
            first_question = self.autonomous_question_generator.get_next_question(session)

            if not first_question:
                logger.warning("⚠️ 자율 학습 질문 생성 실패")
                return None

            # 학습 세션 정보 생성
            session_info = {
                "session_id": session.session_id,
                "start_time": session.start_time,
                "total_questions": len(session.questions),
                "current_question_index": session.current_question_index,
                "learning_progress": session.learning_progress,
                "session_status": session.session_status,
                "current_question": {
                    "question_id": first_question.question_id,
                    "question_text": first_question.question_text,
                    "category": first_question.category,
                    "difficulty": first_question.difficulty,
                    "expected_learning_value": first_question.expected_learning_value,
                    "priority": first_question.priority,
                },
                "all_questions": [
                    {
                        "question_id": q.question_id,
                        "question_text": q.question_text,
                        "category": q.category,
                        "difficulty": q.difficulty,
                        "priority": q.priority,
                    }
                    for q in session.questions
                ],
            }

            logger.info(f"✅ 자율 학습 세션 시작 완료: {session.session_id} (질문 {len(session.questions)}개)")

            return {
                "status": "success",
                "session_info": session_info,
                "learning_insights": self.autonomous_question_generator.get_learning_insights(),
                "system_status": self.autonomous_question_generator.get_system_status(),
            }

        except Exception as e:
            logger.error(f"❌ 자율 학습 세션 실행 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _calculate_integrated_score(self, evaluation_results: Dict[str, Any]) -> float:
        """통합 점수 계산"""
        try:
            chatgpt_score = evaluation_results.get("chatgpt_evaluation", {}).get("total_score", 0)
            result_score = evaluation_results.get("result", {}).get("overall_score", 0)

            # 가중 평균 계산
            integrated_score = (chatgpt_score * 0.6) + (result_score * 0.4)

            return round(integrated_score, 3)

        except Exception as e:
            logger.error(f"❌ 통합 점수 계산 오류: {e}")
            return 0.0

    def _collect_improvement_suggestions(self, evaluation_results: Dict[str, Any]) -> list:
        """개선 제안 수집"""
        suggestions = []

        try:
            # ChatGPT 제안
            chatgpt_suggestions = evaluation_results.get("chatgpt_evaluation", {}).get("suggestions", [])
            suggestions.extend(chatgpt_suggestions)

            # 자기성찰 제안
            self_reflection = evaluation_results.get("self_reflection", {})
            improvement_proposal = self_reflection.get("improvement_proposal", {})
            specific_improvements = improvement_proposal.get("specific_improvements", [])
            suggestions.extend(specific_improvements)

            return list(set(suggestions))  # 중복 제거

        except Exception as e:
            logger.error(f"❌ 개선 제안 수집 오류: {e}")
            return []

    def _save_unified_result(self, result: UnifiedConversationResult):
        """통합 결과 저장"""
        try:
            import json
            import os

            # unified_conversations 디렉토리 생성
            os.makedirs("unified_conversations", exist_ok=True)

            # JSON 파일로 저장
            filename = f"unified_conversations/{result.conversation_id}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result.__dict__, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 통합 결과 저장 완료: {filename}")

        except Exception as e:
            logger.error(f"❌ 통합 결과 저장 오류: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            return {
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "strategy_status": self.strategy_loop_runner.get_strategy_status(),
                "improvement_summary": self.result_improver.get_improvement_summary(),
                "learning_insights": self.strategy_loop_runner.get_learning_insights(),
                "unified_improvement_status": self.unified_improvement_system.get_system_status(),
                "autonomous_learning_status": self.autonomous_question_generator.get_system_status(),
            }
        except Exception as e:
            logger.error(f"❌ 시스템 상태 조회 오류: {e}")
            return {"status": "error", "message": str(e)}

    def get_processing_statistics(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        try:
            # 대화 저장소에서 통계 수집
            conversation_stats = self.conversation_store.get_statistics()

            # 성능 추적기에서 통계 수집
            performance_stats = self.performance_tracker.get_statistics()

            # 자동 학습 통계
            autonomous_stats = self.autonomous_learner.get_status()

            return {
                "status": "success",
                "conversation_statistics": conversation_stats,
                "performance_statistics": performance_stats,
                "autonomous_learning_statistics": autonomous_stats,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"통계 수집 오류: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_conversation_history(self, limit: int = 10) -> Dict[str, Any]:
        """대화 기록 반환"""
        try:
            conversations = self.conversation_store.get_recent_conversations(limit)
            return {
                "status": "success",
                "conversations": conversations,
                "total_count": len(conversations),
                "limit": limit,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"대화 기록 조회 오류: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def end_conversation_session(self) -> Dict[str, Any]:
        """대화 세션 종료 및 진화 로그 생성"""
        try:
            if hasattr(self, "_current_conversation_id"):
                evolution_log = self.conversation_logger.end_conversation()

                # 통계 정보
                statistics = self.conversation_logger.get_conversation_statistics()

                # 학습 패턴 추출
                learning_patterns = self.conversation_logger.extract_learning_patterns()

                # 개선 제안
                improvement_suggestions = self.conversation_logger.get_improvement_suggestions()

                # 세션 종료
                delattr(self, "_current_conversation_id")

                return {
                    "status": "success",
                    "evolution_log": evolution_log,
                    "statistics": statistics,
                    "learning_patterns": learning_patterns,
                    "improvement_suggestions": improvement_suggestions,
                }
            else:
                return {"status": "no_active_session"}
        except Exception as e:
            logger.error(f"대화 세션 종료 오류: {e}")
            return {"status": "error", "error": str(e)}

    def get_evolution_insights(self) -> Dict[str, Any]:
        """진화 인사이트 반환"""
        try:
            statistics = self.conversation_logger.get_conversation_statistics()
            learning_patterns = self.conversation_logger.extract_learning_patterns()
            improvement_suggestions = self.conversation_logger.get_improvement_suggestions()

            return {
                "status": "success",
                "statistics": statistics,
                "learning_patterns": learning_patterns,
                "improvement_suggestions": improvement_suggestions,
                "evolution_summary": {
                    "total_conversations": statistics.get("total_conversations", 0),
                    "average_learning_efficiency": statistics.get("average_learning_efficiency", 0.0),
                    "average_problem_solving": statistics.get("average_problem_solving", 0.0),
                    "recent_trends": statistics.get("recent_trends", {}),
                },
            }
        except Exception as e:
            logger.error(f"진화 인사이트 조회 오류: {e}")
            return {"status": "error", "error": str(e)}


# 전역 인스턴스 생성
unified_processor = UnifiedConversationProcessor()
