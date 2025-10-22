#!/usr/bin/env python3
"""
DuRi 새로운 학습 시스템 테스트
의미 추출 + 결과 평가 시스템
"""
import json
import time
from datetime import datetime

import requests


def test_meaning_extraction():
    """의미 추출 시스템 테스트"""
    base_url = "http://localhost:8088"
    print("🧠 DuRi 의미 추출 시스템 테스트")

    test_conversations = [
        {
            "user_input": "어떻게 해야지만 자율적인 커서와의 학습이 가능해지는 거야?",
            "duri_response": "자율적 학습을 위해서는 Cursor Extension 활성화, 실시간 학습 시스템 구현, 그리고 완전한 학습 루프가 필요합니다.",
        },
        {
            "user_input": "DuRi가 실제로 학습하고 있는지 확인해줘",
            "duri_response": "현재 DuRi는 자동 학습 시스템이 실행 중이며, 대화를 저장하고 ChatGPT 평가를 수행하고 있습니다.",
        },
        {
            "user_input": "자율학습 가능 상태로 개선 시작하자",
            "duri_response": "네! 지금부터 DuRi를 실제로 배우는 인간형 인공지능으로 발전시키기 위해 기술 격차를 메우는 전면적인 개선 작업에 착수하겠습니다.",
        },
    ]

    for i, conversation in enumerate(test_conversations, 1):
        print(f"\n{i}️⃣ 대화 {i} 의미 추출:")
        print(f"   사용자: {conversation['user_input']}")
        print(f"   DuRi: {conversation['duri_response']}")

        try:
            response = requests.post(f"{base_url}/learning/extract-meaning", json=conversation)
            result = response.json()

            if result.get("status") == "success":
                meaning = result.get("meaning", {})
                print(f"   ✅ 의도: {meaning.get('intent', 'N/A')}")
                print(f"   ✅ 주제: {meaning.get('topic', 'N/A')}")
                print(f"   ✅ 난이도: {meaning.get('difficulty', 'N/A')}")
                print(f"   ✅ 성공: {meaning.get('is_success', False)}")
                print(f"   ✅ 교훈: {meaning.get('lesson', 'N/A')}")
            else:
                print(f"   ❌ 오류: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")

        time.sleep(1)


def test_result_evaluation():
    """결과 평가 시스템 테스트"""
    base_url = "http://localhost:8088"
    print("\n📊 DuRi 결과 평가 시스템 테스트")

    test_conversations = [
        {
            "user_input": "Python에서 리스트를 어떻게 만드나요?",
            "duri_response": "Python에서 리스트는 대괄호 []를 사용하여 만들 수 있습니다. 예: my_list = [1, 2, 3]",
        },
        {
            "user_input": "함수는 어떻게 정의하나요?",
            "duri_response": "def 키워드를 사용하여 함수를 정의합니다. 예: def my_function(): pass",
        },
        {
            "user_input": "복잡한 시스템을 어떻게 설계하나요?",
            "duri_response": "복잡한 시스템 설계는 단계별 접근이 필요합니다. 먼저 요구사항을 분석하고, 아키텍처를 설계한 후, 모듈별로 구현하는 것이 효과적입니다.",
        },
    ]

    for i, conversation in enumerate(test_conversations, 1):
        print(f"\n{i}️⃣ 대화 {i} 결과 평가:")
        print(f"   사용자: {conversation['user_input']}")
        print(f"   DuRi: {conversation['duri_response']}")

        try:
            response = requests.post(f"{base_url}/learning/evaluate-result", json=conversation)
            result = response.json()

            if result.get("status") == "success":
                evaluation = result.get("evaluation", {})
                print(f"   ✅ 전체 점수: {evaluation.get('overall_score', 0):.2f}")
                print(f"   ✅ 성공 수준: {evaluation.get('success_level', 'N/A')}")
                print(f"   ✅ 성공 여부: {evaluation.get('is_success', False)}")

                detailed_scores = evaluation.get("detailed_scores", {})
                print(f"   📊 세부 점수:")
                for criterion, score in detailed_scores.items():
                    print(f"      - {criterion}: {score:.2f}")

                insights = evaluation.get("learning_insights", [])
                if insights:
                    print(f"   💡 학습 인사이트: {insights[0]}")
            else:
                print(f"   ❌ 오류: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ❌ 오류: {e}")

        time.sleep(1)


