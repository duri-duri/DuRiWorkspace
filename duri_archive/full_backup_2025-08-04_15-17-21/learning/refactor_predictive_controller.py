"""
DuRi 리팩터링 예측 컨트롤러

예측된 성능 저하에 따른 리팩터링을 자동으로 실행하고 관리합니다.
"""

import json
import logging
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RefactorStatus(Enum):
    """리팩터링 상태"""

    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RefactorType(Enum):
    """리팩터링 유형"""

    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    MEMORY_OPTIMIZATION = "memory_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    ERROR_HANDLING_IMPROVEMENT = "error_handling_improvement"
    MEMORY_LEAK_FIX = "memory_leak_fix"
    CODE_REFACTORING = "code_refactoring"


@dataclass
class RefactorTask:
    """리팩터링 작업"""

    task_id: str
    recommendation_id: str
    target_module: str
    refactor_type: RefactorType
    priority: str
    expected_impact: float
    implementation_cost: str
    risk_level: str
    description: str
    reasoning: str
    status: RefactorStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    actual_impact: Optional[float] = None


@dataclass
class RefactorResult:
    """리팩터링 결과"""

    task_id: str
    success: bool
    execution_time: float
    before_performance: Dict[str, float]
    after_performance: Dict[str, float]
    improvement_percentage: float
    error_details: Optional[str] = None
    rollback_required: bool = False


