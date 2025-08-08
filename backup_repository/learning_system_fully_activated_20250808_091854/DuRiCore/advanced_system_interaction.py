#!/usr/bin/env python3
"""
DuRi 시스템 간 고급 상호작용 시스템 - Phase 1-3 Week 3 Day 8
시스템 간 복잡한 상호작용 및 협력을 관리하는 시스템

기능:
1. 시스템 간 데이터 공유 및 동기화
2. 복잡한 워크플로우 관리
3. 시스템 간 의존성 해결
4. 실시간 협력 메커니즘
"""

import asyncio
import json
import time
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import statistics
import numpy as np
from collections import defaultdict, deque
import threading
import queue
import weakref

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """상호작용 유형"""
    DATA_SHARE = "data_share"
    WORKFLOW = "workflow"
    DEPENDENCY = "dependency"
    COLLABORATION = "collaboration"
    SYNCHRONIZATION = "synchronization"
    COORDINATION = "coordination"

class InteractionStatus(Enum):
    """상호작용 상태"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStatus(Enum):
    """워크플로우 상태"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SystemInteraction:
    """시스템 상호작용"""
    interaction_id: str
    interaction_type: InteractionType
    source_system: str
    target_system: str
    data: Dict[str, Any]
    status: InteractionStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    timeout: float = 30.0

@dataclass
class WorkflowStep:
    """워크플로우 단계"""
    step_id: str
    step_name: str
    system_name: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class Workflow:
    """워크플로우"""
    workflow_id: str
    workflow_name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.INITIALIZED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemDependency:
    """시스템 의존성"""
    dependency_id: str
    dependent_system: str
    required_system: str
    dependency_type: str
    is_required: bool = True
    created_at: datetime = field(default_factory=datetime.now)

