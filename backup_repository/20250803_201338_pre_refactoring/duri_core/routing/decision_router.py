"""
DuRi 모듈 간 교통 정리 계층 (DecisionRouter)

DuRi의 모듈 간 의사결정 흐름을 조정하고 실행 순서를 최적화하는 시스템입니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import asyncio
import threading

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """의사결정 유형"""
    SEQUENTIAL = "sequential"         # 순차적
    PARALLEL = "parallel"             # 병렬
    CONDITIONAL = "conditional"       # 조건부
    PRIORITY = "priority"             # 우선순위
    FALLBACK = "fallback"            # 대체

class ExecutionStatus(Enum):
    """실행 상태"""
    PENDING = "pending"               # 대기 중
    RUNNING = "running"               # 실행 중
    COMPLETED = "completed"           # 완료
    FAILED = "failed"                # 실패
    CANCELLED = "cancelled"          # 취소됨

class ModulePriority(Enum):
    """모듈 우선순위"""
    CRITICAL = "critical"             # 치명적
    HIGH = "high"                    # 높음
    MEDIUM = "medium"                # 보통
    LOW = "low"                      # 낮음
    BACKGROUND = "background"        # 백그라운드

@dataclass
class DecisionNode:
    """의사결정 노드"""
    node_id: str
    module_id: str
    decision_type: DecisionType
    priority: ModulePriority
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_count: int = 0
    max_retries: int = 3
    is_active: bool = True

@dataclass
class ExecutionTask:
    """실행 태스크"""
    task_id: str
    node_id: str
    module_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: timedelta = field(default_factory=lambda: timedelta(0))
    retry_count: int = 0

@dataclass
class DecisionFlow:
    """의사결정 흐름"""
    flow_id: str
    name: str
    nodes: List[DecisionNode] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration: timedelta = field(default_factory=lambda: timedelta(0))

@dataclass
class RoutingReport:
    """라우팅 보고서"""
    report_id: str
    timestamp: datetime
    active_flows: List[DecisionFlow] = field(default_factory=list)
    completed_tasks: List[ExecutionTask] = field(default_factory=list)
    failed_tasks: List[ExecutionTask] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    bottlenecks: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class DecisionRouter:
    """DuRi 모듈 간 교통 정리 계층"""
    
    def __init__(self):
        """DecisionRouter 초기화"""
        # 의사결정 흐름 관리
        self.decision_flows: Dict[str, DecisionFlow] = {}
        self.execution_tasks: Dict[str, ExecutionTask] = {}
        self.module_registry: Dict[str, Callable] = {}
        
        # 실행 큐 및 스케줄러
        self.execution_queue = deque()
        self.priority_queue = defaultdict(deque)
        self.running_tasks: Dict[str, ExecutionTask] = {}
        
        # 라우팅 설정
        self.routing_config = {
            'max_concurrent_tasks': 5,
            'default_timeout_seconds': 30,
            'enable_priority_routing': True,
            'enable_parallel_execution': True,
            'enable_fallback_routing': True,
            'max_retry_attempts': 3
        }
        
        # 성능 메트릭
        self.performance_metrics = {
            'total_tasks_executed': 0,
            'successful_tasks': 0,
            'failed_tasks': 0,
            'average_execution_time': 0.0,
            'peak_concurrent_tasks': 0
        }
        
        # 실행 스레드
        self.execution_thread = None
        self.is_running = False
        
        logger.info("DecisionRouter 초기화 완료")
    
    def register_module(self, module_id: str, module_function: Callable, 
                       priority: ModulePriority = ModulePriority.MEDIUM) -> bool:
        """모듈을 등록합니다."""
        try:
            self.module_registry[module_id] = module_function
            
            logger.info(f"모듈 등록 완료: {module_id} (우선순위: {priority.value})")
            return True
            
        except Exception as e:
            logger.error(f"모듈 등록 실패: {e}")
            return False
    
    def create_decision_flow(self, flow_name: str, nodes: List[DecisionNode]) -> str:
        """의사결정 흐름을 생성합니다."""
        try:
            flow_id = f"flow_{uuid.uuid4().hex[:8]}"
            
            # 의존성 분석
            dependencies = self._analyze_dependencies(nodes)
            
            # 실행 순서 결정
            execution_order = self._determine_execution_order(nodes, dependencies)
            
            decision_flow = DecisionFlow(
                flow_id=flow_id,
                name=flow_name,
                nodes=nodes,
                execution_order=execution_order,
                dependencies=dependencies
            )
            
            self.decision_flows[flow_id] = decision_flow
            
            logger.info(f"의사결정 흐름 생성: {flow_name} ({len(nodes)}개 노드)")
            return flow_id
            
        except Exception as e:
            logger.error(f"의사결정 흐름 생성 실패: {e}")
            return None
    
    def execute_decision_flow(self, flow_id: str, input_data: Dict[str, Any] = None) -> bool:
        """의사결정 흐름을 실행합니다."""
        try:
            if flow_id not in self.decision_flows:
                logger.error(f"의사결정 흐름을 찾을 수 없음: {flow_id}")
                return False
            
            decision_flow = self.decision_flows[flow_id]
            decision_flow.status = ExecutionStatus.RUNNING
            decision_flow.start_time = datetime.now()
            
            # 실행 큐에 태스크 추가
            for node_id in decision_flow.execution_order:
                node = next((n for n in decision_flow.nodes if n.node_id == node_id), None)
                if node and node.is_active:
                    task = self._create_execution_task(node, input_data)
                    self.execution_queue.append(task)
            
            # 실행 스레드 시작
            if not self.is_running:
                self._start_execution_thread()
            
            logger.info(f"의사결정 흐름 실행 시작: {decision_flow.name}")
            return True
            
        except Exception as e:
            logger.error(f"의사결정 흐름 실행 실패: {e}")
            return False
    
    def _analyze_dependencies(self, nodes: List[DecisionNode]) -> Dict[str, List[str]]:
        """의존성을 분석합니다."""
        try:
            dependencies = {}
            
            for node in nodes:
                dependencies[node.node_id] = node.dependencies
            
            return dependencies
            
        except Exception as e:
            logger.error(f"의존성 분석 실패: {e}")
            return {}
    
    def _determine_execution_order(self, nodes: List[DecisionNode], 
                                 dependencies: Dict[str, List[str]]) -> List[str]:
        """실행 순서를 결정합니다."""
        try:
            # 위상 정렬을 사용한 실행 순서 결정
            execution_order = []
            visited = set()
            temp_visited = set()
            
            def dfs(node_id: str):
                if node_id in temp_visited:
                    raise Exception("순환 의존성 감지")
                
                if node_id in visited:
                    return
                
                temp_visited.add(node_id)
                
                for dep in dependencies.get(node_id, []):
                    dfs(dep)
                
                temp_visited.remove(node_id)
                visited.add(node_id)
                execution_order.append(node_id)
            
            # 모든 노드에 대해 DFS 실행
            for node in nodes:
                if node.node_id not in visited:
                    dfs(node.node_id)
            
            return execution_order
            
        except Exception as e:
            logger.error(f"실행 순서 결정 실패: {e}")
            # 기본 순서 (우선순위 기반)
            return [node.node_id for node in sorted(nodes, key=lambda x: x.priority.value, reverse=True)]
    
    def _create_execution_task(self, node: DecisionNode, input_data: Dict[str, Any]) -> ExecutionTask:
        """실행 태스크를 생성합니다."""
        try:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            
            task = ExecutionTask(
                task_id=task_id,
                node_id=node.node_id,
                module_id=node.module_id,
                start_time=datetime.now(),
                status=ExecutionStatus.PENDING
            )
            
            self.execution_tasks[task_id] = task
            return task
            
        except Exception as e:
            logger.error(f"실행 태스크 생성 실패: {e}")
            return None
    
    def _start_execution_thread(self):
        """실행 스레드를 시작합니다."""
        try:
            self.is_running = True
            self.execution_thread = threading.Thread(target=self._execution_worker, daemon=True)
            self.execution_thread.start()
            
            logger.info("실행 스레드 시작")
            
        except Exception as e:
            logger.error(f"실행 스레드 시작 실패: {e}")
    
    def _execution_worker(self):
        """실행 워커 스레드"""
        try:
            while self.is_running:
                if self.execution_queue:
                    # 우선순위 기반 태스크 선택
                    task = self._get_next_task()
                    
                    if task:
                        self._execute_task(task)
                
                time.sleep(0.1)  # 짧은 대기
                
        except Exception as e:
            logger.error(f"실행 워커 오류: {e}")
    
    def _get_next_task(self) -> Optional[ExecutionTask]:
        """다음 실행할 태스크를 가져옵니다."""
        try:
            if not self.execution_queue:
                return None
            
            # 우선순위 기반 선택
            if self.routing_config['enable_priority_routing']:
                for priority in [ModulePriority.CRITICAL, ModulePriority.HIGH, 
                               ModulePriority.MEDIUM, ModulePriority.LOW, ModulePriority.BACKGROUND]:
                    if self.priority_queue[priority]:
                        return self.priority_queue[priority].popleft()
            
            # 기본 큐에서 선택
            if self.execution_queue:
                return self.execution_queue.popleft()
            
            return None
            
        except Exception as e:
            logger.error(f"다음 태스크 선택 실패: {e}")
            return None
    
    def _execute_task(self, task: ExecutionTask):
        """태스크를 실행합니다."""
        try:
            task.status = ExecutionStatus.RUNNING
            task.start_time = datetime.now()
            
            # 모듈 함수 실행
            if task.module_id in self.module_registry:
                module_function = self.module_registry[task.module_id]
                
                # 실행 (시뮬레이션)
                result = self._simulate_module_execution(task.module_id)
                
                if result['success']:
                    task.status = ExecutionStatus.COMPLETED
                    task.result = result['data']
                    self.performance_metrics['successful_tasks'] += 1
                else:
                    task.status = ExecutionStatus.FAILED
                    task.error_message = result['error']
                    self.performance_metrics['failed_tasks'] += 1
            else:
                task.status = ExecutionStatus.FAILED
                task.error_message = f"모듈을 찾을 수 없음: {task.module_id}"
                self.performance_metrics['failed_tasks'] += 1
            
            task.end_time = datetime.now()
            task.execution_time = task.end_time - task.start_time
            
            # 성능 메트릭 업데이트
            self._update_performance_metrics(task)
            
            logger.info(f"태스크 실행 완료: {task.module_id} ({task.status.value})")
            
        except Exception as e:
            logger.error(f"태스크 실행 실패: {e}")
            task.status = ExecutionStatus.FAILED
            task.error_message = str(e)
    
    def _simulate_module_execution(self, module_id: str) -> Dict[str, Any]:
        """모듈 실행을 시뮬레이션합니다."""
        try:
            # 시뮬레이션된 실행 시간
            execution_time = 0.1 + (hash(module_id) % 10) * 0.01
            time.sleep(execution_time)
            
            # 성공 확률 (90%)
            import random
            success = random.random() < 0.9
            
            if success:
                return {
                    'success': True,
                    'data': {
                        'module_id': module_id,
                        'execution_time': execution_time,
                        'result': f"{module_id} 실행 완료"
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f"{module_id} 실행 실패"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_performance_metrics(self, task: ExecutionTask):
        """성능 메트릭을 업데이트합니다."""
        try:
            self.performance_metrics['total_tasks_executed'] += 1
            
            # 평균 실행 시간 업데이트
            execution_time = task.execution_time.total_seconds()
            total_tasks = self.performance_metrics['total_tasks_executed']
            
            self.performance_metrics['average_execution_time'] = (
                (self.performance_metrics['average_execution_time'] * (total_tasks - 1) + execution_time) /
                total_tasks
            )
            
            # 최대 동시 실행 태스크 수 업데이트
            current_running = len(self.running_tasks)
            if current_running > self.performance_metrics['peak_concurrent_tasks']:
                self.performance_metrics['peak_concurrent_tasks'] = current_running
                
        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")
    
    def get_execution_status(self, flow_id: str) -> Optional[Dict[str, Any]]:
        """실행 상태를 반환합니다."""
        try:
            if flow_id not in self.decision_flows:
                return None
            
            decision_flow = self.decision_flows[flow_id]
            
            # 태스크 상태 집계
            flow_tasks = [task for task in self.execution_tasks.values() 
                         if task.node_id in [node.node_id for node in decision_flow.nodes]]
            
            completed_tasks = sum(1 for task in flow_tasks if task.status == ExecutionStatus.COMPLETED)
            failed_tasks = sum(1 for task in flow_tasks if task.status == ExecutionStatus.FAILED)
            running_tasks = sum(1 for task in flow_tasks if task.status == ExecutionStatus.RUNNING)
            
            return {
                'flow_id': flow_id,
                'flow_name': decision_flow.name,
                'status': decision_flow.status.value,
                'total_tasks': len(flow_tasks),
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'running_tasks': running_tasks,
                'progress_percentage': (completed_tasks / len(flow_tasks) * 100) if flow_tasks else 0
            }
            
        except Exception as e:
            logger.error(f"실행 상태 조회 실패: {e}")
            return None
    
    def generate_routing_report(self) -> RoutingReport:
        """라우팅 보고서를 생성합니다."""
        try:
            report_id = f"routing_report_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now()
            
            # 활성 흐름
            active_flows = [flow for flow in self.decision_flows.values() 
                          if flow.status == ExecutionStatus.RUNNING]
            
            # 완료된 태스크
            completed_tasks = [task for task in self.execution_tasks.values() 
                             if task.status == ExecutionStatus.COMPLETED]
            
            # 실패한 태스크
            failed_tasks = [task for task in self.execution_tasks.values() 
                          if task.status == ExecutionStatus.FAILED]
            
            # 병목 지점 식별
            bottlenecks = self._identify_bottlenecks()
            
            # 권장사항 생성
            recommendations = self._generate_recommendations()
            
            report = RoutingReport(
                report_id=report_id,
                timestamp=timestamp,
                active_flows=active_flows,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                performance_metrics=self.performance_metrics.copy(),
                bottlenecks=bottlenecks,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            logger.error(f"라우팅 보고서 생성 실패: {e}")
            return None
    
    def _identify_bottlenecks(self) -> List[str]:
        """병목 지점을 식별합니다."""
        try:
            bottlenecks = []
            
            # 실행 시간이 긴 태스크
            long_running_tasks = [task for task in self.execution_tasks.values() 
                                if task.execution_time.total_seconds() > 5.0]
            
            if long_running_tasks:
                bottlenecks.append(f"{len(long_running_tasks)}개 태스크가 장시간 실행 중")
            
            # 실패율이 높은 모듈
            module_failure_counts = defaultdict(int)
            for task in self.execution_tasks.values():
                if task.status == ExecutionStatus.FAILED:
                    module_failure_counts[task.module_id] += 1
            
            high_failure_modules = [module for module, count in module_failure_counts.items() 
                                  if count >= 3]
            
            if high_failure_modules:
                bottlenecks.append(f"실패율 높은 모듈: {', '.join(high_failure_modules)}")
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"병목 지점 식별 실패: {e}")
            return []
    
    def _generate_recommendations(self) -> List[str]:
        """권장사항을 생성합니다."""
        try:
            recommendations = []
            
            # 성공률 기반 권장사항
            total_tasks = self.performance_metrics['total_tasks_executed']
            success_rate = self.performance_metrics['successful_tasks'] / total_tasks if total_tasks > 0 else 0.0
            
            if success_rate < 0.8:
                recommendations.append("모듈 안정성 개선 필요")
            else:
                recommendations.append("시스템 성능 양호")
            
            # 실행 시간 기반 권장사항
            avg_execution_time = self.performance_metrics['average_execution_time']
            if avg_execution_time > 2.0:
                recommendations.append("실행 시간 최적화 필요")
            
            # 동시 실행 기반 권장사항
            peak_concurrent = self.performance_metrics['peak_concurrent_tasks']
            max_concurrent = self.routing_config['max_concurrent_tasks']
            
            if peak_concurrent >= max_concurrent * 0.8:
                recommendations.append("동시 실행 용량 확장 고려")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return []
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """라우팅 통계를 반환합니다."""
        try:
            total_flows = len(self.decision_flows)
            active_flows = sum(1 for flow in self.decision_flows.values() 
                             if flow.status == ExecutionStatus.RUNNING)
            
            return {
                'total_flows': total_flows,
                'active_flows': active_flows,
                'registered_modules': len(self.module_registry),
                'queued_tasks': len(self.execution_queue),
                'running_tasks': len(self.running_tasks),
                **self.performance_metrics
            }
            
        except Exception as e:
            logger.error(f"라우팅 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_decision_router = None

def get_decision_router() -> DecisionRouter:
    """DecisionRouter 싱글톤 인스턴스 반환"""
    global _decision_router
    if _decision_router is None:
        _decision_router = DecisionRouter()
    return _decision_router 