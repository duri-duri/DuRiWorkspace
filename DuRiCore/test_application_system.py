#!/usr/bin/env python3
"""
DuRiCore Phase 7 - 실제 응용 시스템 테스트
도메인별 특화 모듈과 실제 문제 해결 능력 테스트
"""

import asyncio
import json
import time
from datetime import datetime

from application_system import (ApplicationDomain, ApplicationSystem,
                                ProblemType)


async def test_application_system():
    """실제 응용 시스템 테스트"""
    print("🚀 DuRiCore Phase 7 - 실제 응용 시스템 테스트")
    print("=" * 60)

    # 시스템 초기화
    app_system = ApplicationSystem()
    await app_system.initialize()

    print("✅ 시스템 초기화 완료")

    # 1. 일반 대화 모듈 테스트
    print("\n1️⃣ 일반 대화 모듈 테스트")
    await test_general_conversation(app_system)

    # 2. 문제 해결 모듈 테스트
    print("\n2️⃣ 문제 해결 모듈 테스트")
    await test_problem_solving(app_system)

    # 3. 창작 글쓰기 모듈 테스트
    print("\n3️⃣ 창작 글쓰기 모듈 테스트")
    await test_creative_writing(app_system)

    # 4. 기술 분석 모듈 테스트
    print("\n4️⃣ 기술 분석 모듈 테스트")
    await test_technical_analysis(app_system)

    # 5. 도메인 자동 감지 테스트
    print("\n5️⃣ 도메인 자동 감지 테스트")
    await test_domain_detection(app_system)

    # 6. 통합 시스템 연동 테스트
    print("\n6️⃣ 통합 시스템 연동 테스트")
    await test_integration(app_system)

    # 7. 성능 모니터링 테스트
    print("\n7️⃣ 성능 모니터링 테스트")
    await test_performance_monitoring(app_system)

    print("\n🎉 Phase 7 실제 응용 시스템 테스트 완료!")


