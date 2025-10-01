#!/usr/bin/env python3
"""
재활 PoU 파일럿 고도화 시스템 (Day 32)
개인화된 재활 운동 루틴 생성 및 최적화
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class UserProfile:
    """사용자 프로필"""

    user_id: str
    age: int
    gender: str
    fitness_level: str  # beginner, intermediate, advanced
    injury_history: List[str]
    current_limitations: List[str]
    goals: List[str]
    preferences: Dict[str, Any]


@dataclass
class Exercise:
    """운동 정보"""

    exercise_id: str
    name: str
    category: str
    difficulty_level: int  # 1-5
    target_muscles: List[str]
    equipment_needed: List[str]
    safety_notes: List[str]
    duration_minutes: int
    reps_sets: str


@dataclass
class PersonalizedRoutine:
    """개인화된 운동 루틴"""

    routine_id: str
    user_id: str
    created_at: datetime
    exercises: List[Exercise]
    total_duration: int
    difficulty_score: float
    safety_score: float
    effectiveness_score: float


class RehabPersonalizationEngine:
    """재활 개인화 엔진"""

    def __init__(self):
        self.exercise_database = self._load_exercise_database()
        self.user_profiles = {}
        self.routines = {}
        self.logger = self._setup_logging()

    def _load_exercise_database(self) -> Dict[str, Exercise]:
        """운동 데이터베이스 로드"""
        exercises = {
            "stretch_neck": Exercise(
                exercise_id="stretch_neck",
                name="목 스트레칭",
                category="stretching",
                difficulty_level=1,
                target_muscles=["neck", "shoulders"],
                equipment_needed=[],
                safety_notes=["천천히 움직이기", "통증 시 중단"],
                duration_minutes=3,
                reps_sets="10회 x 2세트",
            ),
            "wall_pushup": Exercise(
                exercise_id="wall_pushup",
                name="벽 푸시업",
                category="strength",
                difficulty_level=2,
                target_muscles=["chest", "shoulders", "triceps"],
                equipment_needed=["wall"],
                safety_notes=["벽에 기대어 안전하게", "무릎 부드럽게"],
                duration_minutes=5,
                reps_sets="8회 x 2세트",
            ),
            "chair_squat": Exercise(
                exercise_id="chair_squat",
                name="의자 스쿼트",
                category="strength",
                difficulty_level=2,
                target_muscles=["quadriceps", "glutes", "core"],
                equipment_needed=["chair"],
                safety_notes=["의자에 앉았다 일어나기", "무릎이 발끝을 넘지 않게"],
                duration_minutes=5,
                reps_sets="8회 x 2세트",
            ),
            "balance_stand": Exercise(
                exercise_id="balance_stand",
                name="균형 서기",
                category="balance",
                difficulty_level=1,
                target_muscles=["core", "legs"],
                equipment_needed=[],
                safety_notes=["벽이나 의자에 손 대고", "넘어지지 않게 주의"],
                duration_minutes=3,
                reps_sets="20초 x 2세트",
            ),
            "ankle_circles": Exercise(
                exercise_id="ankle_circles",
                name="발목 원형 운동",
                category="mobility",
                difficulty_level=1,
                target_muscles=["ankles", "calves"],
                equipment_needed=[],
                safety_notes=["천천히 원형으로", "통증 시 중단"],
                duration_minutes=3,
                reps_sets="8회 x 2세트",
            ),
        }
        return exercises

    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger("rehab_personalization")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            f"rehab_personalization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def create_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """사용자 프로필 생성"""
        profile = UserProfile(
            user_id=user_data["user_id"],
            age=user_data["age"],
            gender=user_data["gender"],
            fitness_level=user_data["fitness_level"],
            injury_history=user_data.get("injury_history", []),
            current_limitations=user_data.get("current_limitations", []),
            goals=user_data.get("goals", []),
            preferences=user_data.get("preferences", {}),
        )

        self.user_profiles[profile.user_id] = profile
        self.logger.info(f"Created user profile for {profile.user_id}")
        return profile

    def generate_personalized_routine(self, user_id: str) -> PersonalizedRoutine:
        """개인화된 운동 루틴 생성"""
        if user_id not in self.user_profiles:
            raise ValueError(f"User profile not found: {user_id}")

        profile = self.user_profiles[user_id]
        self.logger.info(f"Generating personalized routine for {user_id}")

        # 개인화 알고리즘
        selected_exercises = self._select_exercises(profile)
        routine = PersonalizedRoutine(
            routine_id=f"routine_{user_id}_{int(time.time())}",
            user_id=user_id,
            created_at=datetime.now(),
            exercises=selected_exercises,
            total_duration=sum(ex.duration_minutes for ex in selected_exercises),
            difficulty_score=self._calculate_difficulty_score(
                selected_exercises, profile
            ),
            safety_score=self._calculate_safety_score(selected_exercises, profile),
            effectiveness_score=self._calculate_effectiveness_score(
                selected_exercises, profile
            ),
        )

        self.routines[routine.routine_id] = routine
        self.logger.info(
            f"Generated routine {routine.routine_id} with {len(selected_exercises)} exercises"
        )
        return routine

    def _select_exercises(self, profile: UserProfile) -> List[Exercise]:
        """사용자 프로필에 따른 운동 선택"""
        selected = []

        # 기본 운동 (모든 사용자)
        selected.append(self.exercise_database["stretch_neck"])
        selected.append(self.exercise_database["balance_stand"])

        # 피트니스 레벨에 따른 운동 추가
        if profile.fitness_level == "beginner":
            selected.append(self.exercise_database["wall_pushup"])
            selected.append(self.exercise_database["chair_squat"])
        elif profile.fitness_level == "intermediate":
            selected.append(self.exercise_database["wall_pushup"])
            selected.append(self.exercise_database["chair_squat"])
            selected.append(self.exercise_database["ankle_circles"])
        else:  # advanced
            selected.append(self.exercise_database["wall_pushup"])
            selected.append(self.exercise_database["chair_squat"])
            selected.append(self.exercise_database["ankle_circles"])

        # 부상 이력에 따른 운동 조정
        for injury in profile.injury_history:
            if "ankle" in injury.lower():
                # 발목 부상 시 발목 운동 강화
                if self.exercise_database["ankle_circles"] not in selected:
                    selected.append(self.exercise_database["ankle_circles"])

        # 현재 제한사항에 따른 운동 제외
        filtered_exercises = []
        for exercise in selected:
            should_include = True
            for limitation in profile.current_limitations:
                if limitation.lower() in exercise.name.lower():
                    should_include = False
                    break
            if should_include:
                filtered_exercises.append(exercise)

        return filtered_exercises

    def _calculate_difficulty_score(
        self, exercises: List[Exercise], profile: UserProfile
    ) -> float:
        """난이도 점수 계산"""
        if not exercises:
            return 0.0

        avg_difficulty = sum(ex.difficulty_level for ex in exercises) / len(exercises)

        # 사용자 피트니스 레벨에 따른 조정
        fitness_multiplier = {
            "beginner": 0.8,
            "intermediate": 1.0,
            "advanced": 1.2,
        }.get(profile.fitness_level, 1.0)

        return min(5.0, avg_difficulty * fitness_multiplier)

    def _calculate_safety_score(
        self, exercises: List[Exercise], profile: UserProfile
    ) -> float:
        """안전성 점수 계산"""
        if not exercises:
            return 0.0

        base_safety = 100.0

        # 부상 이력에 따른 안전성 감점
        injury_penalty = len(profile.injury_history) * 5.0

        # 현재 제한사항에 따른 안전성 감점
        limitation_penalty = len(profile.current_limitations) * 10.0

        # 운동별 안전성 점수
        exercise_safety = sum(
            100.0 - (ex.difficulty_level * 10.0) for ex in exercises
        ) / len(exercises)

        final_safety = max(
            0.0,
            base_safety - injury_penalty - limitation_penalty + exercise_safety - 50.0,
        )
        return min(100.0, final_safety)

    def _calculate_effectiveness_score(
        self, exercises: List[Exercise], profile: UserProfile
    ) -> float:
        """효과성 점수 계산"""
        if not exercises:
            return 0.0

        # 목표 달성도 계산
        goal_coverage = 0.0
        for goal in profile.goals:
            for exercise in exercises:
                if any(
                    goal.lower() in muscle.lower() for muscle in exercise.target_muscles
                ):
                    goal_coverage += 1.0
                    break

        goal_score = (
            (goal_coverage / len(profile.goals)) * 100.0 if profile.goals else 50.0
        )

        # 운동 다양성 점수
        categories = set(ex.category for ex in exercises)
        diversity_score = min(100.0, len(categories) * 20.0)

        # 총 운동 시간 점수
        total_duration = sum(ex.duration_minutes for ex in exercises)
        duration_score = min(100.0, total_duration * 2.0)

        effectiveness = (goal_score + diversity_score + duration_score) / 3.0
        return min(100.0, effectiveness)

    def optimize_routine(self, routine_id: str) -> PersonalizedRoutine:
        """운동 루틴 최적화"""
        if routine_id not in self.routines:
            raise ValueError(f"Routine not found: {routine_id}")

        routine = self.routines[routine_id]
        profile = self.user_profiles[routine.user_id]

        self.logger.info(f"Optimizing routine {routine_id}")

        # 최적화된 운동 선택
        optimized_exercises = self._select_exercises(profile)

        # 최적화된 루틴 생성
        optimized_routine = PersonalizedRoutine(
            routine_id=f"optimized_{routine_id}",
            user_id=routine.user_id,
            created_at=datetime.now(),
            exercises=optimized_exercises,
            total_duration=sum(ex.duration_minutes for ex in optimized_exercises),
            difficulty_score=self._calculate_difficulty_score(
                optimized_exercises, profile
            ),
            safety_score=self._calculate_safety_score(optimized_exercises, profile),
            effectiveness_score=self._calculate_effectiveness_score(
                optimized_exercises, profile
            ),
        )

        self.routines[optimized_routine.routine_id] = optimized_routine
        self.logger.info(
            f"Optimized routine {routine_id} -> {optimized_routine.routine_id}"
        )
        return optimized_routine

    def generate_report(self) -> Dict[str, Any]:
        """재활 개인화 시스템 리포트 생성"""
        self.logger.info("Generating rehab personalization report")

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_users": len(self.user_profiles),
            "total_routines": len(self.routines),
            "exercise_database_size": len(self.exercise_database),
            "summary": {
                "avg_difficulty_score": 0.0,
                "avg_safety_score": 0.0,
                "avg_effectiveness_score": 0.0,
                "avg_routine_duration": 0.0,
            },
            "user_profiles": list(self.user_profiles.keys()),
            "routines": list(self.routines.keys()),
        }

        # 평균 계산
        if self.routines:
            routines = list(self.routines.values())
            report["summary"]["avg_difficulty_score"] = sum(
                r.difficulty_score for r in routines
            ) / len(routines)
            report["summary"]["avg_safety_score"] = sum(
                r.safety_score for r in routines
            ) / len(routines)
            report["summary"]["avg_effectiveness_score"] = sum(
                r.effectiveness_score for r in routines
            ) / len(routines)
            report["summary"]["avg_routine_duration"] = sum(
                r.total_duration for r in routines
            ) / len(routines)

        return report


def main():
    """메인 실행 함수"""
    print("🚀 재활 개인화 루틴 시스템 시작 (Day 32)")

    engine = RehabPersonalizationEngine()

    # 테스트 사용자 프로필 생성
    test_users = [
        {
            "user_id": "user_001",
            "age": 65,
            "gender": "female",
            "fitness_level": "beginner",
            "injury_history": ["ankle_sprain"],
            "current_limitations": ["knee_pain"],
            "goals": ["balance_improvement", "strength_building"],
            "preferences": {"duration": 30, "equipment": "minimal"},
        },
        {
            "user_id": "user_002",
            "age": 45,
            "gender": "male",
            "fitness_level": "intermediate",
            "injury_history": [],
            "current_limitations": [],
            "goals": ["flexibility", "core_strength"],
            "preferences": {"duration": 45, "equipment": "chair"},
        },
    ]

    # 사용자 프로필 생성 및 루틴 생성
    for user_data in test_users:
        profile = engine.create_user_profile(user_data)
        routine = engine.generate_personalized_routine(profile.user_id)

        print(f"✅ 사용자 {profile.user_id} 루틴 생성 완료")
        print(f"   - 운동 개수: {len(routine.exercises)}개")
        print(f"   - 총 시간: {routine.total_duration}분")
        print(f"   - 난이도: {routine.difficulty_score:.1f}")
        print(f"   - 안전성: {routine.safety_score:.1f}")
        print(f"   - 효과성: {routine.effectiveness_score:.1f}")
        print()

    # 루틴 최적화 테스트
    first_routine_id = list(engine.routines.keys())[0]
    optimized_routine = engine.optimize_routine(first_routine_id)

    print(f"🔄 루틴 최적화 완료: {first_routine_id}")
    print(f"   - 최적화된 난이도: {optimized_routine.difficulty_score:.1f}")
    print(f"   - 최적화된 안전성: {optimized_routine.safety_score:.1f}")
    print(f"   - 최적화된 효과성: {optimized_routine.effectiveness_score:.1f}")
    print()

    # 리포트 생성
    report = engine.generate_report()

    # 리포트 저장
    report_path = (
        f"rehab_personalization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"📋 리포트 생성 완료: {report_path}")
    print(f"👥 총 사용자: {report['total_users']}명")
    print(f"🏃 총 루틴: {report['total_routines']}개")
    print(f"📊 평균 난이도: {report['summary']['avg_difficulty_score']:.1f}")
    print(f"🛡️ 평균 안전성: {report['summary']['avg_safety_score']:.1f}")
    print(f"⚡ 평균 효과성: {report['summary']['avg_effectiveness_score']:.1f}")
    print(f"⏱️ 평균 운동 시간: {report['summary']['avg_routine_duration']:.0f}분")


if __name__ == "__main__":
    main()
