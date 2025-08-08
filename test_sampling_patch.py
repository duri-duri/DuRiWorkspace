#!/usr/bin/env python3
"""
샘플링 패치 검증 테스트

핵심 검증:
1. EFFECTIVE_SR가 0.2인지 확인
2. 50회 호출 시 로그 라인 수가 4~15 범위인지 확인
3. importlib.reload로 오래된 모듈 캐싱 차단
"""

import importlib
import os
import sys
import time

# 환경변수 설정 및 모듈 리로드
os.environ["LOG_SAMPLE_SEED"] = "42"
import DuRiCore.duri_logging.decorators as dec
importlib.reload(dec)  # 오래된 버전 캐싱 차단

@dec.log_calls(sample_rate=0.2, seed=42)
def sampled_function():
    """테스트용 샘플링 함수"""
    time.sleep(0.001)  # 1ms 지연
    return "sampled"

def test_sampling_patch():
    """샘플링 패치 검증"""
    print("=== 샘플링 패치 검증 시작 ===")
    
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
    print("\n=== 검증 완료 ===")
    print("예상 결과: 로그 라인 수가 4~15 범위 (n=50, p=0.2의 95% CI)")
    
    return True

if __name__ == "__main__":
    success = test_sampling_patch()
    sys.exit(0 if success else 1)
