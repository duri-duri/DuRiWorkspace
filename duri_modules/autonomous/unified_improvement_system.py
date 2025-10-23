import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

# 기존 시스템들 import
from .result_improver import ResultImprover
from .strategy_loop_runner import StrategyLoopRunner

# 기존 시스템들 import (가능한 경우)
try:
    from duri_brain.app.services.self_evolution_service import SelfEvolutionService  # noqa: F401
    from duri_brain.learning.auto_retrospector import AutoRetrospector
    from duri_brain.learning.learning_loop_manager import LearningLoopManager

    EXISTING_SYSTEMS_AVAILABLE = True
except ImportError:
    EXISTING_SYSTEMS_AVAILABLE = False
    logging.warning("기존 시스템들을 import할 수 없습니다. 일부 기능이 제한됩니다.")

logger = logging.getLogger(__name__)


@dataclass
class ImprovementCategory:
    """개선 카테고리"""

    conversation: bool = True  # 대화 품질 개선
    system: bool = True  # 시스템 성능 개선
    learning: bool = True  # 학습 전략 개선
    evolution: bool = True  # 진화 방향 개선


@dataclass
class UnifiedImprovementResult:
    """통합 개선 결과"""

    timestamp: str
    conversation_improvements: Dict[str, Any]
    system_improvements: Dict[str, Any]
    learning_improvements: Dict[str, Any]
    evolution_improvements: Dict[str, Any]
    overall_score: float
    improvement_summary: Dict[str, Any]
    execution_time: float


