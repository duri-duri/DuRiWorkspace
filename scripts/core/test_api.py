#!/usr/bin/env python3
"""
API Test Script for DuRi Emotion Processing System
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, Optional

import requests

from duri_common.config.config import Config
from duri_common.config.emotion_labels import ALL_EMOTIONS

# 설정 로드
config = Config()


class EmotionAPITester:
    """DuRi Emotion API 테스터 클래스"""

    def __init__(self, base_url: str = None, timeout: int = 10):
        """
        초기화

        Args:
            base_url (str): API 기본 URL
            timeout (int): 요청 타임아웃 (초)
        """
        self.base_url = base_url or config.get_local_emotion_url().replace("/emotion", "")
        self.timeout = timeout
        self.session = requests.Session()

        # 기본 헤더 설정
        self.session.headers.update({"Content-Type": "application/json", "User-Agent": "DuRi-API-Tester/1.0"})

    def test_health(self) -> bool:
        """헬스 체크 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 헬스 체크 성공: {data}")
                return True
            else:
                print(f"❌ 헬스 체크 실패: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 헬스 체크 오류: {e}")
            return False

    def test_index(self) -> bool:
        """인덱스 페이지 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 인덱스 페이지 성공: {data}")
                return True
            else:
                print(f"❌ 인덱스 페이지 실패: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 인덱스 페이지 오류: {e}")
            return False

    def send_emotion(self, emotion: str, intensity: float = 0.8, **kwargs) -> Optional[Dict]:
        """
        감정 데이터 전송

        Args:
            emotion (str): 감정
            intensity (float): 강도
            **kwargs: 추가 데이터

        Returns:
            Dict: 응답 데이터 또는 None (실패 시)
        """
        payload = {
            "emotion": emotion,
            "intensity": intensity,
            "timestamp": datetime.now().isoformat(),
            **kwargs,
        }

        try:
            response = self.session.post(f"{self.base_url}/emotion", json=payload, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 감정 전송 성공: {emotion} (강도: {intensity})")
                print(f"📤 전송: {json.dumps(payload, ensure_ascii=False)}")
                print(f"📥 응답: {json.dumps(data, ensure_ascii=False)}")
                return data
            else:
                print(f"❌ 감정 전송 실패: HTTP {response.status_code}")
                print(f"📤 전송: {json.dumps(payload, ensure_ascii=False)}")
                print(f"📥 응답: {response.text}")
                return None

        except Exception as e:
            print(f"❌ 감정 전송 오류: {e}")
            return None

    def test_basic_emotions(self) -> None:
        """기본 감정 테스트"""
        print("\n=== 기본 감정 테스트 ===")

        # 하드코딩된 리스트 대신 ALL_EMOTIONS 사용
        emotions = ALL_EMOTIONS[:8]  # 처음 8개 감정만 사용

        for emotion in emotions:
            self.send_emotion(emotion)
            time.sleep(1)  # 1초 대기

    def test_intensity_levels(self, emotion: str = "curious") -> None:
        """강도별 테스트"""
        print(f"\n=== 강도별 테스트 ({emotion}) ===")

        intensities = [0.1, 0.3, 0.5, 0.7, 0.9]

        for intensity in intensities:
            self.send_emotion(emotion, intensity)
            time.sleep(1)

    def test_continuous(self, count: int = 10) -> None:
        """연속 테스트"""
        print(f"\n=== 연속 테스트 ({count}회) ===")

        for i in range(1, count + 1):
            emotion = f"test_emotion_{i}"
            self.send_emotion(emotion)
            time.sleep(0.5)

    def test_custom_emotion(self, emotion: str, intensity: float = 0.8) -> None:
        """사용자 정의 감정 테스트"""
        print("\n=== 사용자 정의 감정 테스트 ===")
        self.send_emotion(emotion, intensity)

    def test_stress(self, count: int = 50, delay: float = 0.1) -> None:
        """스트레스 테스트"""
        print(f"\n=== 스트레스 테스트 ({count}회, {delay}초 간격) ===")

        start_time = time.time()
        success_count = 0

        for i in range(count):
            emotion = f"stress_test_{i}"
            result = self.send_emotion(emotion, 0.5)
            if result:
                success_count += 1
            time.sleep(delay)

        end_time = time.time()
        duration = end_time - start_time
        success_rate = (success_count / count) * 100

        print("\n📊 스트레스 테스트 결과:")
        print(f"   총 요청: {count}")
        print(f"   성공: {success_count}")
        print(f"   실패: {count - success_count}")
        print(f"   성공률: {success_rate:.1f}%")
        print(f"   소요시간: {duration:.2f}초")
        print(f"   평균 응답시간: {duration/count:.3f}초")

    def test_error_cases(self) -> None:
        """오류 케이스 테스트"""
        print("\n=== 오류 케이스 테스트 ===")

        # 빈 감정
        print("\n1. 빈 감정 테스트:")
        self.send_emotion("")

        # 잘못된 JSON
        print("\n2. 잘못된 JSON 테스트:")
        try:
            response = self.session.post(
                f"{self.base_url}/emotion",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            print(f"응답: HTTP {response.status_code}")
        except Exception as e:
            print(f"오류: {e}")

        # 존재하지 않는 엔드포인트
        print("\n3. 존재하지 않는 엔드포인트 테스트:")
        try:
            response = self.session.get(f"{self.base_url}/nonexistent", timeout=self.timeout)
            print(f"응답: HTTP {response.status_code}")
        except Exception as e:
            print(f"오류: {e}")

    def test_all_emotions(self) -> None:
        """모든 감정 테스트"""
        print(f"\n=== 모든 감정 테스트 ({len(ALL_EMOTIONS)}개) ===")

        success_count = 0
        total_count = len(ALL_EMOTIONS)

        for i, emotion in enumerate(ALL_EMOTIONS, 1):
            print(f"\n[{i}/{total_count}] 테스트 중: {emotion}")
            result = self.send_emotion(emotion)
            if result:
                success_count += 1
            time.sleep(0.5)  # 0.5초 대기

        print("\n📊 모든 감정 테스트 결과:")
        print(f"   총 감정: {total_count}")
        print(f"   성공: {success_count}")
        print(f"   실패: {total_count - success_count}")
        print(f"   성공률: {(success_count / total_count) * 100:.1f}%")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="DuRi Emotion API 테스트 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python test_api.py health                    # 헬스 체크
  python test_api.py basic                     # 기본 감정 테스트
  python test_api.py intensity curious         # 강도별 테스트
  python test_api.py continuous 20             # 연속 테스트 (20회)
  python test_api.py custom happy 0.9          # 사용자 정의 테스트
  python test_api.py stress 100 0.05           # 스트레스 테스트
  python test_api.py error                     # 오류 케이스 테스트
  python test_api.py all                       # 모든 테스트 실행
        """,
    )

    parser.add_argument(
        "test_type",
        choices=[
            "health",
            "basic",
            "intensity",
            "continuous",
            "custom",
            "stress",
            "error",
            "all",
        ],
        help="테스트 타입",
    )

    parser.add_argument("--emotion", "-e", default="curious", help="감정 (기본값: curious)")

    parser.add_argument("--intensity", "-i", type=float, default=0.8, help="강도 (기본값: 0.8)")

    parser.add_argument("--count", "-c", type=int, default=10, help="테스트 횟수 (기본값: 10)")

    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="요청 간 대기 시간 (초, 기본값: 1.0)",
    )

    parser.add_argument("--url", "-u", help="API 기본 URL (기본값: 환경변수에서 가져옴)")

    parser.add_argument("--timeout", "-t", type=int, default=10, help="요청 타임아웃 (초, 기본값: 10)")

    parser.add_argument("--verbose", "-v", action="store_true", help="상세 출력")

    args = parser.parse_args()

    # 테스터 초기화
    tester = EmotionAPITester(base_url=args.url, timeout=args.timeout)

    print("🚀 DuRi Emotion API 테스트 시작")
    print(f"📍 API URL: {tester.base_url}")
    print(f"⏱️  타임아웃: {args.timeout}초")
    print("=" * 50)

    try:
        if args.test_type == "health":
            tester.test_health()

        elif args.test_type == "basic":
            tester.test_basic_emotions()

        elif args.test_type == "intensity":
            tester.test_intensity_levels(args.emotion)

        elif args.test_type == "continuous":
            tester.test_continuous(args.count)

        elif args.test_type == "custom":
            tester.test_custom_emotion(args.emotion, args.intensity)

        elif args.test_type == "stress":
            tester.test_stress(args.count, args.delay)

        elif args.test_type == "error":
            tester.test_error_cases()

        elif args.test_type == "all":
            print("=== 전체 테스트 실행 ===")
            tester.test_health()
            tester.test_index()
            tester.test_basic_emotions()
            tester.test_intensity_levels()
            tester.test_continuous(5)
            tester.test_all_emotions()
            tester.test_error_cases()

    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        sys.exit(1)

    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    main()
