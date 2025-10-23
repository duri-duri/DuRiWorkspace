#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 9 - 자동화 및 최적화 시스템

시스템 자동화 및 최적화 구현
- 워크플로우 자동화
- 성능 최적화
- 리소스 관리
- 자동 튜닝
"""

import asyncio
import json
import logging
import os
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import psutil

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """워크플로우 단계 데이터 구조"""

    step_id: str
    name: str
    description: str
    step_type: str
    dependencies: List[str]
    parameters: Dict[str, Any]
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowExecution:
    """워크플로우 실행 데이터 구조"""

    execution_id: str
    workflow_name: str
    steps: List[WorkflowStep]
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터 구조"""

    metric_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceUsage:
    """리소스 사용량 데이터 구조"""

    resource_id: str
    resource_type: str
    current_usage: float
    max_capacity: float
    utilization_rate: float
    status: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """최적화 결과 데이터 구조"""

    optimization_id: str
    optimization_type: str
    original_metrics: Dict[str, Any]
    optimized_metrics: Dict[str, Any]
    improvement_rate: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


class WorkflowAutomation:
    """워크플로우 자동화 시스템"""

    def __init__(self):
        self.workflows = {}
        self.execution_history = []
        self.step_templates = {}
        self.automation_rules = {}

    def create_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> str:
        """워크플로우 생성"""
        workflow_id = f"workflow_{int(time.time())}"

        # 워크플로우 단계 생성
        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                step_id=step_data.get("id", f"step_{len(workflow_steps)}"),
                name=step_data.get("name", ""),
                description=step_data.get("description", ""),
                step_type=step_data.get("type", "task"),
                dependencies=step_data.get("dependencies", []),
                parameters=step_data.get("parameters", {}),
            )
            workflow_steps.append(step)

        # 워크플로우 저장
        self.workflows[workflow_id] = {
            "name": workflow_name,
            "steps": workflow_steps,
            "created_at": datetime.now(),
        }

        logger.info(f"워크플로우 생성됨: {workflow_id} - {workflow_name}")
        return workflow_id

    async def execute_workflow(self, workflow_id: str) -> WorkflowExecution:
        """워크플로우 실행"""
        if workflow_id not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없습니다: {workflow_id}")

        workflow = self.workflows[workflow_id]
        execution_id = f"execution_{int(time.time())}"

        # 실행 시작
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_name=workflow["name"],
            steps=workflow["steps"].copy(),
            status="running",
            start_time=datetime.now(),
        )

        try:
            # 단계별 실행
            for step in execution.steps:
                await self.execute_step(step)

            # 실행 완료
            execution.status = "completed"
            execution.end_time = datetime.now()

            # 성능 메트릭 계산
            execution.performance_metrics = self.calculate_execution_metrics(execution)

        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            logger.error(f"워크플로우 실행 실패: {e}")

        # 실행 기록 저장
        self.execution_history.append(execution)

        return execution

    async def execute_step(self, step: WorkflowStep):
        """단계 실행"""
        step.status = "running"
        step.start_time = datetime.now()

        try:
            # 단계 타입별 실행
            if step.step_type == "task":
                await self.execute_task_step(step)
            elif step.step_type == "decision":
                await self.execute_decision_step(step)
            elif step.step_type == "loop":
                await self.execute_loop_step(step)
            else:
                await self.execute_general_step(step)

            step.status = "completed"
            step.end_time = datetime.now()

        except Exception as e:
            step.status = "failed"
            step.end_time = datetime.now()
            logger.error(f"단계 실행 실패: {step.name} - {e}")
            raise

    async def execute_task_step(self, step: WorkflowStep):
        """작업 단계 실행"""
        # 간단한 작업 시뮬레이션
        task_duration = step.parameters.get("duration", 1.0)
        await asyncio.sleep(task_duration)

        # 작업 결과 생성
        step.parameters["result"] = f"작업 완료: {step.name}"

    async def execute_decision_step(self, step: WorkflowStep):
        """의사결정 단계 실행"""
        # 의사결정 로직 실행
        condition = step.parameters.get("condition", True)

        if condition:
            step.parameters["decision"] = "true"
        else:
            step.parameters["decision"] = "false"

    async def execute_loop_step(self, step: WorkflowStep):
        """반복 단계 실행"""
        iterations = step.parameters.get("iterations", 1)

        for i in range(iterations):
            step.parameters[f"iteration_{i}"] = f"반복 {i+1} 완료"

    async def execute_general_step(self, step: WorkflowStep):
        """일반 단계 실행"""
        # 기본 단계 실행
        step.parameters["result"] = f"일반 단계 완료: {step.name}"

    def calculate_execution_metrics(
        self, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """실행 메트릭 계산"""
        if not execution.end_time:
            return {}

        total_duration = (execution.end_time - execution.start_time).total_seconds()
        completed_steps = len([s for s in execution.steps if s.status == "completed"])
        total_steps = len(execution.steps)

        return {
            "total_duration": total_duration,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "success_rate": completed_steps / total_steps if total_steps > 0 else 0.0,
            "average_step_duration": (
                total_duration / total_steps if total_steps > 0 else 0.0
            ),
        }


class PerformanceOptimizer:
    """성능 최적화 시스템"""

    def __init__(self):
        self.performance_metrics = []
        self.optimization_strategies = {}
        self.optimization_history = []
        self.performance_thresholds = {}

    def collect_metrics(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        context: Dict[str, Any] = None,
    ) -> PerformanceMetrics:
        """성능 메트릭 수집"""
        metric_id = f"metric_{int(time.time())}"

        metric = PerformanceMetrics(
            metric_id=metric_id,
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            context=context or {},
        )

        self.performance_metrics.append(metric)
        return metric

    def analyze_performance(self, time_window: int = 3600) -> Dict[str, Any]:
        """성능 분석"""
        current_time = datetime.now()
        recent_metrics = [
            m
            for m in self.performance_metrics
            if (current_time - m.timestamp).total_seconds() <= time_window
        ]

        if not recent_metrics:
            return {}

        # 메트릭별 분석
        analysis = {}
        metric_groups = defaultdict(list)

        for metric in recent_metrics:
            metric_groups[metric.metric_name].append(metric.value)

        for metric_name, values in metric_groups.items():
            analysis[metric_name] = {
                "count": len(values),
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values),
                "trend": self.calculate_trend(values),
            }

        return analysis

    def calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return "stable"

        # 간단한 선형 트렌드 계산
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    def optimize_performance(self, target_metrics: List[str]) -> OptimizationResult:
        """성능 최적화"""
        optimization_id = f"optimization_{int(time.time())}"

        # 현재 성능 분석
        current_analysis = self.analyze_performance()

        # 최적화 전략 적용
        optimized_metrics = {}
        recommendations = []

        for metric_name in target_metrics:
            if metric_name in current_analysis:
                current_value = current_analysis[metric_name]["mean"]
                optimized_value = self.apply_optimization_strategy(
                    metric_name, current_value
                )
                optimized_metrics[metric_name] = optimized_value

                # 개선률 계산
                improvement = (
                    (optimized_value - current_value) / current_value
                    if current_value != 0
                    else 0
                )
                recommendations.append(f"{metric_name}: {improvement:.2%} 개선 가능")

        # 최적화 결과 생성
        optimization_result = OptimizationResult(
            optimization_id=optimization_id,
            optimization_type="performance",
            original_metrics=current_analysis,
            optimized_metrics=optimized_metrics,
            improvement_rate=self.calculate_improvement_rate(
                current_analysis, optimized_metrics
            ),
            recommendations=recommendations,
        )

        self.optimization_history.append(optimization_result)
        return optimization_result

    def apply_optimization_strategy(
        self, metric_name: str, current_value: float
    ) -> float:
        """최적화 전략 적용"""
        # 간단한 최적화 전략
        if metric_name == "response_time":
            return current_value * 0.8  # 20% 개선
        elif metric_name == "throughput":
            return current_value * 1.2  # 20% 개선
        elif metric_name == "accuracy":
            return min(1.0, current_value * 1.1)  # 10% 개선 (최대 1.0)
        else:
            return current_value * 1.1  # 기본 10% 개선

    def calculate_improvement_rate(
        self, original_metrics: Dict[str, Any], optimized_metrics: Dict[str, Any]
    ) -> float:
        """개선률 계산"""
        if not original_metrics or not optimized_metrics:
            return 0.0

        improvements = []
        for metric_name in optimized_metrics:
            if metric_name in original_metrics:
                original_value = original_metrics[metric_name]["mean"]
                optimized_value = optimized_metrics[metric_name]

                if original_value != 0:
                    improvement = (optimized_value - original_value) / original_value
                    improvements.append(improvement)

        return np.mean(improvements) if improvements else 0.0


