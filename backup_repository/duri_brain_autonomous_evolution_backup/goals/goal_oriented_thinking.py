"""
DuRi 목표 지향적 사고 시스템

DuRi가 스스로 목표를 설정하고 달성하는 고급 기능을 구현합니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 기존 시스템 import
from duri_core.assessment.self_assessment_manager import get_self_assessment_manager, AssessmentCategory
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_core.memory.meta_learning_data import get_meta_learning_data_manager

logger = logging.getLogger(__name__)

class GoalPriority(Enum):
    """목표 우선순위"""
    CRITICAL = "critical"    # 즉시 달성 필요
    HIGH = "high"           # 높은 우선순위
    MEDIUM = "medium"       # 중간 우선순위
    LOW = "low"            # 낮은 우선순위

class GoalStatus(Enum):
    """목표 상태"""
    PENDING = "pending"     # 대기 중
    IN_PROGRESS = "in_progress"  # 진행 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"       # 실패
    CANCELLED = "cancelled"  # 취소됨

class GoalCategory(Enum):
    """목표 카테고리"""
    PERFORMANCE = "performance"  # 성능 개선
    LEARNING = "learning"       # 학습 향상
    CREATIVITY = "creativity"   # 창의성 개발
    STABILITY = "stability"     # 안정성 강화
    INNOVATION = "innovation"   # 혁신

@dataclass
class Goal:
    """목표"""
    goal_id: str
    title: str
    description: str
    category: GoalCategory
    priority: GoalPriority
    status: GoalStatus
    created_at: datetime
    target_completion_date: datetime
    actual_completion_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    success_criteria: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    resources_required: List[str] = field(default_factory=list)
    estimated_effort: str = "medium"  # "low", "medium", "high"
    actual_effort: Optional[str] = None
    notes: List[str] = field(default_factory=list)

@dataclass
class GoalExecutionPlan:
    """목표 실행 계획"""
    plan_id: str
    goal_id: str
    steps: List[Dict[str, Any]]
    estimated_duration: timedelta
    required_resources: List[str]
    risk_assessment: Dict[str, Any]
    success_metrics: List[str]
    created_at: datetime

@dataclass
class GoalProgress:
    """목표 진행 상황"""
    progress_id: str
    goal_id: str
    timestamp: datetime
    progress_percentage: float
    completed_milestones: List[str]
    remaining_tasks: List[str]
    challenges_encountered: List[str]
    solutions_applied: List[str]
    next_steps: List[str]

class GoalOrientedThinking:
    """DuRi 목표 지향적 사고 시스템"""
    
    def __init__(self):
        """GoalOrientedThinking 초기화"""
        self.self_assessment_manager = get_self_assessment_manager()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.learning_loop_manager = None # 지연 초기화
        
        # 목표 관리
        self.active_goals: List[Goal] = []
        self.completed_goals: List[Goal] = []
        self.goal_execution_plans: List[GoalExecutionPlan] = []
        self.goal_progress_history: List[GoalProgress] = []
        
        # 목표 설정 임계값
        self.goal_setting_thresholds = {
            'performance_score': 0.7,  # 성능 점수가 70% 미만이면 성능 목표 설정
            'learning_efficiency': 0.6,  # 학습 효율성이 60% 미만이면 학습 목표 설정
            'creativity_score': 0.5,   # 창의성 점수가 50% 미만이면 창의성 목표 설정
            'stability_score': 0.8     # 안정성 점수가 80% 미만이면 안정성 목표 설정
        }
        
        logger.info("GoalOrientedThinking 초기화 완료")
    
    def should_set_new_goals(self) -> bool:
        """새로운 목표를 설정해야 하는지 확인합니다."""
        try:
            # 최근 자기 평가 결과 확인
            assessment_stats = self.self_assessment_manager.get_assessment_statistics()
            
            if not assessment_stats or assessment_stats.get('total_assessments', 0) == 0:
                return False
            
            latest_score = assessment_stats.get('latest_score', 0.0)
            
            # 전체 점수가 낮거나 활성 목표가 없는 경우
            if latest_score < 0.6 or len(self.active_goals) == 0:
                return True
            
            # 특정 카테고리별 목표 필요성 확인
            return self._check_category_specific_goals()
            
        except Exception as e:
            logger.error(f"목표 설정 필요성 확인 실패: {e}")
            return False
    
    def _check_category_specific_goals(self) -> bool:
        """카테고리별 목표 필요성을 확인합니다."""
        try:
            # 최근 평가 결과에서 카테고리별 점수 확인
            recent_assessments = self.self_assessment_manager.assessment_history[-3:] if self.self_assessment_manager.assessment_history else []
            
            if not recent_assessments:
                return False
            
            latest_assessment = recent_assessments[-1]
            category_scores = latest_assessment.category_scores
            
            # 각 카테고리별 임계값 확인
            for category, threshold in self.goal_setting_thresholds.items():
                if category in category_scores:
                    score = category_scores[category]
                    if score < threshold:
                        logger.info(f"{category} 카테고리 점수가 낮아 목표 설정이 필요합니다: {score:.2f}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"카테고리별 목표 확인 실패: {e}")
            return False
    
    def generate_goals(self) -> List[Goal]:
        """현재 상황을 바탕으로 목표를 생성합니다."""
        try:
            goals = []
            
            # 자기 평가 결과 분석
            assessment_stats = self.self_assessment_manager.get_assessment_statistics()
            if not assessment_stats:
                return goals
            
            latest_assessment = self.self_assessment_manager.assessment_history[-1] if self.self_assessment_manager.assessment_history else None
            if not latest_assessment:
                return goals
            
            # 성능 목표 생성
            if self._should_create_performance_goal(latest_assessment):
                goals.append(self._create_performance_goal(latest_assessment))
            
            # 학습 목표 생성
            if self._should_create_learning_goal(latest_assessment):
                goals.append(self._create_learning_goal(latest_assessment))
            
            # 창의성 목표 생성
            if self._should_create_creativity_goal(latest_assessment):
                goals.append(self._create_creativity_goal(latest_assessment))
            
            # 안정성 목표 생성
            if self._should_create_stability_goal(latest_assessment):
                goals.append(self._create_stability_goal(latest_assessment))
            
            # 혁신 목표 생성 (선택적)
            if self._should_create_innovation_goal(latest_assessment):
                goals.append(self._create_innovation_goal(latest_assessment))
            
            return goals
            
        except Exception as e:
            logger.error(f"목표 생성 실패: {e}")
            return []
    
    def _should_create_performance_goal(self, assessment) -> bool:
        """성능 목표 생성 필요성 확인"""
        try:
            performance_score = assessment.category_scores.get(AssessmentCategory.PERFORMANCE, 0.0)
            return performance_score < self.goal_setting_thresholds['performance_score']
        except Exception:
            return False
    
    def _create_performance_goal(self, assessment) -> Goal:
        """성능 목표 생성"""
        current_score = assessment.category_scores.get(AssessmentCategory.PERFORMANCE, 0.0)
        target_score = min(0.9, current_score + 0.2)  # 20% 개선 목표
        
        return Goal(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            title="시스템 성능 최적화",
            description=f"현재 성능 점수 {current_score:.2f}에서 {target_score:.2f}로 개선",
            category=GoalCategory.PERFORMANCE,
            priority=GoalPriority.HIGH if current_score < 0.5 else GoalPriority.MEDIUM,
            status=GoalStatus.PENDING,
            created_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=7),
            success_criteria=[
                f"성능 점수가 {target_score:.2f} 이상 달성",
                "CPU 사용률 최적화",
                "메모리 사용률 최적화"
            ],
            estimated_effort="medium"
        )
    
    def _should_create_learning_goal(self, assessment) -> bool:
        """학습 목표 생성 필요성 확인"""
        try:
            learning_score = assessment.category_scores.get(AssessmentCategory.LEARNING, 0.0)
            return learning_score < self.goal_setting_thresholds['learning_efficiency']
        except Exception:
            return False
    
    def _create_learning_goal(self, assessment) -> Goal:
        """학습 목표 생성"""
        current_score = assessment.category_scores.get(AssessmentCategory.LEARNING, 0.0)
        target_score = min(0.9, current_score + 0.25)  # 25% 개선 목표
        
        return Goal(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            title="학습 효율성 향상",
            description=f"현재 학습 점수 {current_score:.2f}에서 {target_score:.2f}로 개선",
            category=GoalCategory.LEARNING,
            priority=GoalPriority.HIGH,
            status=GoalStatus.PENDING,
            created_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=14),
            success_criteria=[
                f"학습 점수가 {target_score:.2f} 이상 달성",
                "메타 학습 활성화",
                "학습 경험 수집 증가"
            ],
            estimated_effort="high"
        )
    
    def _should_create_creativity_goal(self, assessment) -> bool:
        """창의성 목표 생성 필요성 확인"""
        try:
            creativity_score = assessment.category_scores.get(AssessmentCategory.CREATIVITY, 0.0)
            return creativity_score < self.goal_setting_thresholds['creativity_score']
        except Exception:
            return False
    
    def _create_creativity_goal(self, assessment) -> Goal:
        """창의성 목표 생성"""
        current_score = assessment.category_scores.get(AssessmentCategory.CREATIVITY, 0.0)
        target_score = min(0.8, current_score + 0.3)  # 30% 개선 목표
        
        return Goal(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            title="창의성 개발",
            description=f"현재 창의성 점수 {current_score:.2f}에서 {target_score:.2f}로 개선",
            category=GoalCategory.CREATIVITY,
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.PENDING,
            created_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=21),
            success_criteria=[
                f"창의성 점수가 {target_score:.2f} 이상 달성",
                "Dream Engine 성능 향상",
                "창의적 전략 수집 증가"
            ],
            estimated_effort="high"
        )
    
    def _should_create_stability_goal(self, assessment) -> bool:
        """안정성 목표 생성 필요성 확인"""
        try:
            stability_score = assessment.category_scores.get(AssessmentCategory.STABILITY, 0.0)
            return stability_score < self.goal_setting_thresholds['stability_score']
        except Exception:
            return False
    
    def _create_stability_goal(self, assessment) -> Goal:
        """안정성 목표 생성"""
        current_score = assessment.category_scores.get(AssessmentCategory.STABILITY, 0.0)
        target_score = min(0.95, current_score + 0.15)  # 15% 개선 목표
        
        return Goal(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            title="시스템 안정성 강화",
            description=f"현재 안정성 점수 {current_score:.2f}에서 {target_score:.2f}로 개선",
            category=GoalCategory.STABILITY,
            priority=GoalPriority.CRITICAL if current_score < 0.6 else GoalPriority.HIGH,
            status=GoalStatus.PENDING,
            created_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=5),
            success_criteria=[
                f"안정성 점수가 {target_score:.2f} 이상 달성",
                "오류율 감소",
                "시스템 가동률 향상"
            ],
            estimated_effort="medium"
        )
    
    def _should_create_innovation_goal(self, assessment) -> bool:
        """혁신 목표 생성 필요성 확인"""
        try:
            # 모든 카테고리가 높은 점수일 때 혁신 목표 생성
            category_scores = assessment.category_scores
            avg_score = sum(category_scores.values()) / len(category_scores) if category_scores else 0.0
            return avg_score > 0.8  # 평균 점수가 80% 이상일 때
        except Exception:
            return False
    
    def _create_innovation_goal(self, assessment) -> Goal:
        """혁신 목표 생성"""
        return Goal(
            goal_id=f"goal_{uuid.uuid4().hex[:8]}",
            title="시스템 혁신",
            description="새로운 기능 개발 및 시스템 진화",
            category=GoalCategory.INNOVATION,
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.PENDING,
            created_at=datetime.now(),
            target_completion_date=datetime.now() + timedelta(days=30),
            success_criteria=[
                "새로운 기능 구현",
                "시스템 진화 달성",
                "사용자 경험 개선"
            ],
            estimated_effort="high"
        )
    
    def create_execution_plan(self, goal: Goal) -> GoalExecutionPlan:
        """목표 실행 계획을 생성합니다."""
        try:
            steps = self._generate_goal_steps(goal)
            estimated_duration = self._estimate_duration(goal)
            required_resources = self._identify_required_resources(goal)
            risk_assessment = self._assess_risks(goal)
            success_metrics = goal.success_criteria
            
            plan = GoalExecutionPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                goal_id=goal.goal_id,
                steps=steps,
                estimated_duration=estimated_duration,
                required_resources=required_resources,
                risk_assessment=risk_assessment,
                success_metrics=success_metrics,
                created_at=datetime.now()
            )
            
            self.goal_execution_plans.append(plan)
            return plan
            
        except Exception as e:
            logger.error(f"실행 계획 생성 실패: {e}")
            return None
    
    def _generate_goal_steps(self, goal: Goal) -> List[Dict[str, Any]]:
        """목표 달성을 위한 단계를 생성합니다."""
        steps = []
        
        if goal.category == GoalCategory.PERFORMANCE:
            steps = [
                {"step": 1, "action": "성능 분석", "duration": "1일", "description": "현재 성능 병목 지점 식별"},
                {"step": 2, "action": "최적화 실행", "duration": "3일", "description": "성능 최적화 알고리즘 실행"},
                {"step": 3, "action": "결과 검증", "duration": "2일", "description": "성능 개선 효과 측정"},
                {"step": 4, "action": "안정화", "duration": "1일", "description": "최적화 결과 안정화"}
            ]
        elif goal.category == GoalCategory.LEARNING:
            steps = [
                {"step": 1, "action": "학습 전략 분석", "duration": "2일", "description": "현재 학습 전략 분석"},
                {"step": 2, "action": "전략 개선", "duration": "5일", "description": "학습 전략 개선 및 적용"},
                {"step": 3, "action": "메타 학습 활성화", "duration": "3일", "description": "메타 학습 시스템 강화"},
                {"step": 4, "action": "효과 측정", "duration": "4일", "description": "학습 효율성 개선 효과 측정"}
            ]
        elif goal.category == GoalCategory.CREATIVITY:
            steps = [
                {"step": 1, "action": "창의성 분석", "duration": "3일", "description": "현재 창의성 수준 분석"},
                {"step": 2, "action": "Dream Engine 강화", "duration": "7일", "description": "Dream Engine 성능 향상"},
                {"step": 3, "action": "창의적 전략 개발", "duration": "5일", "description": "새로운 창의적 전략 개발"},
                {"step": 4, "action": "검증 및 적용", "duration": "6일", "description": "창의적 전략 검증 및 적용"}
            ]
        elif goal.category == GoalCategory.STABILITY:
            steps = [
                {"step": 1, "action": "안정성 진단", "duration": "1일", "description": "시스템 안정성 진단"},
                {"step": 2, "action": "오류 패턴 분석", "duration": "2일", "description": "오류 발생 패턴 분석"},
                {"step": 3, "action": "안정성 개선", "duration": "2일", "description": "안정성 개선 조치 실행"}
            ]
        else:  # INNOVATION
            steps = [
                {"step": 1, "action": "혁신 영역 식별", "duration": "5일", "description": "혁신 가능한 영역 식별"},
                {"step": 2, "action": "새로운 기능 설계", "duration": "10일", "description": "새로운 기능 설계 및 개발"},
                {"step": 3, "action": "테스트 및 검증", "duration": "10일", "description": "새로운 기능 테스트 및 검증"},
                {"step": 4, "action": "배포 및 모니터링", "duration": "5일", "description": "새로운 기능 배포 및 모니터링"}
            ]
        
        return steps
    
    def _estimate_duration(self, goal: Goal) -> timedelta:
        """목표 달성 예상 기간을 추정합니다."""
        if goal.category == GoalCategory.PERFORMANCE:
            return timedelta(days=7)
        elif goal.category == GoalCategory.LEARNING:
            return timedelta(days=14)
        elif goal.category == GoalCategory.CREATIVITY:
            return timedelta(days=21)
        elif goal.category == GoalCategory.STABILITY:
            return timedelta(days=5)
        else:  # INNOVATION
            return timedelta(days=30)
    
    def _identify_required_resources(self, goal: Goal) -> List[str]:
        """목표 달성에 필요한 리소스를 식별합니다."""
        resources = ["시스템 리소스", "메모리", "CPU"]
        
        if goal.category == GoalCategory.LEARNING:
            resources.extend(["학습 데이터", "메타 학습 시스템"])
        elif goal.category == GoalCategory.CREATIVITY:
            resources.extend(["Dream Engine", "창의적 데이터"])
        elif goal.category == GoalCategory.STABILITY:
            resources.extend(["오류 로그", "모니터링 시스템"])
        elif goal.category == GoalCategory.INNOVATION:
            resources.extend(["개발 환경", "테스트 시스템"])
        
        return resources
    
    def _assess_risks(self, goal: Goal) -> Dict[str, Any]:
        """목표 달성의 위험 요소를 평가합니다."""
        risks = {
            "technical_risk": "medium",
            "resource_risk": "low",
            "time_risk": "medium",
            "quality_risk": "low"
        }
        
        if goal.priority == GoalPriority.CRITICAL:
            risks["time_risk"] = "high"
        elif goal.estimated_effort == "high":
            risks["resource_risk"] = "medium"
        
        return risks
    
    def execute_goal(self, goal: Goal) -> bool:
        """목표를 실행합니다."""
        try:
            logger.info(f"목표 실행 시작: {goal.title}")
            
            # 목표 상태를 진행 중으로 변경
            goal.status = GoalStatus.IN_PROGRESS
            
            # 실행 계획 생성
            plan = self.create_execution_plan(goal)
            if not plan:
                goal.status = GoalStatus.FAILED
                return False
            
            # 목표 실행 (실제로는 단계별 실행)
            success = self._execute_goal_steps(goal, plan)
            
            if success:
                goal.status = GoalStatus.COMPLETED
                goal.actual_completion_date = datetime.now()
                goal.progress_percentage = 100.0
                self.completed_goals.append(goal)
                logger.info(f"목표 완료: {goal.title}")
            else:
                goal.status = GoalStatus.FAILED
                logger.error(f"목표 실패: {goal.title}")
            
            return success
            
        except Exception as e:
            logger.error(f"목표 실행 실패: {e}")
            goal.status = GoalStatus.FAILED
            return False
    
    def _execute_goal_steps(self, goal: Goal, plan: GoalExecutionPlan) -> bool:
        """목표 실행 단계를 수행합니다."""
        try:
            # 실제 구현에서는 각 단계를 순차적으로 실행
            # 현재는 시뮬레이션으로 성공 가정
            for i, step in enumerate(plan.steps):
                logger.info(f"단계 {step['step']} 실행: {step['action']}")
                goal.progress_percentage = (i + 1) / len(plan.steps) * 100
                
                # 진행 상황 기록
                progress = GoalProgress(
                    progress_id=f"progress_{uuid.uuid4().hex[:8]}",
                    goal_id=goal.goal_id,
                    timestamp=datetime.now(),
                    progress_percentage=goal.progress_percentage,
                    completed_milestones=[step['action']],
                    remaining_tasks=[],
                    challenges_encountered=[],
                    solutions_applied=[],
                    next_steps=[]
                )
                self.goal_progress_history.append(progress)
                
                time.sleep(0.1)  # 시뮬레이션용 대기
            
            return True
            
        except Exception as e:
            logger.error(f"목표 단계 실행 실패: {e}")
            return False
    
    def get_goal_statistics(self) -> Dict[str, Any]:
        """목표 통계를 반환합니다."""
        try:
            total_goals = len(self.active_goals) + len(self.completed_goals)
            completed_goals = len(self.completed_goals)
            success_rate = completed_goals / total_goals if total_goals > 0 else 0.0
            
            # 카테고리별 통계
            category_stats = defaultdict(int)
            for goal in self.active_goals + self.completed_goals:
                category_stats[goal.category.value] += 1
            
            return {
                "total_goals": total_goals,
                "active_goals": len(self.active_goals),
                "completed_goals": completed_goals,
                "success_rate": success_rate,
                "category_distribution": dict(category_stats),
                "average_completion_time": self._calculate_average_completion_time()
            }
            
        except Exception as e:
            logger.error(f"목표 통계 계산 실패: {e}")
            return {}
    
    def _calculate_average_completion_time(self) -> float:
        """평균 완료 시간을 계산합니다."""
        try:
            completed_goals = [g for g in self.completed_goals if g.actual_completion_date]
            if not completed_goals:
                return 0.0
            
            total_days = sum([
                (g.actual_completion_date - g.created_at).days 
                for g in completed_goals
            ])
            
            return total_days / len(completed_goals)
            
        except Exception as e:
            logger.error(f"평균 완료 시간 계산 실패: {e}")
            return 0.0

    def _get_learning_loop_manager(self):
        """LearningLoopManager를 지연 초기화합니다."""
        if self.learning_loop_manager is None:
            try:
                from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
                self.learning_loop_manager = get_learning_loop_manager()
            except Exception as e:
                logger.warning(f"LearningLoopManager 초기화 실패: {e}")
                return None
        return self.learning_loop_manager

# 싱글톤 인스턴스
_goal_oriented_thinking = None

def get_goal_oriented_thinking() -> GoalOrientedThinking:
    """GoalOrientedThinking 싱글톤 인스턴스 반환"""
    global _goal_oriented_thinking
    if _goal_oriented_thinking is None:
        _goal_oriented_thinking = GoalOrientedThinking()
    return _goal_oriented_thinking 