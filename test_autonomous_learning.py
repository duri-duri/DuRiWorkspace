#!/usr/bin/env python3
"""
DuRi 24/7 자동 학습 시스템 테스트
"""
import json
import time
from datetime import datetime

import requests


def test_autonomous_learning_system():
    """자동 학습 시스템 테스트"""
    base_url = "http://localhost:8088"
    print("🤖 DuRi 24/7 자동 학습 시스템 테스트 시작...")

    # 1. 자동 학습 시작
    print("\n1️⃣ 자동 학습 시작 테스트")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/start")
        result = response.json()
        print(f"   결과: {result}")

        if result.get("status") == "success":
            print("   ✅ 자동 학습 시작 성공")
        else:
            print("   ❌ 자동 학습 시작 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 2. 상태 확인
    print("\n2️⃣ 자동 학습 상태 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/status")
        result = response.json()
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("status") == "success":
            print("   ✅ 상태 확인 성공")
        else:
            print("   ❌ 상태 확인 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 3. 통계 확인
    print("\n3️⃣ 자동 학습 통계 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/statistics")
        result = response.json()
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("status") == "success":
            print("   ✅ 통계 확인 성공")
        else:
            print("   ❌ 통계 확인 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 4. 학습 진행 상황 모니터링 (30초)
    print("\n4️⃣ 학습 진행 상황 모니터링 (30초)")
    for i in range(6):  # 6번 체크 (5초마다)
        try:
            response = requests.get(f"{base_url}/autonomous-learning/status")
            result = response.json()

            if result.get("status") == "success":
                autonomous_data = result.get("autonomous_learning", {})
                cycles = autonomous_data.get("total_learning_cycles", 0)
                problems = autonomous_data.get("total_problems_detected", 0)
                decisions = autonomous_data.get("total_decisions_made", 0)

                print(f"   ⏱️  {i*5+5}초: 사이클={cycles}, 문제={problems}, 결정={decisions}")
            else:
                print(f"   ❌ {i*5+5}초: 상태 확인 실패")

        except Exception as e:
            print(f"   ❌ {i*5+5}초: 오류 - {e}")

        time.sleep(5)

    # 5. 보고서 확인
    print("\n5️⃣ 자동 학습 보고서 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/reports")
        result = response.json()
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("status") == "success":
            reports = result.get("reports", [])
            print(f"   📊 총 {len(reports)}개의 보고서 생성됨")
        else:
            print("   ❌ 보고서 확인 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 6. 자동 학습 중지
    print("\n6️⃣ 자동 학습 중지")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/stop")
        result = response.json()
        print(f"   결과: {result}")

        if result.get("status") == "success":
            print("   ✅ 자동 학습 중지 성공")
        else:
            print("   ❌ 자동 학습 중지 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 7. 최종 상태 확인
    print("\n7️⃣ 최종 상태 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/status")
        result = response.json()
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")

        if result.get("status") == "success":
            autonomous_data = result.get("autonomous_learning", {})
            is_running = autonomous_data.get("is_running", False)

            if not is_running:
                print("   ✅ 자동 학습이 정상적으로 중지됨")
            else:
                print("   ⚠️  자동 학습이 여전히 실행 중")
        else:
            print("   ❌ 최종 상태 확인 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    print("\n🎉 DuRi 24/7 자동 학습 시스템 테스트 완료!")


def test_autonomous_learning_integration():
    """자동 학습과 기존 시스템 통합 테스트"""
    base_url = "http://localhost:8088"
    print("\n🔄 자동 학습과 기존 시스템 통합 테스트")

    # 1. 자동 학습 시작
    print("\n1️⃣ 자동 학습 시작")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/start")
        result = response.json()
        print(f"   결과: {result}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return

    # 2. 대화 데이터 전송 (자동 학습이 백그라운드에서 처리)
    print("\n2️⃣ 대화 데이터 전송 (자동 학습 처리)")
    test_conversations = [
        {
            "user_input": "자동 학습 시스템이 어떻게 작동하나요?",
            "duri_response": "DuRi의 24/7 자동 학습 시스템은 백그라운드에서 지속적으로 학습하며, 문제가 발생하거나 결정이 필요할 때만 사용자에게 보고합니다.",
        },
        {
            "user_input": "문제 감지 기능은 어떻게 작동하나요?",
            "duri_response": "시스템은 오류율, 응답 시간, 메모리 사용량, CPU 사용량, 학습 진전 등을 모니터링하여 임계값을 초과하면 문제로 감지합니다.",
        },
        {
            "user_input": "자동 결정은 어떤 것들이 있나요?",
            "duri_response": "서비스 재시작, 메모리 최적화, 학습률 조정, 데이터 백업 등의 자동 결정을 수행할 수 있습니다.",
        },
    ]

    for i, conversation in enumerate(test_conversations, 1):
        try:
            response = requests.post(f"{base_url}/capture-conversation", json=conversation)
            result = response.json()
            print(f"   대화 {i}: {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"   대화 {i}: 오류 - {e}")

        time.sleep(2)  # 2초 대기

    # 3. 자동 학습 상태 확인
    print("\n3️⃣ 자동 학습 상태 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/status")
        result = response.json()

        if result.get("status") == "success":
            autonomous_data = result.get("autonomous_learning", {})
            cycles = autonomous_data.get("total_learning_cycles", 0)
            problems = autonomous_data.get("total_problems_detected", 0)
            decisions = autonomous_data.get("total_decisions_made", 0)

            print(f"   📊 학습 사이클: {cycles}")
            print(f"   🚨 감지된 문제: {problems}")
            print(f"   ⚙️  자동 결정: {decisions}")
        else:
            print("   ❌ 상태 확인 실패")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 4. 자동 학습 중지
    print("\n4️⃣ 자동 학습 중지")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/stop")
        result = response.json()
        print(f"   결과: {result}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

    print("\n✅ 자동 학습 통합 테스트 완료!")


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 DuRi 24/7 자동 학습 시스템 테스트")
    print("=" * 60)

    # 기본 테스트
    test_autonomous_learning_system()

    # 통합 테스트
    test_autonomous_learning_integration()

    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("=" * 60)