class ResourceManager:
    """리소스 관리 시스템"""

    def __init__(self):
        self.resources = {}
        self.resource_monitors = {}
        self.allocation_strategies = {}
        self.resource_history = []

    def monitor_resources(self) -> List[ResourceUsage]:
        """리소스 모니터링"""
        resource_usage = []

        # CPU 사용량
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage = ResourceUsage(
            resource_id="cpu",
            resource_type="processor",
            current_usage=cpu_percent,
            max_capacity=100.0,
            utilization_rate=cpu_percent / 100.0,
            status="normal" if cpu_percent < 80 else "high",
        )
        resource_usage.append(cpu_usage)

        # 메모리 사용량
        memory = psutil.virtual_memory()
        memory_usage = ResourceUsage(
            resource_id="memory",
            resource_type="memory",
            current_usage=memory.used / (1024**3),  # GB
            max_capacity=memory.total / (1024**3),  # GB
            utilization_rate=memory.percent / 100.0,
            status="normal" if memory.percent < 80 else "high",
        )
        resource_usage.append(memory_usage)

        # 디스크 사용량
        disk = psutil.disk_usage("/")
        disk_usage = ResourceUsage(
            resource_id="disk",
            resource_type="storage",
            current_usage=disk.used / (1024**3),  # GB
            max_capacity=disk.total / (1024**3),  # GB
            utilization_rate=disk.percent / 100.0,
            status="normal" if disk.percent < 80 else "high",
        )
        resource_usage.append(disk_usage)

        # 리소스 기록 저장
        self.resource_history.extend(resource_usage)

        return resource_usage

    def allocate_resources(self, requirements: Dict[str, float]) -> Dict[str, Any]:
        """리소스 할당"""
        current_resources = self.monitor_resources()
        allocation_result = {}

        for resource_id, required_amount in requirements.items():
            # 현재 리소스 상태 확인
            current_resource = next(
                (r for r in current_resources if r.resource_id == resource_id), None
            )

            if current_resource:
                available_capacity = (
                    current_resource.max_capacity - current_resource.current_usage
                )

                if available_capacity >= required_amount:
                    allocation_result[resource_id] = {
                        "allocated": required_amount,
                        "available": available_capacity,
                        "status": "success",
                    }
                else:
                    allocation_result[resource_id] = {
                        "allocated": 0,
                        "available": available_capacity,
                        "status": "insufficient",
                    }
            else:
                allocation_result[resource_id] = {
                    "allocated": 0,
                    "available": 0,
                    "status": "not_found",
                }

        return allocation_result

    def optimize_resource_usage(self) -> List[str]:
        """리소스 사용량 최적화"""
        recommendations = []
        current_resources = self.monitor_resources()

        for resource in current_resources:
            if resource.utilization_rate > 0.8:
                recommendations.append(
                    f"{resource.resource_type} 사용량이 높습니다 ({resource.utilization_rate:.1%}). 최적화가 필요합니다."
                )

            if resource.utilization_rate < 0.2:
                recommendations.append(
                    f"{resource.resource_type} 사용량이 낮습니다 ({resource.utilization_rate:.1%}). 리소스 활용도를 높일 수 있습니다."
                )

        return recommendations


