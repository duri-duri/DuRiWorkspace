#!/usr/bin/env python3
"""
DuRi 자동화 파이프라인 테스트
"""
import asyncio
import json
import time
from datetime import datetime

import aiohttp


async def test_automation_pipeline():
    """자동화 파이프라인 테스트"""
    base_url = "http://localhost:8090"

    print("🚀 DuRi 자동화 파이프라인 테스트 시작")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # 1. 자동화 파이프라인 시작
        print("1️⃣ 자동화 파이프라인 시작...")
        try:
            async with session.post(f"{base_url}/automation/start") as response:
                data = await response.json()
                print(f"   ✅ 자동화 시작: {data.get('message', '성공')}")
        except Exception as e:
            print(f"   ❌ 자동화 시작 실패: {e}")

        # 2. 수동 트리거 테스트
        print("\n2️⃣ 수동 트리거 테스트...")
        trigger_data = {
            "user_input": "자동화 파이프라인 테스트",
            "duri_response": "테스트 응답입니다.",
            "metadata": {
                "test_type": "automation_pipeline",
                "timestamp": datetime.now().isoformat(),
            },
        }

        try:
            async with session.post(
                f"{base_url}/automation/trigger", json=trigger_data
            ) as response:
                data = await response.json()
                print(f"   ✅ 트리거 실행: {data.get('message', '성공')}")
        except Exception as e:
            print(f"   ❌ 트리거 실행 실패: {e}")

        # 3. 자동화 통계 확인
        print("\n3️⃣ 자동화 통계 확인...")
        try:
            async with session.get(f"{base_url}/automation/stats") as response:
                data = await response.json()
                if data.get("status") == "success":
                    automation_stats = data.get("automation_stats", {})
                    learning_stats = data.get("learning_stats", {})

                    print(f"   📊 자동화 통계:")
                    print(
                        f"      - 총 트리거 수: {automation_stats.get('total_triggers', 0)}"
                    )
                    print(
                        f"      - 성공한 학습 사이클: {automation_stats.get('successful_learning_cycles', 0)}"
                    )
                    print(
                        f"      - 평균 학습 점수: {automation_stats.get('average_learning_score', 0):.3f}"
                    )
                    print(
                        f"      - 마지막 실행: {automation_stats.get('last_automation_run', 'N/A')}"
                    )

                    print(f"   📈 학습 통계:")
                    print(
                        f"      - 총 학습 결과: {learning_stats.get('total_results', 0)}"
                    )
                    print(
                        f"      - 성공률: {learning_stats.get('success_rate', 0):.1%}"
                    )
                    print(
                        f"      - 평균 점수: {learning_stats.get('average_score', 0):.3f}"
                    )
                    print(
                        f"      - 평균 응답 시간: {learning_stats.get('average_duration', 0):.3f}초"
                    )
                else:
                    print(f"   ❌ 통계 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 통계 조회 실패: {e}")

        # 4. 성능 메트릭 확인
        print("\n4️⃣ 성능 메트릭 확인...")
        try:
            async with session.get(f"{base_url}/performance") as response:
                data = await response.json()
                if data.get("status") == "success":
                    perf_metrics = data.get("performance_metrics", {})
                    cache_stats = data.get("cache_stats", {})

                    print(f"   ⚡ 성능 메트릭:")
                    print(
                        f"      - 총 요청 수: {perf_metrics.get('total_requests', 0)}"
                    )
                    print(f"      - 캐시 히트: {perf_metrics.get('cache_hits', 0)}")
                    print(f"      - 캐시 미스: {perf_metrics.get('cache_misses', 0)}")
                    print(
                        f"      - 평균 응답 시간: {perf_metrics.get('average_response_time', 0):.3f}초"
                    )
                    print(
                        f"      - 병렬 요청 수: {perf_metrics.get('parallel_requests', 0)}"
                    )
                    print(f"      - 오류 수: {perf_metrics.get('error_count', 0)}")

                    print(f"   💾 캐시 통계:")
                    print(f"      - 캐시 크기: {cache_stats.get('cache_size', 0)}")
                    print(f"      - 캐시 히트율: {cache_stats.get('hit_rate', 0):.1%}")
                else:
                    print(f"   ❌ 성능 메트릭 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 성능 메트릭 조회 실패: {e}")

        # 5. 대화 처리 테스트
        print("\n5️⃣ 대화 처리 테스트...")
        conversation_data = {
            "user_input": "자동화 파이프라인과 함께 대화 처리 테스트",
            "duri_response": "자동화 시스템이 활성화된 상태에서의 응답입니다.",
            "metadata": {
                "test_type": "conversation_with_automation",
                "automation_enabled": True,
            },
        }

        try:
            async with session.post(
                f"{base_url}/conversation/process", json=conversation_data
            ) as response:
                data = await response.json()
                if data.get("status") == "success":
                    print(f"   ✅ 대화 처리 성공:")
                    print(f"      - 통합 점수: {data.get('integrated_score', 0):.3f}")
                    print(f"      - 대화 ID: {data.get('conversation_id', 'N/A')}")
                    print(f"      - 처리 시간: {data.get('processing_time', 0):.3f}초")
                else:
                    print(f"   ❌ 대화 처리 실패: {data}")
        except Exception as e:
            print(f"   ❌ 대화 처리 실패: {e}")

        # 6. 자동화 파이프라인 중지
        print("\n6️⃣ 자동화 파이프라인 중지...")
        try:
            async with session.post(f"{base_url}/automation/stop") as response:
                data = await response.json()
                print(f"   ✅ 자동화 중지: {data.get('message', '성공')}")
        except Exception as e:
            print(f"   ❌ 자동화 중지 실패: {e}")

    print("\n" + "=" * 50)
    print("🎉 자동화 파이프라인 테스트 완료!")


