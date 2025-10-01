#!/usr/bin/env python3
"""
DuRiCore 새로운 API 테스트
FastAPI 분리 완료 후 API 테스트
"""

import json
import time
from typing import Any, Dict

import requests

# API 기본 URL
BASE_URL = "http://localhost:8000"


def test_root_endpoint():
    """루트 엔드포인트 테스트"""
    print("🏠 루트 엔드포인트 테스트...")

    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"오류: {e}")
        return False


def test_system_info():
    """시스템 정보 테스트"""
    print("\n📊 시스템 정보 테스트...")

    try:
        response = requests.get(f"{BASE_URL}/info")
        print(f"상태 코드: {response.status_code}")
        data = response.json()
        print(f"시스템: {data.get('system')}")
        print(f"버전: {data.get('version')}")
        print(f"완료된 엔진: {len(data.get('completed_engines', []))}개")
        return response.status_code == 200
    except Exception as e:
        print(f"오류: {e}")
        return False


def test_emotion_api():
    """감정 API 테스트"""
    print("\n😊 감정 API 테스트...")

    # 감정 분석 테스트
    test_cases = [
        {
            "text": "오늘 정말 기분이 좋아요! 새로운 프로젝트가 성공했어요.",
            "context": {"type": "work", "user_mood": "positive"},
        },
        {
            "text": "너무 화가 나요. 계속 실패만 하고 있어요.",
            "context": {"type": "personal", "user_mood": "negative"},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"입력: {test_case['text']}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/emotion/analyze", json=test_case
            )
            print(f"상태 코드: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"주요 감정: {data.get('primary_emotion')}")
                print(f"강도: {data.get('intensity')}")
                print(f"신뢰도: {data.get('confidence')}")
            else:
                print(f"오류: {response.text}")

        except Exception as e:
            print(f"오류: {e}")

    # 통계 조회 테스트
    try:
        response = requests.get(f"{BASE_URL}/api/v1/emotion/stats")
        print(f"\n통계 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("통계 조회 성공")
    except Exception as e:
        print(f"통계 조회 오류: {e}")


def test_learning_api():
    """학습 API 테스트"""
    print("\n📚 학습 API 테스트...")

    # 학습 처리 테스트
    test_cases = [
        {
            "content": "인공지능에 대한 깊이 있는 텍스트를 읽었습니다. 머신러닝과 딥러닝의 차이점을 이해하게 되었고, 실제 응용 사례들도 배웠습니다.",
            "learning_type": "text",
            "context": {"complexity": "high", "domain": "technology"},
        },
        {
            "content": "가족과 함께 영화를 보면서 아이의 반응을 관찰했습니다. 아이가 어떤 장면에서 웃고, 어떤 장면에서 집중하는지 알 수 있었습니다.",
            "learning_type": "family",
            "context": {
                "family_members": ["parent", "child"],
                "activity": "movie_watching",
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"콘텐츠: {test_case['content'][:50]}...")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/learning/process", json=test_case
            )
            print(f"상태 코드: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"콘텐츠 타입: {data.get('content_type')}")
                print(f"학습 점수: {data.get('learning_score')}")
                print(f"인사이트: {len(data.get('insights', []))}개")
            else:
                print(f"오류: {response.text}")

        except Exception as e:
            print(f"오류: {e}")

    # 콘텐츠 타입 조회 테스트
    try:
        response = requests.get(f"{BASE_URL}/api/v1/learning/content-types")
        print(f"\n콘텐츠 타입 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"지원되는 타입: {data.get('content_types', [])}")
    except Exception as e:
        print(f"콘텐츠 타입 조회 오류: {e}")


def test_ethical_api():
    """윤리 API 테스트"""
    print("\n⚖️ 윤리 API 테스트...")

    # 윤리 분석 테스트
    test_cases = [
        {
            "situation": "친구가 시험에서 부정행위를 했는데, 이를 고발해야 할지 망설이고 있습니다. 친구를 보호하고 싶지만, 공정성도 중요합니다.",
            "context": {"complexity": "medium", "stakeholders": 2},
        },
        {
            "situation": "환경을 위해 자동차 대신 대중교통을 이용하는 것이 좋지만, 시간이 오래 걸려서 불편합니다. 개인의 편의와 공공의 이익 사이에서 갈등합니다.",
            "context": {"complexity": "medium", "stakeholders": 2},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"상황: {test_case['situation'][:50]}...")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ethical/analyze", json=test_case
            )
            print(f"상태 코드: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"윤리 점수: {data.get('ethical_score')}")
                print(f"신뢰도: {data.get('confidence')}")
                print(f"권장 행동: {data.get('recommended_action')}")
            else:
                print(f"오류: {response.text}")

        except Exception as e:
            print(f"오류: {e}")

    # 윤리 원칙 조회 테스트
    try:
        response = requests.get(f"{BASE_URL}/api/v1/ethical/principles")
        print(f"\n윤리 원칙 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"지원되는 원칙: {data.get('principles', [])}")
    except Exception as e:
        print(f"윤리 원칙 조회 오류: {e}")


def test_evolution_api():
    """자기 진화 API 테스트"""
    print("\n🔄 자기 진화 API 테스트...")

    # 자기 진화 분석 테스트
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/evolution/analyze", json={"context": {"test": True}}
        )
        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"진화 점수: {data.get('evolution_score')}")
            print(f"개선 영역: {len(data.get('improvement_areas', []))}개")
            print(f"진화 방향: {len(data.get('evolution_directions', []))}개")
        else:
            print(f"오류: {response.text}")

    except Exception as e:
        print(f"오류: {e}")

    # 개선 영역 조회 테스트
    try:
        response = requests.get(f"{BASE_URL}/api/v1/evolution/improvement-areas")
        print(f"\n개선 영역 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("개선 영역 조회 성공")
    except Exception as e:
        print(f"개선 영역 조회 오류: {e}")


def test_health_api():
    """헬스체크 API 테스트"""
    print("\n💚 헬스체크 API 테스트...")

    # 전체 시스템 헬스체크
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/")
        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"전체 상태: {data.get('status')}")
            print(f"시스템: {data.get('system')}")
            print(f"버전: {data.get('version')}")

            summary = data.get("summary", {})
            print(f"총 엔진: {summary.get('total_engines')}")
            print(f"정상 엔진: {summary.get('healthy_engines')}")
            print(f"건강도: {summary.get('health_percentage')}%")
        else:
            print(f"오류: {response.text}")

    except Exception as e:
        print(f"오류: {e}")

    # 엔진 정보 조회
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/engines")
        print(f"\n엔진 정보 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            engines = data.get("engines", {})
            print(f"등록된 엔진: {len(engines)}개")
            for engine_name, engine_info in engines.items():
                print(
                    f"  - {engine_info.get('name')}: {engine_info.get('description')}"
                )
    except Exception as e:
        print(f"엔진 정보 조회 오류: {e}")

    # 버전 정보 조회
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/version")
        print(f"\n버전 정보 조회 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"시스템: {data.get('system')}")
            print(f"버전: {data.get('version')}")
            print(f"현재 단계: {data.get('phase')}")
    except Exception as e:
        print(f"버전 정보 조회 오류: {e}")


def main():
    """메인 테스트 함수"""
    print("🚀 DuRiCore 새로운 API 테스트 시작!")
    print("=" * 60)

    # 서버가 실행 중인지 확인
    print("서버 연결 확인 중...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 서버가 정상적으로 실행 중입니다.")
        else:
            print("❌ 서버 응답이 예상과 다릅니다.")
            return
    except Exception as e:
        print(f"❌ 서버에 연결할 수 없습니다: {e}")
        print("서버를 먼저 실행해주세요: python DuRiCore/DuRiCore/interface/main.py")
        return

    # 각 API 테스트 실행
    tests = [
        test_root_endpoint,
        test_system_info,
        test_emotion_api,
        test_learning_api,
        test_ethical_api,
        test_evolution_api,
        test_health_api,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"테스트 실행 중 오류: {e}")
            results.append(False)

    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    successful_tests = sum(results)
    total_tests = len(results)

    print(f"총 테스트: {total_tests}")
    print(f"성공: {successful_tests}")
    print(f"실패: {total_tests - successful_tests}")
    print(f"성공률: {(successful_tests / total_tests) * 100:.1f}%")

    if successful_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")


if __name__ == "__main__":
    main()