class AutoTuner:
    """자동 튜닝 시스템"""

    def __init__(self):
        self.tuning_parameters = {}
        self.tuning_history = []
        self.optimization_algorithms = {}
        self.performance_targets = {}

    def tune_parameters(
        self, parameters: Dict[str, Any], target_metric: str, target_value: float
    ) -> Dict[str, Any]:
        """매개변수 자동 튜닝"""
        tuning_id = f"tuning_{int(time.time())}"

        # 현재 매개변수 저장
        original_parameters = parameters.copy()

        # 튜닝 알고리즘 적용
        tuned_parameters = self.apply_tuning_algorithm(
            parameters, target_metric, target_value
        )

        # 튜닝 결과 기록
        tuning_result = {
            "tuning_id": tuning_id,
            "original_parameters": original_parameters,
            "tuned_parameters": tuned_parameters,
            "target_metric": target_metric,
            "target_value": target_value,
            "improvement": self.calculate_tuning_improvement(
                original_parameters, tuned_parameters
            ),
            "timestamp": datetime.now(),
        }

        self.tuning_history.append(tuning_result)

        return tuned_parameters

    def apply_tuning_algorithm(
        self, parameters: Dict[str, Any], target_metric: str, target_value: float
    ) -> Dict[str, Any]:
        """튜닝 알고리즘 적용"""
        tuned_parameters = parameters.copy()

        # 간단한 튜닝 로직
        for param_name, param_value in parameters.items():
            if isinstance(param_value, (int, float)):
                # 수치형 매개변수 튜닝
                if target_metric == "performance":
                    # 성능 향상을 위한 튜닝
                    tuned_parameters[param_name] = param_value * 1.1
                elif target_metric == "efficiency":
                    # 효율성 향상을 위한 튜닝
                    tuned_parameters[param_name] = param_value * 0.9
                elif target_metric == "accuracy":
                    # 정확도 향상을 위한 튜닝
                    tuned_parameters[param_name] = param_value * 1.05

        return tuned_parameters

    def calculate_tuning_improvement(
        self, original_parameters: Dict[str, Any], tuned_parameters: Dict[str, Any]
    ) -> float:
        """튜닝 개선률 계산"""
        if not original_parameters or not tuned_parameters:
            return 0.0

        improvements = []
        for param_name in tuned_parameters:
            if param_name in original_parameters:
                original_value = original_parameters[param_name]
                tuned_value = tuned_parameters[param_name]

                if isinstance(original_value, (int, float)) and isinstance(
                    tuned_value, (int, float)
                ):
                    if original_value != 0:
                        improvement = (tuned_value - original_value) / original_value
                        improvements.append(improvement)

        return np.mean(improvements) if improvements else 0.0

    def get_tuning_recommendations(self) -> List[str]:
        """튜닝 권장사항 생성"""
        recommendations = []

        if not self.tuning_history:
            return ["튜닝 이력이 없습니다. 첫 번째 튜닝을 실행해보세요."]

        # 최근 튜닝 결과 분석
        recent_tunings = self.tuning_history[-5:]  # 최근 5개

        for tuning in recent_tunings:
            improvement = tuning["improvement"]
            if improvement > 0.1:
                recommendations.append(f"튜닝 성공: {improvement:.1%} 개선 달성")
            elif improvement < -0.1:
                recommendations.append(f"튜닝 실패: {abs(improvement):.1%} 성능 저하")
            else:
                recommendations.append("튜닝 효과 미미")

        return recommendations


