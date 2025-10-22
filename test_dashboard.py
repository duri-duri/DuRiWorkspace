#!/usr/bin/env python3
import json
import time

import requests


def test_dashboard():
    base_url = "http://localhost:8088"

    print("🧪 DuRi 대시보드 테스트 시작...")

    # 1. 헬스 체크
    print("\n1️⃣ 헬스 체크...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ 헬스 체크 성공: {response.status_code}")
        print(f"📊 응답: {response.json()}")
    except Exception as e:
        print(f"❌ 헬스 체크 실패: {e}")
        return

    # 2. 대화 캡처 테스트
    print("\n2️⃣ 대화 캡처 테스트...")
    test_conversations = [
        {
            "user_input": "Hello! Please explain the DuRi system.",
            "duri_response": "DuRi is a self-evolving AI system with multiple nodes including brain, evolution, control, and core components. It can learn from conversations and improve itself through self-reflection and external feedback.",
        },
        {
            "user_input": "How does the self-learning loop work?",
            "duri_response": "The self-learning loop involves ChatGPT evaluation, DuRi self-reflection, discussion between DuRi and ChatGPT, and safe code improvement with user approval.",
        },
        {
            "user_input": "What are the key components of DuRi?",
            "duri_response": "Key components include duri_core (port 8080), duri_brain (port 8081), duri_evolution (port 8082), and various modules for evaluation, reflection, and monitoring.",
        },
        {
            "user_input": "Explain the evolution process.",
            "duri_response": "The evolution process involves capturing conversations, evaluating responses, reflecting on feedback, proposing improvements, and applying changes safely with backups and static analysis.",
        },
        {
            "user_input": "How does DuRi improve itself?",
            "duri_response": "DuRi improves itself through automated learning loops, performance monitoring, dashboard visualization, and modular architecture that allows for safe code modifications.",
        },
    ]

    for i, conv in enumerate(test_conversations, 1):
        try:
            data = {
                "user_input": conv["user_input"],
                "duri_response": conv["duri_response"],
                "auto_learn": True,
            }
            response = requests.post(f"{base_url}/capture-conversation", json=data, timeout=30)
            print(f"✅ 대화 {i} 캡처 성공: {response.status_code}")
            result = response.json()
            if response.status_code == 200:
                print(f"📊 학습 가치: {result.get('data', {}).get('learning_value', 'N/A')}")
                print(
                    f"📊 평가 점수: {result.get('learning_summary', {}).get('evaluation_score', 'N/A')}"
                )
            else:
                print(f"❌ 에러: {result}")
        except Exception as e:
            print(f"❌ 대화 {i} 캡처 실패: {e}")

    # 3. 학습 통계 확인
    print("\n3️⃣ 학습 통계 확인...")
    try:
        response = requests.get(f"{base_url}/learning-statistics")
        print(f"✅ 학습 통계 성공: {response.status_code}")
        stats = response.json()
        print(f"📊 총 대화 수: {stats.get('data', {}).get('total_conversations', 'N/A')}")
    except Exception as e:
        print(f"❌ 학습 통계 실패: {e}")

    # 4. 성능 요약 확인
    print("\n4️⃣ 성능 요약 확인...")
    try:
        response = requests.get(f"{base_url}/performance-summary")
        print(f"✅ 성능 요약 성공: {response.status_code}")
        perf = response.json()
        print(f"📊 총 요청 수: {perf.get('data', {}).get('total_requests', 'N/A')}")
    except Exception as e:
        print(f"❌ 성능 요약 실패: {e}")

    # 5. 대시보드 생성
    print("\n5️⃣ 대시보드 생성...")
    try:
        response = requests.get(f"{base_url}/dashboard")
        print(f"✅ 대시보드 생성 성공: {response.status_code}")
        dashboard = response.json()
        print(f"📊 대시보드 경로: {dashboard.get('dashboard_path', 'N/A')}")
        print(f"🌐 대시보드 URL: {dashboard.get('dashboard_url', 'N/A')}")
    except Exception as e:
        print(f"❌ 대시보드 생성 실패: {e}")

    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    test_dashboard()
