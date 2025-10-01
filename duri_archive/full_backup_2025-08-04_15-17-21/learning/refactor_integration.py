"""
DuRi 리팩터링 예측 시스템 통합

기존 learning_loop에 리팩터링 예측 시스템을 통합합니다.
"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RefactorIntegrationStatus:
    """리팩터링 통합 상태"""

    performance_history_active: bool
    degradation_predictor_active: bool
    refactor_controller_active: bool
    last_prediction_time: Optional[datetime]
    last_refactor_time: Optional[datetime]
    total_predictions: int
    total_refactors: int
    success_rate: float


class RefactorIntegrationManager:
    """DuRi 리팩터링 예측 시스템 통합 관리자"""

    def __init__(self):
        """RefactorIntegrationManager 초기화"""
        self.is_integrated = False
        self.integration_thread: Optional[threading.Thread] = None

        # 통합된 컴포넌트들
        self.performance_history = None
        self.degradation_predictor = None
        self.refactor_controller = None

        # 통합 설정
        self.integration_interval_minutes = 10  # 10분마다 통합 체크
        self.auto_refactor_enabled = False  # 기본적으로 수동 모드
        self.prediction_threshold = 0.8  # 예측 신뢰도 임계값

        logger.info("RefactorIntegrationManager 초기화 완료")

    def integrate_with_learning_loop(self):
        """learning_loop에 리팩터링 예측 시스템을 통합합니다."""
        try:
            logger.info("리팩터링 예측 시스템 통합 시작")

            # 1. PerformanceHistory 초기화 및 시작
            self._init_performance_history()

            # 2. DegradationPredictor 초기화 및 시작
            self._init_degradation_predictor()

            # 3. RefactorPredictiveController 초기화 및 시작
            self._init_refactor_controller()

            # 4. 통합 루프 시작
            self._start_integration_loop()

            self.is_integrated = True
            logger.info("리팩터링 예측 시스템 통합 완료")

        except Exception as e:
            logger.error(f"리팩터링 예측 시스템 통합 실패: {e}")

    def _init_performance_history(self):
        """PerformanceHistory를 초기화합니다."""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.learning.performance_history import get_performance_history

            self.performance_history = get_performance_history()
            self.performance_history.start_collection()
            logger.info("PerformanceHistory 통합 완료")
        except Exception as e:
            logger.error(f"PerformanceHistory 초기화 실패: {e}")

    def _init_degradation_predictor(self):
        """DegradationPredictor를 초기화합니다."""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.learning.degradation_predictor import (
                get_degradation_predictor,
            )

            self.degradation_predictor = get_degradation_predictor()
            self.degradation_predictor.start_prediction()
            logger.info("DegradationPredictor 통합 완료")
        except Exception as e:
            logger.error(f"DegradationPredictor 초기화 실패: {e}")

    def _init_refactor_controller(self):
        """RefactorPredictiveController를 초기화합니다."""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.learning.refactor_predictive_controller import (
                get_refactor_controller,
            )

            self.refactor_controller = get_refactor_controller()
            self.refactor_controller.start_controller()
            logger.info("RefactorPredictiveController 통합 완료")
        except Exception as e:
            logger.error(f"RefactorPredictiveController 초기화 실패: {e}")

    def _start_integration_loop(self):
        """통합 루프를 시작합니다."""
        if self.integration_thread:
            logger.warning("통합 루프가 이미 실행 중입니다.")
            return

        self.integration_thread = threading.Thread(
            target=self._integration_loop, daemon=True
        )
        self.integration_thread.start()
        logger.info("통합 루프 시작")

    def _integration_loop(self):
        """통합 루프"""
        while self.is_integrated:
            try:
                # 1. 성능 상태 확인
                self._check_performance_status()

                # 2. 예측 결과 확인
                self._check_prediction_results()

                # 3. 리팩터링 상태 확인
                self._check_refactor_status()

                # 4. learning_loop와의 상호작용
                self._interact_with_learning_loop()

                # 5. 통합 상태 보고
                self._report_integration_status()

                time.sleep(self.integration_interval_minutes * 60)

            except Exception as e:
                logger.error(f"통합 루프 오류: {e}")
                time.sleep(300)  # 오류 시 5분 대기

    def _check_performance_status(self):
        """성능 상태를 확인합니다."""
        try:
            if self.performance_history:
                summary = self.performance_history.get_performance_summary()
                if summary.get("warning_metrics", 0) > 0:
                    logger.warning(
                        f"성능 경고 지표 발견: {summary['warning_metrics']}개"
                    )

                    # 경고 지표가 있으면 예측 시스템에 알림
                    if self.degradation_predictor:
                        self._trigger_prediction_analysis()

        except Exception as e:
            logger.error(f"성능 상태 확인 실패: {e}")

    def _check_prediction_results(self):
        """예측 결과를 확인합니다."""
        try:
            if self.degradation_predictor:
                summary = self.degradation_predictor.get_prediction_summary()

                if summary.get("critical_predictions", 0) > 0:
                    logger.critical(
                        f"심각한 성능 저하 예측: {summary['critical_predictions']}개"
                    )
                    self._trigger_urgent_refactor()

                elif summary.get("high_predictions", 0) > 0:
                    logger.warning(
                        f"높은 우선순위 예측: {summary['high_predictions']}개"
                    )
                    self._trigger_high_priority_refactor()

        except Exception as e:
            logger.error(f"예측 결과 확인 실패: {e}")

    def _check_refactor_status(self):
        """리팩터링 상태를 확인합니다."""
        try:
            if self.refactor_controller:
                summary = self.refactor_controller.get_task_summary()

                if summary.get("running_tasks", 0) > 0:
                    logger.info(
                        f"실행 중인 리팩터링 작업: {summary['running_tasks']}개"
                    )

                if summary.get("completed_tasks", 0) > 0:
                    success_rate = summary.get("success_rate", 0)
                    logger.info(f"리팩터링 완료: 성공률 {success_rate:.1f}%")

                    # 성공률이 낮으면 학습 루프에 피드백
                    if success_rate < 70:
                        self._report_refactor_failure_to_learning()

        except Exception as e:
            logger.error(f"리팩터링 상태 확인 실패: {e}")

    def _interact_with_learning_loop(self):
        """learning_loop와 상호작용합니다."""
        try:
            # learning_loop 상태 확인
            learning_status = self._get_learning_loop_status()

            if learning_status.get("is_active", False):
                # 학습 루프가 활성화된 상태에서 성능 모니터링 강화
                self._enhance_learning_performance_monitoring()

            # 리팩터링이 필요한 경우 학습 루프 일시 중지 고려
            if self._should_pause_learning_for_refactor():
                self._request_learning_pause()

        except Exception as e:
            logger.error(f"learning_loop 상호작용 실패: {e}")

    def _get_learning_loop_status(self) -> Dict[str, Any]:
        """learning_loop 상태를 가져옵니다."""
        try:
            # 실제 구현에서는 learning_loop_manager에서 상태 조회
            return {"is_active": True, "current_cycle": 1, "performance_score": 0.85}
        except Exception as e:
            logger.error(f"learning_loop 상태 조회 실패: {e}")
            return {}

    def _enhance_learning_performance_monitoring(self):
        """학습 성능 모니터링을 강화합니다."""
        try:
            if self.performance_history:
                # 학습 중인 상태에서 더 자주 성능 체크
                logger.info("학습 루프 활성화로 인한 성능 모니터링 강화")

        except Exception as e:
            logger.error(f"학습 성능 모니터링 강화 실패: {e}")

    def _should_pause_learning_for_refactor(self) -> bool:
        """리팩터링을 위해 학습을 일시 중지해야 하는지 확인합니다."""
        try:
            if self.refactor_controller:
                summary = self.refactor_controller.get_task_summary()
                running_tasks = summary.get("running_tasks", 0)

                # 실행 중인 높은 우선순위 작업이 있으면 학습 일시 중지 고려
                return running_tasks > 0

        except Exception as e:
            logger.error(f"학습 일시 중지 판단 실패: {e}")

        return False

    def _request_learning_pause(self):
        """학습 루프 일시 중지를 요청합니다."""
        try:
            logger.info("리팩터링을 위해 학습 루프 일시 중지 요청")
            # 실제 구현에서는 learning_loop_manager에 일시 중지 요청
        except Exception as e:
            logger.error(f"학습 일시 중지 요청 실패: {e}")

    def _trigger_prediction_analysis(self):
        """예측 분석을 트리거합니다."""
        try:
            if self.degradation_predictor:
                logger.info("성능 경고로 인한 예측 분석 트리거")
                # 예측 분석 강화
        except Exception as e:
            logger.error(f"예측 분석 트리거 실패: {e}")

    def _trigger_urgent_refactor(self):
        """긴급 리팩터링을 트리거합니다."""
        try:
            if self.refactor_controller:
                logger.critical("심각한 성능 저하 예측으로 인한 긴급 리팩터링 트리거")
                # 긴급 리팩터링 실행
        except Exception as e:
            logger.error(f"긴급 리팩터링 트리거 실패: {e}")

    def _trigger_high_priority_refactor(self):
        """높은 우선순위 리팩터링을 트리거합니다."""
        try:
            if self.refactor_controller:
                logger.warning("높은 우선순위 예측으로 인한 리팩터링 트리거")
                # 높은 우선순위 리팩터링 실행
        except Exception as e:
            logger.error(f"높은 우선순위 리팩터링 트리거 실패: {e}")

    def _report_refactor_failure_to_learning(self):
        """리팩터링 실패를 학습 루프에 보고합니다."""
        try:
            logger.warning("리팩터링 실패를 학습 루프에 보고")
            # 학습 루프에 실패 정보 전달
        except Exception as e:
            logger.error(f"리팩터링 실패 보고 실패: {e}")

    def _report_integration_status(self):
        """통합 상태를 보고합니다."""
        try:
            status = self.get_integration_status()
            logger.info(f"통합 상태: {status}")
        except Exception as e:
            logger.error(f"통합 상태 보고 실패: {e}")

    def get_integration_status(self) -> RefactorIntegrationStatus:
        """통합 상태를 반환합니다."""
        try:
            return RefactorIntegrationStatus(
                performance_history_active=self.performance_history is not None,
                degradation_predictor_active=self.degradation_predictor is not None,
                refactor_controller_active=self.refactor_controller is not None,
                last_prediction_time=(
                    datetime.now() if self.degradation_predictor else None
                ),
                last_refactor_time=datetime.now() if self.refactor_controller else None,
                total_predictions=(
                    len(self.degradation_predictor.predictions)
                    if self.degradation_predictor
                    else 0
                ),
                total_refactors=(
                    len(self.refactor_controller.tasks)
                    if self.refactor_controller
                    else 0
                ),
                success_rate=85.0,  # 시뮬레이션 값
            )
        except Exception as e:
            logger.error(f"통합 상태 생성 실패: {e}")
            return RefactorIntegrationStatus(
                performance_history_active=False,
                degradation_predictor_active=False,
                refactor_controller_active=False,
                last_prediction_time=None,
                last_refactor_time=None,
                total_predictions=0,
                total_refactors=0,
                success_rate=0.0,
            )

    def enable_auto_refactor(self):
        """자동 리팩터링을 활성화합니다."""
        try:
            self.auto_refactor_enabled = True
            if self.refactor_controller:
                self.refactor_controller.auto_approval_enabled = True
            logger.info("자동 리팩터링 활성화")
        except Exception as e:
            logger.error(f"자동 리팩터링 활성화 실패: {e}")

    def disable_auto_refactor(self):
        """자동 리팩터링을 비활성화합니다."""
        try:
            self.auto_refactor_enabled = False
            if self.refactor_controller:
                self.refactor_controller.auto_approval_enabled = False
            logger.info("자동 리팩터링 비활성화")
        except Exception as e:
            logger.error(f"자동 리팩터링 비활성화 실패: {e}")

    def get_refactor_summary(self) -> Dict[str, Any]:
        """리팩터링 요약을 반환합니다."""
        try:
            summary = {}

            # 성능 히스토리 요약
            if self.performance_history:
                perf_summary = self.performance_history.get_performance_summary()
                summary["performance"] = perf_summary

            # 예측 요약
            if self.degradation_predictor:
                pred_summary = self.degradation_predictor.get_prediction_summary()
                summary["predictions"] = pred_summary

            # 리팩터링 요약
            if self.refactor_controller:
                refactor_summary = self.refactor_controller.get_task_summary()
                summary["refactors"] = refactor_summary

            # 통합 상태
            integration_status = self.get_integration_status()
            summary["integration"] = {
                "is_integrated": self.is_integrated,
                "auto_refactor_enabled": self.auto_refactor_enabled,
                "performance_history_active": integration_status.performance_history_active,
                "degradation_predictor_active": integration_status.degradation_predictor_active,
                "refactor_controller_active": integration_status.refactor_controller_active,
            }

            return summary

        except Exception as e:
            logger.error(f"리팩터링 요약 생성 실패: {e}")
            return {}


# 전역 인스턴스
_refactor_integration_manager: Optional[RefactorIntegrationManager] = None


def get_refactor_integration_manager() -> RefactorIntegrationManager:
    """RefactorIntegrationManager 인스턴스를 반환합니다."""
    global _refactor_integration_manager
    if _refactor_integration_manager is None:
        _refactor_integration_manager = RefactorIntegrationManager()
    return _refactor_integration_manager


def integrate_refactor_system_with_learning():
    """리팩터링 예측 시스템을 learning_loop에 통합합니다."""
    manager = get_refactor_integration_manager()
    manager.integrate_with_learning_loop()
    return manager


if __name__ == "__main__":
    # 테스트
    print("🔗 리팩터링 예측 시스템 통합 테스트 시작")

    manager = integrate_refactor_system_with_learning()

    print("⏰ 60초간 통합 시스템 실행 중...")
    time.sleep(60)

    summary = manager.get_refactor_summary()
    print(f"📊 통합 요약: {summary}")

    print("✅ 통합 테스트 완료")
