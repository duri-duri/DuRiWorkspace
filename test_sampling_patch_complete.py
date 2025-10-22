#!/usr/bin/env python3
"""
샘플링 패치 완전 검증 테스트

로깅 시스템 초기화 + 샘플링 검증
"""

import importlib
import os
import sys
import tempfile
import time

# 환경변수 설정 및 모듈 리로드
os.environ["LOG_SAMPLE_SEED"] = "42"
import DuRiCore.duri_logging.decorators as dec

importlib.reload(dec)  # 오래된 버전 캐싱 차단

# 로깅 시스템 초기화
from DuRiCore.duri_logging.setup import setup_logging

setup_logging()


@dec.log_calls(sample_rate=0.2, seed=42)
def sampled_function():
    """테스트용 샘플링 함수"""
    time.sleep(0.001)  # 1ms 지연
    return "sampled"


def test_sampling_patch_complete():
    """샘플링 패치 완전 검증"""
    print("=== 샘플링 패치 완전 검증 시작 ===")

    # 1. EFFECTIVE_SR 확인
    effective_sr = getattr(sampled_function, "__log_sample_rate__", None)
    print(f"EFFECTIVE_SR = {effective_sr}")

    if effective_sr != 0.2:
        print(f"❌ FAIL: EFFECTIVE_SR가 0.2가 아님 ({effective_sr})")
        return False

    print("✅ EFFECTIVE_SR = 0.2 확인됨")

    # 2. 로그 파일 확인
    log_files = [f for f in os.listdir(".") if f.endswith(".log")]
    print(f"현재 로그 파일들: {log_files}")

    # 3. 50회 호출하여 샘플링 확인
    print("\n50회 호출 중...")
    for i in range(50):
        sampled_function()
        if (i + 1) % 10 == 0:
            print(f"진행률: {i + 1}/50")

    print("✅ 50회 호출 완료")

    # 4. 로그 파일 재확인
    time.sleep(1)  # 로그 파일 쓰기 대기
    log_files_after = [f for f in os.listdir(".") if f.endswith(".log")]
    print(f"호출 후 로그 파일들: {log_files_after}")

    # 5. 최신 로그 파일에서 샘플링 라인 수 확인
    if log_files_after:
        latest_log = max(log_files_after, key=lambda f: os.path.getmtime(f))
        print(f"최신 로그 파일: {latest_log}")

        with open(latest_log, "r") as f:
            lines = f.readlines()
            sampled_lines = [line for line in lines if "sampled_function" in line]
            print(f"sampled_function 관련 로그 라인 수: {len(sampled_lines)}")

            if 4 <= len(sampled_lines) <= 15:
                print(f"✅ PASS: 로그 라인 수 {len(sampled_lines)}가 예상 범위(4~15) 내")
                return True
            else:
                print(f"❌ FAIL: 로그 라인 수 {len(sampled_lines)}가 예상 범위(4~15) 밖")
                return False
    else:
        print("❌ FAIL: 로그 파일이 생성되지 않음")
        return False


if __name__ == "__main__":
    success = test_sampling_patch_complete()
    print(f"\n최종 결과: {'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)
