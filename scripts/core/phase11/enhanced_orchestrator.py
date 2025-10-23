#!/usr/bin/env python3
"""
Phase 11: Enhanced DuRi Orchestrator with Insight Engine Integration

기존 DuRiCore 오케스트레이터를 확장하여 Insight Engine과 통합하고,
내부 사고 시스템과 학습 시스템을 강화합니다.

Author: DuRi Phase 11 Integration Team
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 기존 시스템들 import
try:
    from DuRiCore.duri_orchestrator import DuRiOrchestrator, ExecutionContext, SystemStatus
    from DuRiCore.inner_thinking_system import InnerThinkingSystem
    from DuRiCore.integrated_system_manager import IntegratedSystemManager
    from DuRiCore.unified_learning_system import UnifiedLearningSystem
except Exception as e:
    logging.warning(f"기존 시스템 import 실패: {e}")

    # 플레이스홀더 클래스들
    class DuRiOrchestrator:
        def __init__(self):
            pass

        async def start_execution_loop(self):
            pass

        def stop_execution_loop(self):
            pass

        def generate_status_report(self):
            return {}

    class InnerThinkingSystem:
        def __init__(self):
            pass

        async def think_deeply(self, topic=None):
            return None

    class UnifiedLearningSystem:
        def __init__(self):
            pass

        async def process_learning(self, content, learning_type, context):
            return {}

    class IntegratedSystemManager:
        def __init__(self):
            pass

        async def initialize_all_systems(self):
            pass


# Insight Engine import
try:
    from insight.engine import InsightEngine

    INSIGHT_AVAILABLE = True
except Exception:
    INSIGHT_AVAILABLE = False
    logging.warning("Insight Engine을 찾을 수 없습니다. 기본 모드로 실행됩니다.")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class EnhancedExecutionContext(ExecutionContext):
    """확장된 실행 컨텍스트"""

    conversation_turn: int = 0
    insight_metrics: Dict[str, Any] = field(default_factory=dict)
    learning_context: Dict[str, Any] = field(default_factory=dict)
    reflection_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Phase11Metrics:
    """Phase 11 메트릭"""

    turn_number: int
    execution_time: float
    insight_score: float
    learning_score: float
    reflection_score: float
    overall_quality: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EnhancedDuRiOrchestrator(DuRiOrchestrator):
    """Insight Engine과 통합된 향상된 DuRi 오케스트레이터"""

    def __init__(self):
        super().__init__()

        # execution_loop_active 속성 초기화 (부모 클래스에서 없을 경우)
        if not hasattr(self, "execution_loop_active"):
            self.execution_loop_active = False

        # Insight Engine 초기화
        self.insight_engine = None
        if INSIGHT_AVAILABLE:
            try:
                self.insight_engine = InsightEngine()
                logger.info("✅ Insight Engine 초기화 완료")
            except Exception as e:
                logger.warning(f"⚠️  Insight Engine 초기화 실패: {e}")

        # 내부 사고 시스템 초기화
        self.inner_thinking = InnerThinkingSystem()
        logger.info("✅ 내부 사고 시스템 초기화 완료")

        # 통합 학습 시스템 초기화
        self.unified_learning = UnifiedLearningSystem()
        logger.info("✅ 통합 학습 시스템 초기화 완료")

        # 통합 시스템 매니저 초기화
        self.integrated_manager = IntegratedSystemManager()
        logger.info("✅ 통합 시스템 매니저 초기화 완료")

        # Phase 11 메트릭
        self.phase11_metrics: List[Phase11Metrics] = []
        self.conversation_turn = 0

        logger.info("🚀 Phase 11 Enhanced DuRi Orchestrator 초기화 완료")

    def stop_execution_loop(self):
        """실행 루프 중단"""
        self.execution_loop_active = False
        logger.info("🛑 Phase 11 향상된 실행 루프 중단")

    async def start_enhanced_execution_loop(self):
        """향상된 실행 루프 시작"""
        logger.info("🚀 Phase 11 향상된 실행 루프 시작")

        if self.execution_loop_active:
            logger.warning("⚠️  실행 루프가 이미 활성화되어 있습니다")
            return

        self.execution_loop_active = True

        try:
            # 통합 시스템 매니저 초기화
            await self.integrated_manager.initialize_all_systems()

            while self.execution_loop_active:
                start_time = time.time()
                self.conversation_turn += 1

                # 1. 향상된 Judgment Phase
                judgment_result = await self._execute_enhanced_judgment_phase()

                # 2. 향상된 Action Phase
                action_result = await self._execute_enhanced_action_phase(judgment_result)

                # 3. 향상된 Feedback Phase
                feedback_result = await self._execute_enhanced_feedback_phase(action_result)

                # 4. 내부 사고 및 성찰
                reflection_result = await self._execute_inner_reflection(feedback_result)

                # 5. 외부 학습 트리거
                learning_result = await self._execute_external_learning(feedback_result)

                # 6. Insight Engine 계측
                insight_result = await self._record_insight_metrics(
                    judgment_result,
                    action_result,
                    feedback_result,
                    reflection_result,
                    learning_result,
                )

                # 7. 시스템 상태 업데이트
                await self._update_enhanced_system_status()

                # 8. 성능 모니터링
                await self._monitor_enhanced_performance()

                # 9. 메트릭 기록
                execution_time = time.time() - start_time
                await self._record_phase11_metrics(execution_time, insight_result)

                # 10. 잠시 대기
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"❌ 향상된 실행 루프 오류: {e}")
            self.error_log.append(f"향상된 실행 루프 오류: {e}")
            self.execution_loop_active = False

    async def _execute_enhanced_judgment_phase(self):
        """향상된 판단 단계 실행"""
        logger.info(f"🧠 향상된 Judgment Phase 실행 (턴 {self.conversation_turn})")

        try:
            # 기존 judgment 로직 실행
            if hasattr(super(), "_execute_judgment_phase"):
                result = await super()._execute_judgment_phase()
            else:
                result = {
                    "phase": "judgment",
                    "status": "completed",
                    "turn": self.conversation_turn,
                }

            # Insight Engine 계측
            if self.insight_engine:
                self.insight_engine.record_judgment_quality(result)

            return result

        except Exception as e:
            logger.error(f"❌ Judgment Phase 오류: {e}")
            return {"phase": "judgment", "status": "error", "error": str(e)}

    async def _execute_enhanced_action_phase(self, judgment_result):
        """향상된 액션 단계 실행"""
        logger.info(f"⚡ 향상된 Action Phase 실행 (턴 {self.conversation_turn})")

        try:
            # 기존 action 로직 실행
            if hasattr(super(), "_execute_action_phase"):
                result = await super()._execute_action_phase(judgment_result)
            else:
                result = {
                    "phase": "action",
                    "status": "completed",
                    "turn": self.conversation_turn,
                }

            # Insight Engine 계측
            if self.insight_engine:
                self.insight_engine.record_action_quality(result)

            return result

        except Exception as e:
            logger.error(f"❌ Action Phase 오류: {e}")
            return {"phase": "action", "status": "error", "error": str(e)}

    async def _execute_enhanced_feedback_phase(self, action_result):
        """향상된 피드백 단계 실행"""
        logger.info(f"🔄 향상된 Feedback Phase 실행 (턴 {self.conversation_turn})")

        try:
            # 기존 feedback 로직 실행
            if hasattr(super(), "_execute_feedback_phase"):
                result = await super()._execute_feedback_phase(action_result)
            else:
                result = {
                    "phase": "feedback",
                    "status": "completed",
                    "turn": self.conversation_turn,
                }

            # Insight Engine 계측
            if self.insight_engine:
                self.insight_engine.record_feedback_quality(result)

            return result

        except Exception as e:
            logger.error(f"❌ Feedback Phase 오류: {e}")
            return {"phase": "feedback", "status": "error", "error": str(e)}

    async def _execute_inner_reflection(self, feedback_result):
        """내부 사고 및 성찰 실행"""
        logger.info(f"🤔 내부 사고 및 성찰 실행 (턴 {self.conversation_turn})")

        try:
            # 대화 턴에 대한 자기성찰
            reflection_topic = f"대화 턴 {self.conversation_turn} 분석: {feedback_result}"
            reflection_result = await self.inner_thinking.think_deeply(reflection_topic)

            # 결과 처리
            if reflection_result:
                logger.info(f"✅ 내부 사고 완료: {reflection_result}")
                return {
                    "phase": "inner_reflection",
                    "status": "completed",
                    "result": reflection_result,
                    "turn": self.conversation_turn,
                }
            else:
                return {
                    "phase": "inner_reflection",
                    "status": "completed",
                    "result": "기본 성찰 완료",
                    "turn": self.conversation_turn,
                }

        except Exception as e:
            logger.error(f"❌ 내부 사고 오류: {e}")
            return {"phase": "inner_reflection", "status": "error", "error": str(e)}

    async def _execute_external_learning(self, feedback_result):
        """외부 학습 실행"""
        logger.info(f"📚 외부 학습 실행 (턴 {self.conversation_turn})")

        try:
            # 학습 컨텍스트 생성
            learning_context = {
                "turn": self.conversation_turn,
                "feedback": feedback_result,
                "timestamp": datetime.now().isoformat(),
            }

            # 학습 내용 생성 (실제로는 외부 소스에서 가져옴)
            learning_content = f"턴 {self.conversation_turn} 학습 내용: {feedback_result}"

            # 통합 학습 시스템 실행
            learning_result = await self.unified_learning.process_learning(
                learning_content, "conversation", learning_context
            )

            logger.info(f"✅ 외부 학습 완료: {learning_result}")
            return {
                "phase": "external_learning",
                "status": "completed",
                "result": learning_result,
                "turn": self.conversation_turn,
            }

        except Exception as e:
            logger.error(f"❌ 외부 학습 오류: {e}")
            return {"phase": "external_learning", "status": "error", "error": str(e)}

    async def _record_insight_metrics(
        self,
        judgment_result,
        action_result,
        feedback_result,
        reflection_result,
        learning_result,
    ):
        """Insight Engine 메트릭 기록"""
        if not self.insight_engine:
            return {"insight_score": 0.0}

        try:
            # 전체 턴 메트릭 수집
            turn_metrics = {
                "turn": self.conversation_turn,
                "judgment": judgment_result,
                "action": action_result,
                "feedback": feedback_result,
                "reflection": reflection_result,
                "learning": learning_result,
                "timestamp": datetime.now().isoformat(),
            }

            # Insight Engine에 메트릭 전송
            insight_score = self.insight_engine.analyze_turn_quality(turn_metrics)

            return {"insight_score": insight_score, "metrics": turn_metrics}

        except Exception as e:
            logger.error(f"❌ Insight 메트릭 기록 오류: {e}")
            return {"insight_score": 0.0, "error": str(e)}

    async def _update_enhanced_system_status(self):
        """향상된 시스템 상태 업데이트"""
        try:
            # 기존 시스템 상태 업데이트
            if hasattr(super(), "_update_system_status"):
                await super()._update_system_status()

            # Phase 11 특화 상태 업데이트
            self.system_status.update(
                {
                    "inner_thinking": SystemStatus(
                        name="inner_thinking",
                        status="active",
                        last_activity=datetime.now(),
                        performance_score=0.8,
                    ),
                    "unified_learning": SystemStatus(
                        name="unified_learning",
                        status="active",
                        last_activity=datetime.now(),
                        performance_score=0.7,
                    ),
                    "insight_engine": SystemStatus(
                        name="insight_engine",
                        status="active" if self.insight_engine else "inactive",
                        last_activity=datetime.now(),
                        performance_score=0.9 if self.insight_engine else 0.0,
                    ),
                }
            )

        except Exception as e:
            logger.error(f"❌ 시스템 상태 업데이트 오류: {e}")

    async def _monitor_enhanced_performance(self):
        """향상된 성능 모니터링"""
        try:
            # 기존 성능 모니터링
            if hasattr(super(), "_monitor_performance"):
                await super()._monitor_performance()

            # Phase 11 특화 성능 모니터링
            current_metrics = {
                "turn": self.conversation_turn,
                "active_systems": len([s for s in self.system_status.values() if s.status == "active"]),
                "insight_available": self.insight_engine is not None,
                "timestamp": datetime.now().isoformat(),
            }

            self.performance_metrics[f"turn_{self.conversation_turn}"] = current_metrics

        except Exception as e:
            logger.error(f"❌ 성능 모니터링 오류: {e}")

    async def _record_phase11_metrics(self, execution_time: float, insight_result: Dict[str, Any]):
        """Phase 11 메트릭 기록"""
        try:
            # 각 단계별 점수 계산
            insight_score = insight_result.get("insight_score", 0.0)
            learning_score = 0.7  # 기본값 (실제로는 학습 결과에서 계산)
            reflection_score = 0.8  # 기본값 (실제로는 성찰 결과에서 계산)

            # 전체 품질 점수 계산
            overall_quality = (insight_score + learning_score + reflection_score) / 3

            # 메트릭 생성
            metrics = Phase11Metrics(
                turn_number=self.conversation_turn,
                execution_time=execution_time,
                insight_score=insight_score,
                learning_score=learning_score,
                reflection_score=reflection_score,
                overall_quality=overall_quality,
            )

            self.phase11_metrics.append(metrics)

            logger.info(f"📊 Phase 11 메트릭 기록: 품질 {overall_quality:.2f}, 실행시간 {execution_time:.2f}초")

        except Exception as e:
            logger.error(f"❌ Phase 11 메트릭 기록 오류: {e}")

    def get_phase11_status_report(self) -> Dict[str, Any]:
        """Phase 11 상태 리포트 생성"""
        try:
            # 기존 상태 리포트
            base_report = self.generate_status_report()

            # Phase 11 특화 리포트
            phase11_report = {
                "phase11_metrics": {
                    "total_turns": len(self.phase11_metrics),
                    "average_quality": sum(m.overall_quality for m in self.phase11_metrics)
                    / max(len(self.phase11_metrics), 1),
                    "average_execution_time": sum(m.execution_time for m in self.phase11_metrics)
                    / max(len(self.phase11_metrics), 1),
                    "latest_metrics": (self.phase11_metrics[-1].__dict__ if self.phase11_metrics else None),
                },
                "enhanced_systems": {
                    "inner_thinking": "active",
                    "unified_learning": "active",
                    "insight_engine": "active" if self.insight_engine else "inactive",
                    "integrated_manager": "active",
                },
                "integration_status": {
                    "duri_core": "integrated",
                    "insight_engine": ("integrated" if self.insight_engine else "not_available"),
                    "inner_thinking": "integrated",
                    "unified_learning": "integrated",
                },
            }

            # 통합 리포트
            enhanced_report = {**base_report, **phase11_report}
            enhanced_report["timestamp"] = datetime.now().isoformat()
            enhanced_report["version"] = "Phase 11 Enhanced"

            return enhanced_report

        except Exception as e:
            logger.error(f"❌ Phase 11 상태 리포트 생성 오류: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


async def main():
    """메인 실행 함수"""
    print("🚀 Phase 11 Enhanced DuRi Orchestrator 시작")
    print("=" * 60)

    # 향상된 오케스트레이터 생성
    orchestrator = EnhancedDuRiOrchestrator()

    # 초기 상태 리포트
    initial_report = orchestrator.get_phase11_status_report()
    print(f"📊 초기 상태: {json.dumps(initial_report, indent=2, ensure_ascii=False)}")

    try:
        # 향상된 실행 루프 시작
        await orchestrator.start_enhanced_execution_loop()

    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
        orchestrator.stop_execution_loop()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        orchestrator.stop_execution_loop()

    finally:
        # 최종 상태 리포트
        final_report = orchestrator.get_phase11_status_report()
        print(f"📊 최종 상태: {json.dumps(final_report, indent=2, ensure_ascii=False)}")

        print("\n✅ Phase 11 Enhanced DuRi Orchestrator 종료")


if __name__ == "__main__":
    asyncio.run(main())