async def test_general_conversation(app_system: ApplicationSystem):
    """일반 대화 모듈 테스트"""
    test_inputs = [
        "안녕하세요! 오늘 기분이 정말 좋아요.",
        "요즘 너무 힘들어서 우울해요.",
        "화가 나는 일이 있어서 속상해요.",
        "새로운 일을 시작하려고 하는데 걱정이 많아요.",
        "오늘 날씨가 정말 좋네요!",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(
                user_input, ApplicationDomain.GENERAL_CONVERSATION
            )

            print(f"   {i}. 입력: '{user_input}'")
            print(f"      응답: {result.solution}")
            print(f"      신뢰도: {result.confidence_score:.2f}")
            print(f"      실행시간: {result.execution_time:.2f}초")
            print(f"      추론: {result.reasoning}")

        except Exception as e:
            print(f"   {i}. ❌ 오류: {e}")


async def test_problem_solving(app_system: ApplicationSystem):
    """문제 해결 모듈 테스트"""
    test_inputs = [
        "복잡한 문제를 해결하는 방법을 알려주세요.",
        "창의적인 아이디어를 어떻게 떠올릴 수 있을까요?",
        "데이터 분석을 통한 의사결정 방법을 알려주세요.",
        "전략적 계획을 세우는 방법을 알려주세요.",
        "기술적 문제를 해결하는 체계적 접근법을 알려주세요.",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(
                user_input, ApplicationDomain.PROBLEM_SOLVING
            )

            print(f"   {i}. 입력: '{user_input}'")
            print(f"      해결책: {result.solution}")
            print(f"      신뢰도: {result.confidence_score:.2f}")
            print(f"      실행시간: {result.execution_time:.2f}초")
            print(f"      문제 유형: {result.problem_type.value}")

        except Exception as e:
            print(f"   {i}. ❌ 오류: {e}")


async def test_creative_writing(app_system: ApplicationSystem):
    """창작 글쓰기 모듈 테스트"""
    test_inputs = [
        "재미있는 소설을 써주세요.",
        "자연을 소재로 한 시를 써주세요.",
        "감동적인 이야기를 만들어주세요.",
        "판타지 소설을 써주세요.",
        "일상에 대한 에세이를 써주세요.",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(
                user_input, ApplicationDomain.CREATIVE_WRITING
            )

            print(f"   {i}. 입력: '{user_input}'")
            print(f"      창작물: {result.solution}")
            print(f"      신뢰도: {result.confidence_score:.2f}")
            print(f"      실행시간: {result.execution_time:.2f}초")
            print(
                f"      창의성 점수: {result.performance_metrics.get('creativity', 0):.2f}"
            )

        except Exception as e:
            print(f"   {i}. ❌ 오류: {e}")


async def test_technical_analysis(app_system: ApplicationSystem):
    """기술 분석 모듈 테스트"""
    test_inputs = [
        "코드 성능을 분석하는 방법을 알려주세요.",
        "시스템 최적화 방법을 알려주세요.",
        "보안 취약점을 분석하는 방법을 알려주세요.",
        "알고리즘 효율성을 개선하는 방법을 알려주세요.",
        "기술적 아키텍처를 분석하는 방법을 알려주세요.",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(
                user_input, ApplicationDomain.TECHNICAL_ANALYSIS
            )

            print(f"   {i}. 입력: '{user_input}'")
            print(f"      분석: {result.solution}")
            print(f"      신뢰도: {result.confidence_score:.2f}")
            print(f"      실행시간: {result.execution_time:.2f}초")
            print(
                f"      기술 정확도: {result.performance_metrics.get('technical_accuracy', 0):.2f}"
            )

        except Exception as e:
            print(f"   {i}. ❌ 오류: {e}")


async def test_domain_detection(app_system: ApplicationSystem):
    """도메인 자동 감지 테스트"""
    test_inputs = [
        ("안녕하세요! 오늘 기분이 좋아요.", ApplicationDomain.GENERAL_CONVERSATION),
        (
            "복잡한 문제를 해결하는 방법을 알려주세요.",
            ApplicationDomain.PROBLEM_SOLVING,
        ),
        ("창의적인 이야기를 만들어주세요.", ApplicationDomain.CREATIVE_WRITING),
        (
            "코드 성능을 분석하는 방법을 알려주세요.",
            ApplicationDomain.TECHNICAL_ANALYSIS,
        ),
        (
            "새로운 아이디어를 떠올리는 방법을 알려주세요.",
            ApplicationDomain.PROBLEM_SOLVING,
        ),
    ]

    correct_detections = 0
    total_tests = len(test_inputs)

    for i, (user_input, expected_domain) in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(user_input)
            detected_domain = result.domain

            is_correct = detected_domain == expected_domain
            if is_correct:
                correct_detections += 1
                status = "✅"
            else:
                status = "❌"

            print(f"   {i}. 입력: '{user_input}'")
            print(f"      예상 도메인: {expected_domain.value}")
            print(f"      감지된 도메인: {detected_domain.value}")
            print(f"      정확도: {status}")

        except Exception as e:
            print(f"   {i}. ❌ 오류: {e}")

    accuracy = correct_detections / total_tests * 100
    print(
        f"\n   📊 도메인 감지 정확도: {accuracy:.1f}% ({correct_detections}/{total_tests})"
    )


async def test_integration(app_system: ApplicationSystem):
    """통합 시스템 연동 테스트"""
    print("   🔗 통합 시스템 상태 확인...")

    try:
        status = await app_system.get_system_status()

        print(f"      응용 시스템 상태: {status['application_system']['status']}")
        print(f"      모듈 수: {status['application_system']['modules_count']}")
        print(
            f"      성능 기록 수: {status['application_system']['performance_history_count']}"
        )

        # 통합 시스템 상태 확인
        integrated_status = status["integrated_systems"]
        active_systems = sum(
            1
            for system in integrated_status.values()
            if system.get("status") == "active"
        )
        total_systems = len(integrated_status)

        print(f"      활성 통합 시스템: {active_systems}/{total_systems}")

        # 도메인별 사용 통계
        domain_stats = status["application_system"]["domain_usage_stats"]
        if domain_stats:
            print("      도메인별 사용 통계:")
            for domain, stats in domain_stats.items():
                print(
                    f"         {domain}: {stats['count']}회, 평균 신뢰도 {stats['avg_confidence']:.2f}"
                )

    except Exception as e:
        print(f"   ❌ 통합 시스템 상태 확인 오류: {e}")


async def test_performance_monitoring(app_system: ApplicationSystem):
    """성능 모니터링 테스트"""
    print("   📊 성능 모니터링 테스트...")

    # 연속 처리 테스트
    test_inputs = [
        "안녕하세요!",
        "문제를 해결하는 방법을 알려주세요.",
        "창의적인 이야기를 만들어주세요.",
        "기술적 분석을 해주세요.",
    ]

    start_time = time.time()
    total_confidence = 0
    total_execution_time = 0

    for i, user_input in enumerate(test_inputs, 1):
        try:
            result = await app_system.process_application(user_input)

            total_confidence += result.confidence_score
            total_execution_time += result.execution_time

            print(
                f"      {i}. {result.domain.value}: 신뢰도 {result.confidence_score:.2f}, 시간 {result.execution_time:.2f}초"
            )

        except Exception as e:
            print(f"      {i}. ❌ 오류: {e}")

    total_time = time.time() - start_time
    avg_confidence = total_confidence / len(test_inputs)
    avg_execution_time = total_execution_time / len(test_inputs)

    print(f"\n   📈 성능 요약:")
    print(f"      총 처리 시간: {total_time:.2f}초")
    print(f"      평균 신뢰도: {avg_confidence:.2f}")
    print(f"      평균 실행 시간: {avg_execution_time:.2f}초")
    print(f"      처리량: {len(test_inputs)/total_time:.2f} 요청/초")


async def test_comprehensive_scenarios():
    """포괄적 시나리오 테스트"""
    print("\n🧪 포괄적 시나리오 테스트")
    print("=" * 60)

    app_system = ApplicationSystem()
    await app_system.initialize()

    # 복합 시나리오 테스트
    scenarios = [
        {
            "name": "감정적 대화 + 문제 해결",
            "input": "요즘 너무 힘들어서 우울한데, 이런 상황을 어떻게 해결할 수 있을까요?",
            "expected_domains": [
                ApplicationDomain.GENERAL_CONVERSATION,
                ApplicationDomain.PROBLEM_SOLVING,
            ],
        },
        {
            "name": "창의적 요청 + 기술적 분석",
            "input": "창의적인 웹사이트를 만들고 싶은데, 어떤 기술을 사용하는 것이 좋을까요?",
            "expected_domains": [
                ApplicationDomain.CREATIVE_WRITING,
                ApplicationDomain.TECHNICAL_ANALYSIS,
            ],
        },
        {
            "name": "전략적 계획 + 창의적 사고",
            "input": "새로운 비즈니스를 시작하려고 하는데, 창의적인 전략을 세우고 싶어요.",
            "expected_domains": [
                ApplicationDomain.PROBLEM_SOLVING,
                ApplicationDomain.CREATIVE_WRITING,
            ],
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   입력: '{scenario['input']}'")

        try:
            result = await app_system.process_application(scenario["input"])

            print(f"   감지된 도메인: {result.domain.value}")
            print(f"   문제 유형: {result.problem_type.value}")
            print(f"   응답: {result.solution[:100]}...")
            print(f"   신뢰도: {result.confidence_score:.2f}")

            # 예상 도메인과 비교
            detected_domain = result.domain
            expected_domains = scenario["expected_domains"]

            if detected_domain in expected_domains:
                print(f"   ✅ 도메인 감지 정확")
            else:
                print(
                    f"   ⚠️  도메인 감지 차이 (예상: {[d.value for d in expected_domains]})"
                )

        except Exception as e:
            print(f"   ❌ 시나리오 처리 오류: {e}")


async def main():
    """메인 함수"""
    print("🚀 DuRiCore Phase 7 - 실제 응용 시스템 포괄적 테스트")
    print("=" * 80)

    # 기본 테스트 실행
    await test_application_system()

    # 포괄적 시나리오 테스트 실행
    await test_comprehensive_scenarios()

    print("\n🎉 모든 테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
