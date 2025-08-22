#!/usr/bin/env python3
"""
DuRi 메트릭 샘플 생성 스크립트
"""

import sys
import time
import os

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from duri_core.core.metrics import observe_phase

def generate_samples():
    """각 Phase에 대해 메트릭 샘플 생성"""
    phases = ["plan", "edit", "test", "promote", "gate_enter", "gate_decide"]
    
    print("🚀 메트릭 샘플 생성 시작...")
    
    for phase in phases:
        print(f"   📊 {phase} phase 샘플 생성 중...")
        with observe_phase(phase):
            time.sleep(0.1)  # 0.1초 시뮬레이션
        print(f"   ✅ {phase} phase 완료")
    
    print("🎯 모든 Phase 메트릭 샘플 생성 완료!")

if __name__ == "__main__":
    generate_samples()







