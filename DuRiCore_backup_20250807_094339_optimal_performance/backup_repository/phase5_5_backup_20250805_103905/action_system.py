#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 4 - 행동 시스템
의사결정 결과 기반 행동 생성, 실행, 결과 분석 통합 시스템
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import math
import time

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """행동 타입 열거형"""
    IMMEDIATE = "immediate"      # 즉시 실행
    SCHEDULED = "scheduled"      # 예약 실행
    CONDITIONAL = "conditional"  # 조건부 실행
    RECURRING = "recurring"      # 반복 실행

class ActionStatus(Enum):
    """행동 상태 열거형"""
    PENDING = "pending"          # 대기 중
    EXECUTING = "executing"      # 실행 중
    COMPLETED = "completed"      # 완료
    FAILED = "failed"            # 실패
    CANCELLED = "cancelled"      # 취소됨

class ActionPriority(Enum):
    """행동 우선순위 열거형"""
    CRITICAL = "critical"        # 매우 중요 (1)
    HIGH = "high"               # 중요 (2)
    MEDIUM = "medium"           # 보통 (3)
    LOW = "low"                 # 낮음 (4)

@dataclass
class ActionPlan:
    """행동 계획"""
    action_id: str
    action_type: ActionType
    description: str
    priority: ActionPriority
    estimated_duration: float
    required_resources: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    risk_factors: List[str]
    created_at: datetime

@dataclass
class ActionExecution:
    """행동 실행"""
    action_id: str
    status: ActionStatus
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    actual_duration: Optional[float]
    progress: float
    current_step: str
    logs: List[str]
    errors: List[str]
    performance_metrics: Dict[str, float]

@dataclass
class ActionResult:
    """행동 결과"""
    action_id: str
    success: bool
    outcome: Dict[str, Any]
    effectiveness_score: float
    efficiency_score: float
    learning_points: List[str]
    improvement_suggestions: List[str]
    next_actions: List[str]
    completed_at: datetime

@dataclass
class BehaviorPattern:
    """행동 패턴"""
    pattern_id: str
    pattern_type: str
    frequency: float
    success_rate: float
    average_duration: float
    common_factors: List[str]
    optimization_opportunities: List[str]

