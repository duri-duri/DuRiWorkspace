#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 학습 시스템 모니터링 대시보드
실시간으로 학습 진행 상황을 모니터링하고 시각화합니다.
"""

import asyncio
import json
import logging
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LearningMetrics:
    """학습 메트릭"""

    timestamp: datetime
    system_name: str
    session_id: str
    learning_cycles: int
    problems_detected: int
    decisions_made: int
    confidence_score: float
    progress_score: float
    health_score: float
    status: str


@dataclass
class SystemStatus:
    """시스템 상태"""

    name: str
    is_active: bool
    session_id: Optional[str]
    start_time: Optional[datetime]
    runtime: Optional[str]
    last_activity: Optional[datetime]
    performance_metrics: Dict[str, Any]


class LearningMonitoringDashboard:
    """학습 모니터링 대시보드"""

    def __init__(self):
        self.metrics_history: List[LearningMetrics] = []
        self.system_statuses: Dict[str, SystemStatus] = {}
        self.monitoring_active = False
        self.update_interval = 30  # 30초마다 업데이트
        self.max_history_size = 1000  # 최대 히스토리 크기

        # 모니터링할 시스템들
        self.monitored_systems = [
            "통합 학습 시스템",
            "자율 학습 시스템",
            "학습 루프 매니저",
            "실시간 학습 시스템",
        ]

        logger.info("📊 학습 모니터링 대시보드 초기화 완료")

    async def start_monitoring(self):
        """모니터링 시작"""
        print("🚀 DuRi 학습 시스템 모니터링 대시보드 시작")
        print("=" * 60)

        self.monitoring_active = True

        # 초기 상태 수집
        await self._collect_initial_status()

        # 모니터링 루프 시작
        while self.monitoring_active:
            try:
                await self._update_dashboard()
                await asyncio.sleep(self.update_interval)
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중단 요청됨")
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류: {e}")
                await asyncio.sleep(10)

    async def _collect_initial_status(self):
        """초기 상태 수집"""
        print("📋 초기 시스템 상태 수집 중...")

        for system_name in self.monitored_systems:
            status = await self._get_system_status(system_name)
            self.system_statuses[system_name] = status

            if status.is_active:
                print(f"  ✅ {system_name}: 활성")
            else:
                print(f"  ⏸️ {system_name}: 비활성")

        print("초기 상태 수집 완료\n")

    async def _get_system_status(self, system_name: str) -> SystemStatus:
        """시스템 상태 가져오기"""
        try:
            if system_name == "통합 학습 시스템":
                return await self._get_unified_learning_status()
            elif system_name == "자율 학습 시스템":
                return await self._get_autonomous_learning_status()
            elif system_name == "학습 루프 매니저":
                return await self._get_learning_loop_status()
            elif system_name == "실시간 학습 시스템":
                return await self._get_realtime_learning_status()
            else:
                return SystemStatus(
                    name=system_name,
                    is_active=False,
                    session_id=None,
                    start_time=None,
                    runtime=None,
                    last_activity=None,
                    performance_metrics={},
                )
        except Exception as e:
            logger.error(f"{system_name} 상태 확인 실패: {e}")
            return SystemStatus(
                name=system_name,
                is_active=False,
                session_id=None,
                start_time=None,
                runtime=None,
                last_activity=datetime.now(),
                performance_metrics={"error": str(e)},
            )

    async def _get_unified_learning_status(self) -> SystemStatus:
        """통합 학습 시스템 상태"""
        try:
            from DuRiCore.unified_learning_system import UnifiedLearningSystem

            learning_system = UnifiedLearningSystem()
            active_sessions = [
                s
                for s in learning_system.learning_sessions
                if s.status.value == "in_progress"
            ]

            is_active = len(active_sessions) > 0
            session_id = active_sessions[0].id if active_sessions else None
            start_time = active_sessions[0].start_time if active_sessions else None

            runtime = None
            if start_time:
                runtime = str(datetime.now() - start_time).split(".")[0]

            return SystemStatus(
                name="통합 학습 시스템",
                is_active=is_active,
                session_id=session_id,
                start_time=start_time,
                runtime=runtime,
                last_activity=datetime.now(),
                performance_metrics={
                    "active_sessions": len(active_sessions),
                    "total_sessions": len(learning_system.learning_sessions),
                    "learning_history": len(learning_system.learning_history),
                },
            )
        except Exception as e:
            logger.error(f"통합 학습 시스템 상태 확인 실패: {e}")
            return SystemStatus(
                name="통합 학습 시스템",
                is_active=False,
                session_id=None,
                start_time=None,
                runtime=None,
                last_activity=datetime.now(),
                performance_metrics={"error": str(e)},
            )

    async def _get_autonomous_learning_status(self) -> SystemStatus:
        """자율 학습 시스템 상태"""
        try:
            from duri_modules.autonomous.continuous_learner import \
                AutonomousLearner
            from duri_modules.autonomous.duri_autonomous_core import \
                DuRiAutonomousCore

            autonomous_learner = AutonomousLearner()
            autonomous_core = DuRiAutonomousCore()

            is_active = autonomous_learner.is_running and autonomous_core.is_active
            session_id = (
                autonomous_learner.current_session.session_id
                if autonomous_learner.current_session
                else None
            )
            start_time = (
                autonomous_learner.current_session.start_time
                if autonomous_learner.current_session
                else None
            )

            runtime = None
            if start_time:
                runtime = str(datetime.now() - start_time).split(".")[0]

            return SystemStatus(
                name="자율 학습 시스템",
                is_active=is_active,
                session_id=session_id,
                start_time=start_time,
                runtime=runtime,
                last_activity=datetime.now(),
                performance_metrics={
                    "total_learning_cycles": autonomous_learner.total_learning_cycles,
                    "total_problems_detected": autonomous_learner.total_problems_detected,
                    "total_decisions_made": autonomous_learner.total_decisions_made,
                    "learning_history_count": len(autonomous_learner.learning_history),
                },
            )
        except Exception as e:
            logger.error(f"자율 학습 시스템 상태 확인 실패: {e}")
            return SystemStatus(
                name="자율 학습 시스템",
                is_active=False,
                session_id=None,
                start_time=None,
                runtime=None,
                last_activity=datetime.now(),
                performance_metrics={"error": str(e)},
            )

    async def _get_learning_loop_status(self) -> SystemStatus:
        """학습 루프 매니저 상태"""
        try:
            from duri_brain.learning.learning_loop_manager import \
                get_learning_loop_manager

            learning_loop_manager = get_learning_loop_manager()
            current_status = learning_loop_manager.get_current_status()

            is_active = learning_loop_manager.is_running
            session_id = (
                learning_loop_manager.current_cycle.cycle_id
                if learning_loop_manager.current_cycle
                else None
            )
            start_time = (
                learning_loop_manager.current_cycle.start_time
                if learning_loop_manager.current_cycle
                else None
            )

            runtime = None
            if start_time:
                runtime = str(datetime.now() - start_time).split(".")[0]

            return SystemStatus(
                name="학습 루프 매니저",
                is_active=is_active,
                session_id=session_id,
                start_time=start_time,
                runtime=runtime,
                last_activity=datetime.now(),
                performance_metrics={
                    "learning_cycle_count": learning_loop_manager.learning_cycle_count,
                    "total_cycles": len(learning_loop_manager.learning_cycles),
                    "current_stage": current_status.get("current_stage"),
                    "performance_metrics": current_status.get(
                        "performance_metrics", {}
                    ),
                },
            )
        except Exception as e:
            logger.error(f"학습 루프 매니저 상태 확인 실패: {e}")
            return SystemStatus(
                name="학습 루프 매니저",
                is_active=False,
                session_id=None,
                start_time=None,
                runtime=None,
                last_activity=datetime.now(),
                performance_metrics={"error": str(e)},
            )

    async def _get_realtime_learning_status(self) -> SystemStatus:
        """실시간 학습 시스템 상태"""
        try:
            from duri_modules.autonomous.continuous_learner import \
                AutonomousLearner
            from duri_modules.autonomous.realtime_learner import \
                RealtimeLearner

            autonomous_learner = AutonomousLearner()
            realtime_learner = RealtimeLearner(autonomous_learner)

            is_active = realtime_learner.is_active
            session_id = (
                realtime_learner.current_session.session_id
                if realtime_learner.current_session
                else None
            )
            start_time = (
                realtime_learner.current_session.start_time
                if realtime_learner.current_session
                else None
            )

            runtime = None
            if start_time:
                runtime = str(datetime.now() - start_time).split(".")[0]

            return SystemStatus(
                name="실시간 학습 시스템",
                is_active=is_active,
                session_id=session_id,
                start_time=start_time,
                runtime=runtime,
                last_activity=datetime.now(),
                performance_metrics={
                    "learning_interval": realtime_learner.learning_interval,
                    "total_learning_sessions": len(realtime_learner.learning_history),
                    "last_learning_time": (
                        realtime_learner.last_learning_time.isoformat()
                        if realtime_learner.last_learning_time
                        else None
                    ),
                },
            )
        except Exception as e:
            logger.error(f"실시간 학습 시스템 상태 확인 실패: {e}")
            return SystemStatus(
                name="실시간 학습 시스템",
                is_active=False,
                session_id=None,
                start_time=None,
                runtime=None,
                last_activity=datetime.now(),
                performance_metrics={"error": str(e)},
            )

    async def _update_dashboard(self):
        """대시보드 업데이트"""
        # 화면 클리어
        os.system("clear" if os.name == "posix" else "cls")

        # 현재 시간
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🤖 DuRi 학습 시스템 모니터링 대시보드 - {current_time}")
        print("=" * 60)

        # 시스템 상태 표시
        await self._display_system_statuses()

        # 메트릭 요약 표시
        await self._display_metrics_summary()

        # 최근 활동 표시
        await self._display_recent_activity()

        # 컨트롤 안내
        print("\n" + "=" * 60)
        print("💡 컨트롤: Ctrl+C로 모니터링 종료")
        print("=" * 60)

    async def _display_system_statuses(self):
        """시스템 상태 표시"""
        print("\n📊 시스템 상태")
        print("-" * 40)

        active_count = 0
        total_count = len(self.monitored_systems)

        for system_name in self.monitored_systems:
            status = self.system_statuses.get(system_name)
            if status:
                if status.is_active:
                    active_count += 1
                    status_icon = "🟢"
                    status_text = "활성"
                else:
                    status_icon = "🔴"
                    status_text = "비활성"

                runtime_text = f" (실행: {status.runtime})" if status.runtime else ""
                session_text = f" [{status.session_id}]" if status.session_id else ""

                print(
                    f"  {status_icon} {system_name}: {status_text}{runtime_text}{session_text}"
                )
            else:
                print(f"  ⚪ {system_name}: 상태 확인 불가")

        print(f"\n📈 전체 상태: {active_count}/{total_count} 시스템 활성")

    async def _display_metrics_summary(self):
        """메트릭 요약 표시"""
        if not self.metrics_history:
            print("\n📊 메트릭 요약")
            print("-" * 40)
            print("  아직 수집된 메트릭이 없습니다.")
            return

        print("\n📊 메트릭 요약")
        print("-" * 40)

        # 최근 메트릭들
        recent_metrics = self.metrics_history[-10:]  # 최근 10개

        total_cycles = sum(m.learning_cycles for m in recent_metrics)
        total_problems = sum(m.problems_detected for m in recent_metrics)
        total_decisions = sum(m.decisions_made for m in recent_metrics)
        avg_confidence = (
            sum(m.confidence_score for m in recent_metrics) / len(recent_metrics)
            if recent_metrics
            else 0
        )
        avg_progress = (
            sum(m.progress_score for m in recent_metrics) / len(recent_metrics)
            if recent_metrics
            else 0
        )

        print(f"  🔄 총 학습 사이클: {total_cycles}")
        print(f"  ⚠️ 감지된 문제: {total_problems}")
        print(f"  🤖 자동 결정: {total_decisions}")
        print(f"  📈 평균 신뢰도: {avg_confidence:.2f}")
        print(f"  📊 평균 진행도: {avg_progress:.2f}")

    async def _display_recent_activity(self):
        """최근 활동 표시"""
        print("\n🕒 최근 활동")
        print("-" * 40)

        # 최근 활동 시간순으로 정렬
        recent_activities = []
        for system_name, status in self.system_statuses.items():
            if status.last_activity:
                recent_activities.append((system_name, status.last_activity))

        recent_activities.sort(key=lambda x: x[1], reverse=True)

        for system_name, activity_time in recent_activities[:5]:  # 최근 5개
            time_diff = datetime.now() - activity_time
            time_str = str(time_diff).split(".")[0]
            print(f"  {system_name}: {time_str} 전")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        print("\n🛑 모니터링 중지됨")

    def save_metrics_report(self, filename: str = None):
        """메트릭 리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"learning_metrics_report_{timestamp}.json"

        report_data = {
            "report_time": datetime.now().isoformat(),
            "system_statuses": {
                name: asdict(status) for name, status in self.system_statuses.items()
            },
            "metrics_history": [
                asdict(metric) for metric in self.metrics_history[-100:]
            ],  # 최근 100개
            "summary": {
                "total_metrics_collected": len(self.metrics_history),
                "active_systems": sum(
                    1 for status in self.system_statuses.values() if status.is_active
                ),
                "total_systems": len(self.system_statuses),
            },
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            print(f"📄 메트릭 리포트 저장됨: {filename}")
        except Exception as e:
            logger.error(f"메트릭 리포트 저장 실패: {e}")


async def main():
    """메인 함수"""
    dashboard = LearningMonitoringDashboard()

    try:
        await dashboard.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 모니터링 중단됨")
    finally:
        dashboard.stop_monitoring()

        # 종료 시 리포트 저장
        print("\n📄 메트릭 리포트를 저장하시겠습니까? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ["y", "yes", "네"]:
                dashboard.save_metrics_report()
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")


if __name__ == "__main__":
    asyncio.run(main())
