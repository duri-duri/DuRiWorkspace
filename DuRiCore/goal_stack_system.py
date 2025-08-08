#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.4 - Goal Stack 시스템
Soar 기반 목표/하위목표 구조를 통한 의식적 조절 시스템
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GoalPriority(Enum):
    """목표 우선순위"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class GoalStatus(Enum):
    """목표 상태"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class GoalType(Enum):
    """목표 유형"""
    ACHIEVEMENT = "achievement"  # 달성 목표
    MAINTENANCE = "maintenance"  # 유지 목표
    AVOIDANCE = "avoidance"      # 회피 목표
    LEARNING = "learning"        # 학습 목표
    CREATIVE = "creative"        # 창의적 목표

@dataclass
class SubGoal:
    """하위목표 데이터 클래스"""
    id: str
    name: str
    description: str
    parent_goal_id: str
    priority: GoalPriority
    status: GoalStatus
    created_at: str
    deadline: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    dependencies: List[str] = None
    resources: List[str] = None
    success_criteria: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.resources is None:
            self.resources = []
        if self.success_criteria is None:
            self.success_criteria = []

@dataclass
class Goal:
    """목표 데이터 클래스"""
    id: str
    name: str
    description: str
    goal_type: GoalType
    priority: GoalPriority
    status: GoalStatus
    created_at: str
    deadline: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    sub_goals: List[SubGoal] = None
    dependencies: List[str] = None
    resources: List[str] = None
    success_criteria: List[str] = None
    emotional_weight: float = 1.0
    cognitive_load: float = 1.0
    
    def __post_init__(self):
        if self.sub_goals is None:
            self.sub_goals = []
        if self.dependencies is None:
            self.dependencies = []
        if self.resources is None:
            self.resources = []
        if self.success_criteria is None:
            self.success_criteria = []

@dataclass
class GoalStack:
    """목표 스택 데이터 클래스"""
    active_goals: List[Goal]
    suspended_goals: List[Goal]
    completed_goals: List[Goal]
    failed_goals: List[Goal]
    max_active_goals: int = 5
    max_stack_depth: int = 10

