#!/usr/bin/env python3
"""
DuRi 로깅 안전성 및 메모리 타입 정규화 테스트

모든 로깅 충돌과 메모리 타입 문제를 해결했는지 확인합니다.
"""

import logging
import sys
import traceback

# 테스트 모듈 import
from logging_setup import setup_logging, test_logging_safety
from memory_types import (MemoryType, normalize_memory_type,
                          test_memory_normalization)


def test_comprehensive_logging():
    """종합 로깅 테스트"""
    print("🔍 종합 로깅 안전성 테스트 시작...")

    try:
        # 1. 기본 로깅 설정
        setup_logging()
        logger = logging.getLogger("comprehensive_test")

        # 2. extra 없는 로깅
        logger.info("extra 없는 로깅 테스트")

        # 3. module 키 사용 (충돌 방지)
        logger.info("module 키 사용", extra={"module": "memory"})

        # 4. 예약 키 사용 (우회 확인)
        logger.info("예약 키 사용", extra={"filename": "test.py", "process": 123})

        # 5. component 직접 사용
        logger.info("component 직접 사용", extra={"component": "brain"})

        # 6. 복합 extra 사용
        logger.info(
            "복합 extra",
            extra={
                "module": "test",
                "filename": "test.py",
                "process": 123,
                "custom_field": "value",
            },
        )

        print("✅ 종합 로깅 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ 로깅 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_memory_type_comprehensive():
    """종합 메모리 타입 테스트"""
    print("🔍 종합 메모리 타입 정규화 테스트 시작...")

    try:
        # 1. 기본 타입들
        assert normalize_memory_type("learning") == MemoryType.LEARNING_EXPERIENCE
        assert normalize_memory_type("LEARNING_EXPERIENCE") == MemoryType.LEARNING_EXPERIENCE
        assert normalize_memory_type("Learn_Exp") == MemoryType.LEARNING_EXPERIENCE

        # 2. 별칭 테스트
        assert normalize_memory_type("ethic") == MemoryType.ETHICS
        assert normalize_memory_type("creative") == MemoryType.CREATIVITY
        assert normalize_memory_type("assess") == MemoryType.ASSESSMENT

        # 3. Enum 객체 테스트
        assert normalize_memory_type(MemoryType.GOAL) == MemoryType.GOAL
        assert normalize_memory_type(MemoryType.CREATIVITY) == MemoryType.CREATIVITY

        # 4. None 테스트
        assert normalize_memory_type(None) == MemoryType.LEARNING_EXPERIENCE

        # 5. 대소문자 혼용 테스트
        assert normalize_memory_type("Learning") == MemoryType.LEARNING_EXPERIENCE
        assert normalize_memory_type("CREATIVE") == MemoryType.CREATIVITY
        assert normalize_memory_type("Ethic") == MemoryType.ETHICS

        print("✅ 종합 메모리 타입 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ 메모리 타입 테스트 실패: {e}")
        traceback.print_exc()
        return False


def test_error_handling():
    """오류 처리 테스트"""
    print("🔍 오류 처리 테스트 시작...")

    try:
        # 1. 알 수 없는 메모리 타입
        try:
            normalize_memory_type("unknown_type")
            print("❌ 알 수 없는 타입이 예외를 발생시키지 않음")
            return False
        except ValueError:
            print("✅ 알 수 없는 타입이 올바르게 예외 발생")

        # 2. 잘못된 타입
        try:
            normalize_memory_type(123)
            print("❌ 잘못된 타입이 예외를 발생시키지 않음")
            return False
        except ValueError:
            print("✅ 잘못된 타입이 올바르게 예외 발생")

        print("✅ 오류 처리 테스트 통과")
        return True

    except Exception as e:
        print(f"❌ 오류 처리 테스트 실패: {e}")
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 로깅 안전성 및 메모리 타입 정규화 테스트 시작")
    print("=" * 60)

    tests = [
        ("로깅 안전성", test_logging_safety),
        ("메모리 타입 정규화", test_memory_normalization),
        ("종합 로깅", test_comprehensive_logging),
        ("종합 메모리 타입", test_memory_type_comprehensive),
        ("오류 처리", test_error_handling),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 실행 중...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 테스트 실패")

    print("\n" + "=" * 60)
    print(f"📊 테스트 결과: {passed}/{total} 통과")

    if passed == total:
        print("🎉 모든 테스트 통과! 시스템이 안전합니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
