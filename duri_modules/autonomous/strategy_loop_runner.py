import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .result_improver import ImprovementAction, ResultImprover

logger = logging.getLogger(__name__)


@dataclass
class StrategyExecution:
    strategy_id: str
    action_type: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    start_time: datetime
    end_time: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]


class StrategyLoopRunner:
    def __init__(self):
        self.result_improver = ResultImprover()
        self.execution_history = []
        self.current_strategy = None
        self.is_running = False

        logger.info("🔄 DuRi 전략 루프 러너 초기화 완료")

    def start_improvement_loop(self, evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """개선 루프 시작"""
        try:
            self.is_running = True
            logger.info("🚀 개선 전략 루프 시작")

            # 1. 개선 제안 분석
            actions = self.result_improver.analyze_improvement_suggestions(evaluation_result)

            if not actions:
                logger.warning("⚠️ 실행 가능한 개선 액션이 없습니다")
                return {
                    "status": "no_actions",
                    "message": "실행 가능한 개선 액션이 없습니다",
                }

            # 2. 전략 실행
            execution_results = self._execute_improvement_strategy(actions, evaluation_result)

            # 3. 결과 요약
            summary = self._generate_execution_summary(execution_results)

            self.is_running = False
            logger.info(
                f"✅ 개선 전략 루프 완료: {summary['success_count']}/{summary['total_count']} 성공"
            )

            return {
                "status": "completed",
                "summary": summary,
                "execution_results": execution_results,
            }

        except Exception as e:
            self.is_running = False
            logger.error(f"❌ 개선 전략 루프 오류: {e}")
            return {"status": "error", "message": str(e)}

    def _execute_improvement_strategy(
        self, actions: List[ImprovementAction], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """개선 전략 실행"""
        execution_results = []

        for i, action in enumerate(actions):
            strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"

            execution = StrategyExecution(
                strategy_id=strategy_id,
                action_type=action.action_type,
                description=action.description,
                status="pending",
                start_time=datetime.now(),
                end_time=None,
                result=None,
                error_message=None,
            )

            try:
                logger.info(f"🔧 전략 실행: {action.action_type} - {action.description}")
                execution.status = "running"

                # 액션 실행
                success = self.result_improver.execute_improvement_action(action, context)

                execution.status = "completed" if success else "failed"
                execution.end_time = datetime.now()

                if success:
                    execution.result = {
                        "action_type": action.action_type,
                        "description": action.description,
                        "priority": action.priority,
                        "estimated_effort": action.estimated_effort,
                    }
                else:
                    execution.error_message = "액션 실행 실패"

                execution_results.append(
                    {
                        "strategy_id": strategy_id,
                        "status": execution.status,
                        "action_type": action.action_type,
                        "description": action.description,
                        "success": success,
                        "execution_time": (
                            execution.end_time - execution.start_time
                        ).total_seconds(),
                    }
                )

                self.execution_history.append(execution)

                # 성공한 액션에 대한 추가 처리
                if success:
                    self._post_process_successful_action(action, context)

            except Exception as e:
                execution.status = "failed"
                execution.end_time = datetime.now()
                execution.error_message = str(e)

                execution_results.append(
                    {
                        "strategy_id": strategy_id,
                        "status": "failed",
                        "action_type": action.action_type,
                        "description": action.description,
                        "success": False,
                        "error": str(e),
                    }
                )

                self.execution_history.append(execution)
                logger.error(f"❌ 전략 실행 실패: {action.description} - {e}")

        return execution_results

    def _post_process_successful_action(self, action: ImprovementAction, context: Dict[str, Any]):
        """성공한 액션 후처리"""
        try:
            # 개선 결과를 메모리에 저장
            improvement_summary = self.result_improver.get_improvement_summary()

            # 학습 패턴 업데이트
            self._update_learning_patterns(action, improvement_summary)

            # 성공한 전략 기록
            self._record_successful_strategy(action)

            logger.info(f"📝 성공한 액션 후처리 완료: {action.description}")

        except Exception as e:
            logger.error(f"❌ 후처리 오류: {e}")

    def _update_learning_patterns(self, action: ImprovementAction, summary: Dict[str, Any]):
        """학습 패턴 업데이트"""
        try:
            # 성공률 기반 패턴 학습
            success_rate = summary.get("success_rate", 0)

            if success_rate > 0.7:
                logger.info(f"🎯 높은 성공률 패턴 발견: {action.action_type}")
            elif success_rate < 0.3:
                logger.warning(f"⚠️ 낮은 성공률 패턴 발견: {action.action_type}")

        except Exception as e:
            logger.error(f"❌ 패턴 업데이트 오류: {e}")

    def _record_successful_strategy(self, action: ImprovementAction):
        """성공한 전략 기록"""
        try:
            # 전략 성공 기록을 파일에 저장
            strategy_record = {
                "timestamp": datetime.now().isoformat(),
                "action_type": action.action_type,
                "description": action.description,
                "priority": action.priority,
                "estimated_effort": action.estimated_effort,
                "status": "successful",
            }

            # 간단한 파일 저장 (실제로는 데이터베이스 사용 권장)
            with open("successful_strategies.json", "a") as f:
                f.write(json.dumps(strategy_record) + "\n")

        except Exception as e:
            logger.error(f"❌ 전략 기록 오류: {e}")

    def _generate_execution_summary(
        self, execution_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """실행 결과 요약 생성"""
        try:
            total_count = len(execution_results)
            success_count = sum(1 for result in execution_results if result.get("success", False))
            failed_count = total_count - success_count

            # 액션 타입별 성공률
            action_type_stats = {}
            for result in execution_results:
                action_type = result.get("action_type", "unknown")
                if action_type not in action_type_stats:
                    action_type_stats[action_type] = {"total": 0, "success": 0}

                action_type_stats[action_type]["total"] += 1
                if result.get("success", False):
                    action_type_stats[action_type]["success"] += 1

            # 성공률 계산
            for action_type in action_type_stats:
                total = action_type_stats[action_type]["total"]
                success = action_type_stats[action_type]["success"]
                action_type_stats[action_type]["success_rate"] = success / total if total > 0 else 0

            return {
                "total_count": total_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "overall_success_rate": (success_count / total_count if total_count > 0 else 0),
                "action_type_stats": action_type_stats,
                "execution_time": sum(
                    result.get("execution_time", 0) for result in execution_results
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 요약 생성 오류: {e}")
            return {"error": str(e)}

    def get_strategy_status(self) -> Dict[str, Any]:
        """전략 상태 조회"""
        return {
            "is_running": self.is_running,
            "current_strategy": self.current_strategy,
            "total_executions": len(self.execution_history),
            "recent_executions": [
                {
                    "strategy_id": exec.strategy_id,
                    "action_type": exec.action_type,
                    "status": exec.status,
                    "start_time": exec.start_time.isoformat(),
                }
                for exec in self.execution_history[-5:]  # 최근 5개
            ],
            "improvement_summary": self.result_improver.get_improvement_summary(),
        }

    def stop_improvement_loop(self):
        """개선 루프 중지"""
        self.is_running = False
        logger.info("🛑 개선 전략 루프 중지")

    def get_learning_insights(self) -> Dict[str, Any]:
        """학습 인사이트 생성"""
        try:
            summary = self.result_improver.get_improvement_summary()
            strategy_status = self.get_strategy_status()

            insights = {
                "total_improvements": summary.get("total_improvements", 0),
                "success_rate": summary.get("success_rate", 0),
                "most_effective_actions": [],
                "learning_patterns": [],
                "recommendations": [],
            }

            # 가장 효과적인 액션 분석
            if summary.get("recent_improvements"):
                high_confidence_improvements = [
                    imp for imp in summary["recent_improvements"] if imp.get("confidence", 0) > 0.7
                ]
                insights["most_effective_actions"] = high_confidence_improvements

            # 학습 패턴 분석
            if strategy_status.get("recent_executions"):
                successful_executions = [
                    exec
                    for exec in strategy_status["recent_executions"]
                    if exec.get("status") == "completed"
                ]
                insights["learning_patterns"] = successful_executions

            # 권장사항 생성
            if insights["success_rate"] > 0.8:
                insights["recommendations"].append(
                    "높은 성공률을 유지하고 있습니다. 더 복잡한 개선에 도전해보세요."
                )
            elif insights["success_rate"] < 0.5:
                insights["recommendations"].append(
                    "성공률이 낮습니다. 기본적인 개선부터 시작해보세요."
                )
            else:
                insights["recommendations"].append(
                    "안정적인 성과를 보이고 있습니다. 점진적 개선을 계속하세요."
                )

            return insights

        except Exception as e:
            logger.error(f"❌ 학습 인사이트 생성 오류: {e}")
            return {"error": str(e)}
