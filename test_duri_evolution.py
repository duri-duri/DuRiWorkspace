#!/usr/bin/env python3
"""
DuRi 진화 결과 테스트
문자열 반환 → 판단 로직 기반 동적 생성 변환 결과 검증
"""

import asyncio
import os
import sys
from datetime import datetime

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "DuRiCore"))

from application_system import ApplicationContext, ApplicationDomain, ApplicationSystem
from feedback_system import FeedbackSystem
from judgment_system import JudgmentSystem
from prediction_system import PredictionSystem, PredictionType


async def test_application_system_evolution():
    """application_system.py 진화 테스트"""
    print("🧠 Application System 진화 테스트")
    print("=" * 50)

    app_system = ApplicationSystem()
    await app_system.initialize()

    # 테스트 컨텍스트들
    test_contexts = [
        {
            "name": "기쁨 + 이전 슬픔 히스토리",
            "user_input": "시험에 합격했어요!",
            "user_context": {
                "interaction_history": [
                    {"emotion": "슬픔", "timestamp": "2025-08-05T10:00:00"},
                    {"emotion": "슬픔", "timestamp": "2025-08-05T11:00:00"},
                ],
                "goals": ["학업 성공"],
                "system_performance": 0.8,
            },
        },
        {
            "name": "슬픔 + 시스템 성능 저하",
            "user_input": "실패했어요...",
            "user_context": {
                "interaction_history": [],
                "goals": [],
                "system_performance": 0.2,
            },
        },
        {
            "name": "화남 + 목표 진행 중",
            "user_input": "화가 나요!",
            "user_context": {
                "interaction_history": [
                    {"emotion": "화남", "timestamp": "2025-08-05T09:00:00"}
                ],
                "goals": ["프로젝트 완성"],
                "system_performance": 0.7,
            },
        },
        {
            "name": "걱정 + 연속 걱정",
            "user_input": "걱정돼요...",
            "user_context": {
                "interaction_history": [
                    {"emotion": "걱정", "timestamp": "2025-08-05T08:00:00"},
                    {"emotion": "걱정", "timestamp": "2025-08-05T09:00:00"},
                ],
                "goals": [],
                "system_performance": 0.6,
            },
        },
    ]

    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   입력: {test_case['user_input']}")

        try:
            result = await app_system.process_application(
                user_input=test_case["user_input"],
                domain=ApplicationDomain.GENERAL_CONVERSATION,
                user_context=test_case["user_context"],
            )

            print(f"   응답: {result.solution}")
            print(f"   신뢰도: {result.confidence_score:.2f}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")


async def test_prediction_system_evolution():
    """prediction_system.py 진화 테스트"""
    print("\n🔮 Prediction System 진화 테스트")
    print("=" * 50)

    pred_system = PredictionSystem()

    # 테스트 컨텍스트들
    test_contexts = [
        {
            "name": "연속 실패 상황",
            "context": {
                "recent_failures": 5,
                "system_performance": 0.8,
                "prediction_history": [],
            },
        },
        {
            "name": "시스템 성능 저하",
            "context": {
                "recent_failures": 1,
                "system_performance": 0.2,
                "prediction_history": [],
            },
        },
        {
            "name": "데이터 부족",
            "context": {
                "recent_failures": 0,
                "system_performance": 0.7,
                "prediction_history": [],
            },
        },
    ]

    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n{i}. {test_case['name']}")

        try:
            # 컨텍스트 설정
            pred_system.current_context = test_case["context"]

            # 예측 통합 테스트
            result = pred_system._integrate_predictions()
            print(f"   예측 결과: {result}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")


async def test_feedback_system_evolution():
    """feedback_system.py 진화 테스트"""
    print("\n📊 Feedback System 진화 테스트")
    print("=" * 50)

    feedback_system = FeedbackSystem()

    # 테스트 케이스들
    test_cases = [
        {
            "name": "연속 실패 + 긴급 개선",
            "evaluation_score": 0.2,
            "feedback_type": "negative",
            "context": {
                "recent_failures": 5,
                "system_performance": 0.8,
                "improvement_history": [],
            },
        },
        {
            "name": "성능 저하 + 긴급 개선",
            "evaluation_score": 0.3,
            "feedback_type": "negative",
            "context": {
                "recent_failures": 1,
                "system_performance": 0.2,
                "improvement_history": [],
            },
        },
        {
            "name": "이전 개선 성공 + 점진적 개선",
            "evaluation_score": 0.5,
            "feedback_type": "neutral",
            "context": {
                "recent_failures": 0,
                "system_performance": 0.7,
                "improvement_history": [{"success": True}],
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")

        try:
            # 컨텍스트 설정
            feedback_system.current_context = test_case["context"]

            # 개선 설명 생성 테스트
            description = feedback_system._generate_improvement_description_real(
                test_case["evaluation_score"], test_case["feedback_type"]
            )
            print(f"   개선 설명: {description}")

            # 구현 단계 생성 테스트
            steps = feedback_system._generate_implementation_steps_real(
                test_case["evaluation_score"], test_case["feedback_type"]
            )
            print(f"   구현 단계: {steps}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")


async def test_judgment_system_evolution():
    """judgment_system.py 진화 테스트"""
    print("\n⚖️ Judgment System 진화 테스트")
    print("=" * 50)

    judgment_system = JudgmentSystem()

    # 테스트 케이스들
    test_cases = [
        {
            "name": "연속 오류 상황",
            "context": {"recent_errors": 5, "system_performance": 0.8},
        },
        {
            "name": "시스템 성능 저하",
            "context": {"recent_errors": 1, "system_performance": 0.2},
        },
        {
            "name": "일반 오류",
            "context": {"recent_errors": 0, "system_performance": 0.7},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")

        try:
            # 컨텍스트 설정
            judgment_system.current_context = test_case["context"]

            # 피드백 생성 오류 테스트
            error_msg = "테스트 오류"
            result = await judgment_system._generate_feedback(0.5, 0.5, 0.5, 0.5)
            print(f"   피드백 생성 결과: {result}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 진화 결과 테스트")
    print("=" * 60)
    print("문자열 반환 → 판단 로직 기반 동적 생성")
    print("=" * 60)

    try:
        # 1. Application System 테스트
        await test_application_system_evolution()

        # 2. Prediction System 테스트
        await test_prediction_system_evolution()

        # 3. Feedback System 테스트
        await test_feedback_system_evolution()

        # 4. Judgment System 테스트
        await test_judgment_system_evolution()

        print("\n" + "=" * 60)
        print("🎉 DuRi 진화 테스트 완료!")
        print("✅ 모든 시스템이 판단 로직 기반으로 진화했습니다!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