class RefactorPredictiveController:
    """DuRi 리팩터링 예측 컨트롤러"""

    def __init__(self):
        """RefactorPredictiveController 초기화"""
        self.tasks: List[RefactorTask] = []
        self.results: List[RefactorResult] = []
        self.is_controlling = False
        self.control_thread: Optional[threading.Thread] = None

        # 백업 디렉토리
        self.backup_dir = Path("refactor_backups")
        self.backup_dir.mkdir(exist_ok=True)

        # 리팩터링 설정
        self.auto_approval_enabled = False  # 기본적으로 수동 승인
        self.max_concurrent_tasks = 2
        self.task_timeout_minutes = 30
        self.rollback_on_failure = True

        # 성능 측정
        self.performance_monitor = None
        self._init_performance_monitor()

        logger.info("RefactorPredictiveController 초기화 완료")

    def _init_performance_monitor(self):
        """성능 모니터를 초기화합니다."""
        try:
            from duri_core.utils.performance_monitor import get_performance_monitor

            self.performance_monitor = get_performance_monitor()
        except Exception as e:
            logger.warning(f"성능 모니터 초기화 실패: {e}")

    def start_controller(self):
        """리팩터링 컨트롤러를 시작합니다."""
        if self.is_controlling:
            logger.warning("이미 실행 중입니다.")
            return

        self.is_controlling = True
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_thread.start()
        logger.info("리팩터링 예측 컨트롤러 시작")

    def stop_controller(self):
        """리팩터링 컨트롤러를 중지합니다."""
        self.is_controlling = False
        if self.control_thread:
            self.control_thread.join(timeout=5)
        logger.info("리팩터링 예측 컨트롤러 중지")

    def _control_loop(self):
        """컨트롤 루프"""
        while self.is_controlling:
            try:
                # 새로운 리팩터링 권장사항 확인
                self._check_new_recommendations()

                # 대기 중인 작업 실행
                self._execute_pending_tasks()

                # 완료된 작업 결과 분석
                self._analyze_completed_tasks()

                # 오래된 작업 정리
                self._cleanup_old_tasks()

                time.sleep(300)  # 5분마다 체크

            except Exception as e:
                logger.error(f"컨트롤 루프 오류: {e}")
                time.sleep(60)

    def _check_new_recommendations(self):
        """새로운 리팩터링 권장사항을 확인합니다."""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.learning.degradation_predictor import (
                get_degradation_predictor,
            )

            predictor = get_degradation_predictor()

            active_recommendations = predictor.get_active_recommendations()

            for recommendation in active_recommendations:
                # 이미 처리된 권장사항인지 확인
                if not self._is_recommendation_processed(
                    recommendation.recommendation_id
                ):
                    # 새로운 리팩터링 작업 생성
                    task = self._create_refactor_task(recommendation)
                    if task:
                        self.tasks.append(task)
                        logger.info(f"새로운 리팩터링 작업 생성: {task.task_id}")

                        # 자동 승인이 활성화된 경우 즉시 승인
                        if self.auto_approval_enabled and task.priority in [
                            "high",
                            "urgent",
                        ]:
                            self.approve_task(task.task_id)

        except Exception as e:
            logger.error(f"새로운 권장사항 확인 실패: {e}")

    def _is_recommendation_processed(self, recommendation_id: str) -> bool:
        """권장사항이 이미 처리되었는지 확인합니다."""
        return any(task.recommendation_id == recommendation_id for task in self.tasks)

    def _create_refactor_task(self, recommendation) -> Optional[RefactorTask]:
        """리팩터링 작업을 생성합니다."""
        try:
            task_id = f"REFACTOR_TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{recommendation.recommendation_id}"

            return RefactorTask(
                task_id=task_id,
                recommendation_id=recommendation.recommendation_id,
                target_module=recommendation.target_module,
                refactor_type=RefactorType(recommendation.refactor_type),
                priority=recommendation.priority.value,
                expected_impact=recommendation.expected_impact,
                implementation_cost=recommendation.implementation_cost,
                risk_level=recommendation.risk_level,
                description=recommendation.description,
                reasoning=recommendation.reasoning,
                status=RefactorStatus.PENDING,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"리팩터링 작업 생성 실패: {e}")
            return None

    def _execute_pending_tasks(self):
        """대기 중인 작업을 실행합니다."""
        try:
            # 승인된 작업 중 실행 가능한 작업 찾기
            approved_tasks = [
                task for task in self.tasks if task.status == RefactorStatus.APPROVED
            ]

            # 실행 중인 작업 수 확인
            running_tasks = [
                task for task in self.tasks if task.status == RefactorStatus.IN_PROGRESS
            ]

            available_slots = self.max_concurrent_tasks - len(running_tasks)

            if available_slots > 0:
                # 우선순위 순으로 정렬하여 실행
                approved_tasks.sort(
                    key=lambda x: self._get_priority_score(x.priority), reverse=True
                )

                for task in approved_tasks[:available_slots]:
                    self._execute_task(task)

        except Exception as e:
            logger.error(f"대기 중인 작업 실행 실패: {e}")

    def _get_priority_score(self, priority: str) -> int:
        """우선순위 점수를 반환합니다."""
        priority_scores = {"urgent": 5, "high": 4, "medium": 3, "low": 2, "none": 1}
        return priority_scores.get(priority, 1)

    def _execute_task(self, task: RefactorTask):
        """리팩터링 작업을 실행합니다."""
        try:
            logger.info(f"리팩터링 작업 시작: {task.task_id}")

            # 작업 상태 업데이트
            task.status = RefactorStatus.IN_PROGRESS
            task.started_at = datetime.now()

            # 백업 생성
            backup_path = self._create_backup(task.target_module)

            # 성능 측정 (이전)
            before_performance = self._measure_performance()

            # 리팩터링 실행
            start_time = time.time()
            success = self._perform_refactoring(task)
            execution_time = time.time() - start_time

            # 성능 측정 (이후)
            after_performance = self._measure_performance()

            # 결과 생성
            result = self._create_refactor_result(
                task, success, execution_time, before_performance, after_performance
            )

            # 결과 저장
            self.results.append(result)

            # 작업 상태 업데이트
            if success:
                task.status = RefactorStatus.COMPLETED
                task.completed_at = datetime.now()
                task.actual_impact = result.improvement_percentage
                logger.info(f"리팩터링 작업 완료: {task.task_id}")
            else:
                task.status = RefactorStatus.FAILED
                task.error_message = result.error_details

                # 실패 시 롤백
                if self.rollback_on_failure:
                    self._rollback_refactoring(task, backup_path)

                logger.error(f"리팩터링 작업 실패: {task.task_id}")

        except Exception as e:
            logger.error(f"작업 실행 중 오류: {e}")
            task.status = RefactorStatus.FAILED
            task.error_message = str(e)

    def _create_backup(self, target_module: str) -> Optional[str]:
        """대상 모듈의 백업을 생성합니다."""
        try:
            backup_name = f"{target_module}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.backup_dir / backup_name

            # 실제 파일 경로 찾기
            module_path = self._find_module_path(target_module)
            if module_path and module_path.exists():
                shutil.copytree(module_path, backup_path)
                logger.info(f"백업 생성 완료: {backup_path}")
                return str(backup_path)

        except Exception as e:
            logger.error(f"백업 생성 실패: {e}")

        return None

    def _find_module_path(self, target_module: str) -> Optional[Path]:
        """모듈 경로를 찾습니다."""
        try:
            # 일반적인 모듈 경로 패턴
            possible_paths = [
                Path(f"duri_brain/learning/{target_module}.py"),
                Path(f"duri_core/utils/{target_module}.py"),
                Path(f"duri_brain/app/services/{target_module}.py"),
                Path(f"duri_control/app/services/{target_module}.py"),
            ]

            for path in possible_paths:
                if path.exists():
                    return path

            # 디렉토리로 검색
            for path in possible_paths:
                dir_path = path.parent / path.stem
                if dir_path.exists():
                    return dir_path

        except Exception as e:
            logger.error(f"모듈 경로 찾기 실패: {e}")

        return None

    def _perform_refactoring(self, task: RefactorTask) -> bool:
        """실제 리팩터링을 수행합니다."""
        try:
            # 리팩터링 유형별 실행
            if task.refactor_type == RefactorType.ALGORITHM_OPTIMIZATION:
                return self._optimize_algorithm(task)
            elif task.refactor_type == RefactorType.MEMORY_OPTIMIZATION:
                return self._optimize_memory(task)
            elif task.refactor_type == RefactorType.PERFORMANCE_OPTIMIZATION:
                return self._optimize_performance(task)
            elif task.refactor_type == RefactorType.ERROR_HANDLING_IMPROVEMENT:
                return self._improve_error_handling(task)
            elif task.refactor_type == RefactorType.MEMORY_LEAK_FIX:
                return self._fix_memory_leak(task)
            elif task.refactor_type == RefactorType.CODE_REFACTORING:
                return self._refactor_code(task)
            else:
                logger.warning(f"알 수 없는 리팩터링 유형: {task.refactor_type}")
                return False

        except Exception as e:
            logger.error(f"리팩터링 수행 실패: {e}")
            return False

    def _optimize_algorithm(self, task: RefactorTask) -> bool:
        """알고리즘 최적화를 수행합니다."""
        try:
            # 시뮬레이션: 알고리즘 최적화
            logger.info(f"알고리즘 최적화 실행: {task.target_module}")
            time.sleep(2)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"알고리즘 최적화 실패: {e}")
            return False

    def _optimize_memory(self, task: RefactorTask) -> bool:
        """메모리 최적화를 수행합니다."""
        try:
            # 시뮬레이션: 메모리 최적화
            logger.info(f"메모리 최적화 실행: {task.target_module}")
            time.sleep(1.5)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return False

    def _optimize_performance(self, task: RefactorTask) -> bool:
        """성능 최적화를 수행합니다."""
        try:
            # 시뮬레이션: 성능 최적화
            logger.info(f"성능 최적화 실행: {task.target_module}")
            time.sleep(3)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"성능 최적화 실패: {e}")
            return False

    def _improve_error_handling(self, task: RefactorTask) -> bool:
        """오류 처리를 개선합니다."""
        try:
            # 시뮬레이션: 오류 처리 개선
            logger.info(f"오류 처리 개선 실행: {task.target_module}")
            time.sleep(1)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"오류 처리 개선 실패: {e}")
            return False

    def _fix_memory_leak(self, task: RefactorTask) -> bool:
        """메모리 누수를 수정합니다."""
        try:
            # 시뮬레이션: 메모리 누수 수정
            logger.info(f"메모리 누수 수정 실행: {task.target_module}")
            time.sleep(2.5)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"메모리 누수 수정 실패: {e}")
            return False

    def _refactor_code(self, task: RefactorTask) -> bool:
        """코드 리팩터링을 수행합니다."""
        try:
            # 시뮬레이션: 코드 리팩터링
            logger.info(f"코드 리팩터링 실행: {task.target_module}")
            time.sleep(4)  # 시뮬레이션
            return True
        except Exception as e:
            logger.error(f"코드 리팩터링 실패: {e}")
            return False

    def _measure_performance(self) -> Dict[str, float]:
        """성능을 측정합니다."""
        try:
            if self.performance_monitor:
                return self.performance_monitor.get_current_metrics()
            else:
                # 기본 성능 지표 (시뮬레이션)
                return {
                    "cpu_usage": 65.0,
                    "memory_usage": 70.0,
                    "response_time": 2.5,
                    "error_rate": 0.02,
                }
        except Exception as e:
            logger.error(f"성능 측정 실패: {e}")
            return {}

    def _create_refactor_result(
        self,
        task: RefactorTask,
        success: bool,
        execution_time: float,
        before_performance: Dict[str, float],
        after_performance: Dict[str, float],
    ) -> RefactorResult:
        """리팩터링 결과를 생성합니다."""
        try:
            # 성능 개선률 계산
            improvement_percentage = 0.0
            if before_performance and after_performance:
                # CPU 사용량과 메모리 사용량 기준으로 개선률 계산
                cpu_improvement = (
                    before_performance.get("cpu_usage", 0)
                    - after_performance.get("cpu_usage", 0)
                ) / max(before_performance.get("cpu_usage", 1), 1)
                memory_improvement = (
                    before_performance.get("memory_usage", 0)
                    - after_performance.get("memory_usage", 0)
                ) / max(before_performance.get("memory_usage", 1), 1)
                improvement_percentage = (
                    (cpu_improvement + memory_improvement) / 2 * 100
                )

            return RefactorResult(
                task_id=task.task_id,
                success=success,
                execution_time=execution_time,
                before_performance=before_performance,
                after_performance=after_performance,
                improvement_percentage=improvement_percentage,
                error_details=None if success else "리팩터링 실행 중 오류 발생",
                rollback_required=not success and self.rollback_on_failure,
            )

        except Exception as e:
            logger.error(f"리팩터링 결과 생성 실패: {e}")
            return RefactorResult(
                task_id=task.task_id,
                success=False,
                execution_time=execution_time,
                before_performance={},
                after_performance={},
                improvement_percentage=0.0,
                error_details=str(e),
                rollback_required=True,
            )

    def _rollback_refactoring(self, task: RefactorTask, backup_path: Optional[str]):
        """리팩터링을 롤백합니다."""
        try:
            if backup_path and Path(backup_path).exists():
                logger.info(f"리팩터링 롤백 실행: {task.task_id}")
                # 실제 롤백 로직 구현
                time.sleep(1)  # 시뮬레이션
                logger.info(f"롤백 완료: {task.task_id}")
            else:
                logger.warning(f"백업 파일이 없어 롤백 불가: {task.task_id}")

        except Exception as e:
            logger.error(f"롤백 실패: {e}")

    def _analyze_completed_tasks(self):
        """완료된 작업을 분석합니다."""
        try:
            completed_tasks = [
                task for task in self.tasks if task.status == RefactorStatus.COMPLETED
            ]

            for task in completed_tasks:
                # 성능 개선 효과 분석
                if task.actual_impact and task.actual_impact > 0:
                    logger.info(
                        f"리팩터링 성공: {task.task_id} - 개선률: {task.actual_impact:.1f}%"
                    )
                else:
                    logger.warning(f"리팩터링 효과 미미: {task.task_id}")

        except Exception as e:
            logger.error(f"완료된 작업 분석 실패: {e}")

    def _cleanup_old_tasks(self):
        """오래된 작업을 정리합니다."""
        try:
            cutoff_time = datetime.now() - timedelta(days=7)

            # 오래된 작업 제거
            self.tasks = [task for task in self.tasks if task.created_at > cutoff_time]

            # 오래된 결과 제거
            self.results = [
                result
                for result in self.results
                if result.task_id in [task.task_id for task in self.tasks]
            ]

        except Exception as e:
            logger.error(f"오래된 작업 정리 실패: {e}")

    def approve_task(self, task_id: str) -> bool:
        """작업을 승인합니다."""
        try:
            task = next((t for t in self.tasks if t.task_id == task_id), None)
            if task and task.status == RefactorStatus.PENDING:
                task.status = RefactorStatus.APPROVED
                logger.info(f"작업 승인: {task_id}")
                return True
            else:
                logger.warning(f"작업을 찾을 수 없거나 승인할 수 없음: {task_id}")
                return False
        except Exception as e:
            logger.error(f"작업 승인 실패: {e}")
            return False

    def cancel_task(self, task_id: str) -> bool:
        """작업을 취소합니다."""
        try:
            task = next((t for t in self.tasks if t.task_id == task_id), None)
            if task and task.status in [
                RefactorStatus.PENDING,
                RefactorStatus.APPROVED,
            ]:
                task.status = RefactorStatus.CANCELLED
                logger.info(f"작업 취소: {task_id}")
                return True
            else:
                logger.warning(f"작업을 찾을 수 없거나 취소할 수 없음: {task_id}")
                return False
        except Exception as e:
            logger.error(f"작업 취소 실패: {e}")
            return False

    def get_task_summary(self) -> Dict[str, Any]:
        """작업 요약을 반환합니다."""
        try:
            pending_tasks = [
                t for t in self.tasks if t.status == RefactorStatus.PENDING
            ]
            approved_tasks = [
                t for t in self.tasks if t.status == RefactorStatus.APPROVED
            ]
            running_tasks = [
                t for t in self.tasks if t.status == RefactorStatus.IN_PROGRESS
            ]
            completed_tasks = [
                t for t in self.tasks if t.status == RefactorStatus.COMPLETED
            ]
            failed_tasks = [t for t in self.tasks if t.status == RefactorStatus.FAILED]

            return {
                "total_tasks": len(self.tasks),
                "pending_tasks": len(pending_tasks),
                "approved_tasks": len(approved_tasks),
                "running_tasks": len(running_tasks),
                "completed_tasks": len(completed_tasks),
                "failed_tasks": len(failed_tasks),
                "success_rate": len(completed_tasks) / max(len(self.tasks), 1) * 100,
                "recent_tasks": [
                    {
                        "task_id": task.task_id,
                        "target_module": task.target_module,
                        "priority": task.priority,
                        "status": task.status.value,
                        "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    for task in self.tasks[-5:]  # 최근 5개
                ],
            }

        except Exception as e:
            logger.error(f"작업 요약 생성 실패: {e}")
            return {}


# 전역 인스턴스
_refactor_controller: Optional[RefactorPredictiveController] = None


def get_refactor_controller() -> RefactorPredictiveController:
    """RefactorPredictiveController 인스턴스를 반환합니다."""
    global _refactor_controller
    if _refactor_controller is None:
        _refactor_controller = RefactorPredictiveController()
    return _refactor_controller


if __name__ == "__main__":
    # 테스트
    controller = get_refactor_controller()
    controller.start_controller()

    print("🔧 리팩터링 예측 컨트롤러 테스트 시작")
    print("⏰ 60초간 컨트롤러 실행 중...")

    time.sleep(60)

    summary = controller.get_task_summary()
    print(f"📊 작업 요약: {summary}")

    controller.stop_controller()
    print("✅ 테스트 완료")
