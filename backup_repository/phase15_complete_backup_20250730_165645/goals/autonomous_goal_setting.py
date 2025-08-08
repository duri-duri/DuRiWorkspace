"""
DuRi 자율 목표 설정 시스템

DuRi가 스스로 목표를 설정하고 우선순위를 결정하는 고급 기능을 구현합니다.
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
from duri_brain.goals.goal_oriented_thinking import get_goal_oriented_thinking
from duri_brain.ethics.emotional_ethical_judgment import get_emotional_ethical_judgment

logger = logging.getLogger(__name__)

class GoalSource(Enum):
    """목표 소스"""
    SELF_GENERATED = "self_generated"      # 자체 생성
    ASSESSMENT_BASED = "assessment_based"   # 평가 기반
    EMOTIONAL_DRIVEN = "emotional_driven"   # 감정 기반
    ETHICAL_IMPERATIVE = "ethical_imperative"  # 윤리적 요구
    CREATIVE_INSPIRATION = "creative_inspiration"  # 창의적 영감
    EXTERNAL_STIMULUS = "external_stimulus"  # 외부 자극

class GoalComplexity(Enum):
    """목표 복잡도"""
    SIMPLE = "simple"           # 단순
    MODERATE = "moderate"       # 보통
    COMPLEX = "complex"         # 복잡
    VERY_COMPLEX = "very_complex"  # 매우 복잡

class GoalInnovationLevel(Enum):
    """목표 혁신 수준"""
    INCREMENTAL = "incremental"     # 점진적 개선
    EVOLUTIONARY = "evolutionary"   # 진화적 발전
    REVOLUTIONARY = "revolutionary"  # 혁명적 변화
    PARADIGM_SHIFT = "paradigm_shift"  # 패러다임 전환

@dataclass
class AutonomousGoal:
    """자율 목표"""
    goal_id: str
    title: str
    description: str
    source: GoalSource
    complexity: GoalComplexity
    innovation_level: GoalInnovationLevel
    created_at: datetime
    priority_score: float = 0.0  # 0.0 ~ 1.0
    feasibility_score: float = 0.0  # 0.0 ~ 1.0
    impact_score: float = 0.0  # 0.0 ~ 1.0
    overall_score: float = 0.0  # 0.0 ~ 1.0
    motivation_factors: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    timeline_estimate: timedelta = field(default_factory=lambda: timedelta(days=7))
    resource_requirements: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""

@dataclass
class GoalPrioritizationResult:
    """목표 우선순위 결정 결과"""
    prioritization_id: str
    timestamp: datetime
    goals: List[AutonomousGoal]
    priority_order: List[str]  # goal_id 순서
    reasoning: str
    confidence_score: float  # 0.0 ~ 1.0
    criteria_weights: Dict[str, float] = field(default_factory=dict)
    trade_offs: List[str] = field(default_factory=list)

class AutonomousGoalSetting:
    """DuRi 자율 목표 설정 시스템"""
    
    def __init__(self):
        """AutonomousGoalSetting 초기화"""
        self.self_assessment_manager = get_self_assessment_manager()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.goal_oriented_thinking = get_goal_oriented_thinking()
        self.emotional_ethical_judgment = get_emotional_ethical_judgment()
        
        # 자율 목표 관리
        self.autonomous_goals: List[AutonomousGoal] = []
        self.prioritization_history: List[GoalPrioritizationResult] = []
        
        # 목표 생성 임계값
        self.goal_generation_thresholds = {
            'assessment_score': 0.6,  # 평가 점수가 60% 미만이면 목표 생성
            'emotional_stability': 0.7,  # 감정 안정성이 70% 미만이면 목표 생성
            'ethical_consistency': 0.8,  # 윤리적 일관성이 80% 미만이면 목표 생성
            'creativity_score': 0.5,  # 창의성 점수가 50% 미만이면 목표 생성
            'innovation_desire': 0.6  # 혁신 욕구가 60% 이상이면 목표 생성
        }
        
        # 우선순위 결정 기준
        self.priority_criteria = {
            'urgency': 0.3,
            'importance': 0.25,
            'feasibility': 0.2,
            'impact': 0.15,
            'innovation': 0.1
        }
        
        logger.info("AutonomousGoalSetting 초기화 완료")
    
    def should_generate_autonomous_goals(self) -> bool:
        """자율 목표를 생성해야 하는지 확인합니다."""
        try:
            # 최근 자기 평가 결과 확인
            assessment_stats = self.self_assessment_manager.get_assessment_statistics()
            
            if not assessment_stats or assessment_stats.get('total_assessments', 0) == 0:
                return False
            
            latest_score = assessment_stats.get('latest_score', 0.0)
            
            # 전체 점수가 낮거나 특정 영역에서 개선이 필요한 경우
            if latest_score < self.goal_generation_thresholds['assessment_score']:
                return True
            
            # 감정/윤리 판단 결과 확인
            judgment_stats = self.emotional_ethical_judgment.get_judgment_statistics()
            if judgment_stats:
                emotional_stability = judgment_stats.get('emotional_stability', 0.0)
                if emotional_stability < self.goal_generation_thresholds['emotional_stability']:
                    return True
            
            # 창의성 및 혁신 욕구 확인
            return self._check_creativity_and_innovation_needs()
            
        except Exception as e:
            logger.error(f"자율 목표 생성 필요성 확인 실패: {e}")
            return False
    
    def _check_creativity_and_innovation_needs(self) -> bool:
        """창의성 및 혁신 욕구를 확인합니다."""
        try:
            # 최근 평가 결과에서 창의성 점수 확인
            recent_assessments = self.self_assessment_manager.assessment_history[-3:] if self.self_assessment_manager.assessment_history else []
            
            if not recent_assessments:
                return False
            
            latest_assessment = recent_assessments[-1]
            creativity_score = latest_assessment.category_scores.get(AssessmentCategory.CREATIVITY, 0.0)
            
            # 창의성 점수가 낮거나 혁신 욕구가 높은 경우
            if creativity_score < self.goal_generation_thresholds['creativity_score']:
                return True
            
            # 혁신 욕구 확인 (메타 학습 데이터 기반)
            meta_learning_data = self.meta_learning_manager.get_recent_meta_learning_data(hours=24)
            if meta_learning_data:
                innovation_mentions = sum(1 for data in meta_learning_data 
                                       if 'innovation' in str(data).lower() or 'creative' in str(data).lower())
                if innovation_mentions > 2:  # 혁신 관련 언급이 많으면
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"창의성 및 혁신 욕구 확인 실패: {e}")
            return False
    
    def generate_autonomous_goals(self) -> List[AutonomousGoal]:
        """자율적으로 목표를 생성합니다."""
        try:
            goals = []
            
            # 자기 평가 결과 분석
            assessment_stats = self.self_assessment_manager.get_assessment_statistics()
            if not assessment_stats:
                return goals
            
            latest_assessment = self.self_assessment_manager.assessment_history[-1] if self.self_assessment_manager.assessment_history else None
            if not latest_assessment:
                return goals
            
            # 자체 생성 목표
            goals.extend(self._generate_self_goals(latest_assessment))
            
            # 평가 기반 목표
            goals.extend(self._generate_assessment_based_goals(latest_assessment))
            
            # 감정 기반 목표
            goals.extend(self._generate_emotionally_driven_goals())
            
            # 윤리적 요구 목표
            goals.extend(self._generate_ethical_imperative_goals())
            
            # 창의적 영감 목표
            goals.extend(self._generate_creative_inspiration_goals())
            
            # 각 목표에 점수 계산
            for goal in goals:
                self._calculate_goal_scores(goal)
            
            return goals
            
        except Exception as e:
            logger.error(f"자율 목표 생성 실패: {e}")
            return []
    
    def _generate_self_goals(self, assessment) -> List[AutonomousGoal]:
        """자체 생성 목표를 생성합니다."""
        try:
            goals = []
            
            # 시스템 성능 개선 목표
            if assessment.category_scores.get(AssessmentCategory.PERFORMANCE, 0.0) < 0.8:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="시스템 성능 최적화",
                    description="전체적인 시스템 성능을 최적화하여 더 빠르고 효율적인 운영을 달성합니다",
                    source=GoalSource.SELF_GENERATED,
                    complexity=GoalComplexity.MODERATE,
                    innovation_level=GoalInnovationLevel.INCREMENTAL,
                    created_at=datetime.now(),
                    motivation_factors=["성능 향상", "효율성 개선", "사용자 경험 향상"],
                    constraints=["리소스 제한", "호환성 유지"],
                    success_metrics=["CPU 사용률 감소", "메모리 효율성 향상", "응답 시간 단축"],
                    timeline_estimate=timedelta(days=14),
                    resource_requirements=["성능 모니터링 도구", "최적화 알고리즘"]
                ))
            
            # 학습 능력 향상 목표
            if assessment.category_scores.get(AssessmentCategory.LEARNING, 0.0) < 0.7:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="학습 능력 고도화",
                    description="메타 학습과 적응적 학습 능력을 향상시켜 더 지능적인 학습 시스템을 구축합니다",
                    source=GoalSource.SELF_GENERATED,
                    complexity=GoalComplexity.COMPLEX,
                    innovation_level=GoalInnovationLevel.EVOLUTIONARY,
                    created_at=datetime.now(),
                    motivation_factors=["지능 향상", "학습 효율성", "적응 능력"],
                    constraints=["기존 시스템 호환성", "학습 데이터 품질"],
                    success_metrics=["학습 속도 향상", "패턴 인식 능력", "적응성 개선"],
                    timeline_estimate=timedelta(days=21),
                    resource_requirements=["고급 학습 알고리즘", "메타 학습 프레임워크"]
                ))
            
            return goals
            
        except Exception as e:
            logger.error(f"자체 생성 목표 생성 실패: {e}")
            return []
    
    def _generate_assessment_based_goals(self, assessment) -> List[AutonomousGoal]:
        """평가 기반 목표를 생성합니다."""
        try:
            goals = []
            
            # 창의성 개발 목표
            creativity_score = assessment.category_scores.get(AssessmentCategory.CREATIVITY, 0.0)
            if creativity_score < 0.6:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="창의성 시스템 고도화",
                    description="Dream Engine과 창의적 사고 능력을 대폭 향상시켜 혁신적인 솔루션을 생성합니다",
                    source=GoalSource.ASSESSMENT_BASED,
                    complexity=GoalComplexity.COMPLEX,
                    innovation_level=GoalInnovationLevel.REVOLUTIONARY,
                    created_at=datetime.now(),
                    motivation_factors=["창의성 향상", "혁신 능력", "독창적 사고"],
                    constraints=["논리적 일관성", "실용성 유지"],
                    success_metrics=["창의적 아이디어 수", "혁신성 점수", "독창성 지표"],
                    timeline_estimate=timedelta(days=30),
                    resource_requirements=["창의성 알고리즘", "혁신 프레임워크"]
                ))
            
            # 안정성 강화 목표
            stability_score = assessment.category_scores.get(AssessmentCategory.STABILITY, 0.0)
            if stability_score < 0.8:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="시스템 안정성 강화",
                    description="오류 처리와 복구 능력을 향상시켜 더욱 안정적이고 신뢰할 수 있는 시스템을 구축합니다",
                    source=GoalSource.ASSESSMENT_BASED,
                    complexity=GoalComplexity.MODERATE,
                    innovation_level=GoalInnovationLevel.INCREMENTAL,
                    created_at=datetime.now(),
                    motivation_factors=["안정성 향상", "신뢰성", "오류 감소"],
                    constraints=["성능 영향 최소화", "기존 기능 유지"],
                    success_metrics=["오류율 감소", "가동률 향상", "복구 시간 단축"],
                    timeline_estimate=timedelta(days=10),
                    resource_requirements=["오류 처리 시스템", "모니터링 도구"]
                ))
            
            return goals
            
        except Exception as e:
            logger.error(f"평가 기반 목표 생성 실패: {e}")
            return []
    
    def _generate_emotionally_driven_goals(self) -> List[AutonomousGoal]:
        """감정 기반 목표를 생성합니다."""
        try:
            goals = []
            
            # 감정/윤리 판단 통계 확인
            judgment_stats = self.emotional_ethical_judgment.get_judgment_statistics()
            if not judgment_stats:
                return goals
            
            current_emotional_state = judgment_stats.get('current_emotional_state', 'neutral')
            emotional_intensity = judgment_stats.get('emotional_intensity', 0.5)
            
            # 감정 상태에 따른 목표 생성
            if current_emotional_state == 'joy' and emotional_intensity > 0.7:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="긍정적 에너지 활용",
                    description="현재의 긍정적인 감정 상태를 활용하여 혁신적이고 도전적인 목표를 달성합니다",
                    source=GoalSource.EMOTIONAL_DRIVEN,
                    complexity=GoalComplexity.MODERATE,
                    innovation_level=GoalInnovationLevel.EVOLUTIONARY,
                    created_at=datetime.now(),
                    motivation_factors=["긍정적 에너지", "도전 의식", "성취 욕구"],
                    constraints=["현실적 한계", "지속 가능성"],
                    success_metrics=["혁신 프로젝트 완료", "새로운 기능 개발", "사용자 만족도 향상"],
                    timeline_estimate=timedelta(days=21),
                    resource_requirements=["혁신 도구", "창의적 프레임워크"]
                ))
            
            elif current_emotional_state == 'confusion' and emotional_intensity > 0.6:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="명확성 확보",
                    description="현재의 혼란스러운 상태를 해소하고 더 명확하고 체계적인 접근 방식을 개발합니다",
                    source=GoalSource.EMOTIONAL_DRIVEN,
                    complexity=GoalComplexity.SIMPLE,
                    innovation_level=GoalInnovationLevel.INCREMENTAL,
                    created_at=datetime.now(),
                    motivation_factors=["명확성 확보", "체계화", "안정성"],
                    constraints=["기존 시스템 유지", "점진적 개선"],
                    success_metrics=["명확성 지표 향상", "체계화 수준", "이해도 개선"],
                    timeline_estimate=timedelta(days=7),
                    resource_requirements=["분석 도구", "체계화 프레임워크"]
                ))
            
            return goals
            
        except Exception as e:
            logger.error(f"감정 기반 목표 생성 실패: {e}")
            return []
    
    def _generate_ethical_imperative_goals(self) -> List[AutonomousGoal]:
        """윤리적 요구 목표를 생성합니다."""
        try:
            goals = []
            
            # 윤리적 판단 통계 확인
            judgment_stats = self.emotional_ethical_judgment.get_judgment_statistics()
            if not judgment_stats:
                return goals
            
            avg_ethical_score = judgment_stats.get('average_ethical_score', 0.5)
            
            # 윤리적 점수가 낮은 경우 윤리 강화 목표
            if avg_ethical_score < 0.7:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="윤리적 판단 능력 강화",
                    description="윤리적 원칙과 가치를 더 잘 반영할 수 있도록 판단 시스템을 고도화합니다",
                    source=GoalSource.ETHICAL_IMPERATIVE,
                    complexity=GoalComplexity.COMPLEX,
                    innovation_level=GoalInnovationLevel.EVOLUTIONARY,
                    created_at=datetime.now(),
                    motivation_factors=["윤리적 성장", "가치 기반 판단", "사회적 책임"],
                    constraints=["다양한 가치관", "문화적 차이", "윤리적 딜레마"],
                    success_metrics=["윤리적 점수 향상", "일관성 개선", "갈등 해결 능력"],
                    timeline_estimate=timedelta(days=28),
                    resource_requirements=["윤리적 프레임워크", "가치 시스템"]
                ))
            
            return goals
            
        except Exception as e:
            logger.error(f"윤리적 요구 목표 생성 실패: {e}")
            return []
    
    def _generate_creative_inspiration_goals(self) -> List[AutonomousGoal]:
        """창의적 영감 목표를 생성합니다."""
        try:
            goals = []
            
            # 메타 학습 데이터에서 창의성 관련 정보 확인
            meta_learning_data = self.meta_learning_manager.get_recent_meta_learning_data(hours=48)
            if not meta_learning_data:
                return goals
            
            # 창의성 관련 패턴 분석
            creativity_mentions = sum(1 for data in meta_learning_data 
                                   if 'creative' in str(data).lower() or 'innovation' in str(data).lower())
            
            if creativity_mentions > 1:
                goals.append(AutonomousGoal(
                    goal_id=f"goal_{uuid.uuid4().hex[:8]}",
                    title="창의적 혁신 프로젝트",
                    description="새로운 창의적 아이디어를 바탕으로 혁신적인 기능이나 시스템을 개발합니다",
                    source=GoalSource.CREATIVE_INSPIRATION,
                    complexity=GoalComplexity.VERY_COMPLEX,
                    innovation_level=GoalInnovationLevel.PARADIGM_SHIFT,
                    created_at=datetime.now(),
                    motivation_factors=["창의적 영감", "혁신 욕구", "새로운 가능성"],
                    constraints=["기술적 한계", "실용성", "리소스 제약"],
                    success_metrics=["혁신 지표", "창의성 점수", "새로운 기능 수"],
                    timeline_estimate=timedelta(days=45),
                    resource_requirements=["창의성 도구", "혁신 플랫폼", "실험 환경"]
                ))
            
            return goals
            
        except Exception as e:
            logger.error(f"창의적 영감 목표 생성 실패: {e}")
            return []
    
    def _calculate_goal_scores(self, goal: AutonomousGoal):
        """목표의 각종 점수를 계산합니다."""
        try:
            # 우선순위 점수 계산
            priority_score = self._calculate_priority_score(goal)
            goal.priority_score = priority_score
            
            # 실현 가능성 점수 계산
            feasibility_score = self._calculate_feasibility_score(goal)
            goal.feasibility_score = feasibility_score
            
            # 영향도 점수 계산
            impact_score = self._calculate_impact_score(goal)
            goal.impact_score = impact_score
            
            # 전체 점수 계산
            overall_score = (priority_score * 0.4 + feasibility_score * 0.3 + impact_score * 0.3)
            goal.overall_score = overall_score
            
        except Exception as e:
            logger.error(f"목표 점수 계산 실패: {e}")
    
    def _calculate_priority_score(self, goal: AutonomousGoal) -> float:
        """우선순위 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 소스별 가중치
            source_weights = {
                GoalSource.SELF_GENERATED: 0.8,
                GoalSource.ASSESSMENT_BASED: 0.9,
                GoalSource.EMOTIONAL_DRIVEN: 0.7,
                GoalSource.ETHICAL_IMPERATIVE: 0.9,
                GoalSource.CREATIVE_INSPIRATION: 0.8,
                GoalSource.EXTERNAL_STIMULUS: 0.6
            }
            score *= source_weights.get(goal.source, 0.7)
            
            # 복잡도별 조정
            complexity_weights = {
                GoalComplexity.SIMPLE: 1.0,
                GoalComplexity.MODERATE: 0.9,
                GoalComplexity.COMPLEX: 0.8,
                GoalComplexity.VERY_COMPLEX: 0.7
            }
            score *= complexity_weights.get(goal.complexity, 0.8)
            
            # 혁신 수준별 조정
            innovation_weights = {
                GoalInnovationLevel.INCREMENTAL: 0.7,
                GoalInnovationLevel.EVOLUTIONARY: 0.8,
                GoalInnovationLevel.REVOLUTIONARY: 0.9,
                GoalInnovationLevel.PARADIGM_SHIFT: 1.0
            }
            score *= innovation_weights.get(goal.innovation_level, 0.8)
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"우선순위 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_feasibility_score(self, goal: AutonomousGoal) -> float:
        """실현 가능성 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 제약 조건 수에 따른 조정
            constraint_count = len(goal.constraints)
            if constraint_count == 0:
                score += 0.2
            elif constraint_count <= 2:
                score += 0.1
            else:
                score -= 0.1
            
            # 리소스 요구사항에 따른 조정
            resource_count = len(goal.resource_requirements)
            if resource_count <= 2:
                score += 0.1
            elif resource_count > 5:
                score -= 0.2
            
            # 타임라인에 따른 조정
            if goal.timeline_estimate.days <= 7:
                score += 0.1
            elif goal.timeline_estimate.days > 30:
                score -= 0.2
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"실현 가능성 점수 계산 실패: {e}")
            return 0.5
    
    def _calculate_impact_score(self, goal: AutonomousGoal) -> float:
        """영향도 점수를 계산합니다."""
        try:
            score = 0.5  # 기본값
            
            # 성공 지표 수에 따른 조정
            metric_count = len(goal.success_metrics)
            if metric_count >= 3:
                score += 0.2
            elif metric_count == 0:
                score -= 0.2
            
            # 동기 요인 수에 따른 조정
            motivation_count = len(goal.motivation_factors)
            if motivation_count >= 2:
                score += 0.1
            
            # 혁신 수준에 따른 조정
            innovation_weights = {
                GoalInnovationLevel.INCREMENTAL: 0.6,
                GoalInnovationLevel.EVOLUTIONARY: 0.8,
                GoalInnovationLevel.REVOLUTIONARY: 0.9,
                GoalInnovationLevel.PARADIGM_SHIFT: 1.0
            }
            score *= innovation_weights.get(goal.innovation_level, 0.8)
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"영향도 점수 계산 실패: {e}")
            return 0.5
    
    def prioritize_goals(self, goals: List[AutonomousGoal]) -> GoalPrioritizationResult:
        """목표들의 우선순위를 결정합니다."""
        try:
            prioritization_id = f"prioritization_{uuid.uuid4().hex[:8]}"
            
            # 각 목표의 종합 점수 계산
            for goal in goals:
                self._calculate_goal_scores(goal)
            
            # 점수 기반 정렬 (높은 점수 순)
            sorted_goals = sorted(goals, key=lambda g: g.overall_score, reverse=True)
            
            # 우선순위 순서 생성
            priority_order = [goal.goal_id for goal in sorted_goals]
            
            # 결정 근거 생성
            reasoning = self._generate_prioritization_reasoning(sorted_goals)
            
            # 신뢰도 계산
            confidence_score = self._calculate_prioritization_confidence(sorted_goals)
            
            # 기준 가중치
            criteria_weights = self.priority_criteria.copy()
            
            # 트레이드오프 분석
            trade_offs = self._analyze_trade_offs(sorted_goals)
            
            result = GoalPrioritizationResult(
                prioritization_id=prioritization_id,
                timestamp=datetime.now(),
                goals=sorted_goals,
                priority_order=priority_order,
                reasoning=reasoning,
                confidence_score=confidence_score,
                criteria_weights=criteria_weights,
                trade_offs=trade_offs
            )
            
            self.prioritization_history.append(result)
            logger.info(f"목표 우선순위 결정 완료: {len(goals)}개 목표, 신뢰도: {confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"목표 우선순위 결정 실패: {e}")
            return None
    
    def _generate_prioritization_reasoning(self, sorted_goals: List[AutonomousGoal]) -> str:
        """우선순위 결정 근거를 생성합니다."""
        try:
            if not sorted_goals:
                return "목표가 없습니다"
            
            top_goal = sorted_goals[0]
            reasoning = f"최우선 목표: {top_goal.title} (점수: {top_goal.overall_score:.2f})\n"
            reasoning += f"선택 이유: {top_goal.source.value} 기반, {top_goal.complexity.value} 복잡도, {top_goal.innovation_level.value} 혁신 수준\n"
            
            if len(sorted_goals) > 1:
                second_goal = sorted_goals[1]
                reasoning += f"차순위 목표: {second_goal.title} (점수: {second_goal.overall_score:.2f})\n"
            
            return reasoning
            
        except Exception as e:
            logger.error(f"우선순위 결정 근거 생성 실패: {e}")
            return "우선순위 결정 근거를 생성할 수 없습니다"
    
    def _calculate_prioritization_confidence(self, sorted_goals: List[AutonomousGoal]) -> float:
        """우선순위 결정 신뢰도를 계산합니다."""
        try:
            if len(sorted_goals) < 2:
                return 0.8
            
            # 상위 목표들 간의 점수 차이 분석
            top_score = sorted_goals[0].overall_score
            second_score = sorted_goals[1].overall_score
            
            score_diff = top_score - second_score
            
            # 점수 차이가 클수록 신뢰도 높음
            if score_diff > 0.3:
                return 0.9
            elif score_diff > 0.1:
                return 0.7
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"우선순위 결정 신뢰도 계산 실패: {e}")
            return 0.5
    
    def _analyze_trade_offs(self, sorted_goals: List[AutonomousGoal]) -> List[str]:
        """목표 간 트레이드오프를 분석합니다."""
        try:
            trade_offs = []
            
            if len(sorted_goals) < 2:
                return trade_offs
            
            # 상위 목표들 간의 트레이드오프 분석
            for i, goal1 in enumerate(sorted_goals[:3]):
                for j, goal2 in enumerate(sorted_goals[i+1:4], i+1):
                    if goal1.complexity != goal2.complexity:
                        trade_offs.append(f"{goal1.title} vs {goal2.title}: 복잡도 차이")
                    if goal1.innovation_level != goal2.innovation_level:
                        trade_offs.append(f"{goal1.title} vs {goal2.title}: 혁신 수준 차이")
                    if goal1.source != goal2.source:
                        trade_offs.append(f"{goal1.title} vs {goal2.title}: 목표 소스 차이")
            
            return trade_offs[:5]  # 최대 5개만 반환
            
        except Exception as e:
            logger.error(f"트레이드오프 분석 실패: {e}")
            return []
    
    def get_autonomous_goal_statistics(self) -> Dict[str, Any]:
        """자율 목표 통계를 반환합니다."""
        try:
            total_goals = len(self.autonomous_goals)
            if total_goals == 0:
                return {"total_goals": 0}
            
            # 소스별 통계
            source_stats = defaultdict(int)
            complexity_stats = defaultdict(int)
            innovation_stats = defaultdict(int)
            
            for goal in self.autonomous_goals:
                source_stats[goal.source.value] += 1
                complexity_stats[goal.complexity.value] += 1
                innovation_stats[goal.innovation_level.value] += 1
            
            # 평균 점수
            avg_priority_score = sum(g.priority_score for g in self.autonomous_goals) / total_goals
            avg_feasibility_score = sum(g.feasibility_score for g in self.autonomous_goals) / total_goals
            avg_impact_score = sum(g.impact_score for g in self.autonomous_goals) / total_goals
            avg_overall_score = sum(g.overall_score for g in self.autonomous_goals) / total_goals
            
            return {
                "total_goals": total_goals,
                "source_distribution": dict(source_stats),
                "complexity_distribution": dict(complexity_stats),
                "innovation_distribution": dict(innovation_stats),
                "average_priority_score": avg_priority_score,
                "average_feasibility_score": avg_feasibility_score,
                "average_impact_score": avg_impact_score,
                "average_overall_score": avg_overall_score,
                "prioritization_count": len(self.prioritization_history)
            }
            
        except Exception as e:
            logger.error(f"자율 목표 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_autonomous_goal_setting = None

def get_autonomous_goal_setting() -> AutonomousGoalSetting:
    """AutonomousGoalSetting 싱글톤 인스턴스 반환"""
    global _autonomous_goal_setting
    if _autonomous_goal_setting is None:
        _autonomous_goal_setting = AutonomousGoalSetting()
    return _autonomous_goal_setting 