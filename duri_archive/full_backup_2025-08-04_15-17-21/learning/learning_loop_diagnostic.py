"""
DuRi 학습 루프 진단 도구

학습 루프 활성화 과정을 추적하고 정체 지점을 찾습니다.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Any, Dict, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LearningLoopDiagnostic:
    """학습 루프 진단 도구"""

    def __init__(self):
        """LearningLoopDiagnostic 초기화"""
        self.diagnostic_start_time = None
        self.activation_attempts = []
        self.current_status = {}
        self.blocking_points = []

        logger.info("학습 루프 진단 도구 초기화 완료")

    def diagnose_learning_loop_activation(self) -> Dict[str, Any]:
        """학습 루프 활성화를 진단합니다."""
        self.diagnostic_start_time = datetime.now()
        logger.info(
            f"🔍 === 학습 루프 활성화 진단 시작: {self.diagnostic_start_time} ==="
        )

        diagnostic_result = {
            "start_time": self.diagnostic_start_time.isoformat(),
            "steps": [],
            "blocking_points": [],
            "final_status": {},
            "recommendations": [],
        }

        try:
            # 1단계: 초기 상태 확인
            step1_result = self._check_initial_state()
            diagnostic_result["steps"].append(step1_result)

            # 2단계: 학습 루프 매니저 상태 확인
            step2_result = self._check_learning_loop_manager()
            diagnostic_result["steps"].append(step2_result)

            # 3단계: 활성화 시도 (타임아웃 보호)
            step3_result = self._attempt_activation_with_timeout()
            diagnostic_result["steps"].append(step3_result)

            # 4단계: 활성화 후 상태 확인
            step4_result = self._check_post_activation_state()
            diagnostic_result["steps"].append(step4_result)

            # 5단계: 블로킹 포인트 분석
            diagnostic_result["blocking_points"] = self._analyze_blocking_points()

            # 6단계: 최종 상태 및 권장사항
            diagnostic_result["final_status"] = self._get_final_status()
            diagnostic_result["recommendations"] = self._generate_recommendations(
                diagnostic_result
            )

            logger.info("✅ 학습 루프 진단 완료")
            return diagnostic_result

        except Exception as e:
            logger.error(f"❌ 학습 루프 진단 중 오류: {e}")
            diagnostic_result["error"] = str(e)
            return diagnostic_result

    def _check_initial_state(self) -> Dict[str, Any]:
        """초기 상태를 확인합니다."""
        logger.info("📋 1단계: 초기 상태 확인")

        try:
            from duri_brain.learning.learning_loop_activator import (
                get_learning_loop_activator,
            )
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()
            activator = get_learning_loop_activator()

            initial_state = {
                "learning_loop_manager_exists": learning_loop_manager is not None,
                "activator_exists": activator is not None,
                "learning_loop_running": (
                    learning_loop_manager.is_running if learning_loop_manager else False
                ),
                "activator_activated": activator.is_activated if activator else False,
                "current_cycle_id": (
                    learning_loop_manager.current_cycle_id
                    if learning_loop_manager
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ 초기 상태: {initial_state}")
            return {
                "step": "initial_state_check",
                "success": True,
                "data": initial_state,
            }

        except Exception as e:
            logger.error(f"❌ 초기 상태 확인 실패: {e}")
            return {"step": "initial_state_check", "success": False, "error": str(e)}

    def _check_learning_loop_manager(self) -> Dict[str, Any]:
        """학습 루프 매니저 상태를 확인합니다."""
        logger.info("📋 2단계: 학습 루프 매니저 상태 확인")

        try:
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()

            manager_state = {
                "is_running": learning_loop_manager.is_running,
                "current_cycle": (
                    learning_loop_manager.current_cycle.cycle_id
                    if learning_loop_manager.current_cycle
                    else None
                ),
                "loop_thread_alive": (
                    learning_loop_manager.loop_thread.is_alive()
                    if learning_loop_manager.loop_thread
                    else False
                ),
                "learning_config": learning_loop_manager.learning_config,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ 학습 루프 매니저 상태: {manager_state}")
            return {
                "step": "learning_loop_manager_check",
                "success": True,
                "data": manager_state,
            }

        except Exception as e:
            logger.error(f"❌ 학습 루프 매니저 확인 실패: {e}")
            return {
                "step": "learning_loop_manager_check",
                "success": False,
                "error": str(e),
            }

    def _attempt_activation_with_timeout(self) -> Dict[str, Any]:
        """타임아웃 보호가 포함된 활성화를 시도합니다."""
        logger.info("📋 3단계: 활성화 시도 (타임아웃 보호)")

        try:
            from duri_brain.learning.learning_loop_activator import (
                activate_learning_loop,
            )

            # 결과를 저장할 변수
            result = {"activation_result": None, "error": None, "timeout": False}

            def activate_loop():
                try:
                    activation_result = activate_learning_loop()
                    result["activation_result"] = activation_result
                except Exception as e:
                    result["error"] = str(e)

            # 별도 스레드에서 활성화 시도
            thread = threading.Thread(target=activate_loop, daemon=True)
            thread.start()

            # 타임아웃 대기 (60초)
            timeout = 60
            start_time = time.time()

            logger.info(f"🔄 활성화 시도 중... (타임아웃: {timeout}초)")

            while thread.is_alive() and (time.time() - start_time) < timeout:
                time.sleep(0.5)  # 500ms 간격으로 체크
                elapsed = time.time() - start_time
                if elapsed % 10 == 0:  # 10초마다 로그
                    logger.info(f"⏳ 활성화 대기 중... ({elapsed:.1f}초 경과)")

            if thread.is_alive():
                logger.error(f"❌ 활성화 타임아웃 ({timeout}초)")
                result["timeout"] = True
                return {
                    "step": "activation_attempt",
                    "success": False,
                    "timeout": True,
                    "elapsed_time": timeout,
                }

            if result["error"]:
                logger.error(f"❌ 활성화 실패: {result['error']}")
                return {
                    "step": "activation_attempt",
                    "success": False,
                    "error": result["error"],
                }

            logger.info(f"✅ 활성화 성공: {result['activation_result']}")
            return {
                "step": "activation_attempt",
                "success": True,
                "data": result["activation_result"],
            }

        except Exception as e:
            logger.error(f"❌ 활성화 시도 중 오류: {e}")
            return {"step": "activation_attempt", "success": False, "error": str(e)}

    def _check_post_activation_state(self) -> Dict[str, Any]:
        """활성화 후 상태를 확인합니다."""
        logger.info("📋 4단계: 활성화 후 상태 확인")

        try:
            from duri_brain.learning.learning_loop_activator import (
                get_learning_loop_activator,
            )
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()
            activator = get_learning_loop_activator()

            post_activation_state = {
                "learning_loop_running": learning_loop_manager.is_running,
                "activator_activated": activator.is_activated,
                "current_cycle_id": (
                    learning_loop_manager.current_cycle_id
                    if learning_loop_manager.current_cycle
                    else None
                ),
                "loop_thread_alive": (
                    learning_loop_manager.loop_thread.is_alive()
                    if learning_loop_manager.loop_thread
                    else False
                ),
                "scheduler_thread_alive": (
                    activator.scheduler_thread.is_alive()
                    if activator.scheduler_thread
                    else False
                ),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ 활성화 후 상태: {post_activation_state}")
            return {
                "step": "post_activation_check",
                "success": True,
                "data": post_activation_state,
            }

        except Exception as e:
            logger.error(f"❌ 활성화 후 상태 확인 실패: {e}")
            return {"step": "post_activation_check", "success": False, "error": str(e)}

    def _analyze_blocking_points(self) -> list:
        """블로킹 포인트를 분석합니다."""
        logger.info("📋 5단계: 블로킹 포인트 분석")

        blocking_points = []

        try:
            from duri_brain.learning.learning_loop_activator import (
                get_learning_loop_activator,
            )
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()
            activator = get_learning_loop_activator()

            # 1. 학습 루프 매니저 블로킹 체크
            if learning_loop_manager and not learning_loop_manager.is_running:
                blocking_points.append(
                    {
                        "type": "learning_loop_manager",
                        "issue": "학습 루프가 실행되지 않음",
                        "details": "is_running = False",
                    }
                )

            # 2. 루프 스레드 블로킹 체크
            if learning_loop_manager and learning_loop_manager.loop_thread:
                if not learning_loop_manager.loop_thread.is_alive():
                    blocking_points.append(
                        {
                            "type": "loop_thread",
                            "issue": "학습 루프 스레드가 비활성 상태",
                            "details": "loop_thread.is_alive() = False",
                        }
                    )

            # 3. 활성화 시스템 블로킹 체크
            if activator and not activator.is_activated:
                blocking_points.append(
                    {
                        "type": "activator",
                        "issue": "활성화 시스템이 비활성 상태",
                        "details": "is_activated = False",
                    }
                )

            # 4. 스케줄러 블로킹 체크
            if activator and activator.scheduler_thread:
                if not activator.scheduler_thread.is_alive():
                    blocking_points.append(
                        {
                            "type": "scheduler",
                            "issue": "스케줄러 스레드가 비활성 상태",
                            "details": "scheduler_thread.is_alive() = False",
                        }
                    )

            logger.info(f"✅ 블로킹 포인트 분석 완료: {len(blocking_points)}개 발견")
            return blocking_points

        except Exception as e:
            logger.error(f"❌ 블로킹 포인트 분석 실패: {e}")
            return [
                {
                    "type": "analysis_error",
                    "issue": "분석 중 오류 발생",
                    "details": str(e),
                }
            ]

    def _get_final_status(self) -> Dict[str, Any]:
        """최종 상태를 반환합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import (
                get_learning_loop_activator,
            )
            from duri_brain.learning.learning_loop_manager import (
                get_learning_loop_manager,
            )

            learning_loop_manager = get_learning_loop_manager()
            activator = get_learning_loop_activator()

            final_status = {
                "diagnostic_duration": (
                    datetime.now() - self.diagnostic_start_time
                ).total_seconds(),
                "learning_loop_running": (
                    learning_loop_manager.is_running if learning_loop_manager else False
                ),
                "activator_activated": activator.is_activated if activator else False,
                "current_cycle_id": (
                    learning_loop_manager.current_cycle_id
                    if learning_loop_manager and learning_loop_manager.current_cycle
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
            }

            return final_status

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _generate_recommendations(self, diagnostic_result: Dict[str, Any]) -> list:
        """진단 결과를 바탕으로 권장사항을 생성합니다."""
        recommendations = []

        # 타임아웃 발생 시
        for step in diagnostic_result.get("steps", []):
            if step.get("timeout"):
                recommendations.append(
                    "🕐 활성화 타임아웃 발생: 타임아웃 시간을 늘리거나 블로킹 지점을 수정하세요"
                )

            if not step.get("success"):
                recommendations.append(
                    f"❌ {step.get('step')} 실패: {step.get('error', 'Unknown error')}"
                )

        # 블로킹 포인트가 있는 경우
        blocking_points = diagnostic_result.get("blocking_points", [])
        if blocking_points:
            for point in blocking_points:
                recommendations.append(
                    f"🔒 블로킹 포인트: {point['type']} - {point['issue']}"
                )

        # 학습 루프가 실행되지 않는 경우
        final_status = diagnostic_result.get("final_status", {})
        if not final_status.get("learning_loop_running", False):
            recommendations.append(
                "🔄 학습 루프가 실행되지 않음: 수동으로 활성화하거나 오류를 수정하세요"
            )

        if not recommendations:
            recommendations.append("✅ 모든 시스템이 정상 작동 중입니다")

        return recommendations


# 전역 함수로 실행 가능하도록
def run_learning_loop_diagnostic() -> Dict[str, Any]:
    """학습 루프 진단을 실행합니다 (전역 함수)"""
    diagnostic = LearningLoopDiagnostic()
    return diagnostic.diagnose_learning_loop_activation()


if __name__ == "__main__":
    # 진단 실행
    import sys

    sys.path.append(".")

    print("🔍 === DuRi 학습 루프 진단 시작 ===")

    diagnostic_result = run_learning_loop_diagnostic()

    print(f"\n📊 === 진단 결과 요약 ===")
    print(f"진단 시간: {diagnostic_result.get('start_time', 'Unknown')}")
    print(f"진단 단계: {len(diagnostic_result.get('steps', []))}개")
    print(f"블로킹 포인트: {len(diagnostic_result.get('blocking_points', []))}개")

    # 블로킹 포인트 출력
    blocking_points = diagnostic_result.get("blocking_points", [])
    if blocking_points:
        print(f"\n🔒 === 블로킹 포인트 ===")
        for i, point in enumerate(blocking_points, 1):
            print(f"{i}. {point['type']}: {point['issue']}")
            print(f"   상세: {point['details']}")

    # 권장사항 출력
    recommendations = diagnostic_result.get("recommendations", [])
    if recommendations:
        print(f"\n💡 === 권장사항 ===")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

    print(f"\n✅ === 학습 루프 진단 완료 ===")