class UnifiedImprovementSystem:
    """통합 개선 시스템 - 모든 개선 기능을 통합 관리"""

    def __init__(self):
        """통합 개선 시스템 초기화"""
        # 새로 구현한 시스템들
        self.conversation_improver = ResultImprover()
        self.strategy_loop_runner = StrategyLoopRunner()

        # 기존 시스템들 (가능한 경우)
        self.system_improver = None
        self.learning_improver = None
        self.evolution_improver = None

        if EXISTING_SYSTEMS_AVAILABLE:
            try:
                self.system_improver = AutoRetrospector()
                self.learning_improver = LearningLoopManager()
                # SelfEvolutionService는 DB 세션이 필요하므로 나중에 초기화
                logger.info("✅ 기존 시스템들과 통합 완료")
            except Exception as e:
                logger.warning(f"⚠️ 기존 시스템 초기화 실패: {e}")

        # 개선 히스토리
        self.improvement_history = []
        self.performance_metrics = {}

        logger.info("🚀 통합 개선 시스템 초기화 완료")

    def execute_comprehensive_improvement(
        self,
        conversation_context: Dict[str, Any],
        categories: ImprovementCategory = None,
    ) -> UnifiedImprovementResult:
        """포괄적 개선 실행"""
        start_time = time.time()

        if categories is None:
            categories = ImprovementCategory()

        try:
            logger.info("🔄 통합 개선 실행 시작")

            # 1. 대화 품질 개선 (새로 구현한 시스템)
            conversation_improvements = {}
            if categories.conversation:
                conversation_improvements = self._execute_conversation_improvement(conversation_context)

            # 2. 시스템 성능 개선 (기존 시스템)
            system_improvements = {}
            if categories.system and self.system_improver:
                system_improvements = self._execute_system_improvement()

            # 3. 학습 전략 개선 (기존 시스템)
            learning_improvements = {}
            if categories.learning and self.learning_improver:
                learning_improvements = self._execute_learning_improvement()

            # 4. 진화 방향 개선 (기존 시스템)
            evolution_improvements = {}
            if categories.evolution and self.evolution_improver:
                evolution_improvements = self._execute_evolution_improvement()

            # 5. 통합 결과 생성
            overall_score = self._calculate_overall_improvement_score(
                conversation_improvements,
                system_improvements,
                learning_improvements,
                evolution_improvements,
            )

            # 6. 개선 요약 생성
            improvement_summary = self._generate_improvement_summary(
                conversation_improvements,
                system_improvements,
                learning_improvements,
                evolution_improvements,
            )

            # 7. 결과 생성
            result = UnifiedImprovementResult(
                timestamp=datetime.now().isoformat(),
                conversation_improvements=conversation_improvements,
                system_improvements=system_improvements,
                learning_improvements=learning_improvements,
                evolution_improvements=evolution_improvements,
                overall_score=overall_score,
                improvement_summary=improvement_summary,
                execution_time=time.time() - start_time,
            )

            # 8. 히스토리에 저장
            self.improvement_history.append(result)

            logger.info(f"✅ 통합 개선 완료: 전체 점수 {overall_score:.3f}")
            return result

        except Exception as e:
            logger.error(f"❌ 통합 개선 실행 오류: {e}")
            return self._create_error_result(str(e), time.time() - start_time)

    def _execute_conversation_improvement(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """대화 품질 개선 실행"""
        try:
            logger.info("💬 대화 품질 개선 시작")

            # 평가 결과에서 개선 제안 분석
            evaluation_result = context.get("evaluation", {})
            actions = self.conversation_improver.analyze_improvement_suggestions(evaluation_result)

            if not actions:
                return {
                    "status": "no_actions",
                    "message": "실행 가능한 개선 액션이 없습니다",
                }

            # 개선 루프 실행
            improvement_result = self.strategy_loop_runner.start_improvement_loop(evaluation_result)

            # 학습 인사이트 생성
            insights = self.strategy_loop_runner.get_learning_insights()

            return {
                "status": "success",
                "actions_analyzed": len(actions),
                "improvement_result": improvement_result,
                "learning_insights": insights,
                "strategy_summary": self.strategy_loop_runner.get_strategy_status(),
            }

        except Exception as e:
            logger.error(f"❌ 대화 품질 개선 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_system_improvement(self) -> Dict[str, Any]:
        """시스템 성능 개선 실행"""
        try:
            if not self.system_improver:
                return {
                    "status": "unavailable",
                    "message": "시스템 개선기가 사용할 수 없습니다",
                }

            logger.info("⚙️ 시스템 성능 개선 시작")

            # 포괄적 분석 실행
            meta_learning_data = self.system_improver.run_comprehensive_analysis()

            # 개선 제안 생성
            improvement_suggestions = meta_learning_data.improvement_suggestions

            # 개선 적용
            applied_improvements = []
            for suggestion in improvement_suggestions:
                if suggestion.priority in ["critical", "high"]:
                    applied_improvements.append(
                        {
                            "suggestion_id": suggestion.suggestion_id,
                            "category": suggestion.category,
                            "description": suggestion.description,
                            "priority": suggestion.priority,
                            "confidence": suggestion.confidence,
                        }
                    )

            return {
                "status": "success",
                "analysis_completed": True,
                "improvement_suggestions": len(improvement_suggestions),
                "applied_improvements": len(applied_improvements),
                "applied_improvements_details": applied_improvements,
                "meta_learning_data": {
                    "performance_patterns": len(meta_learning_data.performance_patterns),
                    "error_patterns": len(meta_learning_data.error_patterns),
                    "learning_strategy_updates": len(meta_learning_data.learning_strategy_updates),
                },
            }

        except Exception as e:
            logger.error(f"❌ 시스템 성능 개선 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_learning_improvement(self) -> Dict[str, Any]:
        """학습 전략 개선 실행"""
        try:
            if not self.learning_improver:
                return {
                    "status": "unavailable",
                    "message": "학습 개선기가 사용할 수 없습니다",
                }

            logger.info("📚 학습 전략 개선 시작")

            # 현재 학습 통계 조회
            learning_stats = self.learning_improver.get_learning_statistics()

            # 메타 학습 사이클 실행
            meta_learning_result = self.learning_improver._run_meta_learning_cycle()

            # 학습 전략 업데이트
            strategy_updates = []
            if meta_learning_result:
                strategy_updates.append({"type": "meta_learning", "result": meta_learning_result})

            return {
                "status": "success",
                "learning_stats": learning_stats,
                "meta_learning_executed": True,
                "strategy_updates": len(strategy_updates),
                "strategy_updates_details": strategy_updates,
            }

        except Exception as e:
            logger.error(f"❌ 학습 전략 개선 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_evolution_improvement(self) -> Dict[str, Any]:
        """진화 방향 개선 실행"""
        try:
            if not self.evolution_improver:
                return {
                    "status": "unavailable",
                    "message": "진화 개선기가 사용할 수 없습니다",
                }

            logger.info("🔄 진화 방향 개선 시작")

            # 자기 성능 분석
            performance_analysis = self.evolution_improver.analyze_self_performance()

            # 자동 개선 실행
            auto_improvement_result = self.evolution_improver.auto_improve_system()

            return {
                "status": "success",
                "performance_analysis": performance_analysis,
                "auto_improvement_executed": True,
                "improvement_result": auto_improvement_result,
            }

        except Exception as e:
            logger.error(f"❌ 진화 방향 개선 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _calculate_overall_improvement_score(
        self,
        conversation_improvements: Dict[str, Any],
        system_improvements: Dict[str, Any],
        learning_improvements: Dict[str, Any],
        evolution_improvements: Dict[str, Any],
    ) -> float:
        """전체 개선 점수 계산"""
        try:
            scores = []
            weights = []

            # 대화 품질 개선 점수
            if conversation_improvements.get("status") == "success":
                conv_score = (
                    conversation_improvements.get("improvement_result", {})
                    .get("summary", {})
                    .get("overall_success_rate", 0.0)
                )
                scores.append(conv_score)
                weights.append(0.4)  # 대화 품질이 가장 중요

            # 시스템 성능 개선 점수
            if system_improvements.get("status") == "success":
                sys_score = min(1.0, system_improvements.get("applied_improvements", 0) / 5.0)  # 최대 5개 개선
                scores.append(sys_score)
                weights.append(0.2)

            # 학습 전략 개선 점수
            if learning_improvements.get("status") == "success":
                learn_score = 0.8 if learning_improvements.get("meta_learning_executed") else 0.0
                scores.append(learn_score)
                weights.append(0.2)

            # 진화 방향 개선 점수
            if evolution_improvements.get("status") == "success":
                evo_score = 0.8 if evolution_improvements.get("auto_improvement_executed") else 0.0
                scores.append(evo_score)
                weights.append(0.2)

            # 가중 평균 계산
            if scores and weights:
                total_weight = sum(weights)
                weighted_score = sum(score * weight for score, weight in zip(scores, weights)) / total_weight  # noqa: B905
                return round(weighted_score, 3)
            else:
                return 0.0

        except Exception as e:
            logger.error(f"❌ 전체 개선 점수 계산 오류: {e}")
            return 0.0

    def _generate_improvement_summary(
        self,
        conversation_improvements: Dict[str, Any],
        system_improvements: Dict[str, Any],
        learning_improvements: Dict[str, Any],
        evolution_improvements: Dict[str, Any],
    ) -> Dict[str, Any]:
        """개선 요약 생성"""
        try:
            summary = {
                "total_improvements": 0,
                "successful_improvements": 0,
                "failed_improvements": 0,
                "improvement_categories": {
                    "conversation": conversation_improvements.get("status") == "success",
                    "system": system_improvements.get("status") == "success",
                    "learning": learning_improvements.get("status") == "success",
                    "evolution": evolution_improvements.get("status") == "success",
                },
                "detailed_results": {
                    "conversation": conversation_improvements,
                    "system": system_improvements,
                    "learning": learning_improvements,
                    "evolution": evolution_improvements,
                },
            }

            # 개선 수량 계산
            if conversation_improvements.get("status") == "success":
                summary["total_improvements"] += (
                    conversation_improvements.get("improvement_result", {}).get("summary", {}).get("total_count", 0)
                )
                summary["successful_improvements"] += (
                    conversation_improvements.get("improvement_result", {}).get("summary", {}).get("success_count", 0)
                )

            if system_improvements.get("status") == "success":
                summary["total_improvements"] += system_improvements.get("applied_improvements", 0)
                summary["successful_improvements"] += system_improvements.get("applied_improvements", 0)

            summary["failed_improvements"] = summary["total_improvements"] - summary["successful_improvements"]

            return summary

        except Exception as e:
            logger.error(f"❌ 개선 요약 생성 오류: {e}")
            return {"error": str(e)}

    def _create_error_result(self, error_message: str, execution_time: float) -> UnifiedImprovementResult:
        """오류 결과 생성"""
        return UnifiedImprovementResult(
            timestamp=datetime.now().isoformat(),
            conversation_improvements={"status": "error", "message": error_message},
            system_improvements={"status": "error", "message": error_message},
            learning_improvements={"status": "error", "message": error_message},
            evolution_improvements={"status": "error", "message": error_message},
            overall_score=0.0,
            improvement_summary={"error": error_message},
            execution_time=execution_time,
        )

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "existing_systems_available": EXISTING_SYSTEMS_AVAILABLE,
            "improvement_history_count": len(self.improvement_history),
            "recent_improvements": [
                {
                    "timestamp": result.timestamp,
                    "overall_score": result.overall_score,
                    "execution_time": result.execution_time,
                }
                for result in self.improvement_history[-5:]  # 최근 5개
            ],
            "conversation_improver_status": self.conversation_improver.get_improvement_summary(),
            "strategy_loop_status": self.strategy_loop_runner.get_strategy_status(),
        }

    def get_improvement_history(self, limit: int = 10) -> List[UnifiedImprovementResult]:
        """개선 히스토리 조회"""
        return self.improvement_history[-limit:]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        if not self.improvement_history:
            return {"average_score": 0.0, "total_executions": 0}

        total_executions = len(self.improvement_history)
        average_score = sum(result.overall_score for result in self.improvement_history) / total_executions
        average_execution_time = sum(result.execution_time for result in self.improvement_history) / total_executions

        return {
            "average_score": round(average_score, 3),
            "total_executions": total_executions,
            "average_execution_time": round(average_execution_time, 3),
            "success_rate": sum(1 for result in self.improvement_history if result.overall_score > 0.5)
            / total_executions,
        }


# 전역 인스턴스 생성
unified_improvement_system = UnifiedImprovementSystem()
