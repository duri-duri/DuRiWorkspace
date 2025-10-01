#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 개선된 학습 시스템 활성화 스크립트
오류 처리를 강화하고 모든 학습 시스템을 완전히 활성화합니다.
"""

import asyncio
from datetime import datetime
import logging
import os
import sys
import time
from typing import Any, Dict, List

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("duri_improved_learning_activation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ImprovedLearningActivator:
    """개선된 학습 시스템 활성화 관리자"""

    def __init__(self):
        self.activated_systems = []
        self.monitoring_active = False
        self.monitoring_interval = 60  # 1분마다 모니터링
        self.retry_count = 3  # 재시도 횟수

    async def activate_unified_learning_system(self) -> Dict[str, Any]:
        """통합 학습 시스템 활성화 (개선됨)"""
        for attempt in range(self.retry_count):
            try:
                from DuRiCore.unified_learning_system import (
                    LearningType,
                    UnifiedLearningSystem,
                )

                learning_system = UnifiedLearningSystem()

                # 학습 세션 시작
                session = await learning_system.start_learning_session(
                    learning_type=LearningType.CONTINUOUS,
                    context={"activation_time": datetime.now().isoformat()},
                )

                # 진화 세션도 시작
                from DuRiCore.unified_learning_system import EvolutionType

                evolution_session = await learning_system.start_evolution_session(
                    evolution_type=EvolutionType.INCREMENTAL,
                    context={"activation_time": datetime.now().isoformat()},
                )

                self.activated_systems.append(
                    {
                        "name": "통합 학습 시스템",
                        "session_id": session.id,
                        "evolution_session_id": evolution_session.id,
                        "status": "활성화됨",
                        "start_time": datetime.now(),
                    }
                )

                logger.info(
                    f"✅ 통합 학습 시스템 활성화 완료: {session.id}, {evolution_session.id}"
                )
                return {
                    "success": True,
                    "session_id": session.id,
                    "evolution_session_id": evolution_session.id,
                }

            except Exception as e:
                logger.error(
                    f"❌ 통합 학습 시스템 활성화 실패 (시도 {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt == self.retry_count - 1:
                    return {"success": False, "error": str(e)}
                await asyncio.sleep(2)  # 재시도 전 대기

        return {"success": False, "error": "최대 재시도 횟수 초과"}

    async def activate_autonomous_learning_system(self) -> Dict[str, Any]:
        """자율 학습 시스템 활성화 (개선됨)"""
        for attempt in range(self.retry_count):
            try:
                from duri_modules.autonomous.continuous_learner import AutonomousLearner
                from duri_modules.autonomous.duri_autonomous_core import (
                    DuRiAutonomousCore,
                )

                # 자율 학습 시작
                autonomous_learner = AutonomousLearner()
                autonomous_core = DuRiAutonomousCore()

                # 자율 학습 시작
                learner_started = autonomous_learner.start_autonomous_learning()
                core_started = await autonomous_core.start_autonomous_learning()

                if learner_started and core_started:
                    self.activated_systems.append(
                        {
                            "name": "자율 학습 시스템",
                            "session_id": (
                                autonomous_learner.current_session.session_id
                                if autonomous_learner.current_session
                                else "N/A"
                            ),
                            "status": "활성화됨",
                            "start_time": datetime.now(),
                        }
                    )

                    logger.info("✅ 자율 학습 시스템 활성화 완료")
                    return {
                        "success": True,
                        "learner_active": learner_started,
                        "core_active": core_started,
                    }
                else:
                    logger.error(
                        f"❌ 자율 학습 시스템 활성화 실패 (시도 {attempt + 1}/{self.retry_count})"
                    )
                    if attempt == self.retry_count - 1:
                        return {
                            "success": False,
                            "learner_active": learner_started,
                            "core_active": core_started,
                        }
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(
                    f"❌ 자율 학습 시스템 활성화 실패 (시도 {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt == self.retry_count - 1:
                    return {"success": False, "error": str(e)}
                await asyncio.sleep(2)

        return {"success": False, "error": "최대 재시도 횟수 초과"}

    async def activate_learning_loop_manager(self) -> Dict[str, Any]:
        """학습 루프 매니저 활성화 (개선됨)"""
        for attempt in range(self.retry_count):
            try:
                from duri_brain.learning.learning_loop_manager import (
                    get_learning_loop_manager,
                )

                learning_loop_manager = get_learning_loop_manager()

                # 초기 전략 설정 (더 구체적으로)
                initial_strategy = {
                    "learning_type": "continuous",
                    "intensity": "moderate",
                    "focus_areas": [
                        "general",
                        "problem_solving",
                        "creativity",
                        "ethics",
                    ],
                    "meta_learning_enabled": True,
                    "self_assessment_enabled": True,
                    "emotional_ethical_enabled": True,
                    "autonomous_goal_setting_enabled": True,
                    "creativity_enhancement_enabled": True,
                }

                # 학습 루프 시작
                cycle_id = learning_loop_manager.start_learning_loop(initial_strategy)

                # 활성화 확인
                if learning_loop_manager.is_running:
                    self.activated_systems.append(
                        {
                            "name": "학습 루프 매니저",
                            "session_id": cycle_id,
                            "status": "활성화됨",
                            "start_time": datetime.now(),
                        }
                    )

                    logger.info(f"✅ 학습 루프 매니저 활성화 완료: {cycle_id}")
                    return {"success": True, "cycle_id": cycle_id}
                else:
                    logger.error(
                        f"❌ 학습 루프 매니저 활성화 실패 (시도 {attempt + 1}/{self.retry_count})"
                    )
                    if attempt == self.retry_count - 1:
                        return {"success": False, "error": "학습 루프가 시작되지 않음"}
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(
                    f"❌ 학습 루프 매니저 활성화 실패 (시도 {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt == self.retry_count - 1:
                    return {"success": False, "error": str(e)}
                await asyncio.sleep(2)

        return {"success": False, "error": "최대 재시도 횟수 초과"}

    async def activate_realtime_learner(self) -> Dict[str, Any]:
        """실시간 학습 시스템 활성화 (개선됨)"""
        for attempt in range(self.retry_count):
            try:
                from duri_modules.autonomous.continuous_learner import AutonomousLearner
                from duri_modules.autonomous.realtime_learner import RealtimeLearner

                autonomous_learner = AutonomousLearner()
                realtime_learner = RealtimeLearner(autonomous_learner)

                # 실시간 학습 시작
                realtime_started = realtime_learner.start_realtime_learning()

                if realtime_started:
                    self.activated_systems.append(
                        {
                            "name": "실시간 학습 시스템",
                            "session_id": (
                                realtime_learner.current_session.session_id
                                if realtime_learner.current_session
                                else "N/A"
                            ),
                            "status": "활성화됨",
                            "start_time": datetime.now(),
                        }
                    )

                    logger.info("✅ 실시간 학습 시스템 활성화 완료")
                    return {"success": True}
                else:
                    logger.error(
                        f"❌ 실시간 학습 시스템 활성화 실패 (시도 {attempt + 1}/{self.retry_count})"
                    )
                    if attempt == self.retry_count - 1:
                        return {
                            "success": False,
                            "error": "실시간 학습이 시작되지 않음",
                        }
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(
                    f"❌ 실시간 학습 시스템 활성화 실패 (시도 {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt == self.retry_count - 1:
                    return {"success": False, "error": str(e)}
                await asyncio.sleep(2)

        return {"success": False, "error": "최대 재시도 횟수 초과"}

    async def verify_system_health(self) -> Dict[str, Any]:
        """시스템 상태 검증"""
        print("\n🔍 시스템 상태 검증 중...")

        health_status = {}

        # 각 시스템의 상태 확인
        for system in self.activated_systems:
            system_name = system["name"]

            try:
                if system_name == "통합 학습 시스템":
                    from DuRiCore.unified_learning_system import UnifiedLearningSystem

                    learning_system = UnifiedLearningSystem()
                    active_sessions = [
                        s
                        for s in learning_system.learning_sessions
                        if s.status.value == "in_progress"
                    ]
                    health_status[system_name] = {
                        "active": len(active_sessions) > 0,
                        "session_count": len(active_sessions),
                        "total_sessions": len(learning_system.learning_sessions),
                    }

                elif system_name == "자율 학습 시스템":
                    from duri_modules.autonomous.continuous_learner import (
                        AutonomousLearner,
                    )

                    autonomous_learner = AutonomousLearner()
                    health_status[system_name] = {
                        "active": autonomous_learner.is_running,
                        "learning_cycles": autonomous_learner.total_learning_cycles,
                        "problems_detected": autonomous_learner.total_problems_detected,
                    }

                elif system_name == "학습 루프 매니저":
                    from duri_brain.learning.learning_loop_manager import (
                        get_learning_loop_manager,
                    )

                    learning_loop_manager = get_learning_loop_manager()
                    health_status[system_name] = {
                        "active": learning_loop_manager.is_running,
                        "cycle_count": learning_loop_manager.learning_cycle_count,
                        "total_cycles": len(learning_loop_manager.learning_cycles),
                    }

                elif system_name == "실시간 학습 시스템":
                    from duri_modules.autonomous.continuous_learner import (
                        AutonomousLearner,
                    )
                    from duri_modules.autonomous.realtime_learner import RealtimeLearner

                    autonomous_learner = AutonomousLearner()
                    realtime_learner = RealtimeLearner(autonomous_learner)
                    health_status[system_name] = {
                        "active": realtime_learner.is_active,
                        "learning_interval": realtime_learner.learning_interval,
                        "total_sessions": len(realtime_learner.learning_history),
                    }

            except Exception as e:
                health_status[system_name] = {"active": False, "error": str(e)}

        return health_status

    async def activate_all_learning_systems(self) -> Dict[str, Any]:
        """모든 학습 시스템 활성화 (개선됨)"""
        print("🚀 DuRi 개선된 학습 시스템 활성화 시작")
        print("=" * 60)

        activation_results = {}

        # 1. 통합 학습 시스템 활성화
        print("\n1️⃣ 통합 학습 시스템 활성화 중...")
        result = await self.activate_unified_learning_system()
        activation_results["unified_learning"] = result
        if result["success"]:
            print("   ✅ 통합 학습 시스템 활성화 완료")
        else:
            print(
                f"   ❌ 통합 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}"
            )

        # 2. 자율 학습 시스템 활성화
        print("\n2️⃣ 자율 학습 시스템 활성화 중...")
        result = await self.activate_autonomous_learning_system()
        activation_results["autonomous_learning"] = result
        if result["success"]:
            print("   ✅ 자율 학습 시스템 활성화 완료")
        else:
            print(
                f"   ❌ 자율 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}"
            )

        # 3. 학습 루프 매니저 활성화
        print("\n3️⃣ 학습 루프 매니저 활성화 중...")
        result = await self.activate_learning_loop_manager()
        activation_results["learning_loop_manager"] = result
        if result["success"]:
            print("   ✅ 학습 루프 매니저 활성화 완료")
        else:
            print(
                f"   ❌ 학습 루프 매니저 활성화 실패: {result.get('error', '알 수 없는 오류')}"
            )

        # 4. 실시간 학습 시스템 활성화
        print("\n4️⃣ 실시간 학습 시스템 활성화 중...")
        result = await self.activate_realtime_learner()
        activation_results["realtime_learner"] = result
        if result["success"]:
            print("   ✅ 실시간 학습 시스템 활성화 완료")
        else:
            print(
                f"   ❌ 실시간 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}"
            )

        # 시스템 상태 검증
        print("\n🔍 시스템 상태 검증 중...")
        health_status = await self.verify_system_health()

        # 결과 요약
        print("\n📊 활성화 결과 요약")
        print("-" * 40)

        successful_activations = sum(
            1 for result in activation_results.values() if result["success"]
        )
        total_systems = len(activation_results)

        for system_name, result in activation_results.items():
            status = "✅ 성공" if result["success"] else "❌ 실패"
            print(f"   {system_name}: {status}")

        print(f"\n🎯 전체 성공률: {successful_activations}/{total_systems}")

        # 건강 상태 표시 (개선된 로직)
        print("\n🏥 시스템 건강 상태")
        print("-" * 40)

        # 필수 초기화 통과 여부 (전체 활성화 결과)
        essential_init_success = successful_activations
        total_essential = total_systems

        # 모듈별 상태 (최근 사이클의 오류 존재 여부)
        module_status_success = 0
        total_modules = len(health_status)

        for system_name, health in health_status.items():
            if health.get("active", False):
                print(f"   ✅ {system_name}: 정상 작동")
                module_status_success += 1
            else:
                error = health.get("error", "알 수 없는 오류")
                if "존재형 AI" in error or "최종 실행" in error:
                    print(f"   ⚠️ {system_name}: Degraded (선택적 모듈)")
                    module_status_success += 1  # 선택적 모듈은 성공으로 간주
                else:
                    print(f"   ❌ {system_name}: 문제 발생 - {error}")

        print(f"\n📊 활성화 결과 요약")
        print("-" * 40)
        print(f"   필수 초기화: {essential_init_success}/{total_essential} ✅")
        print(f"   모듈별 상태: {module_status_success}/{total_modules} ✅")

        if essential_init_success == total_essential:
            print("\n🎉 모든 학습 시스템이 성공적으로 활성화되었습니다!")
            print("이제 DuRi가 완전한 자가학습을 시작합니다.")
        elif essential_init_success > 0:
            print(
                f"\n⚠️ 일부 학습 시스템만 활성화되었습니다. ({essential_init_success}/{total_essential})"
            )
            print("문제가 있는 시스템을 수동으로 확인해주세요.")
        else:
            print("\n🚨 모든 학습 시스템 활성화에 실패했습니다.")
            print("시스템 로그를 확인하고 문제를 해결해주세요.")

        return {
            "total_systems": total_systems,
            "successful_activations": successful_activations,
            "activation_results": activation_results,
            "health_status": health_status,
            "activated_systems": self.activated_systems,
        }

    async def start_monitoring(self):
        """학습 시스템 모니터링 시작 (개선됨)"""
        print("\n🔍 학습 시스템 모니터링 시작...")
        self.monitoring_active = True

        while self.monitoring_active:
            try:
                await self._monitor_systems()
                await asyncio.sleep(self.monitoring_interval)
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중단 요청됨")
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류: {e}")
                await asyncio.sleep(10)

    async def _monitor_systems(self):
        """시스템 모니터링 (개선됨)"""
        print(f"\n📊 학습 시스템 상태 모니터링 - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 60)

        health_status = await self.verify_system_health()

        for system in self.activated_systems:
            system_name = system["name"]
            runtime = datetime.now() - system["start_time"]
            runtime_str = str(runtime).split(".")[0]

            health = health_status.get(system_name, {})
            if health.get("active", False):
                status_icon = "🟢"
                status_text = "정상"
            else:
                status_icon = "🔴"
                status_text = "문제"

            print(
                f"  {status_icon} {system_name}: {status_text} (실행 시간: {runtime_str})"
            )

            # 추가 정보 표시
            if "session_count" in health:
                print(f"     활성 세션: {health['session_count']}")
            if "learning_cycles" in health:
                print(f"     학습 사이클: {health['learning_cycles']}")
            if "cycle_count" in health:
                print(f"     루프 사이클: {health['cycle_count']}")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        print("\n🛑 모니터링 중지됨")


async def main():
    """메인 함수"""
    activator = ImprovedLearningActivator()

    # 모든 학습 시스템 활성화
    result = await activator.activate_all_learning_systems()

    if result["successful_activations"] > 0:
        print("\n🔍 모니터링을 시작하시겠습니까? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ["y", "yes", "네"]:
                await activator.start_monitoring()
            else:
                print("모니터링을 시작하지 않습니다.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
    else:
        print("\n❌ 활성화된 시스템이 없어 모니터링을 시작할 수 없습니다.")


if __name__ == "__main__":
    asyncio.run(main())
