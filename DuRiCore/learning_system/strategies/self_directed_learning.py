#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 자기 주도적 학습 전략 (Self-Directed Learning Strategy)

자기 주도적 학습 전략을 구현하는 모듈입니다.
- 호기심 기반 탐구
- 자발적 문제 발견
- 학습 목표 자동 설정
- 자기 주도적 학습 루프
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningMotivation(Enum):
    """학습 동기"""

    CURIOSITY = "curiosity"  # 호기심
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    SELF_IMPROVEMENT = "self_improvement"  # 자기 향상
    EXPLORATION = "exploration"  # 탐구
    MASTERY = "mastery"  # 숙달


class LearningDomain(Enum):
    """학습 영역"""

    COGNITIVE = "cognitive"  # 인지적
    EMOTIONAL = "emotional"  # 감정적
    CREATIVE = "creative"  # 창의적
    INTUITIVE = "intuitive"  # 직관적
    INTEGRATIVE = "integrative"  # 통합적


class LearningPhase(Enum):
    """학습 단계"""

    EXPLORATION = "exploration"  # 탐구
    INVESTIGATION = "investigation"  # 조사
    EXPERIMENTATION = "experimentation"  # 실험
    INTEGRATION = "integration"  # 통합
    APPLICATION = "application"  # 적용


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
    """자기 주도적 학습 결과"""

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