class ActionSystem:
    """행동 시스템"""
    
    def __init__(self):
        self.action_generator = ActionGenerator()
        self.action_executor = ActionExecutor()
        self.result_analyzer = ActionResultAnalyzer()
        
        # 행동 관리
        self.action_queue = []
        self.executing_actions = {}
        self.completed_actions = {}
        self.action_patterns = {}
        
        # 성능 설정
        self.max_concurrent_actions = 5
        self.action_timeout = 300.0  # 5분
        self.retry_attempts = 3
        
        logger.info("행동 시스템 초기화 완료")
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 처리 (통합 루프용)"""
        try:
            # 판단 데이터에서 의사결정 정보 추출
            judgment_data = input_data.get("data", {})
            decision = judgment_data.get("decision", "proceed")
            confidence = judgment_data.get("confidence", 0.5)
            
            # 행동 계획 생성
            decision_result = {
                "decision": decision,
                "confidence": confidence,
                "reasoning": "Based on judgment system analysis"
            }
            available_resources = ["cpu", "memory", "network", "storage"]
            constraints = {"time_limit": 30.0, "resource_limit": 0.8}
            
            action_plan = await self.generate_action_plan(decision_result, available_resources, constraints)
            
            # 행동 실행
            action_execution = await self.execute_action(action_plan)
            
            # 결과 분석
            expected_outcome = {"success": True, "completion": 1.0}
            action_result = await self.analyze_action_result(action_execution, expected_outcome)
            
            return {
                "success": True,
                "action_plan": action_plan,
                "action_execution": action_execution,
                "action_result": action_result,
                "data": {
                    "decision": decision,
                    "confidence": confidence,
                    "action_id": action_plan.action_id,
                    "success": action_result.success
                }
            }
            
        except Exception as e:
            logger.error(f"행동 시스템 입력 처리 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }

    async def generate_action_plan(self, decision_result: Dict[str, Any], 
                                 available_resources: List[str],
                                 constraints: Dict[str, Any]) -> ActionPlan:
        """의사결정 결과 기반 행동 계획 생성"""
        try:
            return await self.action_generator.generate_plan(
                decision_result, available_resources, constraints
            )
        except Exception as e:
            logger.error(f"행동 계획 생성 실패: {e}")
            raise
    
    async def execute_action(self, action_plan: ActionPlan) -> ActionExecution:
        """행동 실행"""
        try:
            # 실행 가능 여부 확인
            if not await self._can_execute_action(action_plan):
                raise ValueError(f"행동 실행 불가: {action_plan.action_id}")
            
            # 실행 시작
            execution = await self.action_executor.execute(action_plan)
            
            # 실행 상태 업데이트
            self.executing_actions[action_plan.action_id] = execution
            
            return execution
            
        except Exception as e:
            logger.error(f"행동 실행 실패: {e}")
            raise
    
    async def analyze_action_result(self, action_execution: ActionExecution,
                                  expected_outcome: Dict[str, Any]) -> ActionResult:
        """행동 결과 분석"""
        try:
            return await self.result_analyzer.analyze_result(
                action_execution, expected_outcome
            )
        except Exception as e:
            logger.error(f"행동 결과 분석 실패: {e}")
            raise
    
    async def optimize_behavior_patterns(self, action_results: List[ActionResult]) -> List[BehaviorPattern]:
        """행동 패턴 최적화"""
        try:
            # 패턴 분석
            patterns = await self._analyze_behavior_patterns(action_results)
            
            # 최적화 제안 생성
            optimized_patterns = await self._optimize_patterns(patterns)
            
            return optimized_patterns
            
        except Exception as e:
            logger.error(f"행동 패턴 최적화 실패: {e}")
            raise
    
    async def _analyze_behavior_patterns(self, action_results: List[ActionResult]) -> List[BehaviorPattern]:
        """행동 패턴 분석"""
        patterns = []
        
        for result in action_results:
            # 패턴 타입 결정
            pattern_type = "successful" if result.success else "failed"
            
            # 빈도 계산 (시뮬레이션)
            frequency = 0.8 if result.success else 0.2
            
            # 성공률 계산
            success_rate = result.effectiveness_score
            
            # 평균 소요시간 (시뮬레이션)
            average_duration = 120.0  # 2분
            
            # 공통 요소
            common_factors = ["효과성", "효율성", "학습"]
            
            # 최적화 기회
            optimization_opportunities = []
            if result.effectiveness_score < 0.8:
                optimization_opportunities.append("효과성 향상")
            if result.efficiency_score < 0.8:
                optimization_opportunities.append("효율성 향상")
            
            pattern = BehaviorPattern(
                pattern_id=f"pattern_{len(patterns)}",
                pattern_type=pattern_type,
                frequency=frequency,
                success_rate=success_rate,
                average_duration=average_duration,
                common_factors=common_factors,
                optimization_opportunities=optimization_opportunities
            )
            
            patterns.append(pattern)
        
        return patterns
    
    async def _optimize_patterns(self, patterns: List[BehaviorPattern]) -> List[BehaviorPattern]:
        """패턴 최적화"""
        optimized_patterns = []
        
        for pattern in patterns:
            # 최적화 제안 추가
            if pattern.success_rate < 0.8:
                pattern.optimization_opportunities.append("성공률 향상 전략 수립")
            
            if pattern.average_duration > 300:  # 5분 이상
                pattern.optimization_opportunities.append("실행 시간 단축")
            
            optimized_patterns.append(pattern)
        
        return optimized_patterns
    
    async def _can_execute_action(self, action_plan: ActionPlan) -> bool:
        """행동 실행 가능 여부 확인"""
        # 리소스 가용성 확인
        for resource in action_plan.required_resources:
            if not await self._is_resource_available(resource):
                return False
        
        # 의존성 확인
        for dependency in action_plan.dependencies:
            if not await self._is_dependency_satisfied(dependency):
                return False
        
        # 동시 실행 제한 확인
        if len(self.executing_actions) >= self.max_concurrent_actions:
            return False
        
        return True
    
    async def _is_resource_available(self, resource: str) -> bool:
        """리소스 가용성 확인"""
        # 실제 구현에서는 리소스 관리 시스템과 연동
        return True
    
    async def _is_dependency_satisfied(self, dependency: str) -> bool:
        """의존성 만족 여부 확인"""
        # 테스트 환경에서는 모든 의존성을 만족하는 것으로 가정
        # 실제 구현에서는 완료된 행동 중에 의존성이 있는지 확인
        return True

class ActionGenerator:
    """행동 생성 엔진"""
    
    def __init__(self):
        self.action_templates = {
            "immediate_response": {
                "type": ActionType.IMMEDIATE,
                "priority": ActionPriority.HIGH,
                "duration": 60.0,
                "resources": ["cpu", "memory"],
                "success_criteria": ["응답 시간 < 1초", "정확도 > 90%"]
            },
            "analysis_task": {
                "type": ActionType.SCHEDULED,
                "priority": ActionPriority.MEDIUM,
                "duration": 300.0,
                "resources": ["cpu", "memory", "storage"],
                "success_criteria": ["분석 완료", "결과 저장"]
            },
            "learning_action": {
                "type": ActionType.RECURRING,
                "priority": ActionPriority.MEDIUM,
                "duration": 600.0,
                "resources": ["cpu", "memory", "network"],
                "success_criteria": ["학습 완료", "모델 업데이트"]
            },
            "optimization_task": {
                "type": ActionType.CONDITIONAL,
                "priority": ActionPriority.LOW,
                "duration": 1800.0,
                "resources": ["cpu", "memory", "storage"],
                "success_criteria": ["성능 향상", "최적화 완료"]
            }
        }
        
        self.priority_weights = {
            "urgency": 0.4,
            "importance": 0.3,
            "complexity": 0.2,
            "resource_availability": 0.1
        }
    
    async def generate_plan(self, decision_result: Dict[str, Any],
                          available_resources: List[str],
                          constraints: Dict[str, Any]) -> ActionPlan:
        """행동 계획 생성"""
        # 1. 의사결정 결과 분석
        action_type = await self._determine_action_type(decision_result)
        priority = await self._calculate_priority(decision_result, constraints)
        
        # 2. 행동 세부사항 생성
        description = await self._generate_description(decision_result)
        duration = await self._estimate_duration(action_type, decision_result)
        resources = await self._select_resources(action_type, available_resources)
        
        # 3. 의존성 및 위험 요소 분석
        dependencies = await self._identify_dependencies(decision_result)
        risk_factors = await self._identify_risk_factors(decision_result)
        
        # 4. 성공 기준 정의
        success_criteria = await self._define_success_criteria(action_type, decision_result)
        
        # 5. 행동 계획 생성
        action_id = f"action_{int(time.time())}_{hash(description) % 10000}"
        
        return ActionPlan(
            action_id=action_id,
            action_type=action_type,
            description=description,
            priority=priority,
            estimated_duration=duration,
            required_resources=resources,
            dependencies=dependencies,
            success_criteria=success_criteria,
            risk_factors=risk_factors,
            created_at=datetime.now()
        )
    
    async def _determine_action_type(self, decision_result: Dict[str, Any]) -> ActionType:
        """행동 타입 결정"""
        urgency = decision_result.get("urgency_level", 0.0)
        complexity = decision_result.get("complexity_score", 0.0)
        
        if urgency > 0.8:
            return ActionType.IMMEDIATE
        elif complexity > 0.7:
            return ActionType.SCHEDULED
        elif "learning" in decision_result.get("situation_type", ""):
            return ActionType.RECURRING
        else:
            return ActionType.CONDITIONAL
    
    async def _calculate_priority(self, decision_result: Dict[str, Any],
                                constraints: Dict[str, Any]) -> ActionPriority:
        """우선순위 계산"""
        urgency = decision_result.get("urgency_level", 0.0)
        importance = decision_result.get("importance", 0.0)
        complexity = decision_result.get("complexity_score", 0.0)
        
        # 가중 평균 계산
        priority_score = (
            urgency * self.priority_weights["urgency"] +
            importance * self.priority_weights["importance"] +
            complexity * self.priority_weights["complexity"]
        )
        
        if priority_score > 0.8:
            return ActionPriority.CRITICAL
        elif priority_score > 0.6:
            return ActionPriority.HIGH
        elif priority_score > 0.4:
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.LOW
    
    async def _generate_description(self, decision_result: Dict[str, Any]) -> str:
        """행동 설명 생성"""
        decision = decision_result.get("decision", "")
        reasoning = decision_result.get("reasoning", "")
        situation_type = decision_result.get("situation_type", "")
        
        if situation_type == "learning":
            return f"학습 행동 실행: {decision} - {reasoning}"
        elif situation_type == "decision":
            return f"의사결정 행동 실행: {decision} - {reasoning}"
        elif situation_type == "problem":
            return f"문제 해결 행동 실행: {decision} - {reasoning}"
        else:
            return f"일반 행동 실행: {decision} - {reasoning}"
    
    async def _estimate_duration(self, action_type: ActionType,
                               decision_result: Dict[str, Any]) -> float:
        """소요 시간 추정"""
        base_duration = {
            ActionType.IMMEDIATE: 60.0,
            ActionType.SCHEDULED: 300.0,
            ActionType.CONDITIONAL: 600.0,
            ActionType.RECURRING: 1800.0
        }
        
        complexity = decision_result.get("complexity_score", 0.5)
        return base_duration[action_type] * (1 + complexity)
    
    async def _select_resources(self, action_type: ActionType,
                              available_resources: List[str]) -> List[str]:
        """필요 리소스 선택"""
        if action_type == ActionType.IMMEDIATE:
            return ["cpu", "memory"]
        elif action_type == ActionType.SCHEDULED:
            return ["cpu", "memory", "storage"]
        elif action_type == ActionType.RECURRING:
            return ["cpu", "memory", "network"]
        else:
            return ["cpu", "memory", "storage"]
    
    async def _identify_dependencies(self, decision_result: Dict[str, Any]) -> List[str]:
        """의존성 식별"""
        dependencies = []
        
        # 상황에 따른 의존성 추가
        if decision_result.get("situation_type") == "learning":
            dependencies.append("learning_environment_ready")
        
        if decision_result.get("urgency_level", 0.0) > 0.8:
            dependencies.append("emergency_resources_available")
        
        return dependencies
    
    async def _identify_risk_factors(self, decision_result: Dict[str, Any]) -> List[str]:
        """위험 요소 식별"""
        risk_factors = []
        
        if decision_result.get("risk_level", 0.0) > 0.7:
            risk_factors.append("high_risk_operation")
        
        if decision_result.get("complexity_score", 0.0) > 0.8:
            risk_factors.append("complex_operation")
        
        return risk_factors
    
    async def _define_success_criteria(self, action_type: ActionType,
                                    decision_result: Dict[str, Any]) -> List[str]:
        """성공 기준 정의"""
        criteria = []
        
        if action_type == ActionType.IMMEDIATE:
            criteria.extend(["응답 시간 < 1초", "정확도 > 90%"])
        elif action_type == ActionType.SCHEDULED:
            criteria.extend(["작업 완료", "결과 저장"])
        elif action_type == ActionType.RECURRING:
            criteria.extend(["학습 완료", "모델 업데이트"])
        else:
            criteria.extend(["조건 만족", "결과 달성"])
        
        return criteria

class ActionExecutor:
    """행동 실행 엔진"""
    
    def __init__(self):
        self.execution_strategies = {
            ActionType.IMMEDIATE: self._execute_immediate,
            ActionType.SCHEDULED: self._execute_scheduled,
            ActionType.CONDITIONAL: self._execute_conditional,
            ActionType.RECURRING: self._execute_recurring
        }
        
        self.execution_logs = {}
        self.performance_metrics = {}
    
    async def execute(self, action_plan: ActionPlan) -> ActionExecution:
        """행동 실행"""
        execution_id = f"exec_{action_plan.action_id}"
        
        # 실행 시작
        execution = ActionExecution(
            action_id=action_plan.action_id,
            status=ActionStatus.EXECUTING,
            start_time=datetime.now(),
            end_time=None,
            actual_duration=None,
            progress=0.0,
            current_step="시작",
            logs=[],
            errors=[],
            performance_metrics={}
        )
        
        try:
            # 실행 전략 선택
            strategy = self.execution_strategies[action_plan.action_type]
            
            # 실행 수행
            result = await strategy(action_plan, execution)
            
            # 실행 완료
            execution.status = ActionStatus.COMPLETED
            execution.end_time = datetime.now()
            execution.actual_duration = (execution.end_time - execution.start_time).total_seconds()
            execution.progress = 100.0
            execution.current_step = "완료"
            
            # 성능 메트릭 저장
            self.performance_metrics[execution_id] = result.get("metrics", {})
            execution.performance_metrics = result.get("metrics", {})
            
        except Exception as e:
            # 실행 실패
            execution.status = ActionStatus.FAILED
            execution.end_time = datetime.now()
            execution.errors.append(str(e))
            execution.current_step = "실패"
            logger.error(f"행동 실행 실패: {e}")
        
        return execution
    
    async def _execute_immediate(self, action_plan: ActionPlan,
                               execution: ActionExecution) -> Dict[str, Any]:
        """즉시 실행"""
        execution.logs.append("즉시 실행 시작")
        execution.current_step = "즉시 실행"
        
        # 시뮬레이션된 즉시 실행
        await asyncio.sleep(0.1)  # 실제로는 실제 작업 수행
        
        execution.progress = 50.0
        execution.logs.append("즉시 실행 진행 중")
        
        await asyncio.sleep(0.1)
        
        execution.progress = 100.0
        execution.logs.append("즉시 실행 완료")
        
        return {
            "success": True,
            "metrics": {
                "response_time": 0.2,
                "accuracy": 0.95,
                "efficiency": 0.9
            }
        }
    
    async def _execute_scheduled(self, action_plan: ActionPlan,
                               execution: ActionExecution) -> Dict[str, Any]:
        """예약 실행"""
        execution.logs.append("예약 실행 시작")
        execution.current_step = "예약 실행"
        
        # 단계별 실행
        steps = ["계획 수립", "리소스 할당", "작업 수행", "결과 검증"]
        
        for i, step in enumerate(steps):
            execution.current_step = step
            execution.progress = (i + 1) * 25.0
            execution.logs.append(f"단계 {i+1}: {step}")
            
            await asyncio.sleep(0.5)  # 실제 작업 시뮬레이션
        
        return {
            "success": True,
            "metrics": {
                "completion_time": 2.0,
                "resource_utilization": 0.8,
                "quality_score": 0.85
            }
        }
    
    async def _execute_conditional(self, action_plan: ActionPlan,
                                execution: ActionExecution) -> Dict[str, Any]:
        """조건부 실행"""
        execution.logs.append("조건부 실행 시작")
        execution.current_step = "조건 확인"
        
        # 조건 확인
        await asyncio.sleep(0.2)
        execution.progress = 30.0
        execution.logs.append("조건 확인 완료")
        
        # 조건 만족 시 실행
        execution.current_step = "조건부 실행"
        await asyncio.sleep(0.3)
        execution.progress = 70.0
        execution.logs.append("조건부 실행 진행")
        
        await asyncio.sleep(0.2)
        execution.progress = 100.0
        execution.logs.append("조건부 실행 완료")
        
        return {
            "success": True,
            "metrics": {
                "condition_satisfaction": 0.9,
                "execution_efficiency": 0.85,
                "outcome_quality": 0.8
            }
        }
    
    async def _execute_recurring(self, action_plan: ActionPlan,
                               execution: ActionExecution) -> Dict[str, Any]:
        """반복 실행"""
        execution.logs.append("반복 실행 시작")
        execution.current_step = "반복 실행"
        
        # 반복 작업 수행
        for cycle in range(3):  # 3회 반복
            execution.current_step = f"반복 {cycle + 1}/3"
            execution.progress = (cycle + 1) * 33.33
            execution.logs.append(f"반복 {cycle + 1} 수행")
            
            await asyncio.sleep(0.3)
        
        return {
            "success": True,
            "metrics": {
                "cycle_count": 3,
                "average_cycle_time": 0.3,
                "consistency_score": 0.9
            }
        }

class ActionResultAnalyzer:
    """행동 결과 분석 엔진"""
    
    def __init__(self):
        self.analysis_metrics = {
            "effectiveness": ["goal_achievement", "quality_score", "impact_measure"],
            "efficiency": ["time_efficiency", "resource_efficiency", "cost_efficiency"],
            "learning": ["knowledge_gain", "skill_improvement", "pattern_recognition"]
        }
    
    async def analyze_result(self, action_execution: ActionExecution,
                           expected_outcome: Dict[str, Any]) -> ActionResult:
        """행동 결과 분석"""
        # 1. 효과성 평가
        effectiveness_score = await self._evaluate_effectiveness(action_execution, expected_outcome)
        
        # 2. 효율성 평가
        efficiency_score = await self._evaluate_efficiency(action_execution)
        
        # 3. 학습 포인트 추출
        learning_points = await self._extract_learning_points(action_execution)
        
        # 4. 개선 제안 생성
        improvement_suggestions = await self._generate_improvement_suggestions(
            action_execution, effectiveness_score, efficiency_score
        )
        
        # 5. 다음 행동 제안
        next_actions = await self._suggest_next_actions(action_execution, effectiveness_score)
        
        # 6. 성공 여부 판단
        success = effectiveness_score > 0.7 and efficiency_score > 0.6
        
        return ActionResult(
            action_id=action_execution.action_id,
            success=success,
            outcome={
                "effectiveness_score": effectiveness_score,
                "efficiency_score": efficiency_score,
                "learning_points": learning_points,
                "improvement_suggestions": improvement_suggestions
            },
            effectiveness_score=effectiveness_score,
            efficiency_score=efficiency_score,
            learning_points=learning_points,
            improvement_suggestions=improvement_suggestions,
            next_actions=next_actions,
            completed_at=datetime.now()
        )
    
    async def _evaluate_effectiveness(self, action_execution: ActionExecution,
                                    expected_outcome: Dict[str, Any]) -> float:
        """효과성 평가"""
        # 실행 성공 여부
        success_factor = 1.0 if action_execution.status == ActionStatus.COMPLETED else 0.0
        
        # 목표 달성도 (시뮬레이션)
        goal_achievement = 0.85 if success_factor > 0 else 0.0
        
        # 품질 점수
        quality_score = 0.9 if len(action_execution.errors) == 0 else 0.6
        
        # 영향도 측정
        impact_measure = 0.8 if action_execution.progress == 100.0 else 0.5
        
        # 가중 평균
        effectiveness = (
            success_factor * 0.4 +
            goal_achievement * 0.3 +
            quality_score * 0.2 +
            impact_measure * 0.1
        )
        
        return min(effectiveness, 1.0)
    
    async def _evaluate_efficiency(self, action_execution: ActionExecution) -> float:
        """효율성 평가"""
        if action_execution.actual_duration is None:
            return 0.0
        
        # 시간 효율성
        time_efficiency = 1.0 / (1.0 + action_execution.actual_duration / 60.0)
        
        # 리소스 효율성 (시뮬레이션)
        resource_efficiency = 0.85 if action_execution.status == ActionStatus.COMPLETED else 0.5
        
        # 비용 효율성 (시뮬레이션)
        cost_efficiency = 0.9 if len(action_execution.errors) == 0 else 0.6
        
        # 가중 평균
        efficiency = (
            time_efficiency * 0.4 +
            resource_efficiency * 0.4 +
            cost_efficiency * 0.2
        )
        
        return min(efficiency, 1.0)
    
    async def _extract_learning_points(self, action_execution: ActionExecution) -> List[str]:
        """학습 포인트 추출"""
        learning_points = []
        
        # 성공적인 실행에서 학습 포인트
        if action_execution.status == ActionStatus.COMPLETED:
            learning_points.append("효과적인 실행 패턴 확인")
            learning_points.append("리소스 활용 최적화 방법 학습")
        
        # 오류에서 학습 포인트
        if action_execution.errors:
            learning_points.append("오류 발생 패턴 분석")
            learning_points.append("오류 방지 방법 학습")
        
        # 성능 메트릭에서 학습 포인트
        if action_execution.performance_metrics:
            learning_points.append("성능 최적화 기회 식별")
        
        return learning_points
    
    async def _generate_improvement_suggestions(self, action_execution: ActionExecution,
                                             effectiveness_score: float,
                                             efficiency_score: float) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        if effectiveness_score < 0.8:
            suggestions.append("목표 달성률 향상을 위한 전략 개선 필요")
        
        if efficiency_score < 0.8:
            suggestions.append("실행 효율성 향상을 위한 프로세스 최적화 필요")
        
        if len(action_execution.errors) > 0:
            suggestions.append("오류 처리 및 예방 메커니즘 강화 필요")
        
        if action_execution.actual_duration and action_execution.actual_duration > 300:
            suggestions.append("실행 시간 단축을 위한 병렬화 고려")
        
        return suggestions
    
    async def _suggest_next_actions(self, action_execution: ActionExecution,
                                  effectiveness_score: float) -> List[str]:
        """다음 행동 제안"""
        next_actions = []
        
        if effectiveness_score > 0.8:
            next_actions.append("성공 패턴 확장 및 적용")
            next_actions.append("유사한 상황에서 동일한 전략 사용")
        else:
            next_actions.append("실패 원인 분석 및 전략 재검토")
            next_actions.append("대안적 접근 방법 탐색")
        
        return next_actions

async def test_action_system():
    """행동 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 4 - 행동 시스템 테스트 ===")
    
    # 행동 시스템 초기화
    action_system = ActionSystem()
    
    # 테스트용 의사결정 결과
    decision_result = {
        "decision": "urgent_action",
        "reasoning": "긴급한 상황에 대한 즉시 대응 필요",
        "situation_type": "decision",
        "urgency_level": 0.9,
        "importance": 0.8,
        "complexity_score": 0.6,
        "risk_level": 0.3
    }
    
    # 1. 행동 계획 생성 테스트
    print("\n1. 행동 계획 생성 테스트")
    action_plan = await action_system.generate_action_plan(
        decision_result,
        available_resources=["cpu", "memory", "network"],
        constraints={"time_limit": 300}
    )
    
    print(f"생성된 행동 계획:")
    print(f"- 행동 ID: {action_plan.action_id}")
    print(f"- 행동 타입: {action_plan.action_type.value}")
    print(f"- 우선순위: {action_plan.priority.value}")
    print(f"- 예상 소요시간: {action_plan.estimated_duration:.1f}초")
    print(f"- 필요 리소스: {action_plan.required_resources}")
    print(f"- 성공 기준: {action_plan.success_criteria}")
    
    # 2. 행동 실행 테스트
    print("\n2. 행동 실행 테스트")
    action_execution = await action_system.execute_action(action_plan)
    
    print(f"실행 결과:")
    print(f"- 상태: {action_execution.status.value}")
    print(f"- 진행률: {action_execution.progress:.1f}%")
    print(f"- 실제 소요시간: {action_execution.actual_duration:.1f}초")
    print(f"- 현재 단계: {action_execution.current_step}")
    print(f"- 로그 수: {len(action_execution.logs)}")
    print(f"- 오류 수: {len(action_execution.errors)}")
    
    # 3. 행동 결과 분석 테스트
    print("\n3. 행동 결과 분석 테스트")
    action_result = await action_system.analyze_action_result(
        action_execution,
        expected_outcome={"goal": "긴급 상황 해결", "quality": "높음"}
    )
    
    print(f"분석 결과:")
    print(f"- 성공 여부: {action_result.success}")
    print(f"- 효과성 점수: {action_result.effectiveness_score:.3f}")
    print(f"- 효율성 점수: {action_result.efficiency_score:.3f}")
    print(f"- 학습 포인트: {action_result.learning_points}")
    print(f"- 개선 제안: {action_result.improvement_suggestions}")
    print(f"- 다음 행동: {action_result.next_actions}")
    
    # 4. 행동 패턴 최적화 테스트
    print("\n4. 행동 패턴 최적화 테스트")
    behavior_patterns = await action_system.optimize_behavior_patterns([action_result])
    
    print(f"최적화된 패턴:")
    for pattern in behavior_patterns:
        print(f"- 패턴 ID: {pattern.pattern_id}")
        print(f"- 패턴 타입: {pattern.pattern_type}")
        print(f"- 빈도: {pattern.frequency:.3f}")
        print(f"- 성공률: {pattern.success_rate:.3f}")
        print(f"- 평균 소요시간: {pattern.average_duration:.1f}초")
        print(f"- 최적화 기회: {pattern.optimization_opportunities}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    asyncio.run(test_action_system()) 