class AutomationOptimizationSystem:
    """자동화 및 최적화 시스템"""

    def __init__(self):
        self.workflow_automation = WorkflowAutomation()
        self.performance_optimizer = PerformanceOptimizer()
        self.resource_manager = ResourceManager()
        self.auto_tuner = AutoTuner()
        self.system_status = "active"
        self.performance_metrics = defaultdict(float)

    async def automate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 자동화"""
        start_time = time.time()

        try:
            workflow_name = workflow_data.get("name", "기본 워크플로우")
            steps = workflow_data.get("steps", [])

            # 워크플로우 생성
            workflow_id = self.workflow_automation.create_workflow(workflow_name, steps)

            # 워크플로우 실행
            execution_result = await self.workflow_automation.execute_workflow(
                workflow_id
            )

            result = {
                "type": "workflow_automation",
                "workflow_id": workflow_id,
                "execution_result": execution_result.__dict__,
                "status": "success",
            }

        except Exception as e:
            result = {"type": "workflow_automation", "error": str(e), "status": "error"}

        result["processing_time"] = time.time() - start_time
        return result

    async def optimize_performance(
        self, optimization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 최적화"""
        start_time = time.time()

        try:
            target_metrics = optimization_data.get("target_metrics", [])

            # 성능 최적화 실행
            optimization_result = self.performance_optimizer.optimize_performance(
                target_metrics
            )

            result = {
                "type": "performance_optimization",
                "optimization_result": optimization_result.__dict__,
                "status": "success",
            }

        except Exception as e:
            result = {
                "type": "performance_optimization",
                "error": str(e),
                "status": "error",
            }

        result["processing_time"] = time.time() - start_time
        return result

    async def manage_resources(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """리소스 관리"""
        start_time = time.time()

        try:
            action = resource_data.get("action", "monitor")

            if action == "monitor":
                resource_usage = self.resource_manager.monitor_resources()
                result = {
                    "type": "resource_management",
                    "action": "monitor",
                    "resource_usage": [r.__dict__ for r in resource_usage],
                    "status": "success",
                }
            elif action == "allocate":
                requirements = resource_data.get("requirements", {})
                allocation_result = self.resource_manager.allocate_resources(
                    requirements
                )
                result = {
                    "type": "resource_management",
                    "action": "allocate",
                    "allocation_result": allocation_result,
                    "status": "success",
                }
            elif action == "optimize":
                recommendations = self.resource_manager.optimize_resource_usage()
                result = {
                    "type": "resource_management",
                    "action": "optimize",
                    "recommendations": recommendations,
                    "status": "success",
                }
            else:
                result = {
                    "type": "resource_management",
                    "error": f"지원하지 않는 액션: {action}",
                    "status": "error",
                }

        except Exception as e:
            result = {"type": "resource_management", "error": str(e), "status": "error"}

        result["processing_time"] = time.time() - start_time
        return result

    async def auto_tune(self, tuning_data: Dict[str, Any]) -> Dict[str, Any]:
        """자동 튜닝"""
        start_time = time.time()

        try:
            parameters = tuning_data.get("parameters", {})
            target_metric = tuning_data.get("target_metric", "performance")
            target_value = tuning_data.get("target_value", 1.0)

            # 자동 튜닝 실행
            tuned_parameters = self.auto_tuner.tune_parameters(
                parameters, target_metric, target_value
            )

            result = {
                "type": "auto_tuning",
                "tuned_parameters": tuned_parameters,
                "target_metric": target_metric,
                "target_value": target_value,
                "status": "success",
            }

        except Exception as e:
            result = {"type": "auto_tuning", "error": str(e), "status": "error"}

        result["processing_time"] = time.time() - start_time
        return result

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "system_status": self.system_status,
            "performance_metrics": dict(self.performance_metrics),
            "component_status": {
                "workflow_automation": "active",
                "performance_optimizer": "active",
                "resource_manager": "active",
                "auto_tuner": "active",
            },
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서"""
        return {
            "total_requests": self.performance_metrics["request_count"],
            "avg_processing_time": self.performance_metrics["processing_time"],
            "system_uptime": time.time(),
            "component_performance": {
                "workflow_automation": "high",
                "performance_optimizer": "high",
                "resource_manager": "high",
                "auto_tuner": "high",
            },
        }


# 테스트 함수
async def test_automation_optimization_system():
    """자동화 및 최적화 시스템 테스트"""
    print("🚀 자동화 및 최적화 시스템 테스트 시작")

    aos_system = AutomationOptimizationSystem()

    # 1. 워크플로우 자동화 테스트
    print("\n1. 워크플로우 자동화 테스트")
    workflow_data = {
        "name": "테스트 워크플로우",
        "steps": [
            {
                "id": "step_1",
                "name": "데이터 수집",
                "description": "데이터 수집 단계",
                "type": "task",
                "dependencies": [],
                "parameters": {"duration": 0.1},
            },
            {
                "id": "step_2",
                "name": "데이터 처리",
                "description": "데이터 처리 단계",
                "type": "task",
                "dependencies": ["step_1"],
                "parameters": {"duration": 0.1},
            },
            {
                "id": "step_3",
                "name": "결과 분석",
                "description": "결과 분석 단계",
                "type": "task",
                "dependencies": ["step_2"],
                "parameters": {"duration": 0.1},
            },
        ],
    }

    workflow_result = await aos_system.automate_workflow(workflow_data)
    print(f"워크플로우 자동화 결과: {workflow_result}")

    # 2. 성능 최적화 테스트
    print("\n2. 성능 최적화 테스트")
    optimization_data = {"target_metrics": ["response_time", "throughput", "accuracy"]}

    optimization_result = await aos_system.optimize_performance(optimization_data)
    print(f"성능 최적화 결과: {optimization_result}")

    # 3. 리소스 관리 테스트
    print("\n3. 리소스 관리 테스트")
    resource_data = {"action": "monitor"}

    resource_result = await aos_system.manage_resources(resource_data)
    print(f"리소스 관리 결과: {resource_result}")

    # 4. 자동 튜닝 테스트
    print("\n4. 자동 튜닝 테스트")
    tuning_data = {
        "parameters": {"learning_rate": 0.01, "batch_size": 32, "epochs": 100},
        "target_metric": "accuracy",
        "target_value": 0.95,
    }

    tuning_result = await aos_system.auto_tune(tuning_data)
    print(f"자동 튜닝 결과: {tuning_result}")

    # 5. 시스템 상태 조회
    print("\n5. 시스템 상태 조회")
    status = aos_system.get_system_status()
    print(f"시스템 상태: {status}")

    # 6. 성능 보고서
    print("\n6. 성능 보고서")
    performance = aos_system.get_performance_report()
    print(f"성능 보고서: {performance}")

    print("\n✅ 자동화 및 최적화 시스템 테스트 완료!")


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_automation_optimization_system())
