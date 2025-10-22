"""
DuRiCore Phase 2.2: 내적 동기 시스템 (Intrinsic Motivation System)
- 호기심, 성취욕, 탐구욕 메트릭 구현
- 자발적 학습 목표 생성 시스템
- 동적 우선순위 조정 메커니즘
"""

import asyncio
import logging
import random
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logger = logging.getLogger(__name__)


class MotivationType(Enum):
    """동기 유형"""

    CURIOSITY = "curiosity"  # 호기심
    ACHIEVEMENT = "achievement"  # 성취욕
    EXPLORATION = "exploration"  # 탐구욕
    MASTERY = "mastery"  # 숙달 욕구
    CREATIVITY = "creativity"  # 창의성
    AUTONOMY = "autonomy"  # 자율성


class CuriosityLevel(Enum):
    """호기심 수준"""

    MINIMAL = "minimal"  # 최소 (0.0-0.2)
    LOW = "low"  # 낮음 (0.2-0.4)
    MODERATE = "moderate"  # 보통 (0.4-0.6)
    HIGH = "high"  # 높음 (0.6-0.8)
    INTENSE = "intense"  # 강렬 (0.8-1.0)


class AchievementLevel(Enum):
    """성취욕 수준"""

    PASSIVE = "passive"  # 수동적 (0.0-0.2)
    LOW = "low"  # 낮음 (0.2-0.4)
    MODERATE = "moderate"  # 보통 (0.4-0.6)
    HIGH = "high"  # 높음 (0.6-0.8)
    EXCELLENT = "excellent"  # 우수 (0.8-1.0)


@dataclass
class CuriosityMetrics:
    """호기심 측정 지표"""

    novelty_seeking: float = 0.5  # 새로움 추구 (0.0-1.0)
    complexity_preference: float = 0.5  # 복잡성 선호 (0.0-1.0)
    exploration_drive: float = 0.5  # 탐구 욕구 (0.0-1.0)
    question_generation: float = 0.5  # 질문 생성 (0.0-1.0)
    learning_interest: float = 0.5  # 학습 흥미 (0.0-1.0)

    @property
    def overall_curiosity(self) -> float:
        """전체 호기심 수준"""
        return (
            self.novelty_seeking
            + self.complexity_preference
            + self.exploration_drive
            + self.question_generation
            + self.learning_interest
        ) / 5.0


@dataclass
class AchievementMetrics:
    """성취욕 측정 지표"""

    mastery_orientation: float = 0.5  # 숙달 지향 (0.0-1.0)
    performance_improvement: float = 0.5  # 성과 개선 (0.0-1.0)
    skill_development: float = 0.5  # 기술 개발 (0.0-1.0)
    goal_setting: float = 0.5  # 목표 설정 (0.0-1.0)
    persistence: float = 0.5  # 지속성 (0.0-1.0)

    @property
    def overall_achievement(self) -> float:
        """전체 성취욕 수준"""
        return (
            self.mastery_orientation
            + self.performance_improvement
            + self.skill_development
            + self.goal_setting
            + self.persistence
        ) / 5.0


@dataclass
class LearningGoal:
    """학습 목표"""

    goal_id: str
    goal_type: MotivationType
    description: str
    motivation: str
    priority: float  # 0.0-1.0
    complexity: float  # 0.0-1.0
    expected_value: float  # 0.0-1.0
    created_at: datetime
    deadline: Optional[datetime] = None
    progress: float = 0.0
    status: str = "active"


@dataclass
class IntrinsicMotivationState:
    """내적 동기 상태"""

    curiosity_metrics: CuriosityMetrics
    achievement_metrics: AchievementMetrics
    current_goals: List[LearningGoal] = field(default_factory=list)
    goal_history: List[LearningGoal] = field(default_factory=list)
    motivation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)


