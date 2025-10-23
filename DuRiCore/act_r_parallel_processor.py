#!/usr/bin/env python3
"""
ACT-R 병렬 처리 시스템
DuRi Phase 6.1 - 성능 23% 향상 목표

기능:
1. asyncio.gather를 활용한 병렬 처리
2. 작업 우선순위 관리
3. 리소스 최적화
4. 성능 모니터링
"""

import asyncio
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """작업 우선순위"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """작업 상태"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ParallelTask:
    """병렬 작업 정보"""

    id: str
    name: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.kwargs is None:
            self.kwargs = {}


class ACTRParallelProcessor:
    """ACT-R 병렬 처리 시스템"""

    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks: Dict[str, ParallelTask] = {}
        self.completed_tasks: List[ParallelTask] = []
        self.task_queue: List[ParallelTask] = []
        self.performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "parallel_efficiency": 0.0,
            "performance_improvement": 0.0,
        }
        self.execution_history = []

        # 성능 측정용
        self.baseline_execution_time = 0.104  # 현재 기준 시간
        self.target_execution_time = 0.08  # 목표 시간 (23% 향상)

        logger.info("🚀 ACT-R 병렬 처리 시스템 초기화 완료")

    async def execute_parallel_tasks(self, tasks: List[ParallelTask]) -> List[Any]:
        """병렬 작업 실행"""
        logger.info(f"⚡ {len(tasks)}개 작업 병렬 실행 시작")

        start_time = time.time()

        try:
            # 작업을 우선순위별로 정렬
            sorted_tasks = sorted(tasks, key=lambda x: x.priority.value)

            # 병렬 실행을 위한 코루틴 생성
            coroutines = []
            for task in sorted_tasks:
                coroutine = self._execute_single_task(task)
                coroutines.append(coroutine)

            # asyncio.gather를 사용한 병렬 실행
            results = await asyncio.gather(*coroutines, return_exceptions=True)

            execution_time = time.time() - start_time

            # 성능 메트릭 업데이트
            self._update_performance_metrics(execution_time, len(tasks))

            logger.info(f"✅ 병렬 실행 완료: {execution_time:.3f}초")
            return results

        except Exception as e:
            logger.error(f"❌ 병렬 실행 실패: {e}")
            return []

    async def _execute_single_task(self, task: ParallelTask) -> Any:
        """단일 작업 실행"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            # 작업 실행
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                # 동기 함수를 비동기로 실행
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, task.function, *task.args, **task.kwargs)

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            task.execution_time = (task.completed_at - task.started_at).total_seconds()

            logger.info(f"✅ 작업 완료: {task.name} ({task.execution_time:.3f}초)")
            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            task.execution_time = (task.completed_at - task.started_at).total_seconds()

            logger.error(f"❌ 작업 실패: {task.name} - {e}")
            return None

    def _update_performance_metrics(self, execution_time: float, task_count: int):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_tasks"] += task_count
        self.performance_metrics["completed_tasks"] += task_count

        # 평균 실행 시간 계산
        if self.completed_tasks:
            avg_time = statistics.mean([task.execution_time for task in self.completed_tasks])
            self.performance_metrics["average_execution_time"] = avg_time

        # 병렬 효율성 계산
        if self.baseline_execution_time > 0:
            efficiency = (self.baseline_execution_time / execution_time) * 100
            self.performance_metrics["parallel_efficiency"] = efficiency

        # 성능 향상률 계산
        if self.baseline_execution_time > 0:
            improvement = ((self.baseline_execution_time - execution_time) / self.baseline_execution_time) * 100
            self.performance_metrics["performance_improvement"] = improvement

    async def execute_judgment_parallel(self, judgment_tasks: List[Callable]) -> List[Any]:
        """판단 작업 병렬 실행"""
        logger.info("🧠 판단 작업 병렬 실행")

        tasks = []
        for i, task_func in enumerate(judgment_tasks):
            task = ParallelTask(
                id=f"judgment_{i}",
                name=f"판단 작업 {i+1}",
                function=task_func,
                priority=TaskPriority.HIGH,
            )
            tasks.append(task)

        return await self.execute_parallel_tasks(tasks)

    async def execute_action_parallel(self, action_tasks: List[Callable]) -> List[Any]:
        """행동 작업 병렬 실행"""
        logger.info("⚡ 행동 작업 병렬 실행")

        tasks = []
        for i, task_func in enumerate(action_tasks):
            task = ParallelTask(
                id=f"action_{i}",
                name=f"행동 작업 {i+1}",
                function=task_func,
                priority=TaskPriority.MEDIUM,
            )
            tasks.append(task)

        return await self.execute_parallel_tasks(tasks)

    async def execute_feedback_parallel(self, feedback_tasks: List[Callable]) -> List[Any]:
        """피드백 작업 병렬 실행"""
        logger.info("🔄 피드백 작업 병렬 실행")

        tasks = []
        for i, task_func in enumerate(feedback_tasks):
            task = ParallelTask(
                id=f"feedback_{i}",
                name=f"피드백 작업 {i+1}",
                function=task_func,
                priority=TaskPriority.LOW,
            )
            tasks.append(task)

        return await self.execute_parallel_tasks(tasks)

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        return {
            "metrics": self.performance_metrics,
            "target_improvement": 23.0,  # 목표 23% 향상
            "current_improvement": self.performance_metrics["performance_improvement"],
            "baseline_time": self.baseline_execution_time,
            "target_time": self.target_execution_time,
            "efficiency": self.performance_metrics["parallel_efficiency"],
            "total_completed": len(self.completed_tasks),
            "success_rate": (
                self.performance_metrics["completed_tasks"] / max(self.performance_metrics["total_tasks"], 1)
            )
            * 100,
        }

    def add_task_to_queue(self, task: ParallelTask):
        """작업 큐에 추가"""
        self.task_queue.append(task)
        logger.info(f"📋 작업 큐에 추가: {task.name}")

    async def process_task_queue(self):
        """작업 큐 처리"""
        if not self.task_queue:
            return []

        # 큐에서 작업 가져오기
        tasks_to_execute = self.task_queue[: self.max_concurrent_tasks]
        self.task_queue = self.task_queue[self.max_concurrent_tasks :]

        return await self.execute_parallel_tasks(tasks_to_execute)


# 테스트용 샘플 함수들
async def sample_judgment_task(data: str) -> Dict[str, Any]:
    """샘플 판단 작업"""
    await asyncio.sleep(0.02)  # 20ms 시뮬레이션
    return {
        "type": "judgment",
        "data": data,
        "result": f"판단 결과: {data}",
        "confidence": 0.85,
    }


async def sample_action_task(action: str) -> Dict[str, Any]:
    """샘플 행동 작업"""
    await asyncio.sleep(0.03)  # 30ms 시뮬레이션
    return {
        "type": "action",
        "action": action,
        "result": f"행동 실행: {action}",
        "status": "success",
    }


async def sample_feedback_task(feedback: str) -> Dict[str, Any]:
    """샘플 피드백 작업"""
    await asyncio.sleep(0.01)  # 10ms 시뮬레이션
    return {
        "type": "feedback",
        "feedback": feedback,
        "result": f"피드백 처리: {feedback}",
        "quality": 0.9,
    }


async def test_parallel_processor():
    """병렬 처리 시스템 테스트"""
    logger.info("🧪 ACT-R 병렬 처리 시스템 테스트 시작")

    processor = ACTRParallelProcessor(max_concurrent_tasks=5)

    # 테스트 작업 생성
    judgment_tasks = [
        lambda: sample_judgment_task("사용자 입력 분석"),
        lambda: sample_judgment_task("컨텍스트 평가"),
        lambda: sample_judgment_task("우선순위 결정"),
    ]

    action_tasks = [
        lambda: sample_action_task("응답 생성"),
        lambda: sample_action_task("메모리 업데이트"),
        lambda: sample_action_task("학습 진행"),
    ]

    feedback_tasks = [
        lambda: sample_feedback_task("성능 평가"),
        lambda: sample_feedback_task("개선점 식별"),
        lambda: sample_feedback_task("다음 단계 계획"),
    ]

    # 병렬 실행 테스트
    start_time = time.time()

    judgment_results = await processor.execute_judgment_parallel(judgment_tasks)
    action_results = await processor.execute_action_parallel(action_tasks)
    feedback_results = await processor.execute_feedback_parallel(feedback_tasks)

    total_time = time.time() - start_time

    # 결과 출력
    logger.info("📊 테스트 결과:")
    logger.info(f"   총 실행 시간: {total_time:.3f}초")
    logger.info(f"   판단 결과: {len(judgment_results)}개")
    logger.info(f"   행동 결과: {len(action_results)}개")
    logger.info(f"   피드백 결과: {len(feedback_results)}개")

    # 성능 리포트
    report = processor.get_performance_report()
    logger.info("📈 성능 리포트:")
    logger.info(f"   성능 향상률: {report['current_improvement']:.1f}%")
    logger.info(f"   병렬 효율성: {report['efficiency']:.1f}%")
    logger.info(f"   성공률: {report['success_rate']:.1f}%")

    return report


if __name__ == "__main__":
    asyncio.run(test_parallel_processor())
