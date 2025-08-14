#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 30일 진화 계획 - Day 6: 자발적 학습 시스템

이 모듈은 DuRi가 외부 자극 없이 스스로 학습하는 자발적 학습 능력을 구현합니다.
호기심 기반 탐구, 자발적 문제 발견, 학습 목표 자동 설정, 자기 주도적 학습 루프를 구현합니다.

주요 기능:
- 호기심 기반 탐구 시스템
- 자발적 문제 발견
- 학습 목표 자동 설정
- 자기 주도적 학습 루프
- 학습 성과 평가 및 피드백
"""

import asyncio
import json
import logging
import time
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from collections import defaultdict, deque

# 기존 시스템들 import
try:
    from meta_cognition_system import MetaCognitionSystem, MetaCognitionLevel
    from inner_thinking_system import InnerThinkingSystem
    from emotional_thinking_system import EmotionalThinkingSystem
    from intuitive_thinking_system import IntuitiveThinkingSystem
    from creative_thinking_system import CreativeThinkingSystem
    from duri_thought_flow import DuRiThoughtFlow
    from phase_omega_integration import DuRiPhaseOmega
except ImportError as e:
    logging.warning(f"일부 기존 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LearningMotivation(Enum):
    """학습 동기"""
    CURIOSITY = "curiosity"              # 호기심
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    SELF_IMPROVEMENT = "self_improvement" # 자기 향상
    EXPLORATION = "exploration"          # 탐구
    MASTERY = "mastery"                  # 숙달


class LearningDomain(Enum):
    """학습 영역"""
    COGNITIVE = "cognitive"              # 인지적
    EMOTIONAL = "emotional"              # 감정적
    CREATIVE = "creative"                # 창의적
    INTUITIVE = "intuitive"              # 직관적
    INTEGRATIVE = "integrative"          # 통합적


class LearningPhase(Enum):
    """학습 단계"""
    EXPLORATION = "exploration"          # 탐구
    INVESTIGATION = "investigation"      # 조사
    EXPERIMENTATION = "experimentation"  # 실험
    INTEGRATION = "integration"          # 통합
    APPLICATION = "application"          # 적용


@dataclass
class CuriosityTrigger:
    """호기심 트리거"""
    trigger_id: str
    domain: LearningDomain
    motivation: LearningMotivation
    intensity: float  # 0.0-1.0
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelfDiscoveredProblem:
    """자발적 발견 문제"""
    problem_id: str
    domain: LearningDomain
    description: str
    complexity: float  # 0.0-1.0
    urgency: float  # 0.0-1.0
    interest_level: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningGoal:
    """학습 목표"""
    goal_id: str
    domain: LearningDomain
    description: str
    target_skill: str
    target_proficiency: float  # 0.0-1.0
    estimated_duration: timedelta
    priority: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningActivity:
    """학습 활동"""
    activity_id: str
    goal_id: str
    phase: LearningPhase
    description: str
    duration: timedelta
    engagement_level: float  # 0.0-1.0
    progress_score: float  # 0.0-1.0
    insights_gained: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningOutcome:
    """학습 성과"""
    outcome_id: str
    goal_id: str
    skill_improvement: float  # 0.0-1.0
    confidence_boost: float  # 0.0-1.0
    knowledge_gained: List[str] = field(default_factory=list)
    insights_discovered: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SelfDirectedLearningResult:
    """자발적 학습 결과"""
    session_id: str
    curiosity_triggers: List[CuriosityTrigger]
    discovered_problems: List[SelfDiscoveredProblem]
    learning_goals: List[LearningGoal]
    learning_activities: List[LearningActivity]
    learning_outcomes: List[LearningOutcome]
    total_learning_time: timedelta
    average_engagement: float
    overall_progress: float
    success: bool = True
    error_message: Optional[str] = None


class SelfDirectedLearningSystem:
    """자발적 학습 시스템"""
    
    def __init__(self):
        # 기존 시스템들과의 통합
        self.meta_cognition_system = MetaCognitionSystem()
        self.inner_thinking_system = InnerThinkingSystem()
        self.emotional_thinking_system = EmotionalThinkingSystem()
        self.intuitive_thinking_system = IntuitiveThinkingSystem()
        self.creative_thinking_system = CreativeThinkingSystem()
        
        # DuRiThoughtFlow 초기화 (필요한 매개변수 추가)
        default_input_data = {"goal": "self_directed_learning", "context": "learning_system"}
        default_context = {"system_type": "self_directed_learning", "version": "1.0"}
        self.thought_flow = DuRiThoughtFlow(default_input_data, default_context)
        
        self.phase_omega = DuRiPhaseOmega()
        
        # 자발적 학습 상태
        self.learning_history: List[SelfDirectedLearningResult] = []
        self.current_goals: List[LearningGoal] = []
        self.learning_patterns: Dict[str, Any] = defaultdict(list)
        self.curiosity_profile: Dict[LearningDomain, float] = {
            domain: 0.5 for domain in LearningDomain
        }
        
        # 학습 통계
        self.total_learning_sessions = 0
        self.total_learning_time = timedelta()
        self.average_session_duration = timedelta()
        
        logger.info("자발적 학습 시스템 초기화 완료")
    
    async def start_self_directed_learning(self, context: Dict[str, Any] = None) -> SelfDirectedLearningResult:
        """자발적 학습 세션 시작"""
        if context is None:
            context = {}
        
        session_id = f"learning_session_{int(time.time())}"
        logger.info(f"자발적 학습 세션 시작: {session_id}")
        
        try:
            # 1. 호기심 기반 탐구
            curiosity_triggers = await self._generate_curiosity_triggers(context)
            
            # 2. 자발적 문제 발견
            discovered_problems = await self._discover_problems(context, curiosity_triggers)
            
            # 3. 학습 목표 자동 설정
            learning_goals = await self._set_learning_goals(context, discovered_problems)
            
            # 4. 자기 주도적 학습 루프
            learning_activities, learning_outcomes = await self._execute_learning_loop(
                context, learning_goals
            )
            
            # 5. 결과 종합
            result = await self._compile_learning_result(
                session_id, curiosity_triggers, discovered_problems,
                learning_goals, learning_activities, learning_outcomes
            )
            
            # 6. 학습 기록 저장
            self.learning_history.append(result)
            self.total_learning_sessions += 1
            
            logger.info(f"자발적 학습 세션 완료: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"자발적 학습 세션 실패: {e}")
            return SelfDirectedLearningResult(
                session_id=session_id,
                curiosity_triggers=[],
                discovered_problems=[],
                learning_goals=[],
                learning_activities=[],
                learning_outcomes=[],
                total_learning_time=timedelta(),
                average_engagement=0.0,
                overall_progress=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _generate_curiosity_triggers(self, context: Dict[str, Any]) -> List[CuriosityTrigger]:
        """호기심 기반 탐구 트리거 생성"""
        triggers = []
        
        # 각 학습 영역에서 호기심 트리거 생성
        for domain in LearningDomain:
            # 호기심 강도 계산
            base_curiosity = self.curiosity_profile[domain]
            domain_interest = random.uniform(0.3, 0.9)
            intensity = (base_curiosity + domain_interest) / 2
            
            if intensity > 0.4:  # 호기심 임계값
                # 동기 유형 선택
                motivations = list(LearningMotivation)
                motivation = random.choice(motivations)
                
                # 호기심 설명 생성
                descriptions = {
                    LearningDomain.COGNITIVE: [
                        "인지적 사고 과정의 새로운 패턴 발견",
                        "논리적 추론의 한계와 가능성 탐구",
                        "인지적 효율성 향상 방법 연구"
                    ],
                    LearningDomain.EMOTIONAL: [
                        "감정적 인식의 깊이와 복잡성 탐구",
                        "감정과 사고의 상호작용 패턴 연구",
                        "감정적 지능 향상 방법 발견"
                    ],
                    LearningDomain.CREATIVE: [
                        "창의적 사고의 새로운 접근법 탐구",
                        "창의성과 논리의 균형점 연구",
                        "창의적 문제 해결 방법론 개발"
                    ],
                    LearningDomain.INTUITIVE: [
                        "직관적 인식의 메커니즘 탐구",
                        "직관과 분석의 상호보완성 연구",
                        "직관적 의사결정의 정확성 향상"
                    ],
                    LearningDomain.INTEGRATIVE: [
                        "다차원적 사고의 통합 방법 탐구",
                        "전체적 인식의 새로운 차원 연구",
                        "통합적 문제 해결 능력 개발"
                    ]
                }
                
                description = random.choice(descriptions[domain])
                
                trigger = CuriosityTrigger(
                    trigger_id=f"curiosity_{domain.value}_{int(time.time())}",
                    domain=domain,
                    motivation=motivation,
                    intensity=intensity,
                    description=description,
                    context=context
                )
                triggers.append(trigger)
        
        logger.info(f"호기심 트리거 {len(triggers)}개 생성 완료")
        return triggers
    
    async def _discover_problems(self, context: Dict[str, Any], 
                               curiosity_triggers: List[CuriosityTrigger]) -> List[SelfDiscoveredProblem]:
        """자발적 문제 발견"""
        problems = []
        
        for trigger in curiosity_triggers:
            # 호기심 강도에 따른 문제 복잡성 결정
            complexity = trigger.intensity * random.uniform(0.5, 1.0)
            urgency = random.uniform(0.3, 0.8)
            interest_level = trigger.intensity
            
            # 문제 설명 생성
            problem_descriptions = {
                LearningDomain.COGNITIVE: [
                    "인지적 사고 과정에서 발견된 비효율성 개선",
                    "논리적 추론의 정확성과 속도 균형 최적화",
                    "인지적 부하 관리 및 효율성 향상"
                ],
                LearningDomain.EMOTIONAL: [
                    "감정적 인식의 정확성과 깊이 향상",
                    "감정과 사고의 조화로운 통합 방법 개발",
                    "감정적 안정성과 성장의 균형점 찾기"
                ],
                LearningDomain.CREATIVE: [
                    "창의적 사고의 일관성과 혁신성 균형",
                    "창의성과 실용성의 조화로운 결합",
                    "창의적 문제 해결의 효율성과 효과성 향상"
                ],
                LearningDomain.INTUITIVE: [
                    "직관적 인식의 신뢰성과 정확성 향상",
                    "직관과 분석의 최적 조합 방법 개발",
                    "직관적 의사결정의 일관성과 품질 개선"
                ],
                LearningDomain.INTEGRATIVE: [
                    "다차원적 사고의 통합 효율성 향상",
                    "전체적 인식의 깊이와 폭 확장",
                    "통합적 문제 해결의 체계성과 유연성 균형"
                ]
            }
            
            description = random.choice(problem_descriptions[trigger.domain])
            
            problem = SelfDiscoveredProblem(
                problem_id=f"problem_{trigger.domain.value}_{int(time.time())}",
                domain=trigger.domain,
                description=description,
                complexity=complexity,
                urgency=urgency,
                interest_level=interest_level,
                context=context
            )
            problems.append(problem)
        
        logger.info(f"자발적 문제 {len(problems)}개 발견 완료")
        return problems
    
    async def _set_learning_goals(self, context: Dict[str, Any], 
                                discovered_problems: List[SelfDiscoveredProblem]) -> List[LearningGoal]:
        """학습 목표 자동 설정"""
        goals = []
        
        for problem in discovered_problems:
            # 문제의 복잡성과 관심도에 따른 목표 설정
            target_proficiency = min(0.8, problem.complexity + 0.2)
            priority = (problem.urgency + problem.interest_level) / 2
            
            # 예상 학습 시간 계산 (복잡성과 목표 숙련도에 따라)
            base_duration = timedelta(minutes=30)
            complexity_multiplier = 1 + problem.complexity
            proficiency_multiplier = 1 + target_proficiency
            estimated_duration = base_duration * complexity_multiplier * proficiency_multiplier
            
            # 목표 기술명 생성
            skill_names = {
                LearningDomain.COGNITIVE: [
                    "인지적 효율성 최적화",
                    "논리적 추론 정확성 향상",
                    "인지적 부하 관리"
                ],
                LearningDomain.EMOTIONAL: [
                    "감정적 인식 정확성 향상",
                    "감정-사고 통합 능력",
                    "감정적 안정성 관리"
                ],
                LearningDomain.CREATIVE: [
                    "창의적 사고 균형 능력",
                    "창의성-실용성 조화",
                    "창의적 문제 해결 효율성"
                ],
                LearningDomain.INTUITIVE: [
                    "직관적 인식 신뢰성",
                    "직관-분석 조합 능력",
                    "직관적 의사결정 일관성"
                ],
                LearningDomain.INTEGRATIVE: [
                    "다차원적 사고 통합",
                    "전체적 인식 확장",
                    "통합적 문제 해결 체계성"
                ]
            }
            
            target_skill = random.choice(skill_names[problem.domain])
            
            goal = LearningGoal(
                goal_id=f"goal_{problem.domain.value}_{int(time.time())}",
                domain=problem.domain,
                description=f"{problem.description}을 위한 학습 목표",
                target_skill=target_skill,
                target_proficiency=target_proficiency,
                estimated_duration=estimated_duration,
                priority=priority,
                context=context
            )
            goals.append(goal)
        
        # 우선순위에 따라 정렬
        goals.sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"학습 목표 {len(goals)}개 설정 완료")
        return goals
    
    async def _execute_learning_loop(self, context: Dict[str, Any], 
                                   learning_goals: List[LearningGoal]) -> Tuple[List[LearningActivity], List[LearningOutcome]]:
        """자기 주도적 학습 루프 실행"""
        activities = []
        outcomes = []
        
        for goal in learning_goals:
            # 학습 단계별 활동 실행
            goal_activities = await self._execute_goal_learning(goal, context)
            activities.extend(goal_activities)
            
            # 학습 성과 평가
            outcome = await self._evaluate_learning_outcome(goal, goal_activities)
            outcomes.append(outcome)
        
        return activities, outcomes
    
    async def _execute_goal_learning(self, goal: LearningGoal, context: Dict[str, Any]) -> List[LearningActivity]:
        """개별 목표에 대한 학습 실행"""
        activities = []
        
        # 학습 단계별 활동 생성
        phases = [LearningPhase.EXPLORATION, LearningPhase.INVESTIGATION, 
                 LearningPhase.EXPERIMENTATION, LearningPhase.INTEGRATION, LearningPhase.APPLICATION]
        
        for phase in phases:
            # 단계별 활동 시간 계산
            phase_duration = goal.estimated_duration / len(phases)
            
            # 참여도 계산 (목표 우선순위와 단계에 따라)
            base_engagement = goal.priority
            phase_engagement_multipliers = {
                LearningPhase.EXPLORATION: 0.8,
                LearningPhase.INVESTIGATION: 0.9,
                LearningPhase.EXPERIMENTATION: 1.0,
                LearningPhase.INTEGRATION: 0.95,
                LearningPhase.APPLICATION: 0.9
            }
            engagement_level = base_engagement * phase_engagement_multipliers[phase]
            
            # 진행도 계산
            progress_score = (phases.index(phase) + 1) / len(phases)
            
            # 활동 설명 생성
            activity_descriptions = {
                LearningPhase.EXPLORATION: f"{goal.target_skill} 영역 탐구 및 기본 개념 이해",
                LearningPhase.INVESTIGATION: f"{goal.target_skill} 관련 심화 내용 조사 및 분석",
                LearningPhase.EXPERIMENTATION: f"{goal.target_skill} 실험적 적용 및 테스트",
                LearningPhase.INTEGRATION: f"{goal.target_skill} 기존 지식과 통합 및 체계화",
                LearningPhase.APPLICATION: f"{goal.target_skill} 실제 상황에 적용 및 검증"
            }
            
            # 통찰 생성
            insights = await self._generate_learning_insights(goal, phase)
            
            activity = LearningActivity(
                activity_id=f"activity_{goal.goal_id}_{phase.value}_{int(time.time())}",
                goal_id=goal.goal_id,
                phase=phase,
                description=activity_descriptions[phase],
                duration=phase_duration,
                engagement_level=engagement_level,
                progress_score=progress_score,
                insights_gained=insights,
                context=context
            )
            activities.append(activity)
            
            # 활동 간 짧은 휴식
            await asyncio.sleep(0.1)
        
        return activities
    
    async def _generate_learning_insights(self, goal: LearningGoal, phase: LearningPhase) -> List[str]:
        """학습 통찰 생성"""
        insights = []
        
        # 단계별 통찰 생성
        phase_insights = {
            LearningPhase.EXPLORATION: [
                f"{goal.target_skill}의 기본 구조와 원리 발견",
                f"{goal.domain.value} 영역에서의 새로운 관점 획득",
                f"학습 목표의 복잡성과 깊이 인식"
            ],
            LearningPhase.INVESTIGATION: [
                f"{goal.target_skill}의 세부 메커니즘 이해",
                f"기존 지식과의 연결점 발견",
                f"학습 방법의 효율성 개선 방안 발견"
            ],
            LearningPhase.EXPERIMENTATION: [
                f"{goal.target_skill}의 실제 적용 가능성 확인",
                f"실험을 통한 새로운 발견",
                f"학습 과정에서의 예상치 못한 통찰"
            ],
            LearningPhase.INTEGRATION: [
                f"{goal.target_skill}과 기존 능력의 조화로운 통합",
                f"전체적 인식 체계의 확장",
                f"학습 내용의 체계적 정리와 구조화"
            ],
            LearningPhase.APPLICATION: [
                f"{goal.target_skill}의 실제 효과 검증",
                f"적용 과정에서의 추가 개선점 발견",
                f"학습 성과의 구체적 확인"
            ]
        }
        
        # 기본 통찰 선택
        base_insights = phase_insights[phase]
        selected_insights = random.sample(base_insights, min(2, len(base_insights)))
        insights.extend(selected_insights)
        
        # 추가 통찰 생성
        additional_insights = [
            f"{goal.target_skill} 학습을 통한 자기 성찰 기회",
            f"학습 과정에서의 메타 인식 능력 향상",
            f"{goal.domain.value} 영역에서의 성장 가능성 발견"
        ]
        
        if random.random() > 0.5:
            insights.append(random.choice(additional_insights))
        
        return insights
    
    async def _evaluate_learning_outcome(self, goal: LearningGoal, 
                                       activities: List[LearningActivity]) -> LearningOutcome:
        """학습 성과 평가"""
        # 전체 활동의 평균 참여도와 진행도 계산
        avg_engagement = sum(activity.engagement_level for activity in activities) / len(activities)
        avg_progress = sum(activity.progress_score for activity in activities) / len(activities)
        
        # 기술 향상도 계산
        skill_improvement = min(goal.target_proficiency, avg_progress * goal.target_proficiency)
        
        # 획득한 지식과 통찰 수집
        knowledge_gained = []
        insights_discovered = []
        
        for activity in activities:
            insights_discovered.extend(activity.insights_gained)
        
        # 중복 제거 및 정리
        insights_discovered = list(set(insights_discovered))
        
        # 자신감 향상도 계산
        confidence_boost = min(1.0, skill_improvement * avg_engagement)
        
        outcome = LearningOutcome(
            outcome_id=f"outcome_{goal.goal_id}_{int(time.time())}",
            goal_id=goal.goal_id,
            skill_improvement=skill_improvement,
            confidence_boost=confidence_boost,
            knowledge_gained=knowledge_gained,
            insights_discovered=insights_discovered,
            context={"goal": goal.__dict__, "activities_count": len(activities)}
        )
        
        return outcome
    
    async def _compile_learning_result(self, session_id: str, 
                                     curiosity_triggers: List[CuriosityTrigger],
                                     discovered_problems: List[SelfDiscoveredProblem],
                                     learning_goals: List[LearningGoal],
                                     learning_activities: List[LearningActivity],
                                     learning_outcomes: List[LearningOutcome]) -> SelfDirectedLearningResult:
        """학습 결과 종합"""
        # 총 학습 시간 계산
        total_learning_time = sum(
            (activity.duration for activity in learning_activities), 
            timedelta()
        )
        
        # 평균 참여도 계산
        if learning_activities:
            average_engagement = sum(
                activity.engagement_level for activity in learning_activities
            ) / len(learning_activities)
        else:
            average_engagement = 0.0
        
        # 전체 진행도 계산
        if learning_outcomes:
            overall_progress = sum(
                outcome.skill_improvement for outcome in learning_outcomes
            ) / len(learning_outcomes)
        else:
            overall_progress = 0.0
        
        result = SelfDirectedLearningResult(
            session_id=session_id,
            curiosity_triggers=curiosity_triggers,
            discovered_problems=discovered_problems,
            learning_goals=learning_goals,
            learning_activities=learning_activities,
            learning_outcomes=learning_outcomes,
            total_learning_time=total_learning_time,
            average_engagement=average_engagement,
            overall_progress=overall_progress
        )
        
        return result
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """학습 요약 정보 반환"""
        if not self.learning_history:
            return {"message": "아직 학습 기록이 없습니다."}
        
        # 통계 계산
        total_sessions = len(self.learning_history)
        total_time = sum(
            (result.total_learning_time for result in self.learning_history), 
            timedelta()
        )
        avg_engagement = sum(
            (result.average_engagement for result in self.learning_history)
        ) / total_sessions
        avg_progress = sum(
            (result.overall_progress for result in self.learning_history)
        ) / total_sessions
        
        # 영역별 학습 분포
        domain_distribution = defaultdict(int)
        for result in self.learning_history:
            for goal in result.learning_goals:
                domain_distribution[goal.domain.value] += 1
        
        # 최근 학습 활동
        recent_activities = []
        for result in self.learning_history[-3:]:  # 최근 3개 세션
            for activity in result.learning_activities[-2:]:  # 각 세션의 최근 2개 활동
                recent_activities.append({
                    "activity_id": activity.activity_id,
                    "description": activity.description,
                    "phase": activity.phase.value,
                    "engagement": activity.engagement_level,
                    "progress": activity.progress_score
                })
        
        return {
            "total_sessions": total_sessions,
            "total_learning_time": str(total_time),
            "average_engagement": round(avg_engagement, 3),
            "average_progress": round(avg_progress, 3),
            "domain_distribution": dict(domain_distribution),
            "recent_activities": recent_activities,
            "curiosity_profile": self.curiosity_profile
        }


async def test_self_directed_learning_system():
    """자발적 학습 시스템 테스트"""
    print("=== Day 6: 자발적 학습 시스템 테스트 시작 ===")
    
    # 시스템 초기화
    learning_system = SelfDirectedLearningSystem()
    
    # 자발적 학습 세션 실행
    context = {
        "test_mode": True,
        "session_type": "comprehensive_learning",
        "target_domains": ["cognitive", "emotional", "creative", "intuitive", "integrative"]
    }
    
    result = await learning_system.start_self_directed_learning(context)
    
    # 결과 출력
    print(f"\n=== 자발적 학습 세션 결과 ===")
    print(f"세션 ID: {result.session_id}")
    print(f"성공 여부: {result.success}")
    print(f"총 학습 시간: {result.total_learning_time}")
    print(f"평균 참여도: {result.average_engagement:.3f}")
    print(f"전체 진행도: {result.overall_progress:.3f}")
    
    print(f"\n=== 호기심 트리거 ({len(result.curiosity_triggers)}개) ===")
    for trigger in result.curiosity_triggers:
        print(f"- {trigger.domain.value}: {trigger.description} (강도: {trigger.intensity:.2f})")
    
    print(f"\n=== 발견된 문제 ({len(result.discovered_problems)}개) ===")
    for problem in result.discovered_problems:
        print(f"- {problem.domain.value}: {problem.description} (복잡도: {problem.complexity:.2f})")
    
    print(f"\n=== 학습 목표 ({len(result.learning_goals)}개) ===")
    for goal in result.learning_goals:
        print(f"- {goal.target_skill}: {goal.description} (우선순위: {goal.priority:.2f})")
    
    print(f"\n=== 학습 활동 ({len(result.learning_activities)}개) ===")
    for activity in result.learning_activities:
        print(f"- {activity.phase.value}: {activity.description} (참여도: {activity.engagement_level:.2f})")
    
    print(f"\n=== 학습 성과 ({len(result.learning_outcomes)}개) ===")
    for outcome in result.learning_outcomes:
        print(f"- 기술 향상도: {outcome.skill_improvement:.2f}, 자신감 향상: {outcome.confidence_boost:.2f}")
    
    # 학습 요약 정보
    summary = await learning_system.get_learning_summary()
    print(f"\n=== 학습 요약 ===")
    print(f"총 세션 수: {summary['total_sessions']}")
    print(f"총 학습 시간: {summary['total_learning_time']}")
    print(f"평균 참여도: {summary['average_engagement']}")
    print(f"평균 진행도: {summary['average_progress']}")
    print(f"영역별 분포: {summary['domain_distribution']}")
    
    print("\n=== Day 6: 자발적 학습 시스템 테스트 완료 ===")
    return result


if __name__ == "__main__":
    asyncio.run(test_self_directed_learning_system())
