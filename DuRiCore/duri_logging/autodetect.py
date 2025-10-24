#!/usr/bin/env python3
"""
DuRi 모듈 자동 감지 시스템

경로/모듈명으로 컴포넌트를 자동 추론합니다.
"""

import re

# DuRi 모듈 규칙 (우선순위 고정 - 긴 패턴이 앞에)
RAW_RULES = [
    (r"\bduri_evolution\b", "evolution"),  # 가장 구체적인 패턴 우선
    (r"\bduri_core\b", "core"),
    (r"\bduri_brain\b", "brain"),
    (r"\bduri_modules\b", "modules"),
    (r"\bjudg(e)?ment\b", "judgment"),
    (r"\blearning\b", "learning"),
    (r"\bmemory\b", "memory"),
    (r"\bautonomous\b", "autonomous"),
    (r"\bcreativity\b", "creativity"),
    (r"\bgoals\b", "goals"),
    (r"\bethics\b", "ethics"),
    (r"\bmeta_learning\b", "meta_learning"),
    (r"\bretrospector\b", "retrospector"),
    (r"\bconversation\b", "conversation"),
    (r"\bunified\b", "unified"),
]

# 사전컴파일된 정규식 규칙
RULES = [(re.compile(pattern, re.IGNORECASE), tag) for pattern, tag in RAW_RULES]


def infer_component(logger_name: str, default: str = "_") -> str:
    """
    로거 이름에서 컴포넌트를 추론합니다.

    Args:
        logger_name: 로거 이름 (예: "DuRiCore.learning.engine")
        default: 매칭되지 않을 때 반환할 기본값

    Returns:
        추론된 컴포넌트 태그
    """
    for pattern, tag in RULES:
        if pattern.search(logger_name):
            return tag

    return default


def get_component_from_path(file_path: str, default: str = "_") -> str:
    """
    파일 경로에서 컴포넌트를 추론합니다.

    Args:
        file_path: 파일 경로 (예: "DuRiCore/learning/engine.py")
        default: 매칭되지 않을 때 반환할 기본값

    Returns:
        추론된 컴포넌트 태그
    """
    # 경로 구분자를 공백으로 변환하여 검색
    path_normalized = file_path.replace("/", " ").replace("\\", " ")

    for pattern, tag in RULES:
        if pattern.search(path_normalized):
            return tag

    return default


def get_component_from_module(module_name: str, default: str = "_") -> str:
    """
    모듈 이름에서 컴포넌트를 추론합니다.

    Args:
        module_name: 모듈 이름 (예: "DuRiCore.learning.engine")
        default: 매칭되지 않을 때 반환할 기본값

    Returns:
        추론된 컴포넌트 태그
    """
    return infer_component(module_name, default)


def test_autodetect():
    """자동 감지 시스템을 테스트합니다."""
    test_cases = [
        # (logger_name, expected_component)
        ("DuRiCore.duri_evolution.run", "evolution"),
        ("DuRiCore.duri_core.memory", "core"),
        ("DuRiCore.duri_brain.learning", "brain"),
        ("DuRiCore.duri_modules.autonomous", "modules"),
        ("DuRiCore.learning.engine", "learning"),
        ("DuRiCore.judgment.selector", "judgment"),
        ("DuRiCore.memory.store", "memory"),
        ("DuRiCore.autonomous.core", "autonomous"),
        ("DuRiCore.creativity.generator", "creativity"),
        ("DuRiCore.goals.setter", "goals"),
        ("DuRiCore.ethics.judge", "ethics"),
        ("DuRiCore.meta_learning.analyzer", "meta_learning"),
        ("DuRiCore.retrospector.analyzer", "retrospector"),
        ("DuRiCore.conversation.service", "conversation"),
        ("DuRiCore.unified.system", "unified"),
        ("unknown.module", "_"),  # 매칭되지 않는 경우
    ]

    for logger_name, expected in test_cases:
        result = infer_component(logger_name)
        assert result == expected, f"Expected {expected} for {logger_name}, got {result}"

    # 경로 테스트
    path_test_cases = [
        ("DuRiCore/learning/engine.py", "learning"),
        ("DuRiCore/duri_brain/judgment.py", "brain"),
        ("unknown/path/file.py", "_"),
    ]

    for file_path, expected in path_test_cases:
        result = get_component_from_path(file_path)
        assert result == expected, f"Expected {expected} for {file_path}, got {result}"

    print("✅ 자동 감지 시스템 테스트 통과")
    return True


def get_all_components() -> list:
    """모든 지원되는 컴포넌트 목록을 반환합니다."""
    return [tag for _, tag in RAW_RULES]


if __name__ == "__main__":
    test_autodetect()