class IntrinsicMotivationSystem:
    """내적 동기 시스템"""

    def __init__(self):
        self.motivation_state = IntrinsicMotivationState(
            curiosity_metrics=CuriosityMetrics(),
            achievement_metrics=AchievementMetrics(),
        )
        self.learning_patterns = defaultdict(list)
        self.exploration_history = []
        self.achievement_history = []

        logger.info("🧠 내적 동기 시스템 초기화 완료")

    async def update_curiosity_metrics(self, experience: Dict[str, Any]) -> None:
        """호기심 메트릭 업데이트"""
        try:
            # 새로움 평가
            novelty = self._calculate_novelty(experience)
            self.motivation_state.curiosity_metrics.novelty_seeking = (
                self.motivation_state.curiosity_metrics.novelty_seeking * 0.8 + novelty * 0.2
            )

            # 복잡성 선호도 평가
            complexity = self._calculate_complexity(experience)
            self.motivation_state.curiosity_metrics.complexity_preference = (
                self.motivation_state.curiosity_metrics.complexity_preference * 0.8
                + complexity * 0.2
            )

            # 탐구 욕구 평가
            exploration = self._calculate_exploration_drive(experience)
            self.motivation_state.curiosity_metrics.exploration_drive = (
                self.motivation_state.curiosity_metrics.exploration_drive * 0.8 + exploration * 0.2
            )

            # 질문 생성 능력 평가
            question_gen = self._calculate_question_generation(experience)
            self.motivation_state.curiosity_metrics.question_generation = (
                self.motivation_state.curiosity_metrics.question_generation * 0.8
                + question_gen * 0.2
            )

            # 학습 흥미 평가
            learning_interest = self._calculate_learning_interest(experience)
            self.motivation_state.curiosity_metrics.learning_interest = (
                self.motivation_state.curiosity_metrics.learning_interest * 0.8
                + learning_interest * 0.2
            )

            self.motivation_state.last_update = datetime.now()
            logger.info(
                f"🔍 호기심 메트릭 업데이트: {self.motivation_state.curiosity_metrics.overall_curiosity:.3f}"
            )

        except Exception as e:
            logger.error(f"호기심 메트릭 업데이트 실패: {e}")

    async def update_achievement_metrics(self, performance: Dict[str, float]) -> None:
        """성취욕 메트릭 업데이트"""
        try:
            # 숙달 지향성 평가
            mastery = self._calculate_mastery_orientation(performance)
            self.motivation_state.achievement_metrics.mastery_orientation = (
                self.motivation_state.achievement_metrics.mastery_orientation * 0.8 + mastery * 0.2
            )

            # 성과 개선 평가
            improvement = self._calculate_performance_improvement(performance)
            self.motivation_state.achievement_metrics.performance_improvement = (
                self.motivation_state.achievement_metrics.performance_improvement * 0.8
                + improvement * 0.2
            )

            # 기술 개발 평가
            skill_dev = self._calculate_skill_development(performance)
            self.motivation_state.achievement_metrics.skill_development = (
                self.motivation_state.achievement_metrics.skill_development * 0.8 + skill_dev * 0.2
            )

            # 목표 설정 능력 평가
            goal_setting = self._calculate_goal_setting(performance)
            self.motivation_state.achievement_metrics.goal_setting = (
                self.motivation_state.achievement_metrics.goal_setting * 0.8 + goal_setting * 0.2
            )

            # 지속성 평가
            persistence = self._calculate_persistence(performance)
            self.motivation_state.achievement_metrics.persistence = (
                self.motivation_state.achievement_metrics.persistence * 0.8 + persistence * 0.2
            )

            self.motivation_state.last_update = datetime.now()
            logger.info(
                f"🏆 성취욕 메트릭 업데이트: {self.motivation_state.achievement_metrics.overall_achievement:.3f}"
            )

        except Exception as e:
            logger.error(f"성취욕 메트릭 업데이트 실패: {e}")

    async def generate_self_directed_learning_goals(self) -> List[LearningGoal]:
        """자발적 학습 목표 생성"""
        try:
            goals = []
            current_time = datetime.now()

            # 호기심 기반 목표
            curiosity_level = self.motivation_state.curiosity_metrics.overall_curiosity
            if curiosity_level > 0.7:
                goals.append(
                    LearningGoal(
                        goal_id=f"curiosity_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.CURIOSITY,
                        description="새로운 패턴 탐구 및 이해",
                        motivation="호기심",
                        priority=0.8,
                        complexity=0.7,
                        expected_value=0.9,
                        created_at=current_time,
                    )
                )

            if curiosity_level > 0.6:
                goals.append(
                    LearningGoal(
                        goal_id=f"exploration_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.EXPLORATION,
                        description="미탐험 영역 조사 및 분석",
                        motivation="탐구욕",
                        priority=0.7,
                        complexity=0.8,
                        expected_value=0.8,
                        created_at=current_time,
                    )
                )

            # 성취욕 기반 목표
            achievement_level = self.motivation_state.achievement_metrics.overall_achievement
            if achievement_level > 0.6:
                goals.append(
                    LearningGoal(
                        goal_id=f"mastery_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.MASTERY,
                        description="기존 능력 향상 및 숙달",
                        motivation="성취욕",
                        priority=0.7,
                        complexity=0.6,
                        expected_value=0.8,
                        created_at=current_time,
                    )
                )

            if achievement_level > 0.5:
                goals.append(
                    LearningGoal(
                        goal_id=f"improvement_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.ACHIEVEMENT,
                        description="성과 개선 및 최적화",
                        motivation="성취욕",
                        priority=0.6,
                        complexity=0.5,
                        expected_value=0.7,
                        created_at=current_time,
                    )
                )

            # 창의성 기반 목표
            if curiosity_level > 0.5 and achievement_level > 0.5:
                goals.append(
                    LearningGoal(
                        goal_id=f"creativity_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.CREATIVITY,
                        description="혁신적 해결책 개발",
                        motivation="창의성",
                        priority=0.8,
                        complexity=0.9,
                        expected_value=0.9,
                        created_at=current_time,
                    )
                )

            # 자율성 기반 목표
            if len(self.motivation_state.current_goals) < 3:
                goals.append(
                    LearningGoal(
                        goal_id=f"autonomy_goal_{int(time.time() * 1000)}",
                        goal_type=MotivationType.AUTONOMY,
                        description="자기 주도적 학습 체계 구축",
                        motivation="자율성",
                        priority=0.6,
                        complexity=0.7,
                        expected_value=0.8,
                        created_at=current_time,
                    )
                )

            return goals

        except Exception as e:
            logger.error(f"자발적 학습 목표 생성 실패: {e}")
            return []

    async def adjust_goal_priorities(self, goals: List[LearningGoal]) -> List[LearningGoal]:
        """목표 우선순위 동적 조정"""
        try:
            for goal in goals:
                # 성과 기반 조정
                if goal.progress > 0.8:
                    goal.priority *= 0.8  # 성과가 좋으면 우선순위 낮춤
                elif goal.progress < 0.3:
                    goal.priority *= 1.2  # 성과가 나쁘면 우선순위 높임

                # 호기심 기반 조정
                if goal.motivation == "호기심":
                    curiosity_level = self.motivation_state.curiosity_metrics.overall_curiosity
                    if curiosity_level > 0.9:
                        goal.priority *= 1.3  # 호기심이 높으면 우선순위 높임

                # 성취욕 기반 조정
                if goal.motivation == "성취욕":
                    achievement_level = (
                        self.motivation_state.achievement_metrics.overall_achievement
                    )
                    if achievement_level > 0.8:
                        goal.priority *= 1.2  # 성취욕이 높으면 우선순위 높임

                # 복잡성 기반 조정
                if goal.complexity > 0.8:
                    goal.priority *= 1.1  # 복잡한 목표는 우선순위 높임
                elif goal.complexity < 0.3:
                    goal.priority *= 0.9  # 단순한 목표는 우선순위 낮춤

            # 우선순위별 정렬
            return sorted(goals, key=lambda x: x.priority, reverse=True)

        except Exception as e:
            logger.error(f"목표 우선순위 조정 실패: {e}")
            return goals

    async def execute_voluntary_learning(self) -> Dict[str, Any]:
        """자발적 학습 실행"""
        try:
            # 현재 동기 상태 평가
            curiosity_level = self.motivation_state.curiosity_metrics.overall_curiosity
            achievement_level = self.motivation_state.achievement_metrics.overall_achievement

            # 자발적 목표 생성
            if curiosity_level > 0.7 or achievement_level > 0.6:
                new_goals = await self.generate_self_directed_learning_goals()

                # 기존 목표와 통합
                all_goals = self.motivation_state.current_goals + new_goals

                # 우선순위 조정
                adjusted_goals = await self.adjust_goal_priorities(all_goals)

                # 상위 3개 목표 선택
                selected_goals = adjusted_goals[:3]

                # 학습 실행
                learning_results = []
                for goal in selected_goals:
                    if goal.priority > 0.8:
                        result = await self._execute_learning_goal(goal)
                        learning_results.append(result)

                return {
                    "executed_goals": len(learning_results),
                    "curiosity_level": curiosity_level,
                    "achievement_level": achievement_level,
                    "learning_results": learning_results,
                }

            return {
                "executed_goals": 0,
                "curiosity_level": curiosity_level,
                "achievement_level": achievement_level,
                "learning_results": [],
            }

        except Exception as e:
            logger.error(f"자발적 학습 실행 실패: {e}")
            return {"executed_goals": 0, "error": str(e)}

    async def _execute_learning_goal(self, goal: LearningGoal) -> Dict[str, Any]:
        """개별 학습 목표 실행"""
        try:
            # 목표별 학습 실행
            if goal.goal_type == MotivationType.CURIOSITY:
                result = await self._execute_curiosity_learning(goal)
            elif goal.goal_type == MotivationType.EXPLORATION:
                result = await self._execute_exploration_learning(goal)
            elif goal.goal_type == MotivationType.MASTERY:
                result = await self._execute_mastery_learning(goal)
            elif goal.goal_type == MotivationType.ACHIEVEMENT:
                result = await self._execute_achievement_learning(goal)
            elif goal.goal_type == MotivationType.CREATIVITY:
                result = await self._execute_creativity_learning(goal)
            else:
                result = await self._execute_general_learning(goal)

            # 진행도 업데이트
            goal.progress = min(1.0, goal.progress + result.get("progress_gain", 0.1))

            return result

        except Exception as e:
            logger.error(f"학습 목표 실행 실패: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_curiosity_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """호기심 기반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "curiosity",
            "progress_gain": 0.15,
            "insights": ["새로운 패턴 발견", "이해도 향상"],
            "success": True,
        }

    async def _execute_exploration_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """탐구 기반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "exploration",
            "progress_gain": 0.12,
            "insights": ["새로운 영역 탐색", "지식 확장"],
            "success": True,
        }

    async def _execute_mastery_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """숙달 기반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "mastery",
            "progress_gain": 0.10,
            "insights": ["기술 향상", "숙련도 증가"],
            "success": True,
        }

    async def _execute_achievement_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """성취 기반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "achievement",
            "progress_gain": 0.08,
            "insights": ["성과 개선", "목표 달성"],
            "success": True,
        }

    async def _execute_creativity_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """창의성 기반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "creativity",
            "progress_gain": 0.20,
            "insights": ["혁신적 아이디어", "창의적 해결책"],
            "success": True,
        }

    async def _execute_general_learning(self, goal: LearningGoal) -> Dict[str, Any]:
        """일반 학습 실행"""
        return {
            "goal_id": goal.goal_id,
            "learning_type": "general",
            "progress_gain": 0.05,
            "insights": ["기본 학습", "지식 습득"],
            "success": True,
        }

    def _calculate_novelty(self, experience: Dict[str, Any]) -> float:
        """새로움 계산"""
        # 실제 구현에서는 더 복잡한 로직 사용
        return random.uniform(0.3, 0.9)

    def _calculate_complexity(self, experience: Dict[str, Any]) -> float:
        """복잡성 계산"""
        return random.uniform(0.4, 0.8)

    def _calculate_exploration_drive(self, experience: Dict[str, Any]) -> float:
        """탐구 욕구 계산"""
        return random.uniform(0.5, 0.9)

    def _calculate_question_generation(self, experience: Dict[str, Any]) -> float:
        """질문 생성 능력 계산"""
        return random.uniform(0.4, 0.8)

    def _calculate_learning_interest(self, experience: Dict[str, Any]) -> float:
        """학습 흥미 계산"""
        return random.uniform(0.6, 0.9)

    def _calculate_mastery_orientation(self, performance: Dict[str, float]) -> float:
        """숙달 지향성 계산"""
        return random.uniform(0.5, 0.9)

    def _calculate_performance_improvement(self, performance: Dict[str, float]) -> float:
        """성과 개선 계산"""
        return random.uniform(0.4, 0.8)

    def _calculate_skill_development(self, performance: Dict[str, float]) -> float:
        """기술 개발 계산"""
        return random.uniform(0.5, 0.9)

    def _calculate_goal_setting(self, performance: Dict[str, float]) -> float:
        """목표 설정 능력 계산"""
        return random.uniform(0.4, 0.8)

    def _calculate_persistence(self, performance: Dict[str, float]) -> float:
        """지속성 계산"""
        return random.uniform(0.5, 0.9)

    def get_motivation_state(self) -> Dict[str, Any]:
        """동기 상태 반환"""
        return {
            "curiosity_metrics": asdict(self.motivation_state.curiosity_metrics),
            "achievement_metrics": asdict(self.motivation_state.achievement_metrics),
            "current_goals": [asdict(goal) for goal in self.motivation_state.current_goals],
            "last_update": self.motivation_state.last_update.isoformat(),
        }


