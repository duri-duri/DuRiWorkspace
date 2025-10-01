#!/usr/bin/env python3
"""
V1 프로토콜 통합 재활 시스템 (Day 32 Enhanced)
원장님의 재활 철학과 V1 프로토콜을 완전 통합한 시스템
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class V1ProtocolConfig:
    """V1 프로토콜 설정"""

    session_duration_min: int = 20  # 15-25분
    weekly_frequency: int = 4  # 주 3-5일
    checkup_weeks: int = 4  # 4-6주 점검
    rpe_range: tuple = (4, 6)  # RPE 4-6
    pain_threshold: int = 5  # 통증 ≥5/10
    volume_increase_limit: float = 0.1  # 주간 볼륨 +5-10%
    compliance_threshold: float = 0.6  # 순응도 <60%

    # 자세 관리 원칙
    posture_check_weight_threshold: float = (
        0.7  # 자세 체크 무게 임계값 (최대 무게의 70%)
    )
    posture_collapse_reduction: float = 0.2  # 자세 붕괴 시 무게 감소율 (20%)


@dataclass
class UserProfileV1:
    """V1 프로토콜 사용자 프로필"""

    user_id: str
    age: int
    gender: str
    fitness_level: str
    injury_history: List[str]
    current_limitations: List[str]
    goals: List[str]
    preferences: Dict[str, Any]
    v1_protocol: V1ProtocolConfig
    current_rpe: int = 4
    current_pain_level: int = 0
    compliance_rate: float = 1.0
    session_count: int = 0


@dataclass
class ExerciseV1:
    """V1 프로토콜 운동"""

    exercise_id: str
    name: str
    category: str
    difficulty_level: int
    target_muscles: List[str]
    equipment_needed: List[str]
    safety_notes: List[str]
    duration_minutes: int
    reps_sets: str
    rpe_level: int
    pain_sensitivity: str  # low, medium, high


@dataclass
class PersonalizedRoutineV1:
    """V1 프로토콜 개인화 루틴"""

    routine_id: str
    user_id: str
    created_at: datetime
    exercises: List[ExerciseV1]
    total_duration: int
    difficulty_score: float
    safety_score: float
    effectiveness_score: float
    v1_compliance_score: float
    rpe_score: float
    pain_management_score: float


class V1ProtocolRehabSystem:
    """V1 프로토콜 통합 재활 시스템"""

    def __init__(self):
        self.v1_config = V1ProtocolConfig()
        self.exercise_database = self._load_v1_exercise_database()
        self.user_profiles = {}
        self.routines = {}
        self.logger = self._setup_logging()

    def _load_v1_exercise_database(self) -> Dict[str, ExerciseV1]:
        """V1 프로토콜 운동 데이터베이스"""
        exercises = {
            "stretch_neck": ExerciseV1(
                exercise_id="stretch_neck",
                name="목 스트레칭",
                category="stretching",
                difficulty_level=1,
                target_muscles=["neck", "shoulders"],
                equipment_needed=[],
                safety_notes=["천천히 움직이기", "통증 시 중단"],
                duration_minutes=3,
                reps_sets="10회 x 2세트",
                rpe_level=3,
                pain_sensitivity="low",
            ),
            "wall_pushup": ExerciseV1(
                exercise_id="wall_pushup",
                name="벽 푸시업",
                category="strength",
                difficulty_level=2,
                target_muscles=["chest", "shoulders", "triceps"],
                equipment_needed=["wall"],
                safety_notes=["벽에 기대어 안전하게", "무릎 부드럽게"],
                duration_minutes=5,
                reps_sets="8회 x 2세트",
                rpe_level=4,
                pain_sensitivity="medium",
            ),
            "chair_squat": ExerciseV1(
                exercise_id="chair_squat",
                name="의자 스쿼트",
                category="strength",
                difficulty_level=2,
                target_muscles=["quadriceps", "glutes", "core"],
                equipment_needed=["chair"],
                safety_notes=["의자에 앉았다 일어나기", "무릎이 발끝을 넘지 않게"],
                duration_minutes=5,
                reps_sets="8회 x 2세트",
                rpe_level=5,
                pain_sensitivity="high",
            ),
            "balance_stand": ExerciseV1(
                exercise_id="balance_stand",
                name="균형 서기",
                category="balance",
                difficulty_level=1,
                target_muscles=["core", "legs"],
                equipment_needed=[],
                safety_notes=["벽이나 의자에 손 대고", "넘어지지 않게 주의"],
                duration_minutes=3,
                reps_sets="20초 x 2세트",
                rpe_level=3,
                pain_sensitivity="low",
            ),
            "ankle_circles": ExerciseV1(
                exercise_id="ankle_circles",
                name="발목 원형 운동",
                category="mobility",
                difficulty_level=1,
                target_muscles=["ankles", "calves"],
                equipment_needed=[],
                safety_notes=["천천히 원형으로", "통증 시 중단"],
                duration_minutes=3,
                reps_sets="8회 x 2세트",
                rpe_level=2,
                pain_sensitivity="low",
            ),
        }
        return exercises

    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger("v1_protocol_rehab")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(
            f"v1_protocol_rehab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def create_user_profile_v1(self, user_data: Dict[str, Any]) -> UserProfileV1:
        """V1 프로토콜 사용자 프로필 생성"""
        profile = UserProfileV1(
            user_id=user_data["user_id"],
            age=user_data["age"],
            gender=user_data["gender"],
            fitness_level=user_data["fitness_level"],
            injury_history=user_data.get("injury_history", []),
            current_limitations=user_data.get("current_limitations", []),
            goals=user_data.get("goals", []),
            preferences=user_data.get("preferences", {}),
            v1_protocol=self.v1_config,
            current_rpe=user_data.get("current_rpe", 4),
            current_pain_level=user_data.get("current_pain_level", 0),
            compliance_rate=user_data.get("compliance_rate", 1.0),
            session_count=user_data.get("session_count", 0),
        )

        self.user_profiles[profile.user_id] = profile
        self.logger.info(f"Created V1 protocol user profile for {profile.user_id}")
        return profile

    def generate_v1_routine(self, user_id: str) -> PersonalizedRoutineV1:
        """V1 프로토콜 개인화 루틴 생성"""
        if user_id not in self.user_profiles:
            raise ValueError(f"User profile not found: {user_id}")

        profile = self.user_profiles[user_id]
        self.logger.info(f"Generating V1 protocol routine for {user_id}")

        # V1 프로토콜 준수 운동 선택
        selected_exercises = self._select_v1_exercises(profile)

        routine = PersonalizedRoutineV1(
            routine_id=f"v1_routine_{user_id}_{int(time.time())}",
            user_id=user_id,
            created_at=datetime.now(),
            exercises=selected_exercises,
            total_duration=sum(ex.duration_minutes for ex in selected_exercises),
            difficulty_score=self._calculate_v1_difficulty_score(
                selected_exercises, profile
            ),
            safety_score=self._calculate_v1_safety_score(selected_exercises, profile),
            effectiveness_score=self._calculate_v1_effectiveness_score(
                selected_exercises, profile
            ),
            v1_compliance_score=self._calculate_v1_compliance_score(
                selected_exercises, profile
            ),
            rpe_score=self._calculate_v1_rpe_score(selected_exercises, profile),
            pain_management_score=self._calculate_v1_pain_management_score(
                selected_exercises, profile
            ),
        )

        self.routines[routine.routine_id] = routine
        self.logger.info(f"Generated V1 routine {routine.routine_id}")
        return routine

    def _select_v1_exercises(self, profile: UserProfileV1) -> List[ExerciseV1]:
        """V1 프로토콜에 따른 운동 선택"""
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

        # V1 프로토콜 준수 필터링
        filtered_exercises = []
        for exercise in selected:
            # 통증 관리: 현재 통증 레벨이 높으면 통증 민감도가 높은 운동 제외
            if profile.current_pain_level >= profile.v1_protocol.pain_threshold:
                if exercise.pain_sensitivity == "high":
                    continue

            # RPE 관리: 현재 RPE가 높으면 RPE 레벨이 높은 운동 제외
            if profile.current_rpe >= profile.v1_protocol.rpe_range[1]:
                if exercise.rpe_level > profile.current_rpe:
                    continue

            # 순응도 관리: 순응도가 낮으면 운동 수 줄이기
            if profile.compliance_rate < profile.v1_protocol.compliance_threshold:
                if len(filtered_exercises) >= 3:  # 최대 3개로 제한
                    break

            filtered_exercises.append(exercise)

        return filtered_exercises

    def _calculate_v1_difficulty_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 난이도 점수"""
        if not exercises:
            return 0.0

        avg_difficulty = sum(ex.difficulty_level for ex in exercises) / len(exercises)

        # V1 프로토콜 조정
        fitness_multiplier = {
            "beginner": 0.8,
            "intermediate": 1.0,
            "advanced": 1.2,
        }.get(profile.fitness_level, 1.0)

        # 순응도 조정
        compliance_multiplier = max(0.5, profile.compliance_rate)

        return min(5.0, avg_difficulty * fitness_multiplier * compliance_multiplier)

    def _calculate_v1_safety_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 안전성 점수 (Day 32 Enhanced)"""
        if not exercises:
            return 0.0

        base_safety = 100.0

        # 통증 관리 점수 (완화된 감점)
        pain_management = 0.0
        for exercise in exercises:
            if profile.current_pain_level >= profile.v1_protocol.pain_threshold:
                if exercise.pain_sensitivity == "high":
                    pain_management -= 10.0  # 20.0 → 10.0으로 완화
                elif exercise.pain_sensitivity == "medium":
                    pain_management -= 5.0  # 10.0 → 5.0으로 완화

        # RPE 관리 점수 (완화된 감점)
        rpe_management = 0.0
        for exercise in exercises:
            if exercise.rpe_level > profile.current_rpe:
                rpe_management -= 8.0  # 15.0 → 8.0으로 완화

        # 안전성 보너스 (V1 프로토콜 준수)
        safety_bonus = 5.0  # V1 프로토콜 준수 보너스

        final_safety = base_safety + pain_management + rpe_management + safety_bonus
        return max(0.0, min(100.0, final_safety))

    def _calculate_v1_effectiveness_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 효과성 점수"""
        if not exercises:
            return 0.0

        # 목표 달성도
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

        # 운동 다양성
        categories = set(ex.category for ex in exercises)
        diversity_score = min(100.0, len(categories) * 20.0)

        # V1 프로토콜 준수도
        v1_compliance = self._calculate_v1_compliance_score(exercises, profile)

        effectiveness = (goal_score + diversity_score + v1_compliance) / 3.0
        return min(100.0, effectiveness)

    def _calculate_v1_compliance_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 준수도 점수"""
        score = 100.0

        # 세션 시간 준수 (15-25분)
        total_duration = sum(ex.duration_minutes for ex in exercises)
        if total_duration < profile.v1_protocol.session_duration_min - 5:
            score -= 20.0
        elif total_duration > profile.v1_protocol.session_duration_min + 5:
            score -= 10.0

        # RPE 범위 준수 (4-6)
        avg_rpe = (
            sum(ex.rpe_level for ex in exercises) / len(exercises) if exercises else 0
        )
        if avg_rpe < profile.v1_protocol.rpe_range[0]:
            score -= 15.0
        elif avg_rpe > profile.v1_protocol.rpe_range[1]:
            score -= 25.0

        # 통증 관리 준수
        if profile.current_pain_level >= profile.v1_protocol.pain_threshold:
            high_pain_exercises = [
                ex for ex in exercises if ex.pain_sensitivity == "high"
            ]
            if high_pain_exercises:
                score -= 30.0

        return max(0.0, score)

    def _calculate_v1_rpe_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 RPE 점수"""
        if not exercises:
            return 0.0

        avg_rpe = sum(ex.rpe_level for ex in exercises) / len(exercises)
        target_rpe = (
            profile.v1_protocol.rpe_range[0] + profile.v1_protocol.rpe_range[1]
        ) / 2

        # RPE 차이에 따른 점수 계산
        rpe_diff = abs(avg_rpe - target_rpe)
        if rpe_diff <= 0.5:
            return 100.0
        elif rpe_diff <= 1.0:
            return 80.0
        elif rpe_diff <= 1.5:
            return 60.0
        else:
            return 40.0

    def _calculate_v1_pain_management_score(
        self, exercises: List[ExerciseV1], profile: UserProfileV1
    ) -> float:
        """V1 프로토콜 통증 관리 점수"""
        if profile.current_pain_level < profile.v1_protocol.pain_threshold:
            return 100.0

        score = 100.0
        for exercise in exercises:
            if exercise.pain_sensitivity == "high":
                score -= 30.0
            elif exercise.pain_sensitivity == "medium":
                score -= 15.0

        return max(0.0, score)

    def generate_v1_report(self) -> Dict[str, Any]:
        """V1 프로토콜 시스템 리포트"""
        self.logger.info("Generating V1 protocol report")

        report = {
            "timestamp": datetime.now().isoformat(),
            "v1_protocol_version": "1.0",
            "total_users": len(self.user_profiles),
            "total_routines": len(self.routines),
            "v1_protocol_config": {
                "session_duration_min": self.v1_config.session_duration_min,
                "weekly_frequency": self.v1_config.weekly_frequency,
                "checkup_weeks": self.v1_config.checkup_weeks,
                "rpe_range": self.v1_config.rpe_range,
                "pain_threshold": self.v1_config.pain_threshold,
                "volume_increase_limit": self.v1_config.volume_increase_limit,
                "compliance_threshold": self.v1_config.compliance_threshold,
            },
            "summary": {
                "avg_difficulty_score": 0.0,
                "avg_safety_score": 0.0,
                "avg_effectiveness_score": 0.0,
                "avg_v1_compliance_score": 0.0,
                "avg_rpe_score": 0.0,
                "avg_pain_management_score": 0.0,
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
            report["summary"]["avg_v1_compliance_score"] = sum(
                r.v1_compliance_score for r in routines
            ) / len(routines)
            report["summary"]["avg_rpe_score"] = sum(
                r.rpe_score for r in routines
            ) / len(routines)
            report["summary"]["avg_pain_management_score"] = sum(
                r.pain_management_score for r in routines
            ) / len(routines)
            report["summary"]["avg_routine_duration"] = sum(
                r.total_duration for r in routines
            ) / len(routines)

        return report


def main():
    """메인 실행 함수"""
    print("🚀 V1 프로토콜 통합 재활 시스템 시작 (Day 32 Enhanced)")

    system = V1ProtocolRehabSystem()

    # V1 프로토콜 테스트 사용자
    test_users = [
        {
            "user_id": "v1_user_001",
            "age": 65,
            "gender": "female",
            "fitness_level": "beginner",
            "injury_history": ["ankle_sprain"],
            "current_limitations": ["knee_pain"],
            "goals": ["balance_improvement", "strength_building"],
            "preferences": {"duration": 20, "equipment": "minimal"},
            "current_rpe": 4,
            "current_pain_level": 3,
            "compliance_rate": 0.8,
            "session_count": 5,
        },
        {
            "user_id": "v1_user_002",
            "age": 45,
            "gender": "male",
            "fitness_level": "intermediate",
            "injury_history": [],
            "current_limitations": [],
            "goals": ["flexibility", "core_strength"],
            "preferences": {"duration": 25, "equipment": "chair"},
            "current_rpe": 5,
            "current_pain_level": 1,
            "compliance_rate": 0.9,
            "session_count": 12,
        },
    ]

    # V1 프로토콜 사용자 프로필 생성 및 루틴 생성
    for user_data in test_users:
        profile = system.create_user_profile_v1(user_data)
        routine = system.generate_v1_routine(profile.user_id)

        print(f"✅ V1 프로토콜 사용자 {profile.user_id} 루틴 생성 완료")
        print(f"   - 운동 개수: {len(routine.exercises)}개")
        print(f"   - 총 시간: {routine.total_duration}분")
        print(f"   - 난이도: {routine.difficulty_score:.1f}")
        print(f"   - 안전성: {routine.safety_score:.1f}")
        print(f"   - 효과성: {routine.effectiveness_score:.1f}")
        print(f"   - V1 준수도: {routine.v1_compliance_score:.1f}")
        print(f"   - RPE 점수: {routine.rpe_score:.1f}")
        print(f"   - 통증 관리: {routine.pain_management_score:.1f}")
        print()

    # V1 프로토콜 리포트 생성
    report = system.generate_v1_report()

    # 리포트 저장
    report_path = f"v1_protocol_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"📋 V1 프로토콜 리포트 생성 완료: {report_path}")
    print(f"👥 총 사용자: {report['total_users']}명")
    print(f"🏃 총 루틴: {report['total_routines']}개")
    print(f"📊 평균 난이도: {report['summary']['avg_difficulty_score']:.1f}")
    print(f"🛡️ 평균 안전성: {report['summary']['avg_safety_score']:.1f}")
    print(f"⚡ 평균 효과성: {report['summary']['avg_effectiveness_score']:.1f}")
    print(f"✅ 평균 V1 준수도: {report['summary']['avg_v1_compliance_score']:.1f}")
    print(f"💪 평균 RPE 점수: {report['summary']['avg_rpe_score']:.1f}")
    print(f"🩹 평균 통증 관리: {report['summary']['avg_pain_management_score']:.1f}")
    print(f"⏱️ 평균 운동 시간: {report['summary']['avg_routine_duration']:.0f}분")


if __name__ == "__main__":
    main()