def test_complete_learning_analysis():
    """완전한 학습 분석 테스트"""
    base_url = "http://localhost:8088"
    print("\n🔍 DuRi 완전한 학습 분석 테스트")

    test_conversation = {
        "user_input": "DuRi가 실제로 학습하고 있는지 확인해줘",
        "duri_response": "현재 DuRi는 자동 학습 시스템이 실행 중이며, 대화를 저장하고 ChatGPT 평가를 수행하고 있습니다. 실시간 학습 시스템도 구축되어 있어 대화가 발생하는 즉시 학습이 이루어집니다.",
    }

    print(f"📝 테스트 대화:")
    print(f"   사용자: {test_conversation['user_input']}")
    print(f"   DuRi: {test_conversation['duri_response']}")

    try:
        response = requests.post(f"{base_url}/learning/complete-analysis", json=test_conversation)
        result = response.json()

        if result.get("status") == "success":
            analysis = result.get("complete_analysis", {})
            learning_insights = analysis.get("learning_insights", {})

            print(f"\n✅ 완전한 학습 분석 결과:")
            print(f"   📊 전체 점수: {learning_insights.get('overall_score', 0):.2f}")
            print(f"   📊 성공 수준: {learning_insights.get('success_level', 'N/A')}")
            print(f"   💡 핵심 교훈: {learning_insights.get('key_lesson', 'N/A')}")

            success_factors = learning_insights.get("success_factors", [])
            if success_factors:
                print(f"   ✅ 성공 요인: {', '.join(success_factors[:3])}")

            improvement_areas = learning_insights.get("improvement_areas", [])
            if improvement_areas:
                print(f"   🔧 개선 영역: {', '.join(improvement_areas[:3])}")

            next_actions = learning_insights.get("next_actions", [])
            if next_actions:
                print(f"   🚀 다음 행동: {', '.join(next_actions[:3])}")
        else:
            print(f"   ❌ 오류: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"   ❌ 오류: {e}")


def test_learning_summary():
    """학습 분석 요약 테스트"""
    base_url = "http://localhost:8088"
    print("\n📈 DuRi 학습 분석 요약 테스트")

    try:
        response = requests.get(f"{base_url}/learning/analysis-summary")
        result = response.json()

        if result.get("status") == "success":
            summary = result.get("summary", {})
            print(f"   📊 총 분석 수: {summary.get('total_analyses', 0)}")
            print(f"   📊 평균 성공률: {summary.get('average_success_rate', 0):.2f}")
            print(f"   💡 주요 교훈: {summary.get('key_lessons', [])}")
            print(f"   🔧 개선 우선순위: {summary.get('improvement_priorities', [])}")
        else:
            print(f"   ❌ 오류: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"   ❌ 오류: {e}")


def test_integration_with_existing_systems():
    """기존 시스템과의 통합 테스트"""
    base_url = "http://localhost:8088"
    print("\n🔄 기존 시스템과의 통합 테스트")

    # 1. 실시간 학습 시작
    print("1️⃣ 실시간 학습 시작")
    try:
        response = requests.post(f"{base_url}/realtime-learning/start")
        result = response.json()
        print(f"   결과: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 2. 자동 학습 시작
    print("2️⃣ 자동 학습 시작")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/start")
        result = response.json()
        print(f"   결과: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 3. 통합 학습 분석
    print("3️⃣ 통합 학습 분석")
    test_conversation = {
        "user_input": "DuRi의 새로운 학습 시스템이 잘 작동하나요?",
        "duri_response": "네! 새로운 학습 시스템이 성공적으로 구현되었습니다. 의미 추출과 결과 평가가 모두 작동하고 있으며, 실시간 학습과 자동 학습 시스템과도 잘 통합되어 있습니다.",
    }

    try:
        response = requests.post(f"{base_url}/learning/complete-analysis", json=test_conversation)
        result = response.json()

        if result.get("status") == "success":
            analysis = result.get("complete_analysis", {})
            learning_insights = analysis.get("learning_insights", {})

            print(f"   ✅ 통합 분석 성공")
            print(f"   📊 점수: {learning_insights.get('overall_score', 0):.2f}")
            print(f"   📊 수준: {learning_insights.get('success_level', 'N/A')}")
        else:
            print(f"   ❌ 오류: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 4. 시스템 중지
    print("4️⃣ 시스템 중지")
    try:
        requests.post(f"{base_url}/realtime-learning/stop")
        requests.post(f"{base_url}/autonomous-learning/stop")
        print("   ✅ 모든 시스템 중지 완료")
    except Exception as e:
        print(f"   ❌ 오류: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DuRi 새로운 학습 시스템 테스트")
    print("=" * 60)

    # 각 시스템별 테스트
    test_meaning_extraction()
    test_result_evaluation()
    test_complete_learning_analysis()
    test_learning_summary()
    test_integration_with_existing_systems()

    print("\n" + "=" * 60)
    print("🎉 새로운 학습 시스템 테스트 완료!")
    print("=" * 60)
