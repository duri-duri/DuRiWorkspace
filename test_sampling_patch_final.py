#!/usr/bin/env python3
"""
샘플링 패치 최종 검증 테스트

새로운 로그 파일 생성 + 샘플링 검증
"""

import importlib
import logging
import os
import sys
import time
from datetime import datetime

# 환경변수 설정 및 모듈 리로드
os.environ["LOG_SAMPLE_SEED"] = "42"
import DuRiCore.duri_logging.decorators as dec  # noqa: E402

importlib.reload(dec)  # 오래된 버전 캐싱 차단

# 새로운 로그 파일 설정
log_filename = f"sampling_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
)


@dec.log_calls(sample_rate=0.2, seed=42)
def sampled_function():
    """테스트용 샘플링 함수"""
    time.sleep(0.001)  # 1ms 지연
    return "sampled"


def test_sampling_patch_final():
    """샘플링 패치 최종 검증"""
    print("=== 샘플링 패치 최종 검증 시작 ===")
    print(f"로그 파일: {log_filename}")

    # 1. EFFECTIVE_SR 확인
    effective_sr = getattr(sampled_function, "__log_sample_rate__", None)
    print(f"EFFECTIVE_SR = {effective_sr}")

    if effective_sr != 0.2:
        print(f"❌ FAIL: EFFECTIVE_SR가 0.2가 아님 ({effective_sr})")
        return False

    print("✅ EFFECTIVE_SR = 0.2 확인됨")

    # 2. 50회 호출하여 샘플링 확인
    print("\n50회 호출 중...")
    for i in range(50):
        sampled_function()
        if (i + 1) % 10 == 0:
            print(f"진행률: {i + 1}/50")

    print("✅ 50회 호출 완료")

    # 3. 로그 파일에서 샘플링 라인 수 확인
    time.sleep(1)  # 로그 파일 쓰기 대기

    if os.path.exists(log_filename):
        with open(log_filename, "r") as f:
            lines = f.readlines()
            sampled_lines = [line for line in lines if "sampled_function" in line]
            sampled_calls = len(sampled_lines) // 2  # 시작+완료 = 2라인
            print(f"sampled_function 관련 로그 라인 수: {len(sampled_lines)}")
            print(f"로깅된 호출 수: {sampled_calls}/50")
            print(f"실제 샘플링 비율: {sampled_calls/50:.1%}")

            # n=50, p=0.2의 95% CI: 약 5~15회 (더 관대한 범위)
            if 5 <= sampled_calls <= 15:
                print(f"✅ PASS: 로깅된 호출 수 {sampled_calls}가 예상 범위(5~15) 내")
                print("예상: n=50, p=0.2의 95% CI ≈ 5~15회")
                return True
            else:
                print(f"❌ FAIL: 로깅된 호출 수 {sampled_calls}가 예상 범위(5~15) 밖")
                print("예상: n=50, p=0.2의 95% CI ≈ 5~15회")
                return False
    else:
        print("❌ FAIL: 로그 파일이 생성되지 않음")
        return False


if __name__ == "__main__":
    success = test_sampling_patch_final()
    print(f"\n최종 결과: {'✅ PASS' if success else '❌ FAIL'}")
    sys.exit(0 if success else 1)
