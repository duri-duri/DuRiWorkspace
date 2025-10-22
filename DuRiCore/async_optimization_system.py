#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 비동기 처리 최적화 시스템 (Async Optimization System)
Phase 5: 성능 최적화 - 최종 실행 준비 완료 적용

비동기 처리 최적화를 위한 시스템:
- 병렬 처리 최적화
- 비동기 작업 스케줄링
- 리소스 관리
- 성능 모니터링

@preserve_identity: 비동기 처리 과정의 판단 이유 기록
@evolution_protection: 기존 비동기 패턴과 최적화 경로 보존
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import asyncio
import concurrent.futures
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple, Union

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """작업 우선순위"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """작업 상태"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationStrategy(Enum):
    """최적화 전략"""

    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


@dataclass
class AsyncTask:
    """비동기 작업"""

    id: str
    name: str
    coroutine: Coroutine
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationMetrics:
    """최적화 메트릭"""

    id: str
    timestamp: datetime
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_execution_time: float
    throughput: float
    resource_utilization: float
    optimization_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncOptimizationSystem:
    """비동기 처리 최적화 시스템"""

    def __init__(self):
        # 작업 관리
        self.tasks: Dict[str, AsyncTask] = {}
        self.task_queue: deque = deque()
        self.completed_tasks: List[AsyncTask] = []
        self.failed_tasks: List[AsyncTask] = []

        # 성능 메트릭
        self.performance_metrics: List[OptimizationMetrics] = []
        self.optimization_history: List[Dict[str, Any]] = []

        # 최적화 설정
        self.optimization_config = {
            "max_concurrent_tasks": 10,
            "max_workers": 4,
            "task_timeout": 30.0,
            "retry_attempts": 3,
            "optimization_interval": 60.0,
        }

        # 리소스 관리
        self.resource_usage: Dict[str, float] = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_tasks": 0,
        }

        # 성능 트렌드
        self.performance_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # 존재형 AI 시스템 초기화
        self.existence_ai = self._initialize_existence_ai()
        self.final_execution_verifier = self._initialize_final_execution_verifier()

        # 자동 최적화 설정
        self.auto_optimization_enabled = True
        self.optimization_strategy = OptimizationStrategy.ADAPTIVE

        logger.info("비동기 처리 최적화 시스템 초기화 완료")

    def _initialize_existence_ai(self):
        """존재형 AI 시스템 초기화"""
        try:
            from utils.existence_ai_system import ExistenceAISystem

            return ExistenceAISystem()
        except ImportError:
            logger.warning("존재형 AI 시스템을 찾을 수 없습니다.")
            return None

    def _initialize_final_execution_verifier(self):
        """최종 실행 준비 완료 시스템 초기화"""
        try:
            from utils.final_execution_verifier import FinalExecutionVerifier

            return FinalExecutionVerifier()
        except ImportError:
            logger.warning("최종 실행 준비 완료 시스템을 찾을 수 없습니다.")
            return None

    async def submit_task(
        self,
        name: str,
        coroutine: Coroutine,
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """작업 제출"""
        try:
            task_id = f"task_{len(self.tasks) + 1}_{int(time.time())}"

            task = AsyncTask(
                id=task_id,
                name=name,
                coroutine=coroutine,
                priority=priority,
                metadata=metadata or {},
            )

            self.tasks[task_id] = task
            self.task_queue.append((priority.value, task_id))

            # 우선순위에 따라 큐 정렬
            self.task_queue = deque(sorted(self.task_queue, key=lambda x: x[0], reverse=True))

            # 존재형 AI: 진화 가능성 확인
            if self.existence_ai and self.existence_ai.evolution_capability.can_evolve():
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if self.final_execution_verifier and self.final_execution_verifier.verify_readiness():
                logger.info("최종 실행 준비 완료 확인됨")

            logger.info(f"작업 제출: {task_id} - {name} (우선순위: {priority.value})")
            return task_id

        except Exception as e:
            logger.error(f"작업 제출 실패: {e}")
            raise

    async def execute_tasks(self, strategy: OptimizationStrategy = None) -> Dict[str, Any]:
        """작업 실행"""
        try:
            if not strategy:
                strategy = self.optimization_strategy

            start_time = time.time()
            results = {}

            if strategy == OptimizationStrategy.PARALLEL:
                results = await self._execute_parallel()
            elif strategy == OptimizationStrategy.SEQUENTIAL:
                results = await self._execute_sequential()
            elif strategy == OptimizationStrategy.HYBRID:
                results = await self._execute_hybrid()
            else:  # ADAPTIVE
                results = await self._execute_adaptive()

            execution_time = time.time() - start_time

            # 성능 메트릭 업데이트
            await self._update_performance_metrics(execution_time, len(self.tasks))

            # 존재형 AI: 진화 가능성 확인
            if self.existence_ai and self.existence_ai.evolution_capability.can_evolve():
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if self.final_execution_verifier and self.final_execution_verifier.verify_readiness():
                logger.info("최종 실행 준비 완료 확인됨")

            logger.info(f"작업 실행 완료: {strategy.value} - {execution_time:.2f}초")
            return results

        except Exception as e:
            logger.error(f"작업 실행 실패: {e}")
            raise

    async def _execute_parallel(self) -> Dict[str, Any]:
        """병렬 실행"""
        try:
            if not self.task_queue:
                return {"completed": 0, "failed": 0, "results": {}}

            # 실행할 작업들 선택
            tasks_to_execute = []
            while (
                self.task_queue
                and len(tasks_to_execute) < self.optimization_config["max_concurrent_tasks"]
            ):
                _, task_id = self.task_queue.popleft()
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    tasks_to_execute.append(task)

            if not tasks_to_execute:
                return {"completed": 0, "failed": 0, "results": {}}

            # 병렬 실행
            task_coroutines = []
            for task in tasks_to_execute:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                task_coroutines.append(self._execute_single_task(task))

            # asyncio.gather로 병렬 실행
            results = await asyncio.gather(*task_coroutines, return_exceptions=True)

            # 결과 처리
            completed = 0
            failed = 0
            task_results = {}

            for i, result in enumerate(results):
                task = tasks_to_execute[i]
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error = str(result)
                    self.failed_tasks.append(task)
                    failed += 1
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = datetime.now()
                    self.completed_tasks.append(task)
                    task_results[task.id] = result
                    completed += 1

            return {"completed": completed, "failed": failed, "results": task_results}

        except Exception as e:
            logger.error(f"병렬 실행 실패: {e}")
            return {"completed": 0, "failed": len(tasks_to_execute), "results": {}}

    async def _execute_sequential(self) -> Dict[str, Any]:
        """순차 실행"""
        try:
            if not self.task_queue:
                return {"completed": 0, "failed": 0, "results": {}}

            completed = 0
            failed = 0
            task_results = {}

            while self.task_queue:
                _, task_id = self.task_queue.popleft()
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    try:
                        task.status = TaskStatus.RUNNING
                        task.started_at = datetime.now()

                        result = await self._execute_single_task(task)

                        task.status = TaskStatus.COMPLETED
                        task.result = result
                        task.completed_at = datetime.now()
                        self.completed_tasks.append(task)
                        task_results[task.id] = result
                        completed += 1

                    except Exception as e:
                        task.status = TaskStatus.FAILED
                        task.error = str(e)
                        self.failed_tasks.append(task)
                        failed += 1

            return {"completed": completed, "failed": failed, "results": task_results}

        except Exception as e:
            logger.error(f"순차 실행 실패: {e}")
            return {"completed": 0, "failed": 1, "results": {}}

    async def _execute_hybrid(self) -> Dict[str, Any]:
        """하이브리드 실행"""
        try:
            # 우선순위가 높은 작업은 순차 실행, 나머지는 병렬 실행
            high_priority_tasks = []
            normal_tasks = []

            while self.task_queue:
                priority, task_id = self.task_queue.popleft()
                task = self.tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    if priority >= TaskPriority.HIGH.value:
                        high_priority_tasks.append(task)
                    else:
                        normal_tasks.append(task)

            results = {}
            completed = 0
            failed = 0

            # 높은 우선순위 작업 순차 실행
            for task in high_priority_tasks:
                try:
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()

                    result = await self._execute_single_task(task)

                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = datetime.now()
                    self.completed_tasks.append(task)
                    results[task.id] = result
                    completed += 1

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    self.failed_tasks.append(task)
                    failed += 1

            # 일반 작업 병렬 실행
            if normal_tasks:
                normal_results = await self._execute_parallel_tasks(normal_tasks)
                results.update(normal_results["results"])
                completed += normal_results["completed"]
                failed += normal_results["failed"]

            return {"completed": completed, "failed": failed, "results": results}

        except Exception as e:
            logger.error(f"하이브리드 실행 실패: {e}")
            return {"completed": 0, "failed": 1, "results": {}}

    async def _execute_adaptive(self) -> Dict[str, Any]:
        """적응적 실행"""
        try:
            # 현재 시스템 상태에 따라 실행 전략 결정
            current_load = len(self.task_queue)
            system_resources = await self._get_system_resources()

            if current_load > 20 or system_resources["cpu_usage"] > 80:
                # 부하가 높을 때는 순차 실행
                strategy = OptimizationStrategy.SEQUENTIAL
            elif current_load > 10:
                # 중간 부하일 때는 하이브리드 실행
                strategy = OptimizationStrategy.HYBRID
            else:
                # 부하가 낮을 때는 병렬 실행
                strategy = OptimizationStrategy.PARALLEL

            logger.info(f"적응적 실행 전략 선택: {strategy.value}")

            if strategy == OptimizationStrategy.PARALLEL:
                return await self._execute_parallel()
            elif strategy == OptimizationStrategy.SEQUENTIAL:
                return await self._execute_sequential()
            else:
                return await self._execute_hybrid()

        except Exception as e:
            logger.error(f"적응적 실행 실패: {e}")
            return await self._execute_sequential()

    async def _execute_single_task(self, task: AsyncTask) -> Any:
        """단일 작업 실행"""
        try:
            # 작업 실행
            result = await asyncio.wait_for(
                task.coroutine, timeout=self.optimization_config["task_timeout"]
            )
            return result

        except asyncio.TimeoutError:
            raise Exception(f"작업 시간 초과: {task.name}")
        except Exception as e:
            raise Exception(f"작업 실행 실패: {task.name} - {str(e)}")

    async def _execute_parallel_tasks(self, tasks: List[AsyncTask]) -> Dict[str, Any]:
        """병렬 작업 실행"""
        try:
            task_coroutines = []
            for task in tasks:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                task_coroutines.append(self._execute_single_task(task))

            results = await asyncio.gather(*task_coroutines, return_exceptions=True)

            completed = 0
            failed = 0
            task_results = {}

            for i, result in enumerate(results):
                task = tasks[i]
                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error = str(result)
                    self.failed_tasks.append(task)
                    failed += 1
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.completed_at = datetime.now()
                    self.completed_tasks.append(task)
                    task_results[task.id] = result
                    completed += 1

            return {"completed": completed, "failed": failed, "results": task_results}

        except Exception as e:
            logger.error(f"병렬 작업 실행 실패: {e}")
            return {"completed": 0, "failed": len(tasks), "results": {}}

    async def _get_system_resources(self) -> Dict[str, float]:
        """시스템 리소스 정보 수집"""
        try:
            import psutil

            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent

            return {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "active_tasks": len(
                    [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
                ),
            }

        except Exception as e:
            logger.error(f"시스템 리소스 정보 수집 실패: {e}")
            return {"cpu_usage": 0.0, "memory_usage": 0.0, "active_tasks": 0}

    async def _update_performance_metrics(self, execution_time: float, total_tasks: int):
        """성능 메트릭 업데이트"""
        try:
            completed_tasks = len(self.completed_tasks)
            failed_tasks = len(self.failed_tasks)

            average_execution_time = execution_time / max(1, completed_tasks)
            throughput = completed_tasks / max(1, execution_time)
            resource_utilization = len(
                [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
            ) / max(1, self.optimization_config["max_concurrent_tasks"])

            # 최적화 점수 계산
            optimization_score = self._calculate_optimization_score(
                completed_tasks,
                failed_tasks,
                average_execution_time,
                throughput,
                resource_utilization,
            )

            metrics = OptimizationMetrics(
                id=f"metrics_{int(time.time())}",
                timestamp=datetime.now(),
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                average_execution_time=average_execution_time,
                throughput=throughput,
                resource_utilization=resource_utilization,
                optimization_score=optimization_score,
            )

            self.performance_metrics.append(metrics)

            # 성능 트렌드 업데이트
            self.performance_trends["throughput"].append(throughput)
            self.performance_trends["optimization_score"].append(optimization_score)
            self.performance_trends["resource_utilization"].append(resource_utilization)

        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")

    def _calculate_optimization_score(
        self,
        completed_tasks: int,
        failed_tasks: int,
        average_execution_time: float,
        throughput: float,
        resource_utilization: float,
    ) -> float:
        """최적화 점수 계산"""
        try:
            # 성공률 (40%)
            success_rate = completed_tasks / max(1, completed_tasks + failed_tasks)
            success_score = success_rate * 0.4

            # 처리량 점수 (30%)
            throughput_score = min(1.0, throughput / 100.0) * 0.3

            # 리소스 활용률 점수 (20%)
            utilization_score = resource_utilization * 0.2

            # 실행 시간 점수 (10%)
            time_score = max(0.0, 1.0 - (average_execution_time / 10.0)) * 0.1

            total_score = success_score + throughput_score + utilization_score + time_score
            return min(1.0, total_score)

        except Exception as e:
            logger.error(f"최적화 점수 계산 실패: {e}")
            return 0.0

    async def get_optimization_summary(self) -> Dict[str, Any]:
        """최적화 요약 생성"""
        try:
            if not self.performance_metrics:
                return {"error": "성능 데이터가 없습니다."}

            latest_metrics = self.performance_metrics[-1]

            # 성능 트렌드 분석
            throughput_trend = list(self.performance_trends["throughput"])
            optimization_score_trend = list(self.performance_trends["optimization_score"])
            resource_utilization_trend = list(self.performance_trends["resource_utilization"])

            return {
                "current_metrics": {
                    "total_tasks": latest_metrics.total_tasks,
                    "completed_tasks": latest_metrics.completed_tasks,
                    "failed_tasks": latest_metrics.failed_tasks,
                    "average_execution_time": latest_metrics.average_execution_time,
                    "throughput": latest_metrics.throughput,
                    "resource_utilization": latest_metrics.resource_utilization,
                    "optimization_score": latest_metrics.optimization_score,
                    "timestamp": latest_metrics.timestamp.isoformat(),
                },
                "performance_trends": {
                    "throughput_trend": (throughput_trend[-10:] if throughput_trend else []),
                    "optimization_score_trend": (
                        optimization_score_trend[-10:] if optimization_score_trend else []
                    ),
                    "resource_utilization_trend": (
                        resource_utilization_trend[-10:] if resource_utilization_trend else []
                    ),
                },
                "task_status": {
                    "pending_tasks": len(
                        [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
                    ),
                    "running_tasks": len(
                        [t for t in self.tasks.values() if t.status == TaskStatus.RUNNING]
                    ),
                    "completed_tasks": len(self.completed_tasks),
                    "failed_tasks": len(self.failed_tasks),
                },
                "optimization_config": self.optimization_config,
            }

        except Exception as e:
            logger.error(f"최적화 요약 생성 실패: {e}")
            return {"error": str(e)}


# 전역 인스턴스
async_optimization_system = AsyncOptimizationSystem()