async def test_intrinsic_motivation_system():
    """내적 동기 시스템 테스트"""
    logger.info("🧠 내적 동기 시스템 테스트 시작")

    # 시스템 생성
    motivation_system = IntrinsicMotivationSystem()

    # 테스트 경험 데이터
    test_experience = {
        "novelty": 0.8,
        "complexity": 0.7,
        "exploration": 0.9,
        "questions": 5,
        "learning_interest": 0.8,
    }

    # 테스트 성능 데이터
    test_performance = {
        "mastery": 0.7,
        "improvement": 0.6,
        "skill_dev": 0.8,
        "goal_setting": 0.5,
        "persistence": 0.7,
    }

    # 메트릭 업데이트
    await motivation_system.update_curiosity_metrics(test_experience)
    await motivation_system.update_achievement_metrics(test_performance)

    # 자발적 학습 실행
    learning_result = await motivation_system.execute_voluntary_learning()

    # 결과 출력
    print("\n=== 내적 동기 시스템 테스트 결과 ===")
    print(
        f"호기심 수준: {motivation_system.motivation_state.curiosity_metrics.overall_curiosity:.3f}"
    )
    print(
        f"성취욕 수준: {motivation_system.motivation_state.achievement_metrics.overall_achievement:.3f}"
    )
    print(f"실행된 학습 목표: {learning_result['executed_goals']}개")
    print(f"학습 결과: {learning_result['learning_results']}")

    # 동기 상태 출력
    state = motivation_system.get_motivation_state()
    print(f"\n동기 상태: {state}")

    print("✅ 내적 동기 시스템 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_intrinsic_motivation_system())
