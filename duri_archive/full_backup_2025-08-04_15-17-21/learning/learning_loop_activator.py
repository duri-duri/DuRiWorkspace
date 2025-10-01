"""
DuRi 학습 루프 활성화 시스템

LearningLoopManager를 활성화하고 실제 학습이 가능하게 루프를 실행 상태로 전환합니다.
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import schedule

from duri_brain.learning.learning_loop_manager import (
    LearningLoopManager,
    get_learning_loop_manager,
)
from duri_core.memory.memory_sync import ExperienceSource, MemoryType, get_memory_sync
from duri_core.utils.fallback_handler import get_fallback_handler
from duri_core.utils.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


@dataclass
class LearningLoopSchedule:
    """학습 루프 스케줄"""

    cycle_interval: int = 300  # 5분마다
    meta_learning_interval: int = 3600  # 1시간마다
    assessment_interval: int = 1800  # 30분마다
    creativity_interval: int = 7200  # 2시간마다
    max_cycles_per_day: int = 288  # 하루 최대 288회 (5분마다)
    active_hours: List[int] = field(
        default_factory=lambda: list(range(24))
    )  # 24시간 활성


@dataclass
class ActivationResult:
    """활성화 결과"""

    success: bool
    cycle_id: Optional[str] = None
    error_message: Optional[str] = None
    memory_stored: bool = False
    fallback_used: bool = False


class DuRiLearningLoopActivator:
    """DuRi 학습 루프 활성화 시스템"""

    def __init__(self):
        """DuRiLearningLoopActivator 초기화"""
        self.learning_loop_manager = get_learning_loop_manager()
        self.memory_sync = get_memory_sync()
        self.fallback_handler = get_fallback_handler()
        self.performance_monitor = get_performance_monitor()

        # 스케줄 설정
        self.schedule_config = LearningLoopSchedule()

        # 활성화 상태
        self.is_activated = False
        self.scheduler_thread = None
        self.activation_time = None

        # 트리거 함수들
        self.trigger_functions = {}

        logger.info("DuRi 학습 루프 활성화 시스템 초기화 완료")

    def activate(self) -> ActivationResult:
        """학습 루프를 활성화합니다."""
        try:
            logger.info("🔄 === DuRi 학습 루프 활성화 시작 ===")

            # 1. 기본 전략 설정
            initial_strategy = self._create_initial_strategy()

            # 2. 학습 루프 시작 (타임아웃 보호)
            cycle_id = self._start_learning_loop_with_timeout(initial_strategy)

            if not cycle_id:
                raise Exception("학습 루프 시작 실패")

            # 3. 스케줄러 시작 (비블로킹)
            self._start_scheduler_non_blocking()

            # 4. 트리거 연결
            self._connect_triggers()

            # 5. 메모리 동기화 설정
            self._setup_memory_sync()

            # 6. 성능 모니터링 시작
            self._start_performance_monitoring()

            # 7. 활성화 상태 업데이트
            self.is_activated = True
            self.activation_time = datetime.now()

            # 8. 메모리에 활성화 기록 저장
            self._store_activation_memory(cycle_id, initial_strategy)

            logger.info(f"✅ 학습 루프 활성화 완료: {cycle_id}")

            return ActivationResult(success=True, cycle_id=cycle_id, memory_stored=True)

        except Exception as e:
            logger.error(f"❌ 학습 루프 활성화 실패: {e}")

            # Fallback 처리
            fallback_result = self._handle_activation_fallback(e)

            return ActivationResult(
                success=False, error_message=str(e), fallback_used=fallback_result
            )

    def _create_initial_strategy(self) -> Dict[str, Any]:
        """초기 학습 전략을 생성합니다."""
        return {
            "learning_approach": "adaptive",
            "intensity": "moderate",
            "focus_areas": [
                "strategy_imitation",
                "practice_optimization",
                "feedback_integration",
                "challenge_adaptation",
                "improvement_mechanism",
            ],
            "performance_targets": {
                "imitation_success_rate": 0.8,
                "practice_efficiency": 0.7,
                "feedback_quality": 0.9,
                "challenge_completion": 0.6,
                "improvement_rate": 0.5,
            },
            "meta_learning_enabled": True,
            "self_assessment_enabled": True,
            "goal_oriented_thinking_enabled": True,
            "emotional_ethical_judgment_enabled": True,
            "autonomous_goal_setting_enabled": True,
            "creativity_enhancement_enabled": True,
        }

    def _start_learning_loop_with_timeout(
        self, initial_strategy: Dict[str, Any]
    ) -> Optional[str]:
        """타임아웃 보호가 포함된 학습 루프 시작"""
        try:
            import threading
            import time

            # 결과를 저장할 변수
            result = {"cycle_id": None, "error": None}

            def start_loop():
                try:
                    cycle_id = self.learning_loop_manager.start_learning_loop(
                        initial_strategy
                    )
                    result["cycle_id"] = cycle_id
                except Exception as e:
                    result["error"] = str(e)

            # 별도 스레드에서 학습 루프 시작
            thread = threading.Thread(target=start_loop, daemon=True)
            thread.start()

            # 타임아웃 대기 (30초)
            timeout = 30
            start_time = time.time()

            while thread.is_alive() and (time.time() - start_time) < timeout:
                time.sleep(0.1)  # 100ms 간격으로 체크

            if thread.is_alive():
                logger.error(f"❌ 학습 루프 시작 타임아웃 ({timeout}초)")
                return None

            if result["error"]:
                logger.error(f"❌ 학습 루프 시작 실패: {result['error']}")
                return None

            return result["cycle_id"]

        except Exception as e:
            logger.error(f"❌ 학습 루프 시작 중 오류: {e}")
            return None

    def _start_scheduler_non_blocking(self):
        """비블로킹 스케줄러를 시작합니다."""
        logger.info("📅 === 학습 루프 스케줄러 시작 (비블로킹) ===")

        # 주기적 학습 사이클 스케줄
        schedule.every(self.schedule_config.cycle_interval).seconds.do(
            self._trigger_learning_cycle
        )

        # 메타 학습 스케줄
        schedule.every(self.schedule_config.meta_learning_interval).seconds.do(
            self._trigger_meta_learning
        )

        # 자기 평가 스케줄
        schedule.every(self.schedule_config.assessment_interval).seconds.do(
            self._trigger_self_assessment
        )

        # 창의성 고도화 스케줄
        schedule.every(self.schedule_config.creativity_interval).seconds.do(
            self._trigger_creativity_enhancement
        )

        # 스케줄러 스레드 시작 (타임아웃 보호)
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler_with_timeout, daemon=True
        )
        self.scheduler_thread.start()

        logger.info("✅ 스케줄러 시작 완료 (비블로킹)")

    def _run_scheduler_with_timeout(self):
        """타임아웃 보호가 포함된 스케줄러 실행"""
        logger.info("🔄 스케줄러 실행 중 (타임아웃 보호)...")

        max_iterations = 3600  # 최대 1시간 (3600초)
        iteration_count = 0

        while self.is_activated and iteration_count < max_iterations:
            try:
                schedule.run_pending()
                time.sleep(1)
                iteration_count += 1

                # 주기적으로 상태 체크
                if iteration_count % 60 == 0:  # 1분마다
                    logger.debug(
                        f"스케줄러 실행 중... ({iteration_count}/{max_iterations})"
                    )

            except Exception as e:
                logger.error(f"스케줄러 오류: {e}")
                time.sleep(5)

        if iteration_count >= max_iterations:
            logger.warning("⚠️ 스케줄러 최대 실행 시간 도달")
        else:
            logger.info("✅ 스케줄러 정상 종료")

    def _connect_triggers(self):
        """트리거 함수들을 연결합니다."""
        logger.info("🔗 === 트리거 연결 ===")

        self.trigger_functions = {
            "learning_cycle": self._trigger_learning_cycle,
            "meta_learning": self._trigger_meta_learning,
            "self_assessment": self._trigger_self_assessment,
            "goal_oriented_thinking": self._trigger_goal_oriented_thinking,
            "emotional_ethical_judgment": self._trigger_emotional_ethical_judgment,
            "autonomous_goal_setting": self._trigger_autonomous_goal_setting,
            "creativity_enhancement": self._trigger_creativity_enhancement,
        }

        logger.info(f"✅ {len(self.trigger_functions)}개 트리거 연결 완료")

    def _setup_memory_sync(self):
        """메모리 동기화를 설정합니다."""
        logger.info("💾 === 메모리 동기화 설정 ===")

        # 학습 결과 저장 콜백 등록
        self.learning_loop_manager.result_callback = self._store_learning_result

        logger.info("✅ 메모리 동기화 설정 완료")

    def _start_performance_monitoring(self):
        """성능 모니터링을 시작합니다."""
        logger.info("📊 === 성능 모니터링 시작 ===")

        # 학습 루프 성능 모니터링 시작
        self.performance_monitor.start_monitoring("learning_loop")

        logger.info("✅ 성능 모니터링 시작 완료")

    def _trigger_learning_cycle(self):
        """학습 사이클을 트리거합니다."""
        try:
            if not self.learning_loop_manager.is_running:
                logger.warning("학습 루프가 비활성 상태입니다.")
                return

            logger.info("🔄 학습 사이클 트리거됨")

            # 현재 상태 확인
            status = self.learning_loop_manager.get_current_status()

            # 메모리에 트리거 이벤트 저장
            self._store_trigger_event("learning_cycle", status)

        except Exception as e:
            logger.error(f"학습 사이클 트리거 오류: {e}")
            self._handle_trigger_fallback("learning_cycle", e)

    def _trigger_meta_learning(self):
        """메타 학습을 트리거합니다."""
        try:
            logger.info("🧠 메타 학습 트리거됨")

            # 메타 학습 실행
            self.learning_loop_manager._run_meta_learning_cycle()

            # 메모리에 메타 학습 결과 저장
            self._store_meta_learning_result()

        except Exception as e:
            logger.error(f"메타 학습 트리거 오류: {e}")
            self._handle_trigger_fallback("meta_learning", e)

    def _trigger_self_assessment(self):
        """자기 평가를 트리거합니다."""
        try:
            logger.info("🔍 자기 평가 트리거됨")

            # 자기 평가 실행
            self.learning_loop_manager._run_self_assessment_cycle()

            # 메모리에 평가 결과 저장
            self._store_assessment_result()

        except Exception as e:
            logger.error(f"자기 평가 트리거 오류: {e}")
            self._handle_trigger_fallback("self_assessment", e)

    def _trigger_goal_oriented_thinking(self):
        """목표 지향적 사고를 트리거합니다."""
        try:
            logger.info("🎯 목표 지향적 사고 트리거됨")

            # 목표 지향적 사고 실행
            self.learning_loop_manager._run_goal_oriented_thinking_cycle()

        except Exception as e:
            logger.error(f"목표 지향적 사고 트리거 오류: {e}")
            self._handle_trigger_fallback("goal_oriented_thinking", e)

    def _trigger_emotional_ethical_judgment(self):
        """감정/윤리 판단을 트리거합니다."""
        try:
            logger.info("❤️ 감정/윤리 판단 트리거됨")

            # 감정/윤리 판단 실행
            self.learning_loop_manager._run_emotional_ethical_judgment_cycle()

        except Exception as e:
            logger.error(f"감정/윤리 판단 트리거 오류: {e}")
            self._handle_trigger_fallback("emotional_ethical_judgment", e)

    def _trigger_autonomous_goal_setting(self):
        """자율 목표 설정을 트리거합니다."""
        try:
            logger.info("🎯 자율 목표 설정 트리거됨")

            # 자율 목표 설정 실행
            self.learning_loop_manager._run_autonomous_goal_setting_cycle()

        except Exception as e:
            logger.error(f"자율 목표 설정 트리거 오류: {e}")
            self._handle_trigger_fallback("autonomous_goal_setting", e)

    def _trigger_creativity_enhancement(self):
        """창의성 고도화를 트리거합니다."""
        try:
            logger.info("✨ 창의성 고도화 트리거됨")

            # 창의성 고도화 실행
            self.learning_loop_manager._run_creativity_enhancement_cycle()

        except Exception as e:
            logger.error(f"창의성 고도화 트리거 오류: {e}")
            self._handle_trigger_fallback("creativity_enhancement", e)

    def _store_learning_result(self, result: Any):
        """학습 결과를 메모리에 저장합니다."""
        try:
            content = {
                "type": "learning_result",
                "cycle_id": result.cycle.cycle_id if hasattr(result, "cycle") else None,
                "overall_performance": getattr(result, "overall_performance", 0.0),
                "improvement_score": getattr(result, "improvement_score", 0.0),
                "recommendations": getattr(result, "recommendations", []),
                "next_actions": getattr(result, "next_actions", []),
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.9,
                tags=["learning_loop", "result"],
            )

            logger.info("💾 학습 결과 메모리 저장 완료")

        except Exception as e:
            logger.error(f"학습 결과 저장 오류: {e}")

    def _store_trigger_event(self, trigger_type: str, status: Dict[str, Any]):
        """트리거 이벤트를 메모리에 저장합니다."""
        try:
            content = {
                "type": "trigger_event",
                "trigger_type": trigger_type,
                "status": status,
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.SYSTEM_EVENT,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.8,
                tags=["trigger", trigger_type],
            )

        except Exception as e:
            logger.error(f"트리거 이벤트 저장 오류: {e}")

    def _store_meta_learning_result(self):
        """메타 학습 결과를 메모리에 저장합니다."""
        try:
            content = {
                "type": "meta_learning_result",
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.85,
                tags=["meta_learning"],
            )

        except Exception as e:
            logger.error(f"메타 학습 결과 저장 오류: {e}")

    def _store_assessment_result(self):
        """평가 결과를 메모리에 저장합니다."""
        try:
            content = {
                "type": "assessment_result",
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.85,
                tags=["self_assessment"],
            )

        except Exception as e:
            logger.error(f"평가 결과 저장 오류: {e}")

    def _store_activation_memory(self, cycle_id: str, strategy: Dict[str, Any]):
        """활성화 기록을 메모리에 저장합니다."""
        try:
            content = {
                "type": "learning_loop_activation",
                "cycle_id": cycle_id,
                "strategy": strategy,
                "activation_time": self.activation_time.isoformat(),
                "status": "activated",
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.SYSTEM_EVENT,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.95,
                tags=["activation", "learning_loop"],
            )

            logger.info("💾 활성화 기록 메모리 저장 완료")

        except Exception as e:
            logger.error(f"활성화 기록 저장 오류: {e}")

    def _handle_activation_fallback(self, error: Exception) -> bool:
        """활성화 실패 시 Fallback 처리를 합니다."""
        try:
            logger.warning("🔄 Fallback 처리 시작")

            # Fallback 핸들러에 오류 전달
            fallback_result = self.fallback_handler.handle_error(
                "learning_loop_activation",
                error,
                {"component": "LearningLoopActivator"},
            )

            if fallback_result.get("success", False):
                logger.info("✅ Fallback 처리 성공")
                return True
            else:
                logger.error("❌ Fallback 처리 실패")
                return False

        except Exception as e:
            logger.error(f"Fallback 처리 중 오류: {e}")
            return False

    def _handle_trigger_fallback(self, trigger_type: str, error: Exception):
        """트리거 실패 시 Fallback 처리를 합니다."""
        try:
            logger.warning(f"🔄 {trigger_type} 트리거 Fallback 처리")

            fallback_result = self.fallback_handler.handle_error(
                f"learning_loop_trigger_{trigger_type}",
                error,
                {"trigger_type": trigger_type},
            )

            if fallback_result.get("success", False):
                logger.info(f"✅ {trigger_type} Fallback 처리 성공")
            else:
                logger.error(f"❌ {trigger_type} Fallback 처리 실패")

        except Exception as e:
            logger.error(f"{trigger_type} Fallback 처리 중 오류: {e}")

    def get_activation_status(self) -> Dict[str, Any]:
        """활성화 상태를 반환합니다."""
        return {
            "is_activated": self.is_activated,
            "activation_time": (
                self.activation_time.isoformat() if self.activation_time else None
            ),
            "learning_loop_running": self.learning_loop_manager.is_running,
            "scheduler_running": self.scheduler_thread
            and self.scheduler_thread.is_alive(),
            "trigger_functions_count": len(self.trigger_functions),
            "schedule_config": {
                "cycle_interval": self.schedule_config.cycle_interval,
                "meta_learning_interval": self.schedule_config.meta_learning_interval,
                "assessment_interval": self.schedule_config.assessment_interval,
                "creativity_interval": self.schedule_config.creativity_interval,
            },
        }

    def deactivate(self):
        """학습 루프를 비활성화합니다."""
        try:
            logger.info("🛑 === DuRi 학습 루프 비활성화 시작 ===")

            # 1. 스케줄러 중지
            self.is_activated = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)

            # 2. 학습 루프 중지
            self.learning_loop_manager.stop_learning_loop()

            # 3. 성능 모니터링 중지
            self.performance_monitor.stop_monitoring("learning_loop")

            # 4. 메모리에 비활성화 기록 저장
            self._store_deactivation_memory()

            logger.info("✅ 학습 루프 비활성화 완료")

        except Exception as e:
            logger.error(f"❌ 학습 루프 비활성화 실패: {e}")

    def _store_deactivation_memory(self):
        """비활성화 기록을 메모리에 저장합니다."""
        try:
            content = {
                "type": "learning_loop_deactivation",
                "deactivation_time": datetime.now().isoformat(),
                "total_runtime": (
                    (datetime.now() - self.activation_time).total_seconds()
                    if self.activation_time
                    else 0
                ),
                "status": "deactivated",
            }

            self.memory_sync.store_experience(
                memory_type=MemoryType.SYSTEM_EVENT,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(content, ensure_ascii=False),
                confidence=0.95,
                tags=["deactivation", "learning_loop"],
            )

            logger.info("💾 비활성화 기록 메모리 저장 완료")

        except Exception as e:
            logger.error(f"비활성화 기록 저장 오류: {e}")


# 전역 함수로 실행 가능하도록
def activate_learning_loop() -> ActivationResult:
    """학습 루프를 활성화합니다 (전역 함수)"""
    activator = DuRiLearningLoopActivator()
    return activator.activate()


def get_learning_loop_activator() -> DuRiLearningLoopActivator:
    """학습 루프 활성화 시스템을 반환합니다 (전역 함수)"""
    return DuRiLearningLoopActivator()


if __name__ == "__main__":
    # 활성화 실행
    import sys

    sys.path.append(".")

    result = activate_learning_loop()
    print(f"🎯 활성화 결과: {'✅ 성공' if result.success else '❌ 실패'}")
    if result.success:
        print(f"📋 사이클 ID: {result.cycle_id}")
        print(f"💾 메모리 저장: {'✅ 완료' if result.memory_stored else '❌ 실패'}")
    else:
        print(f"❌ 오류: {result.error_message}")
        print(f"🔄 Fallback 사용: {'✅ 예' if result.fallback_used else '❌ 아니오'}")