class SelfDirectedLearningStrategy:
    """자기 주도적 학습 전략"""

    def __init__(self):
        """초기화"""
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

        logger.info("자기 주도적 학습 전략 초기화 완료")

    async def start_self_directed_learning(
        self, context: Dict[str, Any] = None
    ) -> SelfDirectedLearningResult:
        """자기 주도적 학습 시작"""
        session_id = f"self_directed_session_{int(time.time())}"
        start_time = datetime.now()

        try:
            # 1. 호기심 트리거 생성
            curiosity_triggers = await self._generate_curiosity_triggers(context or {})

            # 2. 문제 발견
            discovered_problems = await self._discover_problems(
                context or {}, curiosity_triggers
            )

            # 3. 학습 목표 설정
            learning_goals = await self._set_learning_goals(
                context or {}, discovered_problems
            )

            # 4. 학습 루프 실행
            learning_activities, learning_outcomes = await self._execute_learning_loop(
                context or {}, learning_goals
            )

            # 5. 결과 컴파일
            end_time = datetime.now()
            total_learning_time = end_time - start_time

            result = await self._compile_learning_result(
                session_id,
                curiosity_triggers,
                discovered_problems,
                learning_goals,
                learning_activities,
                learning_outcomes,
                total_learning_time,
            )

            self.learning_history.append(result)
            self.total_learning_sessions += 1
            self.total_learning_time += total_learning_time

            logger.info(
                f"자기 주도적 학습 완료: {session_id} (지속시간: {total_learning_time})"
            )
            return result

        except Exception as e:
            logger.error(f"자기 주도적 학습 실패: {e}")
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
                error_message=str(e),
            )

    async def _generate_curiosity_triggers(
        self, context: Dict[str, Any]
    ) -> List[CuriosityTrigger]:
        """호기심 트리거 생성"""
        triggers = []

        # 도메인별 호기심 트리거 생성
        for domain in LearningDomain:
            if self.curiosity_profile[domain] > 0.3:  # 호기심 임계값
                trigger = CuriosityTrigger(
                    trigger_id=f"trigger_{int(time.time())}_{domain.value}",
                    domain=domain,
                    motivation=LearningMotivation.CURIOSITY,
                    intensity=self.curiosity_profile[domain],
                    description=f"{domain.value} 영역에 대한 호기심이 발생했습니다.",
                    context=context,
                )
                triggers.append(trigger)

        # 컨텍스트 기반 추가 트리거
        if "recent_topics" in context:
            for topic in context["recent_topics"][:3]:  # 최근 3개 토픽
                trigger = CuriosityTrigger(
                    trigger_id=f"trigger_{int(time.time())}_topic_{topic}",
                    domain=LearningDomain.COGNITIVE,
                    motivation=LearningMotivation.EXPLORATION,
                    intensity=0.7,
                    description=f"'{topic}' 주제에 대한 탐구 욕구가 발생했습니다.",
                    context=context,
                )
                triggers.append(trigger)

        logger.info(f"호기심 트리거 {len(triggers)}개 생성")
        return triggers

    async def _discover_problems(
        self, context: Dict[str, Any], curiosity_triggers: List[CuriosityTrigger]
    ) -> List[SelfDiscoveredProblem]:
        """문제 발견"""
        problems = []

        # 호기심 트리거 기반 문제 발견
        for trigger in curiosity_triggers:
            problem = SelfDiscoveredProblem(
                problem_id=f"problem_{int(time.time())}_{trigger.domain.value}",
                domain=trigger.domain,
                description=f"{trigger.domain.value} 영역에서 발견된 문제: {trigger.description}",
                complexity=trigger.intensity,
                urgency=0.5,  # 기본 긴급도
                interest_level=trigger.intensity,
                context=context,
            )
            problems.append(problem)

        # 컨텍스트 기반 문제 발견
        if "challenges" in context:
            for challenge in context["challenges"]:
                problem = SelfDiscoveredProblem(
                    problem_id=f"problem_{int(time.time())}_challenge_{len(problems)}",
                    domain=LearningDomain.INTEGRATIVE,
                    description=f"발견된 도전 과제: {challenge}",
                    complexity=0.7,
                    urgency=0.8,
                    interest_level=0.9,
                    context=context,
                )
                problems.append(problem)

        logger.info(f"문제 {len(problems)}개 발견")
        return problems

    async def _set_learning_goals(
        self, context: Dict[str, Any], discovered_problems: List[SelfDiscoveredProblem]
    ) -> List[LearningGoal]:
        """학습 목표 설정"""
        goals = []

        # 문제 기반 학습 목표 설정
        for problem in discovered_problems:
            goal = LearningGoal(
                goal_id=f"goal_{int(time.time())}_{problem.domain.value}",
                domain=problem.domain,
                description=f"{problem.description} 해결을 위한 학습",
                target_skill=f"{problem.domain.value}_problem_solving",
                target_proficiency=0.8,
                estimated_duration=timedelta(hours=2),
                priority=problem.interest_level,
                context=context,
            )
            goals.append(goal)

        # 컨텍스트 기반 추가 목표
        if "learning_objectives" in context:
            for objective in context["learning_objectives"]:
                goal = LearningGoal(
                    goal_id=f"goal_{int(time.time())}_objective_{len(goals)}",
                    domain=LearningDomain.COGNITIVE,
                    description=objective["description"],
                    target_skill=objective.get("skill", "general_learning"),
                    target_proficiency=objective.get("proficiency", 0.7),
                    estimated_duration=timedelta(
                        hours=objective.get("duration_hours", 1)
                    ),
                    priority=objective.get("priority", 0.5),
                    context=context,
                )
                goals.append(goal)

        logger.info(f"학습 목표 {len(goals)}개 설정")
        return goals

    async def _execute_learning_loop(
        self, context: Dict[str, Any], learning_goals: List[LearningGoal]
    ) -> Tuple[List[LearningActivity], List[LearningOutcome]]:
        """학습 루프 실행"""
        activities = []
        outcomes = []

        for goal in learning_goals:
            # 목표별 학습 활동 실행
            goal_activities = await self._execute_goal_learning(goal, context)
            activities.extend(goal_activities)

            # 학습 성과 평가
            outcome = await self._evaluate_learning_outcome(goal, goal_activities)
            outcomes.append(outcome)

        logger.info(f"학습 루프 완료: {len(activities)}개 활동, {len(outcomes)}개 성과")
        return activities, outcomes

    async def _execute_goal_learning(
        self, goal: LearningGoal, context: Dict[str, Any]
    ) -> List[LearningActivity]:
        """목표별 학습 실행"""
        activities = []

        # 학습 단계별 활동 생성
        for phase in LearningPhase:
            activity = LearningActivity(
                activity_id=f"activity_{int(time.time())}_{goal.goal_id}_{phase.value}",
                goal_id=goal.goal_id,
                phase=phase,
                description=f"{goal.description} - {phase.value} 단계",
                duration=goal.estimated_duration / len(LearningPhase),
                engagement_level=0.8,
                progress_score=0.2 * (list(LearningPhase).index(phase) + 1),
                insights_gained=await self._generate_learning_insights(goal, phase),
                context=context,
            )
            activities.append(activity)

        return activities

    async def _generate_learning_insights(
        self, goal: LearningGoal, phase: LearningPhase
    ) -> List[str]:
        """학습 통찰 생성"""
        insights = []

        # 단계별 통찰 생성
        if phase == LearningPhase.EXPLORATION:
            insights.append(
                f"{goal.domain.value} 영역 탐구를 통해 새로운 관점을 발견했습니다."
            )
        elif phase == LearningPhase.INVESTIGATION:
            insights.append(
                f"{goal.target_skill}에 대한 심층 조사를 통해 패턴을 발견했습니다."
            )
        elif phase == LearningPhase.EXPERIMENTATION:
            insights.append(f"실험을 통해 {goal.target_skill}의 실용성을 확인했습니다.")
        elif phase == LearningPhase.INTEGRATION:
            insights.append(
                f"다양한 지식을 통합하여 {goal.target_skill}을 체계화했습니다."
            )
        elif phase == LearningPhase.APPLICATION:
            insights.append(
                f"{goal.target_skill}을 실제 상황에 적용하여 효과를 검증했습니다."
            )

        return insights

    async def _evaluate_learning_outcome(
        self, goal: LearningGoal, activities: List[LearningActivity]
    ) -> LearningOutcome:
        """학습 성과 평가"""
        # 활동 기반 성과 계산
        total_progress = sum(activity.progress_score for activity in activities)
        average_progress = total_progress / len(activities) if activities else 0.0

        # 통찰 수집
        all_insights = []
        for activity in activities:
            all_insights.extend(activity.insights_gained)

        outcome = LearningOutcome(
            outcome_id=f"outcome_{int(time.time())}_{goal.goal_id}",
            goal_id=goal.goal_id,
            skill_improvement=min(average_progress, 1.0),
            confidence_boost=min(average_progress * 0.8, 1.0),
            knowledge_gained=[f"{goal.target_skill} 관련 지식"],
            insights_discovered=all_insights,
            context={"goal": goal.description},
        )

        return outcome

    async def _compile_learning_result(
        self,
        session_id: str,
        curiosity_triggers: List[CuriosityTrigger],
        discovered_problems: List[SelfDiscoveredProblem],
        learning_goals: List[LearningGoal],
        learning_activities: List[LearningActivity],
        learning_outcomes: List[LearningOutcome],
        total_learning_time: timedelta,
    ) -> SelfDirectedLearningResult:
        """학습 결과 컴파일"""
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
            overall_progress=overall_progress,
            success=True,
        )

        return result

    async def get_learning_summary(self) -> Dict[str, Any]:
        """학습 요약 조회"""
        if not self.learning_history:
            return {"error": "학습 이력이 없습니다"}

        # 통계 계산
        total_sessions = len(self.learning_history)
        successful_sessions = len([r for r in self.learning_history if r.success])
        average_engagement = (
            sum(r.average_engagement for r in self.learning_history) / total_sessions
        )
        average_progress = (
            sum(r.overall_progress for r in self.learning_history) / total_sessions
        )

        # 도메인별 통계
        domain_stats = defaultdict(lambda: {"count": 0, "total_progress": 0.0})
        for result in self.learning_history:
            for goal in result.learning_goals:
                domain_stats[goal.domain.value]["count"] += 1
                domain_stats[goal.domain.value][
                    "total_progress"
                ] += goal.target_proficiency

        for domain in domain_stats:
            if domain_stats[domain]["count"] > 0:
                domain_stats[domain]["average_progress"] = (
                    domain_stats[domain]["total_progress"]
                    / domain_stats[domain]["count"]
                )

        return {
            "total_sessions": total_sessions,
            "successful_sessions": successful_sessions,
            "success_rate": (
                successful_sessions / total_sessions if total_sessions > 0 else 0.0
            ),
            "average_engagement": average_engagement,
            "average_progress": average_progress,
            "total_learning_time": str(self.total_learning_time),
            "domain_statistics": dict(domain_stats),
            "recent_sessions": [
                {
                    "session_id": r.session_id,
                    "overall_progress": r.overall_progress,
                    "average_engagement": r.average_engagement,
                    "total_learning_time": str(r.total_learning_time),
                    "success": r.success,
                }
                for r in self.learning_history[-5:]  # 최근 5개 세션
            ],
        }
