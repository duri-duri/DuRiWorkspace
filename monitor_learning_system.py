#!/usr/bin/env python3
"""
DuRi 학습 시스템 모니터링 스크립트

24/7 자가 학습 시스템의 상태를 실시간으로 모니터링합니다.
CPU, 메모리, 학습률, 경험 데이터 수, 전략 변경 횟수를 추적합니다.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import psutil

from duri_brain.learning.auto_retrospector import get_auto_retrospector

# DuRi 모듈 import
from duri_core.memory.memory_sync import get_memory_sync
from duri_modules.autonomous.duri_autonomous_core import get_duri_autonomous_core
from DuRiCore.unified_learning_system import get_unified_learning_system

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("learning_monitor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class LearningSystemMonitor:
    """학습 시스템 모니터링 클래스"""

    def __init__(self):
        """모니터링 시스템 초기화"""
        self.memory_sync = get_memory_sync()
        self.auto_retrospector = get_auto_retrospector()
        self.unified_learning = get_unified_learning_system()
        self.autonomous_core = get_duri_autonomous_core()

        # 모니터링 설정
        self.monitor_interval = 60  # 1분마다 체크
        self.alert_thresholds = {
            "cpu_usage": 80.0,  # CPU 사용률 80% 이상 시 알림
            "memory_usage": 85.0,  # 메모리 사용률 85% 이상 시 알림
            "learning_rate": 0.1,  # 학습률 10% 미만 시 알림
            "experience_count": 10,  # 경험 데이터 10개 미만 시 알림
        }

        # 모니터링 히스토리
        self.monitoring_history: List[Dict[str, Any]] = []
        self.max_history_size = 100

        logger.info("🔍 학습 시스템 모니터링 시작")

    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 수집"""
        try:
            # CPU 및 메모리 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 디스크 사용률
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": cpu_percent,
                "memory_usage": memory_percent,
                "memory_available": memory.available / (1024**3),  # GB
                "disk_usage": disk_percent,
                "disk_free": disk.free / (1024**3),  # GB
            }
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 중 오류: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "memory_available": 0.0,
                "disk_usage": 0.0,
                "disk_free": 0.0,
            }

    def get_learning_metrics(self) -> Dict[str, Any]:
        """학습 시스템 메트릭 수집"""
        try:
            # 경험 데이터 수
            experiences = self.memory_sync.get_recent_experiences(limit=1000)
            experience_count = len(experiences)

            # 학습률 계산
            if experiences:
                success_count = sum(
                    1 for e in experiences if e.get("outcome") == "success"
                )
                learning_rate = success_count / len(experiences)
            else:
                learning_rate = 0.0

            # 학습 세션 수
            learning_sessions = len(self.unified_learning.learning_sessions)
            evolution_sessions = len(self.unified_learning.evolution_sessions)

            # 자율 학습 상태
            autonomous_status = {
                "is_active": (
                    self.autonomous_core.is_active
                    if hasattr(self.autonomous_core, "is_active")
                    else False
                ),
                "continuous_learner_active": (
                    hasattr(self.autonomous_core, "continuous_learner")
                    and self.autonomous_core.continuous_learner.is_active
                    if hasattr(self.autonomous_core, "continuous_learner")
                    else False
                ),
                "realtime_learner_active": (
                    hasattr(self.autonomous_core, "realtime_learner")
                    and self.autonomous_core.realtime_learner.is_active
                    if hasattr(self.autonomous_core, "realtime_learner")
                    else False
                ),
            }

            return {
                "experience_count": experience_count,
                "learning_rate": learning_rate,
                "learning_sessions": learning_sessions,
                "evolution_sessions": evolution_sessions,
                "autonomous_status": autonomous_status,
                "last_analysis_time": (
                    self.auto_retrospector.last_analysis_time.isoformat()
                    if self.auto_retrospector.last_analysis_time
                    else None
                ),
            }
        except Exception as e:
            logger.error(f"학습 메트릭 수집 중 오류: {e}")
            return {
                "experience_count": 0,
                "learning_rate": 0.0,
                "learning_sessions": 0,
                "evolution_sessions": 0,
                "autonomous_status": {
                    "is_active": False,
                    "continuous_learner_active": False,
                    "realtime_learner_active": False,
                },
                "last_analysis_time": None,
            }

    def check_alerts(self, metrics: Dict[str, Any]) -> List[str]:
        """알림 조건 확인"""
        alerts = []

        # CPU 사용률 알림
        if metrics.get("cpu_usage", 0) > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"⚠️ CPU 사용률 높음: {metrics['cpu_usage']:.1f}%")

        # 메모리 사용률 알림
        if metrics.get("memory_usage", 0) > self.alert_thresholds["memory_usage"]:
            alerts.append(f"⚠️ 메모리 사용률 높음: {metrics['memory_usage']:.1f}%")

        # 학습률 알림
        learning_rate = metrics.get("learning_rate", 0)
        if learning_rate < self.alert_thresholds["learning_rate"]:
            alerts.append(f"⚠️ 학습률 낮음: {learning_rate:.2%}")

        # 경험 데이터 수 알림
        experience_count = metrics.get("experience_count", 0)
        if experience_count < self.alert_thresholds["experience_count"]:
            alerts.append(f"⚠️ 경험 데이터 부족: {experience_count}개")

        return alerts

    def save_monitoring_data(self, metrics: Dict[str, Any]):
        """모니터링 데이터 저장"""
        self.monitoring_history.append(metrics)

        # 히스토리 크기 제한
        if len(self.monitoring_history) > self.max_history_size:
            self.monitoring_history = self.monitoring_history[-self.max_history_size :]

    def print_status_dashboard(
        self,
        system_metrics: Dict[str, Any],
        learning_metrics: Dict[str, Any],
        alerts: List[str],
    ):
        """상태 대시보드 출력"""
        print("\n" + "=" * 80)
        print(
            f"🔍 DuRi 학습 시스템 모니터링 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 80)

        # 시스템 상태
        print("\n📊 시스템 상태:")
        print(f"  CPU 사용률: {system_metrics['cpu_usage']:.1f}%")
        print(
            f"  메모리 사용률: {system_metrics['memory_usage']:.1f}% (사용 가능: {system_metrics['memory_available']:.1f}GB)"
        )
        print(
            f"  디스크 사용률: {system_metrics['disk_usage']:.1f}% (여유 공간: {system_metrics['disk_free']:.1f}GB)"
        )

        # 학습 상태
        print("\n🧠 학습 시스템 상태:")
        print(f"  경험 데이터 수: {learning_metrics['experience_count']}개")
        print(f"  학습률: {learning_metrics['learning_rate']:.2%}")
        print(f"  학습 세션: {learning_metrics['learning_sessions']}개")
        print(f"  진화 세션: {learning_metrics['evolution_sessions']}개")

        # 자율 학습 상태
        autonomous_status = learning_metrics["autonomous_status"]
        print(f"  자율 학습 활성화: {'✅' if autonomous_status['is_active'] else '❌'}")
        print(
            f"  연속 학습: {'✅' if autonomous_status['continuous_learner_active'] else '❌'}"
        )
        print(
            f"  실시간 학습: {'✅' if autonomous_status['realtime_learner_active'] else '❌'}"
        )

        # 알림
        if alerts:
            print("\n🚨 알림:")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print("\n✅ 모든 시스템 정상")

        print("=" * 80)

    async def run_monitoring_loop(self):
        """모니터링 루프 실행"""
        logger.info("🔄 모니터링 루프 시작")

        while True:
            try:
                # 메트릭 수집
                system_metrics = self.get_system_metrics()
                learning_metrics = self.get_learning_metrics()

                # 통합 메트릭
                combined_metrics = {**system_metrics, **learning_metrics}

                # 알림 확인
                alerts = self.check_alerts(combined_metrics)

                # 데이터 저장
                self.save_monitoring_data(combined_metrics)

                # 대시보드 출력
                self.print_status_dashboard(system_metrics, learning_metrics, alerts)

                # 알림이 있으면 로그에 기록
                if alerts:
                    for alert in alerts:
                        logger.warning(alert)

                # 대기
                await asyncio.sleep(self.monitor_interval)

            except KeyboardInterrupt:
                logger.info("🛑 모니터링 중단 요청됨")
                break
            except Exception as e:
                logger.error(f"모니터링 루프 중 오류: {e}")
                await asyncio.sleep(10)  # 오류 시 10초 대기

    def export_monitoring_data(self, filename: str = None):
        """모니터링 데이터 내보내기"""
        if filename is None:
            filename = (
                f"learning_monitor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.monitoring_history, f, ensure_ascii=False, indent=2)
            logger.info(f"📊 모니터링 데이터 내보내기 완료: {filename}")
        except Exception as e:
            logger.error(f"모니터링 데이터 내보내기 중 오류: {e}")


def main():
    """메인 함수"""
    print("🚀 DuRi 학습 시스템 모니터링 시작")
    print("Ctrl+C로 중단할 수 있습니다.")

    monitor = LearningSystemMonitor()

    try:
        # 비동기 모니터링 루프 실행
        asyncio.run(monitor.run_monitoring_loop())
    except KeyboardInterrupt:
        print("\n🛑 모니터링 중단됨")
        # 종료 시 데이터 내보내기
        monitor.export_monitoring_data()
    except Exception as e:
        logger.error(f"모니터링 실행 중 오류: {e}")


if __name__ == "__main__":
    main()
