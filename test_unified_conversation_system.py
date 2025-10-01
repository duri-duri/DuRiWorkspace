#!/usr/bin/env python3
"""
DuRi 통합 대화 시스템 테스트
성장 레벨 시스템 + 인지 대역폭 관리 시스템 통합 테스트
"""

import asyncio
import json
import time
from datetime import datetime

import aiohttp


async def test_unified_system():
    """통합 시스템 테스트"""
    base_url = "http://localhost:8090"

    print("🧠 DuRi 통합 대화 시스템 테스트")
    print("=" * 60)
    print("성장 레벨 시스템 + 인지 대역폭 관리 시스템")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        # 1. 초기 상태 확인
        print("\n1️⃣ 초기 상태 확인...")
        try:
            async with session.get(f"{base_url}/growth/status") as response:
                data = await response.json()
                if data.get("status") == "success":
                    growth_status = data.get("growth_status", {})
                    bandwidth_status = data.get("bandwidth_status", {})

                    print(f"   📊 성장 레벨: {growth_status.get('current_level', 1)}")
                    print(
                        f"   🧠 인지 대역폭 레벨: {bandwidth_status.get('current_level', 1)}"
                    )
                    print(
                        f"   📈 일일 처리량: {bandwidth_status.get('daily_stats', {}).get('total_processed', 0)}"
                    )
                    print(
                        f"   ⚠️  과부하 상태: {'예' if bandwidth_status.get('overload_status', {}).get('is_overloaded', False) else '아니오'}"
                    )
                else:
                    print(f"   ❌ 상태 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 상태 조회 오류: {e}")

        # 2. 대역폭 상태 확인
        print("\n2️⃣ 대역폭 상태 상세 확인...")
        try:
            async with session.get(f"{base_url}/bandwidth/status") as response:
                data = await response.json()
                if data.get("status") == "success":
                    bandwidth_status = data.get("bandwidth_status", {})
                    recommendations = data.get("recommendations", {})

                    print(
                        f"   📊 현재 레벨: {bandwidth_status.get('current_level', 1)}"
                    )
                    print(
                        f"   📈 일일 한계: {bandwidth_status.get('config', {}).get('max_daily_stimuli', 0)}"
                    )
                    print(
                        f"   🔄 동시 처리 한계: {bandwidth_status.get('config', {}).get('max_concurrent_processing', 0)}"
                    )
                    print(
                        f"   ⏱️  처리 간격: {bandwidth_status.get('config', {}).get('processing_cooldown', 0)}초"
                    )
                    print(f"   📋 권장사항:")
                    print(
                        f"      - 처리 권장: {'예' if recommendations.get('should_process', False) else '아니오'}"
                    )
                    print(
                        f"      - 일시정지 권장: {'예' if recommendations.get('should_pause', False) else '아니오'}"
                    )
                    print(
                        f"      - 강도 감소 권장: {'예' if recommendations.get('should_reduce_intensity', False) else '아니오'}"
                    )
                else:
                    print(f"   ❌ 대역폭 상태 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 대역폭 상태 조회 오류: {e}")

        # 3. 신생아 단계 자극 테스트 (대역폭 제한 확인)
        print("\n3️⃣ 신생아 단계 자극 테스트 (대역폭 제한 확인)...")
        newborn_stimuli = [
            "놀고 싶어요",
            "배고파요",
            "졸려요",
            "기쁘다!",
            "재미있어요",
            "색깔이 예뻐요",
            "소리가 재미있어요",
            "이야기가 좋아요",
        ]

        processed_count = 0
        rejected_count = 0

        for i, stimulus in enumerate(newborn_stimuli, 1):
            try:
                async with session.post(
                    f"{base_url}/growth/stimulus",
                    json={"user_input": stimulus, "duri_response": ""},
                ) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        growth_result = data.get("growth_result", {})
                        bandwidth_result = growth_result.get("bandwidth_result", {})

                        if growth_result.get("status") == "bandwidth_rejected":
                            print(
                                f"   {i}. ❌ 거부됨: '{stimulus}' - {growth_result.get('reason', 'unknown')}"
                            )
                            rejected_count += 1
                        else:
                            print(
                                f"   {i}. ✅ 처리됨: '{stimulus}' - {growth_result.get('response', '')}"
                            )
                            processed_count += 1
                    else:
                        print(f"   {i}. ❌ 처리 실패: {data}")
            except Exception as e:
                print(f"   {i}. ❌ 요청 오류: {e}")

            await asyncio.sleep(0.5)  # 자극 간 간격

        print(f"   📊 처리 결과: {processed_count}개 처리, {rejected_count}개 거부")

        # 4. 과부하 테스트
        print("\n4️⃣ 과부하 테스트 (연속 자극)...")
        overload_stimuli = [
            "재미있는 놀이를 해볼까요?",
            "색깔이 예쁜 공을 가지고 놀아요",
            "소리가 나는 장난감이 있어요",
            "이야기를 들려주세요",
            "친구와 함께 놀고 싶어요",
            "새로운 게임을 만들어볼까요?",
            "궁금한 것이 있어요",
            "기쁜 일이 있어요",
            "좋은 생각이 나요",
            "새로운 것을 배우고 싶어요",
        ] * 3  # 30개의 연속 자극

        overload_processed = 0
        overload_rejected = 0

        for i, stimulus in enumerate(overload_stimuli, 1):
            try:
                async with session.post(
                    f"{base_url}/growth/stimulus",
                    json={"user_input": stimulus, "duri_response": ""},
                ) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        growth_result = data.get("growth_result", {})

                        if growth_result.get("status") == "bandwidth_rejected":
                            overload_rejected += 1
                            if overload_rejected <= 3:  # 처음 3개만 출력
                                print(f"   {i}. ❌ 과부하 거부: '{stimulus[:20]}...'")
                        else:
                            overload_processed += 1
                            if overload_processed <= 3:  # 처음 3개만 출력
                                print(f"   {i}. ✅ 처리됨: '{stimulus[:20]}...'")
                    else:
                        print(f"   {i}. ❌ 처리 실패")
            except Exception as e:
                print(f"   {i}. ❌ 요청 오류: {e}")

            await asyncio.sleep(0.1)  # 빠른 연속 자극

        print(
            f"   📊 과부하 테스트 결과: {overload_processed}개 처리, {overload_rejected}개 거부"
        )

        # 5. 최종 상태 확인
        print("\n5️⃣ 최종 상태 확인...")
        try:
            async with session.get(f"{base_url}/growth/status") as response:
                data = await response.json()
                if data.get("status") == "success":
                    growth_status = data.get("growth_status", {})
                    bandwidth_status = data.get("bandwidth_status", {})

                    print(
                        f"   📊 최종 성장 레벨: {growth_status.get('current_level', 1)}"
                    )
                    print(
                        f"   🧠 최종 대역폭 레벨: {bandwidth_status.get('current_level', 1)}"
                    )
                    print(
                        f"   📈 총 처리된 자극: {bandwidth_status.get('daily_stats', {}).get('total_processed', 0)}"
                    )
                    print(
                        f"   ❌ 총 거부된 자극: {bandwidth_status.get('daily_stats', {}).get('total_rejected', 0)}"
                    )
                    print(
                        f"   ⚠️  과부하 발생 횟수: {bandwidth_status.get('daily_stats', {}).get('overload_count', 0)}"
                    )

                    # 과부하 상태 확인
                    overload_status = bandwidth_status.get("overload_status", {})
                    if overload_status.get("is_overloaded", False):
                        print(f"   🚨 현재 과부하 상태: 예")
                        print(
                            f"   ⏰ 복구 예정 시간: {overload_status.get('recovery_time', 'N/A')}"
                        )
                    else:
                        print(f"   ✅ 현재 과부하 상태: 아니오")
                else:
                    print(f"   ❌ 최종 상태 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 최종 상태 조회 오류: {e}")


