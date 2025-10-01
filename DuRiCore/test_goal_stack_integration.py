#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.4 - Goal Stack 시스템 통합 테스트
Goal Stack 시스템이 통합 시스템 매니저에 제대로 통합되었는지 확인
"""

import asyncio
from datetime import datetime
import json
import logging
import time
from typing import Any, Dict, List

from goal_stack_system import GoalPriority, GoalStackSystem, GoalStatus, GoalType

# 테스트 대상 시스템들
from integrated_system_manager import IntegratedSystemManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GoalStackIntegrationTest:
    """Goal Stack 시스템 통합 테스트"""

    def __init__(self):
        """초기화"""
        self.integrated_manager = IntegratedSystemManager()
        self.goal_stack_system = GoalStackSystem()
        self.test_results = []

    async def run_comprehensive_test(self):
        """종합 테스트 실행"""
        logger.info("=== Goal Stack 시스템 통합 테스트 시작 ===")

        test_suites = [
            self.test_goal_stack_basic_functionality,
            self.test_goal_stack_integration,
            self.test_goal_priority_system,
            self.test_goal_conflict_resolution,
            self.test_goal_based_behavior_control,
            self.test_integrated_cycle_with_goals,
        ]

        for test_suite in test_suites:
            try:
                result = await test_suite()
                self.test_results.append(result)
                logger.info(
                    f"테스트 완료: {result['test_name']} - 성공: {result['success']}"
                )
            except Exception as e:
                error_result = {
                    "test_name": test_suite.__name__,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                self.test_results.append(error_result)
                logger.error(f"테스트 실패: {test_suite.__name__} - {e}")

        # 전체 결과 요약
        await self.generate_test_summary()

    async def test_goal_stack_basic_functionality(self) -> Dict[str, Any]:
        """Goal Stack 기본 기능 테스트"""
        test_name = "Goal Stack 기본 기능 테스트"
        start_time = time.time()

        try:
            # 1. 목표 생성 테스트
            goal1 = self.goal_stack_system.create_goal(
                name="프로젝트 완료",
                description="중요한 프로젝트를 완료합니다",
                goal_type=GoalType.ACHIEVEMENT,
                priority=GoalPriority.HIGH,
                emotional_weight=0.8,
            )

            goal2 = self.goal_stack_system.create_goal(
                name="학습 진행",
                description="새로운 기술을 학습합니다",
                goal_type=GoalType.LEARNING,
                priority=GoalPriority.MEDIUM,
                emotional_weight=0.6,
            )

            # 2. 하위목표 생성 테스트
            sub_goal = self.goal_stack_system.create_sub_goal(
                parent_goal_id=goal1.id,
                name="요구사항 분석",
                description="프로젝트 요구사항을 분석합니다",
                priority=GoalPriority.HIGH,
            )

            # 3. 진행률 업데이트 테스트
            self.goal_stack_system.update_goal_progress(goal1.id, 0.3)
            self.goal_stack_system.update_goal_progress(goal2.id, 0.7)

            # 4. 활성 목표 확인
            active_goals = self.goal_stack_system.get_active_goals()
            stack_status = self.goal_stack_system.get_goal_stack_status()

            # 검증
            assert len(active_goals) > 0, "활성 목표가 없음"
            assert stack_status["active_goals_count"] > 0, "활성 목표 수가 0"
            assert goal1.progress == 0.3, "진행률 업데이트 실패"
            assert goal2.progress == 0.7, "진행률 업데이트 실패"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "active_goals_count": len(active_goals),
                "stack_utilization": stack_status["stack_utilization"],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_goal_stack_integration(self) -> Dict[str, Any]:
        """Goal Stack 통합 시스템 테스트"""
        test_name = "Goal Stack 통합 시스템 테스트"
        start_time = time.time()

        try:
            # 통합 시스템 매니저에서 Goal Stack 시스템 접근
            goal_stack_system = self.integrated_manager.goal_stack_system

            # 목표 생성
            goal = goal_stack_system.create_goal(
                name="통합 테스트 목표",
                description="통합 시스템 테스트를 위한 목표",
                goal_type=GoalType.ACHIEVEMENT,
                priority=GoalPriority.HIGH,
            )

            # 통합 사이클에서 Goal Stack 시스템 실행
            context = {
                "situation": "통합 테스트 상황",
                "available_resources": ["time", "energy", "attention"],
                "emotion": {"type": "excited", "intensity": 0.7},
            }

            goal_result = await self.integrated_manager._execute_goal_stack_system(
                context
            )

            # 검증
            assert "active_goals" in goal_result, "활성 목표 정보 없음"
            assert "stack_status" in goal_result, "스택 상태 정보 없음"
            assert "next_action" in goal_result, "다음 행동 추천 없음"
            assert "current_focus" in goal_result, "현재 집중 정보 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "goal_result_keys": list(goal_result.keys()),
                "active_goals_count": len(goal_result["active_goals"]),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_goal_priority_system(self) -> Dict[str, Any]:
        """목표 우선순위 시스템 테스트"""
        test_name = "목표 우선순위 시스템 테스트"
        start_time = time.time()

        try:
            # 다양한 우선순위의 목표 생성
            goals = []
            priorities = [
                GoalPriority.CRITICAL,
                GoalPriority.HIGH,
                GoalPriority.MEDIUM,
                GoalPriority.LOW,
            ]

            for i, priority in enumerate(priorities):
                goal = self.goal_stack_system.create_goal(
                    name=f"우선순위 테스트 목표 {i+1}",
                    description=f"우선순위 {priority.name} 테스트",
                    goal_type=GoalType.ACHIEVEMENT,
                    priority=priority,
                    emotional_weight=0.5 + (i * 0.1),
                )
                goals.append(goal)

            # 우선순위 점수 계산
            context = {"available_resources": ["time", "energy"]}
            priority_scores = []

            for goal in goals:
                score = self.goal_stack_system.calculate_goal_priority_score(
                    goal, context
                )
                priority_scores.append(
                    {
                        "goal_name": goal.name,
                        "priority": goal.priority.name,
                        "score": score,
                    }
                )

            # 우선순위별 정렬 확인
            sorted_scores = sorted(
                priority_scores, key=lambda x: x["score"], reverse=True
            )

            # 검증
            assert len(priority_scores) == len(goals), "우선순위 점수 계산 실패"
            assert sorted_scores[0]["priority"] == "CRITICAL", "최고 우선순위 확인 실패"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "priority_scores": priority_scores,
                "highest_priority": sorted_scores[0]["goal_name"],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_goal_conflict_resolution(self) -> Dict[str, Any]:
        """목표 충돌 해결 시스템 테스트"""
        test_name = "목표 충돌 해결 시스템 테스트"
        start_time = time.time()

        try:
            # 충돌이 발생할 수 있는 목표들 생성
            conflict_goal1 = self.goal_stack_system.create_goal(
                name="충돌 목표 1",
                description="리소스 충돌 테스트",
                goal_type=GoalType.ACHIEVEMENT,
                priority=GoalPriority.HIGH,
                resources=["time", "energy"],
            )

            conflict_goal2 = self.goal_stack_system.create_goal(
                name="충돌 목표 2",
                description="리소스 충돌 테스트",
                goal_type=GoalType.ACHIEVEMENT,
                priority=GoalPriority.MEDIUM,
                resources=["time", "energy"],
            )

            # 충돌 해결 실행
            conflicts = self.goal_stack_system.resolve_goal_conflicts()

            # 검증
            assert isinstance(conflicts, list), "충돌 해결 결과가 리스트가 아님"

            # 충돌 해결 후 상태 확인
            active_goals = self.goal_stack_system.get_active_goals()
            suspended_goals = self.goal_stack_system.goal_stack.suspended_goals

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "conflicts_found": len(conflicts),
                "active_goals_after_resolution": len(active_goals),
                "suspended_goals_after_resolution": len(suspended_goals),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_goal_based_behavior_control(self) -> Dict[str, Any]:
        """목표 기반 행동 제어 테스트"""
        test_name = "목표 기반 행동 제어 테스트"
        start_time = time.time()

        try:
            # 다양한 유형의 목표 생성
            achievement_goal = self.goal_stack_system.create_goal(
                name="달성 목표",
                description="달성형 목표 테스트",
                goal_type=GoalType.ACHIEVEMENT,
                priority=GoalPriority.HIGH,
            )

            learning_goal = self.goal_stack_system.create_goal(
                name="학습 목표",
                description="학습형 목표 테스트",
                goal_type=GoalType.LEARNING,
                priority=GoalPriority.MEDIUM,
            )

            creative_goal = self.goal_stack_system.create_goal(
                name="창의적 목표",
                description="창의형 목표 테스트",
                goal_type=GoalType.CREATIVE,
                priority=GoalPriority.LOW,
            )

            # 목표별 행동 추천 테스트
            context = {"available_resources": ["time", "energy", "creativity"]}

            achievement_action = self.goal_stack_system.get_next_action_recommendation(
                context
            )

            # 검증
            assert "action" in achievement_action, "행동 추천에 action 필드 없음"
            assert "goal_id" in achievement_action, "행동 추천에 goal_id 필드 없음"
            assert "reason" in achievement_action, "행동 추천에 reason 필드 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "recommended_action": achievement_action["action"],
                "goal_type": achievement_action.get("goal_name", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_integrated_cycle_with_goals(self) -> Dict[str, Any]:
        """목표가 포함된 통합 사이클 테스트"""
        test_name = "목표가 포함된 통합 사이클 테스트"
        start_time = time.time()

        try:
            # 통합 사이클 실행을 위한 컨텍스트
            context = {
                "situation": "목표 기반 통합 테스트",
                "priority": "high",
                "complexity": "medium",
                "available_resources": ["time", "energy", "attention"],
                "emotion": {"type": "focused", "intensity": 0.8},
            }

            # 통합 사이클 실행
            result = await self.integrated_manager.run_integrated_cycle(context)

            # 검증
            assert "goal_result" in result, "통합 결과에 goal_result 없음"
            assert "overall_score" in result, "통합 결과에 overall_score 없음"
            assert "duration" in result, "통합 결과에 duration 없음"

            goal_result = result["goal_result"]
            assert "active_goals" in goal_result, "목표 결과에 active_goals 없음"
            assert "next_action" in goal_result, "목표 결과에 next_action 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "overall_score": result["overall_score"],
                "goal_result_keys": list(goal_result.keys()),
                "active_goals_in_cycle": len(goal_result["active_goals"]),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def generate_test_summary(self):
        """테스트 결과 요약 생성"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests

        total_duration = sum(result.get("duration", 0) for result in self.test_results)

        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (successful_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results,
        }

        # 결과 출력
        print("\n=== Goal Stack 시스템 통합 테스트 결과 ===")
        print(f"총 테스트 수: {total_tests}")
        print(f"성공한 테스트: {successful_tests}")
        print(f"실패한 테스트: {failed_tests}")
        print(f"성공률: {summary['test_summary']['success_rate']:.1f}%")
        print(f"총 소요 시간: {total_duration:.3f}초")

        # 실패한 테스트들 출력
        if failed_tests > 0:
            print("\n실패한 테스트들:")
            for result in self.test_results:
                if not result["success"]:
                    print(
                        f"  - {result['test_name']}: {result.get('error', 'Unknown error')}"
                    )

        # 결과를 파일로 저장
        with open(
            "goal_stack_integration_test_results.json", "w", encoding="utf-8"
        ) as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info(
            "테스트 결과가 goal_stack_integration_test_results.json에 저장되었습니다."
        )
        return summary


async def main():
    """메인 테스트 실행"""
    tester = GoalStackIntegrationTest()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
