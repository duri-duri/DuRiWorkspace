#!/usr/bin/env python3
"""
DuRi 메모리 타입 정규화

메모리 타입을 안전하게 정규화하고 별칭을 지원합니다.
"""

from enum import Enum
from typing import Union

class MemoryType(str, Enum):
    """메모리 타입 Enum"""
    LEARNING_EXPERIENCE = "LEARNING_EXPERIENCE"
    ETHICS = "ETHICS"
    GOAL = "GOAL"
    CREATIVITY = "CREATIVITY"
    ASSESSMENT = "ASSESSMENT"
    EXTERNAL = "EXTERNAL"
    META_LEARNING = "META_LEARNING"

# 별칭 매핑 (소문자)
ALIASES = {
    "learning": "LEARNING_EXPERIENCE",
    "learn_exp": "LEARNING_EXPERIENCE",
    "experience": "LEARNING_EXPERIENCE",
    "ethic": "ETHICS",
    "ethical": "ETHICS",
    "goal_state": "GOAL",
    "goals": "GOAL",
    "creative": "CREATIVITY",
    "creativity": "CREATIVITY",
    "assess": "ASSESSMENT",
    "assessment": "ASSESSMENT",
    "external": "EXTERNAL",
    "ext": "EXTERNAL",
    "meta": "META_LEARNING",
    "meta_learning": "META_LEARNING"
}

def normalize_memory_type(v: Union[str, MemoryType, None]) -> MemoryType:
    """
    메모리 타입을 정규화합니다.
    
    Args:
        v: 정규화할 메모리 타입 (문자열, Enum, None)
        
    Returns:
        정규화된 MemoryType
        
    Raises:
        ValueError: 알 수 없는 메모리 타입인 경우
    """
    # None 처리
    if v is None:
        return MemoryType.LEARNING_EXPERIENCE
    
    # 이미 MemoryType인 경우
    if isinstance(v, MemoryType):
        return v
    
    # 문자열 처리
    if isinstance(v, str):
        key_raw = v.strip()
        
        # 1) 정식 Enum 이름으로 들어온 경우 (대문자)
        key_up = key_raw.upper()
        if key_up in MemoryType.__members__:
            return MemoryType[key_up]
        
        # 2) 별칭으로 들어온 경우 (소문자 비교)
        key_low = key_raw.lower()
        if key_low in ALIASES:
            return MemoryType(ALIASES[key_low])
        
        # 3) 값 자체가 정식 값일 때도 허용
        try:
            return MemoryType(key_up)
        except ValueError:
            pass
    
    raise ValueError(f"Unknown memory type: {v!r}")

def test_memory_normalization():
    """메모리 타입 정규화를 테스트합니다."""
    # 기본 테스트
    assert normalize_memory_type("learning") == MemoryType.LEARNING_EXPERIENCE
    assert normalize_memory_type("LEARNING_EXPERIENCE") == MemoryType.LEARNING_EXPERIENCE
    assert normalize_memory_type("Learn_Exp") == MemoryType.LEARNING_EXPERIENCE
    assert normalize_memory_type("CREATIVITY") == MemoryType.CREATIVITY
    assert normalize_memory_type(MemoryType.GOAL) == MemoryType.GOAL
    
    # 별칭 테스트
    assert normalize_memory_type("ethic") == MemoryType.ETHICS
    assert normalize_memory_type("creative") == MemoryType.CREATIVITY
    assert normalize_memory_type("assess") == MemoryType.ASSESSMENT
    
    # None 테스트
    assert normalize_memory_type(None) == MemoryType.LEARNING_EXPERIENCE
    
    print("✅ 메모리 타입 정규화 테스트 통과")
    return True

if __name__ == "__main__":
    test_memory_normalization()
