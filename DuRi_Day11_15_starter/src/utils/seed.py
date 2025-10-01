# Seed Management Utilities
"""
공통 시드 관리 유틸리티
플래키 방지를 위한 결정적 실행 보장
"""
import os
import random

import numpy as np


def set_deterministic_seed(seed: int):
    """모든 랜덤 시드를 결정적으로 설정"""
    # Python 내장 random
    random.seed(seed)

    # NumPy (있는 경우)
    try:
        np.random.seed(seed)
    except ImportError:
        pass

    # 환경변수 설정
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["PYTHONHASHSEED"] = str(seed)


def get_consistent_seed(base_seed: int, day: int, variant: str) -> int:
    """Day와 Variant에 따른 일관된 시드 생성"""
    # 간단한 해시 기반 시드 생성
    hash_input = f"{base_seed}_{day}_{variant}"
    return hash(hash_input) % (2**31)  # 32비트 정수 범위
