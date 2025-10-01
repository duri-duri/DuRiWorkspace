#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 7: 창의적 문제 해결 시스템 간단 테스트
"""

import asyncio
import json
from datetime import datetime

from creative_problem_solving_system import (
    CreativeProblem,
    CreativeProblemSolvingSystem,
    ProblemComplexity,
    ProblemType,
)


async def test_simple_creative_problem_solving():
    """간단한 창의적 문제 해결 테스트"""
    print("=== Day 7: 창의적 문제 해결 시스템 간단 테스트 ===")

    try:
        # 시스템 초기화
        print("1. 창의적 문제 해결 시스템 초기화...")
        solving_system = CreativeProblemSolvingSystem()
        print("✅ 시스템 초기화 완료")

        # 테스트 문제 생성
        test_problem = CreativeProblem(
            problem_id="test_problem_001",
            title="지속가능한 도시 교통 시스템 설계",
            description="기존의 자동차 중심 교통 시스템을 환경 친화적이고 효율적인 지속가능한 교통 시스템으로 전환하는 방안을 설계해야 합니다.",
            problem_type=ProblemType.SYSTEMIC,
            complexity=ProblemComplexity.COMPLEX,
            constraints=["예산 제한", "기존 인프라 활용", "시민 수용성"],
            stakeholders=["시민", "정부", "교통업체", "환경단체"],
        )

        # 창의적 문제 해결 실행
        context = {
            "test_mode": True,
            "problem_domain": "urban_planning",
            "stakeholder_needs": ["accessibility", "sustainability", "efficiency"],
        }

        print("\n2. 창의적 문제 해결 실행...")
        result = await solving_system.solve_creative_problem(test_problem, context)

        # 결과 출력
        print(f"\n=== 창의적 문제 해결 결과 ===")
        print(f"프로세스 ID: {result.process_id}")
        print(f"문제: {result.problem.title}")
        print(f"성공 여부: {result.success}")
        print(f"해결 시간: {result.solving_duration:.2f}초")
        print(f"전체 품질: {result.overall_quality.value}")

        print(f"\n=== 문제 재정의 ({len(result.problem_reframes)}개) ===")
        for reframe in result.problem_reframes[:3]:  # 처음 3개만 출력
            print(
                f"- {reframe.reframed_title} (접근법: {reframe.reframe_approach.value})"
            )

        print(f"\n=== 창의적 해결책 ({len(result.solutions)}개) ===")
        for solution in result.solutions[:3]:  # 처음 3개만 출력
            print(
                f"- {solution.title} (품질: {solution.quality.value}, 점수: {solution.overall_score:.2f})"
            )

        print(f"\n=== 창의적 패턴 ({len(result.patterns_used)}개) ===")
        for pattern in result.patterns_used:
            print(f"- {pattern.pattern_name} (성공률: {pattern.success_rate:.2f})")

        print(f"\n=== 검증 결과 ({len(result.validations)}개) ===")
        for validation in result.validations[:3]:  # 처음 3개만 출력
            print(
                f"- {validation.validation_method}: {validation.validation_score:.2f}"
            )

        print(f"\n=== 성과 지표 ===")
        print(f"평균 혁신성 점수: {result.average_innovation_score:.3f}")
        print(f"평균 실행 가능성 점수: {result.average_feasibility_score:.3f}")
        print(f"평균 영향도 점수: {result.average_impact_score:.3f}")

        # 시스템 요약 정보
        print(f"\n=== 시스템 요약 ===")
        summary = await solving_system.get_creative_problem_solving_summary()
        print(f"총 해결된 문제: {summary['total_problems_solved']}")
        print(f"평균 해결 시간: {summary['average_solving_time']}초")
        print(f"성공률: {summary['success_rate']}")
        print(f"총 해결책: {summary['total_solutions']}")
        print(f"총 검증: {summary['total_validations']}")
        print(f"창의적 패턴: {summary['creative_patterns']}개")

        print("\n=== Day 7: 창의적 문제 해결 시스템 테스트 완료 ===")
        return result

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_simple_creative_problem_solving())