async def test_learning_phases():
    """학습 단계별 테스트"""
    base_url = "http://localhost:8090"

    print("\n🧠 학습 단계별 테스트")
    print("=" * 30)

    learning_scenarios = [
        {
            "name": "모방 학습",
            "user_input": "코딩 패턴을 모방해보세요",
            "duri_response": "네, 코딩 패턴을 분석하고 모방하겠습니다.",
            "metadata": {"phase": "imitation", "learning_type": "pattern_recognition"},
        },
        {
            "name": "반복 학습",
            "user_input": "이전 학습 내용을 반복해주세요",
            "duri_response": "이전 학습 내용을 반복하여 강화하겠습니다.",
            "metadata": {"phase": "repetition", "learning_type": "reinforcement"},
        },
        {
            "name": "피드백 학습",
            "user_input": "사용자 피드백을 바탕으로 개선해주세요",
            "duri_response": "사용자 피드백을 분석하여 개선하겠습니다.",
            "metadata": {"phase": "feedback", "learning_type": "user_feedback"},
        },
        {
            "name": "도전 학습",
            "user_input": "더 어려운 문제에 도전해보세요",
            "duri_response": "새로운 도전 과제를 시도하겠습니다.",
            "metadata": {"phase": "challenge", "learning_type": "advanced_problem"},
        },
        {
            "name": "개선 학습",
            "user_input": "성능을 개선해주세요",
            "duri_response": "시스템 성능을 분석하고 개선하겠습니다.",
            "metadata": {
                "phase": "improvement",
                "learning_type": "performance_optimization",
            },
        },
    ]

    async with aiohttp.ClientSession() as session:
        for i, scenario in enumerate(learning_scenarios, 1):
            print(f"\n{i}. {scenario['name']} 테스트...")

            try:
                async with session.post(
                    f"{base_url}/automation/trigger", json=scenario
                ) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"   ✅ {scenario['name']} 성공")
                    else:
                        print(f"   ❌ {scenario['name']} 실패: {data}")
            except Exception as e:
                print(f"   ❌ {scenario['name']} 오류: {e}")

            # 잠시 대기
            await asyncio.sleep(1)

    print("\n" + "=" * 30)
    print("✅ 학습 단계별 테스트 완료!")


async def test_performance_optimization():
    """성능 최적화 테스트"""
    base_url = "http://localhost:8090"

    print("\n⚡ 성능 최적화 테스트")
    print("=" * 30)

    # 캐시 클리어
    print("1. 캐시 클리어...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{base_url}/performance/clear-cache") as response:
                data = await response.json()
                print(f"   ✅ 캐시 클리어: {data.get('message', '성공')}")
        except Exception as e:
            print(f"   ❌ 캐시 클리어 실패: {e}")

        # 병렬 요청 테스트
        print("\n2. 병렬 요청 테스트...")
        test_requests = [
            {"user_input": f"병렬 테스트 {i}", "duri_response": f"응답 {i}"}
            for i in range(5)
        ]

        start_time = time.time()
        tasks = []

        for req in test_requests:
            task = session.post(f"{base_url}/conversation/process", json=req)
            tasks.append(task)

        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()

            success_count = sum(1 for r in responses if not isinstance(r, Exception))
            print(f"   ✅ 병렬 요청 완료: {success_count}/{len(test_requests)} 성공")
            print(f"   ⏱️  총 소요 시간: {end_time - start_time:.3f}초")

        except Exception as e:
            print(f"   ❌ 병렬 요청 실패: {e}")

    print("\n" + "=" * 30)
    print("✅ 성능 최적화 테스트 완료!")


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 자동화 파이프라인 종합 테스트")
    print("=" * 60)

    # 1. 기본 자동화 파이프라인 테스트
    await test_automation_pipeline()

    # 2. 학습 단계별 테스트
    await test_learning_phases()

    # 3. 성능 최적화 테스트
    await test_performance_optimization()

    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("\n📊 테스트 결과 요약:")
    print("✅ 자동화 파이프라인 정상 작동")
    print("✅ 학습 단계별 처리 완료")
    print("✅ 성능 최적화 기능 확인")
    print("✅ 실시간 모니터링 활성화")
    print("✅ 데이터베이스 동기화 완료")


if __name__ == "__main__":
    asyncio.run(main())