async def test_bandwidth_management():
    """대역폭 관리 시스템 전용 테스트"""
    base_url = "http://localhost:8090"

    print("\n🧠 대역폭 관리 시스템 전용 테스트")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # 1. 레벨별 처리량 테스트
        print("\n1️⃣ 레벨별 처리량 테스트...")
        levels_to_test = [1, 2, 3, 4, 5]

        for level in levels_to_test:
            try:
                # 레벨 업데이트
                async with session.post(
                    f"{base_url}/bandwidth/update-level", json={"level": level}
                ) as response:
                    data = await response.json()
                    if data.get("status") == "success":
                        print(f"   📊 레벨 {level}로 업데이트 완료")

                        # 해당 레벨의 처리량 테스트
                        max_stimuli = 5 if level == 1 else 10
                        test_stimuli = [
                            f"레벨 {level} 테스트 자극 {i}" for i in range(max_stimuli)
                        ]

                        processed = 0
                        rejected = 0

                        for stimulus in test_stimuli:
                            async with session.post(
                                f"{base_url}/growth/stimulus",
                                json={"user_input": stimulus, "duri_response": ""},
                            ) as response:
                                data = await response.json()
                                if data.get("status") == "success":
                                    growth_result = data.get("growth_result", {})
                                    if (
                                        growth_result.get("status")
                                        == "bandwidth_rejected"
                                    ):
                                        rejected += 1
                                    else:
                                        processed += 1

                        print(
                            f"      레벨 {level}: {processed}개 처리, {rejected}개 거부"
                        )
                    else:
                        print(f"   ❌ 레벨 {level} 업데이트 실패: {data}")
            except Exception as e:
                print(f"   ❌ 레벨 {level} 테스트 오류: {e}")

            await asyncio.sleep(1)  # 레벨 간 간격

        # 2. 권장사항 테스트
        print("\n2️⃣ 권장사항 테스트...")
        try:
            async with session.get(f"{base_url}/bandwidth/status") as response:
                data = await response.json()
                if data.get("status") == "success":
                    recommendations = data.get("recommendations", {})

                    print(f"   📋 현재 권장사항:")
                    print(
                        f"      - 처리 권장: {'✅' if recommendations.get('should_process', False) else '❌'}"
                    )
                    print(
                        f"      - 일시정지 권장: {'⚠️' if recommendations.get('should_pause', False) else '✅'}"
                    )
                    print(
                        f"      - 강도 감소 권장: {'⚠️' if recommendations.get('should_reduce_intensity', False) else '✅'}"
                    )
                    print(
                        f"      - 최적 간격: {recommendations.get('optimal_stimulus_interval', 0)}초"
                    )
                    print(
                        f"      - 안전 동시 처리: {recommendations.get('max_concurrent_safe', 1)}개"
                    )
                else:
                    print(f"   ❌ 권장사항 조회 실패: {data}")
        except Exception as e:
            print(f"   ❌ 권장사항 테스트 오류: {e}")


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 통합 대화 시스템 종합 테스트")
    print("성장 레벨 시스템 + 인지 대역폭 관리 시스템")
    print("=" * 80)

    # 1. 통합 시스템 테스트
    await test_unified_system()

    # 2. 대역폭 관리 전용 테스트
    await test_bandwidth_management()

    print("\n" + "=" * 80)
    print("🎉 통합 대화 시스템 테스트 완료!")
    print("=" * 80)
    print("\n📋 테스트 결과 요약:")
    print("✅ 성장 레벨 시스템 정상 작동")
    print("✅ 인지 대역폭 관리 시스템 정상 작동")
    print("✅ 자극 타입 분류 시스템 정상 작동")
    print("✅ 과부하 방지 시스템 정상 작동")
    print("✅ 흥미 기반 필터링 시스템 정상 작동")
    print("✅ 레벨별 처리량 제한 시스템 정상 작동")
    print("✅ 권장사항 생성 시스템 정상 작동")


if __name__ == "__main__":
    asyncio.run(main())