class AdvancedSystemInteraction:
    """고급 시스템 상호작용 시스템"""
    
    def __init__(self):
        """초기화"""
        self.interactions: Dict[str, SystemInteraction] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.dependencies: Dict[str, SystemDependency] = {}
        self.system_registry: Dict[str, Any] = {}
        self.interaction_queue = asyncio.Queue()
        self.workflow_queue = asyncio.Queue()
        self.active_interactions: Set[str] = set()
        self.active_workflows: Set[str] = set()
        
        # 상호작용 설정
        self.interaction_config = {
            "max_concurrent_interactions": 10,
            "interaction_timeout": 30.0,
            "retry_attempts": 3,
            "sync_interval": 1.0
        }
        
        # 워크플로우 설정
        self.workflow_config = {
            "max_concurrent_workflows": 5,
            "workflow_timeout": 300.0,
            "step_timeout": 60.0,
            "retry_attempts": 3
        }
        
        # 모니터링 데이터
        self.interaction_metrics = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "average_interaction_time": 0.0
        }
        
        self.workflow_metrics = {
            "total_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "average_workflow_time": 0.0
        }
        
        logger.info("고급 시스템 상호작용 시스템 초기화 완료")
    
    async def register_system(self, system_name: str, system_instance: Any) -> bool:
        """시스템 등록"""
        try:
            self.system_registry[system_name] = system_instance
            logger.info(f"시스템 등록 완료: {system_name}")
            return True
        except Exception as e:
            logger.error(f"시스템 등록 실패: {system_name} - {e}")
            return False
    
    async def create_interaction(self, interaction_type: InteractionType, 
                               source_system: str, target_system: str, 
                               data: Dict[str, Any], priority: int = 0) -> str:
        """상호작용 생성"""
        interaction_id = f"interaction_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        interaction = SystemInteraction(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            source_system=source_system,
            target_system=target_system,
            data=data,
            status=InteractionStatus.PENDING,
            priority=priority
        )
        
        self.interactions[interaction_id] = interaction
        await self.interaction_queue.put(interaction)
        
        logger.info(f"상호작용 생성: {interaction_id} ({interaction_type.value})")
        return interaction_id
    
    async def execute_interaction(self, interaction_id: str) -> Dict[str, Any]:
        """상호작용 실행"""
        if interaction_id not in self.interactions:
            raise ValueError(f"상호작용을 찾을 수 없음: {interaction_id}")
        
        interaction = self.interactions[interaction_id]
        start_time = time.time()
        
        try:
            # 상호작용 상태 업데이트
            interaction.status = InteractionStatus.ACTIVE
            interaction.updated_at = datetime.now()
            self.active_interactions.add(interaction_id)
            
            logger.info(f"상호작용 실행 시작: {interaction_id}")
            
            # 상호작용 유형에 따른 실행
            if interaction.interaction_type == InteractionType.DATA_SHARE:
                result = await self._execute_data_share(interaction)
            elif interaction.interaction_type == InteractionType.WORKFLOW:
                result = await self._execute_workflow_interaction(interaction)
            elif interaction.interaction_type == InteractionType.DEPENDENCY:
                result = await self._execute_dependency_resolution(interaction)
            elif interaction.interaction_type == InteractionType.COLLABORATION:
                result = await self._execute_collaboration(interaction)
            elif interaction.interaction_type == InteractionType.SYNCHRONIZATION:
                result = await self._execute_synchronization(interaction)
            elif interaction.interaction_type == InteractionType.COORDINATION:
                result = await self._execute_coordination(interaction)
            else:
                raise ValueError(f"지원하지 않는 상호작용 유형: {interaction.interaction_type}")
            
            # 상호작용 완료
            interaction.status = InteractionStatus.COMPLETED
            interaction.updated_at = datetime.now()
            self.active_interactions.discard(interaction_id)
            
            # 메트릭 업데이트
            execution_time = time.time() - start_time
            self._update_interaction_metrics(True, execution_time)
            
            logger.info(f"상호작용 실행 완료: {interaction_id} ({execution_time:.2f}초)")
            return result
            
        except Exception as e:
            # 상호작용 실패
            interaction.status = InteractionStatus.FAILED
            interaction.updated_at = datetime.now()
            self.active_interactions.discard(interaction_id)
            
            # 메트릭 업데이트
            execution_time = time.time() - start_time
            self._update_interaction_metrics(False, execution_time)
            
            logger.error(f"상호작용 실행 실패: {interaction_id} - {e}")
            raise
    
    async def create_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> str:
        """워크플로우 생성"""
        workflow_id = f"workflow_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                step_id=f"step_{len(workflow_steps)}_{uuid.uuid4().hex[:4]}",
                step_name=step_data.get("name", f"Step {len(workflow_steps)}"),
                system_name=step_data.get("system"),
                action=step_data.get("action"),
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", [])
            )
            workflow_steps.append(step)
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            steps=workflow_steps
        )
        
        self.workflows[workflow_id] = workflow
        await self.workflow_queue.put(workflow)
        
        logger.info(f"워크플로우 생성: {workflow_id} ({workflow_name})")
        return workflow_id
    
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """워크플로우 실행"""
        if workflow_id not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없음: {workflow_id}")
        
        workflow = self.workflows[workflow_id]
        start_time = time.time()
        
        try:
            # 워크플로우 상태 업데이트
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            self.active_workflows.add(workflow_id)
            
            logger.info(f"워크플로우 실행 시작: {workflow_id}")
            
            # 워크플로우 단계 실행
            results = {}
            for step in workflow.steps:
                # 의존성 확인
                if not await self._check_step_dependencies(step, results):
                    raise Exception(f"단계 의존성 실패: {step.step_id}")
                
                # 단계 실행
                step_result = await self._execute_workflow_step(step)
                results[step.step_id] = step_result
                
                # 단계 완료
                step.status = "completed"
                step.result = step_result
                step.completed_at = datetime.now()
            
            # 워크플로우 완료
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            self.active_workflows.discard(workflow_id)
            
            # 메트릭 업데이트
            execution_time = time.time() - start_time
            self._update_workflow_metrics(True, execution_time)
            
            logger.info(f"워크플로우 실행 완료: {workflow_id} ({execution_time:.2f}초)")
            return {"workflow_id": workflow_id, "status": "completed", "results": results}
            
        except Exception as e:
            # 워크플로우 실패
            workflow.status = WorkflowStatus.FAILED
            self.active_workflows.discard(workflow_id)
            
            # 메트릭 업데이트
            execution_time = time.time() - start_time
            self._update_workflow_metrics(False, execution_time)
            
            logger.error(f"워크플로우 실행 실패: {workflow_id} - {e}")
            raise
    
    async def add_dependency(self, dependent_system: str, required_system: str, 
                           dependency_type: str = "functional") -> str:
        """의존성 추가"""
        dependency_id = f"dependency_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        dependency = SystemDependency(
            dependency_id=dependency_id,
            dependent_system=dependent_system,
            required_system=required_system,
            dependency_type=dependency_type
        )
        
        self.dependencies[dependency_id] = dependency
        logger.info(f"의존성 추가: {dependent_system} -> {required_system}")
        return dependency_id
    
    async def resolve_dependencies(self, system_name: str) -> List[str]:
        """의존성 해결"""
        resolved_systems = []
        pending_systems = [system_name]
        visited = set()
        
        while pending_systems:
            current_system = pending_systems.pop(0)
            
            if current_system in visited:
                continue
            
            visited.add(current_system)
            
            # 현재 시스템의 의존성 찾기
            for dependency in self.dependencies.values():
                if dependency.dependent_system == current_system:
                    required_system = dependency.required_system
                    if required_system not in visited and required_system not in resolved_systems:
                        pending_systems.append(required_system)
            
            resolved_systems.append(current_system)
        
        return resolved_systems
    
    async def _execute_data_share(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """데이터 공유 실행"""
        source_system = interaction.source_system
        target_system = interaction.target_system
        data = interaction.data
        
        # 소스 시스템에서 데이터 가져오기
        source_data = await self._get_system_data(source_system, data.get("data_key"))
        
        # 타겟 시스템에 데이터 전송
        result = await self._send_data_to_system(target_system, source_data)
        
        return {
            "interaction_type": "data_share",
            "source_system": source_system,
            "target_system": target_system,
            "data_size": len(str(source_data)),
            "result": result
        }
    
    async def _execute_workflow_interaction(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """워크플로우 상호작용 실행"""
        workflow_id = interaction.data.get("workflow_id")
        if not workflow_id or workflow_id not in self.workflows:
            raise ValueError(f"워크플로우를 찾을 수 없음: {workflow_id}")
        
        workflow_result = await self.execute_workflow(workflow_id)
        
        return {
            "interaction_type": "workflow",
            "workflow_id": workflow_id,
            "result": workflow_result
        }
    
    async def _execute_dependency_resolution(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """의존성 해결 실행"""
        system_name = interaction.data.get("system_name")
        if not system_name:
            raise ValueError("시스템 이름이 필요합니다")
        
        resolved_systems = await self.resolve_dependencies(system_name)
        
        return {
            "interaction_type": "dependency_resolution",
            "system_name": system_name,
            "resolved_systems": resolved_systems
        }
    
    async def _execute_collaboration(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """협력 실행"""
        systems = interaction.data.get("systems", [])
        collaboration_type = interaction.data.get("collaboration_type", "parallel")
        
        if collaboration_type == "parallel":
            # 병렬 협력
            tasks = []
            for system_name in systems:
                task = self._execute_system_action(system_name, interaction.data.get("action"))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # 순차 협력
            results = []
            for system_name in systems:
                result = await self._execute_system_action(system_name, interaction.data.get("action"))
                results.append(result)
        
        return {
            "interaction_type": "collaboration",
            "systems": systems,
            "collaboration_type": collaboration_type,
            "results": results
        }
    
    async def _execute_synchronization(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """동기화 실행"""
        systems = interaction.data.get("systems", [])
        sync_data = interaction.data.get("sync_data", {})
        
        # 모든 시스템에 동기화 데이터 전송
        sync_results = []
        for system_name in systems:
            result = await self._send_data_to_system(system_name, sync_data)
            sync_results.append({"system": system_name, "result": result})
        
        return {
            "interaction_type": "synchronization",
            "systems": systems,
            "sync_results": sync_results
        }
    
    async def _execute_coordination(self, interaction: SystemInteraction) -> Dict[str, Any]:
        """조율 실행"""
        coordinator_system = interaction.source_system
        target_systems = interaction.data.get("target_systems", [])
        coordination_action = interaction.data.get("coordination_action")
        
        # 조율자 시스템이 다른 시스템들을 조율
        coordination_results = []
        for target_system in target_systems:
            result = await self._coordinate_systems(coordinator_system, target_system, coordination_action)
            coordination_results.append({"target_system": target_system, "result": result})
        
        return {
            "interaction_type": "coordination",
            "coordinator_system": coordinator_system,
            "target_systems": target_systems,
            "coordination_results": coordination_results
        }
    
    async def _execute_workflow_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """워크플로우 단계 실행"""
        system_name = step.system_name
        action = step.action
        parameters = step.parameters
        
        if system_name not in self.system_registry:
            raise ValueError(f"시스템을 찾을 수 없음: {system_name}")
        
        system_instance = self.system_registry[system_name]
        
        # 시스템 액션 실행
        if hasattr(system_instance, action):
            method = getattr(system_instance, action)
            if asyncio.iscoroutinefunction(method):
                result = await method(**parameters)
            else:
                result = method(**parameters)
        else:
            raise ValueError(f"액션을 찾을 수 없음: {system_name}.{action}")
        
        return {"step_id": step.step_id, "result": result}
    
    async def _check_step_dependencies(self, step: WorkflowStep, completed_results: Dict[str, Any]) -> bool:
        """단계 의존성 확인"""
        for dependency in step.dependencies:
            if dependency not in completed_results:
                return False
        return True
    
    async def _get_system_data(self, system_name: str, data_key: str) -> Any:
        """시스템에서 데이터 가져오기"""
        if system_name not in self.system_registry:
            raise ValueError(f"시스템을 찾을 수 없음: {system_name}")
        
        system_instance = self.system_registry[system_name]
        
        if hasattr(system_instance, "get_data"):
            if asyncio.iscoroutinefunction(system_instance.get_data):
                return await system_instance.get_data(data_key)
            else:
                return system_instance.get_data(data_key)
        else:
            # 기본 데이터 반환
            return {"system": system_name, "data_key": data_key, "timestamp": datetime.now()}
    
    async def _send_data_to_system(self, system_name: str, data: Any) -> Dict[str, Any]:
        """시스템에 데이터 전송"""
        if system_name not in self.system_registry:
            raise ValueError(f"시스템을 찾을 수 없음: {system_name}")
        
        system_instance = self.system_registry[system_name]
        
        if hasattr(system_instance, "receive_data"):
            if asyncio.iscoroutinefunction(system_instance.receive_data):
                return await system_instance.receive_data(data)
            else:
                return system_instance.receive_data(data)
        else:
            # 기본 수신 처리
            return {"system": system_name, "received": True, "timestamp": datetime.now()}
    
    async def _execute_system_action(self, system_name: str, action: str) -> Dict[str, Any]:
        """시스템 액션 실행"""
        if system_name not in self.system_registry:
            raise ValueError(f"시스템을 찾을 수 없음: {system_name}")
        
        system_instance = self.system_registry[system_name]
        
        if hasattr(system_instance, action):
            method = getattr(system_instance, action)
            if asyncio.iscoroutinefunction(method):
                return await method()
            else:
                return method()
        else:
            return {"system": system_name, "action": action, "status": "not_found"}
    
    async def _coordinate_systems(self, coordinator: str, target: str, action: str) -> Dict[str, Any]:
        """시스템 조율"""
        # 조율자 시스템이 타겟 시스템을 조율
        coordination_data = {
            "coordinator": coordinator,
            "target": target,
            "action": action,
            "timestamp": datetime.now()
        }
        
        return await self._send_data_to_system(target, coordination_data)
    
    def _update_interaction_metrics(self, success: bool, execution_time: float):
        """상호작용 메트릭 업데이트"""
        self.interaction_metrics["total_interactions"] += 1
        
        if success:
            self.interaction_metrics["successful_interactions"] += 1
        else:
            self.interaction_metrics["failed_interactions"] += 1
        
        # 평균 실행 시간 업데이트
        total = self.interaction_metrics["total_interactions"]
        current_avg = self.interaction_metrics["average_interaction_time"]
        self.interaction_metrics["average_interaction_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def _update_workflow_metrics(self, success: bool, execution_time: float):
        """워크플로우 메트릭 업데이트"""
        self.workflow_metrics["total_workflows"] += 1
        
        if success:
            self.workflow_metrics["completed_workflows"] += 1
        else:
            self.workflow_metrics["failed_workflows"] += 1
        
        # 평균 실행 시간 업데이트
        total = self.workflow_metrics["total_workflows"]
        current_avg = self.workflow_metrics["average_workflow_time"]
        self.workflow_metrics["average_workflow_time"] = (
            (current_avg * (total - 1) + execution_time) / total
        )
    
    def get_interaction_metrics(self) -> Dict[str, Any]:
        """상호작용 메트릭 반환"""
        return self.interaction_metrics.copy()
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """워크플로우 메트릭 반환"""
        return self.workflow_metrics.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "registered_systems": list(self.system_registry.keys()),
            "active_interactions": len(self.active_interactions),
            "active_workflows": len(self.active_workflows),
            "total_interactions": len(self.interactions),
            "total_workflows": len(self.workflows),
            "total_dependencies": len(self.dependencies)
        }

async def test_advanced_system_interaction():
    """고급 시스템 상호작용 테스트"""
    print("=== 고급 시스템 상호작용 테스트 시작 ===")
    
    # 고급 시스템 상호작용 초기화
    interaction_system = AdvancedSystemInteraction()
    
    # 가상 시스템 등록
    class MockSystem:
        def __init__(self, name: str):
            self.name = name
            self.data = {}
        
        async def get_data(self, key: str):
            return {"system": self.name, "key": key, "value": f"data_{key}"}
        
        async def receive_data(self, data):
            self.data[datetime.now().isoformat()] = data
            return {"system": self.name, "received": True}
        
        async def process_data(self):
            return {"system": self.name, "processed": len(self.data)}
    
    # 시스템 등록
    systems = ["lida_attention", "realtime_learning", "dynamic_reasoning", "semantic_connection"]
    for system_name in systems:
        mock_system = MockSystem(system_name)
        await interaction_system.register_system(system_name, mock_system)
    
    print(f"등록된 시스템 수: {len(interaction_system.system_registry)}")
    
    # 1. 데이터 공유 상호작용 테스트
    print("\n1. 데이터 공유 상호작용 테스트")
    data_share_id = await interaction_system.create_interaction(
        InteractionType.DATA_SHARE,
        "lida_attention",
        "realtime_learning",
        {"data_key": "attention_data"}
    )
    
    data_share_result = await interaction_system.execute_interaction(data_share_id)
    print(f"데이터 공유 결과: {data_share_result}")
    
    # 2. 워크플로우 테스트
    print("\n2. 워크플로우 테스트")
    workflow_steps = [
        {"name": "데이터 수집", "system": "lida_attention", "action": "get_data", "parameters": {"key": "test"}},
        {"name": "데이터 처리", "system": "realtime_learning", "action": "process_data", "parameters": {}},
        {"name": "결과 분석", "system": "dynamic_reasoning", "action": "process_data", "parameters": {}}
    ]
    
    workflow_id = await interaction_system.create_workflow("테스트 워크플로우", workflow_steps)
    workflow_result = await interaction_system.execute_workflow(workflow_id)
    print(f"워크플로우 결과: {workflow_result['status']}")
    
    # 3. 의존성 해결 테스트
    print("\n3. 의존성 해결 테스트")
    await interaction_system.add_dependency("realtime_learning", "lida_attention")
    await interaction_system.add_dependency("dynamic_reasoning", "realtime_learning")
    
    resolved_systems = await interaction_system.resolve_dependencies("dynamic_reasoning")
    print(f"의존성 해결 결과: {resolved_systems}")
    
    # 4. 협력 상호작용 테스트
    print("\n4. 협력 상호작용 테스트")
    collaboration_id = await interaction_system.create_interaction(
        InteractionType.COLLABORATION,
        "lida_attention",
        "realtime_learning",
        {
            "systems": ["lida_attention", "realtime_learning", "dynamic_reasoning"],
            "action": "process_data",
            "collaboration_type": "parallel"
        }
    )
    
    collaboration_result = await interaction_system.execute_interaction(collaboration_id)
    print(f"협력 상호작용 결과: {collaboration_result}")
    
    # 5. 메트릭 확인
    print("\n5. 메트릭 확인")
    interaction_metrics = interaction_system.get_interaction_metrics()
    workflow_metrics = interaction_system.get_workflow_metrics()
    system_status = interaction_system.get_system_status()
    
    print(f"상호작용 메트릭: {interaction_metrics}")
    print(f"워크플로우 메트릭: {workflow_metrics}")
    print(f"시스템 상태: {system_status}")
    
    print("\n=== 고급 시스템 상호작용 테스트 완료 ===")
    
    return {
        "interaction_metrics": interaction_metrics,
        "workflow_metrics": workflow_metrics,
        "system_status": system_status
    }

if __name__ == "__main__":
    asyncio.run(test_advanced_system_interaction()) 