class GoalStackSystem:
    """Goal Stack 시스템 - Soar 기반 목표 관리"""
    
    def __init__(self):
        """초기화"""
        self.goal_stack = GoalStack(
            active_goals=[],
            suspended_goals=[],
            completed_goals=[],
            failed_goals=[]
        )
        self.goal_history = []
        self.goal_patterns = {}
        self.conflict_resolution_rules = []
        self.resource_allocation = {}
        self.cognitive_load_monitor = {}
        
        # Soar 기반 의사결정 매트릭스
        self.decision_matrix = {
            'urgency': 0.3,
            'importance': 0.4,
            'feasibility': 0.2,
            'emotional_value': 0.1
        }
        
        logger.info("Goal Stack 시스템 초기화 완료")
    
    def create_goal(self, name: str, description: str, goal_type: GoalType,
                   priority: GoalPriority, deadline: Optional[str] = None,
                   dependencies: List[str] = None, resources: List[str] = None,
                   success_criteria: List[str] = None, emotional_weight: float = 1.0) -> Goal:
        """새 목표 생성"""
        goal_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        goal = Goal(
            id=goal_id,
            name=name,
            description=description,
            goal_type=goal_type,
            priority=priority,
            status=GoalStatus.PENDING,
            created_at=created_at,
            deadline=deadline,
            dependencies=dependencies or [],
            resources=resources or [],
            success_criteria=success_criteria or [],
            emotional_weight=emotional_weight
        )
        
        # 목표 스택에 추가
        self._add_goal_to_stack(goal)
        self.goal_history.append(goal)
        
        logger.info(f"새 목표 생성: {name} (ID: {goal_id})")
        return goal
    
    def create_sub_goal(self, parent_goal_id: str, name: str, description: str,
                       priority: GoalPriority, deadline: Optional[str] = None,
                       dependencies: List[str] = None, resources: List[str] = None,
                       success_criteria: List[str] = None) -> SubGoal:
        """하위목표 생성"""
        sub_goal_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        sub_goal = SubGoal(
            id=sub_goal_id,
            name=name,
            description=description,
            parent_goal_id=parent_goal_id,
            priority=priority,
            status=GoalStatus.PENDING,
            created_at=created_at,
            deadline=deadline,
            dependencies=dependencies or [],
            resources=resources or [],
            success_criteria=success_criteria or []
        )
        
        # 부모 목표에 하위목표 추가
        parent_goal = self._find_goal_by_id(parent_goal_id)
        if parent_goal:
            parent_goal.sub_goals.append(sub_goal)
            logger.info(f"하위목표 생성: {name} (부모: {parent_goal.name})")
        else:
            logger.error(f"부모 목표를 찾을 수 없음: {parent_goal_id}")
        
        return sub_goal
    
    def _add_goal_to_stack(self, goal: Goal):
        """목표를 스택에 추가"""
        if len(self.goal_stack.active_goals) < self.goal_stack.max_active_goals:
            goal.status = GoalStatus.ACTIVE
            self.goal_stack.active_goals.append(goal)
        else:
            # 우선순위 기반 교체 또는 대기
            self._handle_goal_overflow(goal)
    
    def _handle_goal_overflow(self, new_goal: Goal):
        """목표 스택 오버플로우 처리"""
        # 가장 낮은 우선순위 목표 찾기
        lowest_priority_goal = min(
            self.goal_stack.active_goals,
            key=lambda g: g.priority.value
        )
        
        if new_goal.priority.value < lowest_priority_goal.priority.value:
            # 새 목표가 더 높은 우선순위인 경우 교체
            lowest_priority_goal.status = GoalStatus.SUSPENDED
            self.goal_stack.suspended_goals.append(lowest_priority_goal)
            self.goal_stack.active_goals.remove(lowest_priority_goal)
            
            new_goal.status = GoalStatus.ACTIVE
            self.goal_stack.active_goals.append(new_goal)
            
            logger.info(f"목표 교체: {lowest_priority_goal.name} → {new_goal.name}")
        else:
            # 새 목표를 대기 상태로
            new_goal.status = GoalStatus.SUSPENDED
            self.goal_stack.suspended_goals.append(new_goal)
            logger.info(f"목표 대기: {new_goal.name}")
    
    def _find_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        """ID로 목표 찾기"""
        for goal in self.goal_stack.active_goals + self.goal_stack.suspended_goals:
            if goal.id == goal_id:
                return goal
        return None
    
    def update_goal_progress(self, goal_id: str, progress: float, 
                           status: Optional[GoalStatus] = None) -> bool:
        """목표 진행률 업데이트"""
        goal = self._find_goal_by_id(goal_id)
        if not goal:
            logger.error(f"목표를 찾을 수 없음: {goal_id}")
            return False
        
        goal.progress = max(0.0, min(1.0, progress))
        
        if status:
            goal.status = status
        
        if goal.progress >= 1.0 and goal.status != GoalStatus.COMPLETED:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.now().isoformat()
            self._move_goal_to_completed(goal)
            logger.info(f"목표 완료: {goal.name}")
        
        return True
    
    def _move_goal_to_completed(self, goal: Goal):
        """완료된 목표를 완료 목록으로 이동"""
        if goal in self.goal_stack.active_goals:
            self.goal_stack.active_goals.remove(goal)
        elif goal in self.goal_stack.suspended_goals:
            self.goal_stack.suspended_goals.remove(goal)
        
        self.goal_stack.completed_goals.append(goal)
        
        # 대기 중인 목표 중 하나를 활성화
        if self.goal_stack.suspended_goals:
            next_goal = max(
                self.goal_stack.suspended_goals,
                key=lambda g: g.priority.value
            )
            next_goal.status = GoalStatus.ACTIVE
            self.goal_stack.active_goals.append(next_goal)
            self.goal_stack.suspended_goals.remove(next_goal)
            logger.info(f"대기 목표 활성화: {next_goal.name}")
    
    def get_active_goals(self) -> List[Goal]:
        """활성 목표 목록 반환"""
        return self.goal_stack.active_goals.copy()
    
    async def get_current_goals(self) -> List[Goal]:
        """현재 목표 목록 반환 (비동기 버전)"""
        try:
            return self.goal_stack.active_goals.copy()
        except Exception as e:
            logger.error(f"현재 목표 반환 중 오류: {e}")
            return []
    
    def get_goal_stack_status(self) -> Dict[str, Any]:
        """목표 스택 상태 반환"""
        return {
            'active_goals_count': len(self.goal_stack.active_goals),
            'suspended_goals_count': len(self.goal_stack.suspended_goals),
            'completed_goals_count': len(self.goal_stack.completed_goals),
            'failed_goals_count': len(self.goal_stack.failed_goals),
            'max_active_goals': self.goal_stack.max_active_goals,
            'stack_utilization': len(self.goal_stack.active_goals) / self.goal_stack.max_active_goals
        }
    
    def calculate_goal_priority_score(self, goal: Goal, context: Dict[str, Any]) -> float:
        """Soar 기반 목표 우선순위 점수 계산"""
        urgency_score = self._calculate_urgency_score(goal, context)
        importance_score = self._calculate_importance_score(goal, context)
        feasibility_score = self._calculate_feasibility_score(goal, context)
        emotional_score = self._calculate_emotional_score(goal, context)
        
        total_score = (
            urgency_score * self.decision_matrix['urgency'] +
            importance_score * self.decision_matrix['importance'] +
            feasibility_score * self.decision_matrix['feasibility'] +
            emotional_score * self.decision_matrix['emotional_value']
        )
        
        return total_score
    
    def _calculate_urgency_score(self, goal: Goal, context: Dict[str, Any]) -> float:
        """긴급성 점수 계산"""
        if not goal.deadline:
            return 0.5
        
        deadline = datetime.fromisoformat(goal.deadline)
        now = datetime.now()
        time_remaining = (deadline - now).total_seconds()
        
        if time_remaining <= 0:
            return 1.0
        elif time_remaining < 3600:  # 1시간 이내
            return 0.9
        elif time_remaining < 86400:  # 1일 이내
            return 0.7
        elif time_remaining < 604800:  # 1주 이내
            return 0.5
        else:
            return 0.3
    
    def _calculate_importance_score(self, goal: Goal, context: Dict[str, Any]) -> float:
        """중요성 점수 계산"""
        priority_mapping = {
            GoalPriority.CRITICAL: 1.0,
            GoalPriority.HIGH: 0.8,
            GoalPriority.MEDIUM: 0.6,
            GoalPriority.LOW: 0.4,
            GoalPriority.BACKGROUND: 0.2
        }
        
        base_score = priority_mapping.get(goal.priority, 0.5)
        
        # 의존성 기반 보정
        dependency_factor = 1.0
        if goal.dependencies:
            completed_deps = sum(1 for dep_id in goal.dependencies 
                               if self._is_goal_completed(dep_id))
            dependency_factor = completed_deps / len(goal.dependencies)
        
        return base_score * dependency_factor
    
    def _calculate_feasibility_score(self, goal: Goal, context: Dict[str, Any]) -> float:
        """실행 가능성 점수 계산"""
        # 리소스 가용성 확인
        resource_score = 1.0
        if goal.resources:
            available_resources = context.get('available_resources', [])
            resource_score = sum(1 for resource in goal.resources 
                               if resource in available_resources) / len(goal.resources)
        
        # 진행률 기반 보정
        progress_factor = 1.0 - goal.progress * 0.3  # 진행률이 높을수록 실행 가능성 증가
        
        return resource_score * progress_factor
    
    def _calculate_emotional_score(self, goal: Goal, context: Dict[str, Any]) -> float:
        """감정적 가치 점수 계산"""
        return goal.emotional_weight
    
    def _is_goal_completed(self, goal_id: str) -> bool:
        """목표 완료 여부 확인"""
        for goal in self.goal_stack.completed_goals:
            if goal.id == goal_id:
                return True
        return False
    
    def get_next_action_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """다음 행동 추천 (Soar 기반)"""
        if not self.goal_stack.active_goals:
            return {
                'action': 'create_new_goal',
                'reason': '활성 목표가 없음',
                'priority': 'medium'
            }
        
        # 가장 높은 우선순위 목표 선택
        best_goal = max(
            self.goal_stack.active_goals,
            key=lambda g: self.calculate_goal_priority_score(g, context)
        )
        
        # 목표 유형별 행동 추천
        action_recommendation = self._get_goal_type_action(best_goal, context)
        
        return {
            'action': action_recommendation['action'],
            'goal_id': best_goal.id,
            'goal_name': best_goal.name,
            'reason': action_recommendation['reason'],
            'priority': best_goal.priority.name.lower(),
            'progress': best_goal.progress,
            'deadline': best_goal.deadline
        }
    
    def _get_goal_type_action(self, goal: Goal, context: Dict[str, Any]) -> Dict[str, Any]:
        """목표 유형별 행동 추천"""
        if goal.goal_type == GoalType.ACHIEVEMENT:
            return {
                'action': 'work_on_achievement',
                'reason': f'달성 목표 진행: {goal.name}'
            }
        elif goal.goal_type == GoalType.MAINTENANCE:
            return {
                'action': 'maintain_status',
                'reason': f'유지 목표 확인: {goal.name}'
            }
        elif goal.goal_type == GoalType.AVOIDANCE:
            return {
                'action': 'avoid_risk',
                'reason': f'회피 목표 모니터링: {goal.name}'
            }
        elif goal.goal_type == GoalType.LEARNING:
            return {
                'action': 'learn_and_practice',
                'reason': f'학습 목표 수행: {goal.name}'
            }
        elif goal.goal_type == GoalType.CREATIVE:
            return {
                'action': 'creative_exploration',
                'reason': f'창의적 목표 탐색: {goal.name}'
            }
        else:
            return {
                'action': 'general_progress',
                'reason': f'일반 목표 진행: {goal.name}'
            }
    
    def add_conflict_resolution_rule(self, rule: Dict[str, Any]):
        """충돌 해결 규칙 추가"""
        self.conflict_resolution_rules.append(rule)
        logger.info(f"충돌 해결 규칙 추가: {rule.get('name', 'unnamed')}")
    
    def resolve_goal_conflicts(self) -> List[Dict[str, Any]]:
        """목표 간 충돌 해결"""
        conflicts = []
        
        # 리소스 충돌 확인
        resource_conflicts = self._check_resource_conflicts()
        conflicts.extend(resource_conflicts)
        
        # 시간 충돌 확인
        time_conflicts = self._check_time_conflicts()
        conflicts.extend(time_conflicts)
        
        # 우선순위 충돌 확인
        priority_conflicts = self._check_priority_conflicts()
        conflicts.extend(priority_conflicts)
        
        # 충돌 해결 적용
        for conflict in conflicts:
            self._apply_conflict_resolution(conflict)
        
        return conflicts
    
    def _check_resource_conflicts(self) -> List[Dict[str, Any]]:
        """리소스 충돌 확인"""
        conflicts = []
        resource_usage = {}
        
        for goal in self.goal_stack.active_goals:
            for resource in goal.resources:
                if resource not in resource_usage:
                    resource_usage[resource] = []
                resource_usage[resource].append(goal.id)
        
        for resource, goal_ids in resource_usage.items():
            if len(goal_ids) > 1:
                conflicts.append({
                    'type': 'resource_conflict',
                    'resource': resource,
                    'conflicting_goals': goal_ids,
                    'severity': 'medium'
                })
        
        return conflicts
    
    def _check_time_conflicts(self) -> List[Dict[str, Any]]:
        """시간 충돌 확인"""
        conflicts = []
        active_goals = self.goal_stack.active_goals
        
        for i, goal1 in enumerate(active_goals):
            for goal2 in active_goals[i+1:]:
                if self._goals_have_time_conflict(goal1, goal2):
                    conflicts.append({
                        'type': 'time_conflict',
                        'goal1_id': goal1.id,
                        'goal2_id': goal2.id,
                        'severity': 'high'
                    })
        
        return conflicts
    
    def _goals_have_time_conflict(self, goal1: Goal, goal2: Goal) -> bool:
        """두 목표 간 시간 충돌 확인"""
        if not goal1.deadline or not goal2.deadline:
            return False
        
        deadline1 = datetime.fromisoformat(goal1.deadline)
        deadline2 = datetime.fromisoformat(goal2.deadline)
        
        # 간단한 시간 겹침 확인
        time_diff = abs((deadline1 - deadline2).total_seconds())
        return time_diff < 3600  # 1시간 이내
        
    def _check_priority_conflicts(self) -> List[Dict[str, Any]]:
        """우선순위 충돌 확인"""
        conflicts = []
        active_goals = self.goal_stack.active_goals
        
        # 동일한 우선순위를 가진 목표들 확인
        priority_groups = {}
        for goal in active_goals:
            priority = goal.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(goal.id)
        
        for priority, goal_ids in priority_groups.items():
            if len(goal_ids) > 1:
                conflicts.append({
                    'type': 'priority_conflict',
                    'priority': priority.name,
                    'conflicting_goals': goal_ids,
                    'severity': 'low'
                })
        
        return conflicts
    
    def _apply_conflict_resolution(self, conflict: Dict[str, Any]):
        """충돌 해결 적용"""
        if conflict['type'] == 'resource_conflict':
            self._resolve_resource_conflict(conflict)
        elif conflict['type'] == 'time_conflict':
            self._resolve_time_conflict(conflict)
        elif conflict['type'] == 'priority_conflict':
            self._resolve_priority_conflict(conflict)
    
    def _resolve_resource_conflict(self, conflict: Dict[str, Any]):
        """리소스 충돌 해결"""
        goal_ids = conflict['conflicting_goals']
        goals = [self._find_goal_by_id(gid) for gid in goal_ids]
        goals = [g for g in goals if g is not None]
        
        if goals:
            # 우선순위가 가장 높은 목표 유지, 나머지는 대기
            best_goal = max(goals, key=lambda g: g.priority.value)
            for goal in goals:
                if goal.id != best_goal.id:
                    goal.status = GoalStatus.SUSPENDED
                    if goal in self.goal_stack.active_goals:
                        self.goal_stack.active_goals.remove(goal)
                        self.goal_stack.suspended_goals.append(goal)
    
    def _resolve_time_conflict(self, conflict: Dict[str, Any]):
        """시간 충돌 해결"""
        goal1 = self._find_goal_by_id(conflict['goal1_id'])
        goal2 = self._find_goal_by_id(conflict['goal2_id'])
        
        if goal1 and goal2:
            # 더 긴급한 목표 우선
            if goal1.priority.value < goal2.priority.value:
                goal2.status = GoalStatus.SUSPENDED
                if goal2 in self.goal_stack.active_goals:
                    self.goal_stack.active_goals.remove(goal2)
                    self.goal_stack.suspended_goals.append(goal2)
            else:
                goal1.status = GoalStatus.SUSPENDED
                if goal1 in self.goal_stack.active_goals:
                    self.goal_stack.active_goals.remove(goal1)
                    self.goal_stack.suspended_goals.append(goal1)
    
    def _resolve_priority_conflict(self, conflict: Dict[str, Any]):
        """우선순위 충돌 해결"""
        # 우선순위 충돌은 일반적으로 허용됨 (자연스러운 경쟁)
        # 필요시 세부 조정 규칙 추가 가능
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            'total_goals': len(self.goal_history),
            'active_goals': len(self.goal_stack.active_goals),
            'suspended_goals': len(self.goal_stack.suspended_goals),
            'completed_goals': len(self.goal_stack.completed_goals),
            'failed_goals': len(self.goal_stack.failed_goals),
            'stack_utilization': len(self.goal_stack.active_goals) / self.goal_stack.max_active_goals,
            'conflict_resolution_rules': len(self.conflict_resolution_rules),
            'decision_matrix': self.decision_matrix
        }
    
    def export_goal_data(self) -> Dict[str, Any]:
        """목표 데이터 내보내기"""
        return {
            'goal_stack': asdict(self.goal_stack),
            'goal_history': [asdict(goal) for goal in self.goal_history],
            'system_status': self.get_system_status(),
            'exported_at': datetime.now().isoformat()
        }

    async def align_goals(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """목표 정렬 - 고급 AI 통합 시스템용 인터페이스"""
        try:
            # 컨텍스트에서 목표 관련 정보 추출
            goal_info = self._extract_goals_from_context(context)
            
            # 기존 목표들과 정렬
            aligned_goals = self._align_goals_with_context(goal_info, context)
            
            # 목표 우선순위 재조정
            self._reprioritize_goals(aligned_goals, context)
            
            return {
                'aligned_goals': aligned_goals,
                'goal_stack_status': self.get_goal_stack_status(),
                'next_action': self.get_next_action_recommendation(context),
                'conflict_resolution': self.resolve_goal_conflicts()
            }
        except Exception as e:
            logger.error(f"목표 정렬 중 오류: {e}")
            return {
                'aligned_goals': [],
                'goal_stack_status': self.get_goal_stack_status(),
                'next_action': {},
                'conflict_resolution': []
            }

    def _extract_goals_from_context(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컨텍스트에서 목표 정보 추출"""
        goals = []
        
        # 문제 해결 목표
        if 'problem' in context:
            goals.append({
                'name': '문제 해결',
                'description': context['problem'],
                'goal_type': GoalType.ACHIEVEMENT,
                'priority': GoalPriority.HIGH
            })
        
        # 이해관계자 관리 목표
        if 'stakeholders' in context:
            goals.append({
                'name': '이해관계자 관리',
                'description': f"이해관계자: {', '.join(context['stakeholders'])}",
                'goal_type': GoalType.MAINTENANCE,
                'priority': GoalPriority.MEDIUM
            })
        
        # 제약조건 관리 목표
        if 'constraints' in context:
            goals.append({
                'name': '제약조건 관리',
                'description': f"제약조건: {', '.join(context['constraints'])}",
                'goal_type': GoalType.AVOIDANCE,
                'priority': GoalPriority.MEDIUM
            })
        
        # 기회 활용 목표
        if 'opportunities' in context:
            goals.append({
                'name': '기회 활용',
                'description': f"기회: {', '.join(context['opportunities'])}",
                'goal_type': GoalType.ACHIEVEMENT,
                'priority': GoalPriority.HIGH
            })
        
        # 리스크 관리 목표
        if 'risks' in context:
            goals.append({
                'name': '리스크 관리',
                'description': f"리스크: {', '.join(context['risks'])}",
                'goal_type': GoalType.AVOIDANCE,
                'priority': GoalPriority.HIGH
            })
        
        return goals

    def _align_goals_with_context(self, goal_info: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컨텍스트와 목표 정렬"""
        aligned_goals = []
        
        for goal_data in goal_info:
            # 기존 목표와 중복 확인
            existing_goal = self._find_similar_goal(goal_data)
            
            if existing_goal:
                # 기존 목표 업데이트
                aligned_goals.append({
                    'action': 'update',
                    'goal_id': existing_goal.id,
                    'goal_data': goal_data,
                    'priority_adjustment': self._calculate_priority_adjustment(goal_data, context)
                })
            else:
                # 새 목표 생성
                aligned_goals.append({
                    'action': 'create',
                    'goal_data': goal_data,
                    'priority': self._calculate_context_priority(goal_data, context)
                })
        
        return aligned_goals

    def _find_similar_goal(self, goal_data: Dict[str, Any]) -> Optional[Goal]:
        """유사한 목표 찾기"""
        for goal in self.goal_stack.active_goals:
            if goal.name.lower() in goal_data['name'].lower() or goal_data['name'].lower() in goal.name.lower():
                return goal
        return None

    def _calculate_priority_adjustment(self, goal_data: Dict[str, Any], context: Dict[str, Any]) -> float:
        """우선순위 조정 계산"""
        base_priority = goal_data.get('priority', GoalPriority.MEDIUM).value
        context_urgency = self._assess_context_urgency(context)
        context_importance = self._assess_context_importance(context)
        
        adjustment = (context_urgency + context_importance) / 2
        return min(1.0, base_priority + adjustment)

    def _calculate_context_priority(self, goal_data: Dict[str, Any], context: Dict[str, Any]) -> GoalPriority:
        """컨텍스트 기반 우선순위 계산"""
        urgency_score = self._assess_context_urgency(context)
        importance_score = self._assess_context_importance(context)
        
        if urgency_score > 0.8 and importance_score > 0.8:
            return GoalPriority.CRITICAL
        elif urgency_score > 0.6 or importance_score > 0.6:
            return GoalPriority.HIGH
        elif urgency_score > 0.4 or importance_score > 0.4:
            return GoalPriority.MEDIUM
        else:
            return GoalPriority.LOW

    def _assess_context_urgency(self, context: Dict[str, Any]) -> float:
        """컨텍스트 긴급성 평가"""
        urgency_keywords = ['urgent', 'critical', 'emergency', 'deadline', 'immediate']
        context_text = str(context).lower()
        
        urgency_count = sum(1 for keyword in urgency_keywords if keyword in context_text)
        return min(1.0, urgency_count * 0.2)

    def _assess_context_importance(self, context: Dict[str, Any]) -> float:
        """컨텍스트 중요성 평가"""
        importance_keywords = ['important', 'critical', 'essential', 'vital', 'key', 'strategic']
        context_text = str(context).lower()
        
        importance_count = sum(1 for keyword in importance_keywords if keyword in context_text)
        return min(1.0, importance_count * 0.2)

    def _reprioritize_goals(self, aligned_goals: List[Dict[str, Any]], context: Dict[str, Any]):
        """목표 우선순위 재조정"""
        for aligned_goal in aligned_goals:
            if aligned_goal['action'] == 'update':
                goal_id = aligned_goal['goal_id']
                goal = self._find_goal_by_id(goal_id)
                if goal:
                    # 우선순위 조정
                    new_priority_score = aligned_goal.get('priority_adjustment', 0.5)
                    goal.priority = self._score_to_priority(new_priority_score)
            elif aligned_goal['action'] == 'create':
                # 새 목표 생성
                goal_data = aligned_goal['goal_data']
                priority = aligned_goal.get('priority', GoalPriority.MEDIUM)
                
                self.create_goal(
                    name=goal_data['name'],
                    description=goal_data['description'],
                    goal_type=goal_data['goal_type'],
                    priority=priority
                )

    def _score_to_priority(self, score: float) -> GoalPriority:
        """점수를 우선순위로 변환"""
        if score >= 0.8:
            return GoalPriority.CRITICAL
        elif score >= 0.6:
            return GoalPriority.HIGH
        elif score >= 0.4:
            return GoalPriority.MEDIUM
        elif score >= 0.2:
            return GoalPriority.LOW
        else:
            return GoalPriority.BACKGROUND

# 테스트 함수
async def test_goal_stack_system():
    """Goal Stack 시스템 테스트"""
    system = GoalStackSystem()
    
    # 테스트 목표 생성
    goal1 = system.create_goal(
        name="프로젝트 완료",
        description="중요한 프로젝트를 완료합니다",
        goal_type=GoalType.ACHIEVEMENT,
        priority=GoalPriority.HIGH,
        deadline=(datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)).isoformat(),
        emotional_weight=0.8
    )
    
    goal2 = system.create_goal(
        name="학습 진행",
        description="새로운 기술을 학습합니다",
        goal_type=GoalType.LEARNING,
        priority=GoalPriority.MEDIUM,
        emotional_weight=0.6
    )
    
    # 하위목표 생성
    sub_goal1 = system.create_sub_goal(
        parent_goal_id=goal1.id,
        name="요구사항 분석",
        description="프로젝트 요구사항을 분석합니다",
        priority=GoalPriority.HIGH
    )
    
    # 진행률 업데이트
    system.update_goal_progress(goal1.id, 0.3)
    system.update_goal_progress(goal2.id, 0.7)
    
    # 다음 행동 추천
    context = {'available_resources': ['time', 'energy']}
    recommendation = system.get_next_action_recommendation(context)
    
    # 충돌 해결
    conflicts = system.resolve_goal_conflicts()
    
    # 결과 출력
    print("=== Goal Stack 시스템 테스트 결과 ===")
    print(f"활성 목표 수: {len(system.get_active_goals())}")
    print(f"다음 행동 추천: {recommendation}")
    print(f"충돌 수: {len(conflicts)}")
    print(f"시스템 상태: {system.get_system_status()}")

if __name__ == "__main__":
    asyncio.run(test_goal_stack_system()) 