#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 6: 자발적 학습 시스템 간단 테스트
"""

import asyncio

from self_directed_learning_system import SelfDirectedLearningSystem


async def test_simple_learning():
    """간단한 자발적 학습 테스트"""
    print("=== Day 6: 자발적 학습 시스템 간단 테스트 ===")

    try:
        # 시스템 초기화
        print("1. 자발적 학습 시스템 초기화...")
        learning_system = SelfDirectedLearningSystem()
        print("✅ 시스템 초기화 완료")

        # 기본 컨텍스트 설정
        context = {
            "test_mode": True,
            "session_type": "simple_learning",
            "target_domains": ["cognitive", "emotional"],
        }

        # 자발적 학습 세션 실행
        print("\n2. 자발적 학습 세션 실행...")
        result = await learning_system.start_self_directed_learning(context)

        # 결과 출력
        print("\n=== 자발적 학습 세션 결과 ===")
        print(f"세션 ID: {result.session_id}")
        print(f"성공 여부: {result.success}")
        print(f"총 학습 시간: {result.total_learning_time}")
        print(f"평균 참여도: {result.average_engagement:.3f}")
        print(f"전체 진행도: {result.overall_progress:.3f}")

        print(f"\n=== 호기심 트리거 ({len(result.curiosity_triggers)}개) ===")
        for trigger in result.curiosity_triggers[:3]:  # 처음 3개만 출력
            print(f"- {trigger.domain.value}: {trigger.description} (강도: {trigger.intensity:.2f})")

        print(f"\n=== 발견된 문제 ({len(result.discovered_problems)}개) ===")
        for problem in result.discovered_problems[:3]:  # 처음 3개만 출력
            print(f"- {problem.domain.value}: {problem.description} (복잡도: {problem.complexity:.2f})")

        print(f"\n=== 학습 목표 ({len(result.learning_goals)}개) ===")
        for goal in result.learning_goals[:3]:  # 처음 3개만 출력
            print(f"- {goal.target_skill}: {goal.description} (우선순위: {goal.priority:.2f})")

        print(f"\n=== 학습 활동 ({len(result.learning_activities)}개) ===")
        for activity in result.learning_activities[:3]:  # 처음 3개만 출력
            print(f"- {activity.phase.value}: {activity.description} (참여도: {activity.engagement_level:.2f})")

        print(f"\n=== 학습 성과 ({len(result.learning_outcomes)}개) ===")
        for outcome in result.learning_outcomes[:3]:  # 처음 3개만 출력
            print(f"- 기술 향상도: {outcome.skill_improvement:.2f}, 자신감 향상: {outcome.confidence_boost:.2f}")

        # 학습 요약 정보
        print("\n=== 학습 요약 ===")
        summary = await learning_system.get_learning_summary()
        if isinstance(summary, dict) and "total_sessions" in summary:
            print(f"총 세션 수: {summary['total_sessions']}")
            print(f"총 학습 시간: {summary['total_learning_time']}")
            print(f"평균 참여도: {summary['average_engagement']}")
            print(f"평균 진행도: {summary['average_progress']}")
            print(f"영역별 분포: {summary['domain_distribution']}")
        else:
            print(f"학습 요약: {summary}")

        print("\n=== Day 6: 자발적 학습 시스템 테스트 완료 ===")
        return result

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_simple_learning())
