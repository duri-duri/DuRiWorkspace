#!/usr/bin/env python3
"""
DuRi 로깅 시스템 통합 테스트

회귀 방지를 위한 종합 테스트를 제공합니다.
"""

import logging
import os
import random
import sys
import time
from typing import Any, Dict, List

# DuRiCore 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_rules_matching_accuracy():
    """RULES 매칭 정확도 테스트"""
    print("🔍 RULES 매칭 정확도 테스트 시작...")

    from DuRiCore.duri_logging.autodetect import (get_all_components,
                                                  infer_component)

    # 각 패키지 경로→라벨 테스트
    test_cases = [
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
        ("unknown.module", "_"),
    ]

    correct_matches = 0
    total_tests = len(test_cases)

    for logger_name, expected in test_cases:
        result = infer_component(logger_name)
        if result == expected:
            correct_matches += 1
        else:
            print(f"❌ 매칭 실패: {logger_name} -> 예상: {expected}, 실제: {result}")

    accuracy = correct_matches / total_tests
    print(f"✅ RULES 매칭 정확도: {accuracy:.2%} ({correct_matches}/{total_tests})")

    # 지원되는 컴포넌트 목록 확인
    components = get_all_components()
    print(f"📋 지원되는 컴포넌트: {len(components)}개")

    return accuracy >= 0.95  # 95% 이상 정확도 요구


def test_context_fields():
    """컨텍스트 필드 존재성 테스트"""
    print("🔍 컨텍스트 필드 존재성 테스트 시작...")

    from DuRiCore.duri_logging.context import (clear_context, get_context,
                                               set_learning_session_id,
                                               set_phase, set_request_id,
                                               set_session_id)

    # 컨텍스트 설정
    set_request_id("test_req_123")
    set_session_id("test_sess_456")
    set_learning_session_id("test_learn_789")
    set_phase("testing")

    # 컨텍스트 가져오기
    ctx = get_context()

    # 필수 필드 확인
    required_fields = ["request_id", "session_id", "learning_session_id", "phase"]
    missing_fields = []

    for field in required_fields:
        if field not in ctx:
            missing_fields.append(field)
        elif ctx[field] == "-":
            missing_fields.append(field)

    if missing_fields:
        print(f"❌ 누락된 필드: {missing_fields}")
        return False

    print(f"✅ 컨텍스트 필드 확인: {list(ctx.keys())}")

    # 초기화 테스트
    clear_context()
    ctx_after_clear = get_context()

    for field in required_fields:
        if ctx_after_clear[field] != "-":
            print(f"❌ 초기화 실패: {field} = {ctx_after_clear[field]}")
            return False

    print("✅ 컨텍스트 초기화 확인")
    return True


def test_pii_masking():
    """PII 마스킹 유효성 테스트"""
    print("🔍 PII 마스킹 유효성 테스트 시작...")

    from DuRiCore.duri_logging.setup import setup_logging

    # 로깅 시스템 초기화
    setup_logging()
    logger = logging.getLogger("test.pii")

    # PII 데이터 로깅 테스트
    sensitive_data = {
        "patient_name": "John Doe",
        "phone": "123-456-7890",
        "email": "john.doe@example.com",
        "ssn": "123-45-6789",
        "id_number": "ID123456",
        "address": "123 Main St",
    }

    # 로그 캡처를 위한 핸들러
    log_records = []

    class TestHandler(logging.Handler):
        def emit(self, record):
            log_records.append(record)

    logger.addHandler(TestHandler())

    # PII가 포함된 로그 생성
    logger.info("PII 테스트", extra=sensitive_data)

    # 로그 레코드 확인
    if not log_records:
        print("❌ 로그 레코드가 생성되지 않음")
        return False

    record = log_records[0]

    # PII 마스킹 확인 (extra 필드에서)
    if hasattr(record, "extra_kwargs"):
        for key, value in record.extra_kwargs.items():
            if key in sensitive_data and value != "[REDACTED]":
                print(f"❌ PII 마스킹 실패: {key} = {value}")
                return False

    print("✅ PII 마스킹 확인")
    return True


def test_sampling_functionality():
    """샘플링 기능 테스트"""
    print("🔍 샘플링 기능 테스트 시작...")

    import os
    import random

    from DuRiCore.duri_logging.decorators import log_calls
    from DuRiCore.duri_logging.setup import setup_logging

    # 로깅 시스템 초기화
    setup_logging()

    # 환경변수 설정으로 재현성 확보
    os.environ["LOG_SAMPLE_SEED"] = "42"
    os.environ["LOG_SAMPLE_RATE"] = "0.2"  # 20% 샘플링

    # 샘플링 데코레이터 테스트 (20% 샘플링)
    call_count = 0

    @log_calls(sample_rate=0.2, seed=42)
    def sampled_function():
        nonlocal call_count
        call_count += 1
        return "sampled"

    # 여러 번 호출하여 샘플링 확인
    total_calls = 50  # 테스트 크기
    for _ in range(total_calls):
        sampled_function()

    # 이항분포 신뢰구간 계산 (95% 신뢰구간)
    # n=50, p=0.2일 때 허용 범위
    # 근사적으로 정규분포 사용: μ = np = 10, σ = sqrt(np(1-p)) = sqrt(8) ≈ 2.83
    # 95% 신뢰구간: μ ± 1.96σ ≈ 10 ± 5.5
    expected_mean = total_calls * 0.2  # 10
    expected_std = (total_calls * 0.2 * 0.8) ** 0.5  # sqrt(8) ≈ 2.83
    margin = 1.96 * expected_std  # 약 5.5

    expected_min = max(0, int(expected_mean - margin))  # 약 4
    expected_max = min(total_calls, int(expected_mean + margin))  # 약 15

    actual_rate = call_count / total_calls
    print(f"📊 샘플링 결과: {call_count}/{total_calls} ({actual_rate:.1%})")
    print(
        f"📊 예상 범위: {expected_min}~{expected_max} ({expected_min/total_calls:.1%}~{expected_max/total_calls:.1%})"
    )
    print(f"📊 이론적 평균: {expected_mean:.1f}, 표준편차: {expected_std:.1f}")

    if expected_min <= call_count <= expected_max:
        print(f"✅ 샘플링 정상: {call_count}/{total_calls} ({actual_rate:.1%})")
        return True
    else:
        print(f"❌ 샘플링 비정상: {call_count}/{total_calls} ({actual_rate:.1%})")
        return False


def test_logging_format():
    """로깅 포맷 테스트"""
    print("🔍 로깅 포맷 테스트 시작...")

    from DuRiCore.duri_logging.adapter import get_logger
    from DuRiCore.duri_logging.setup import setup_logging

    # 로깅 시스템 초기화
    setup_logging()

    # 로그 캡처
    log_records = []

    class TestHandler(logging.Handler):
        def emit(self, record):
            log_records.append(record)

    # 테스트 로거 생성
    logger = get_logger("DuRiCore.learning.engine")
    logger.addHandler(TestHandler())

    # 로그 생성
    logger.info("포맷 테스트")

    if not log_records:
        print("❌ 로그 레코드가 생성되지 않음")
        return False

    record = log_records[0]

    # 필수 필드 확인
    required_fields = [
        "component",
        "request_id",
        "session_id",
        "learning_session_id",
        "phase",
    ]
    missing_fields = []

    for field in required_fields:
        if not hasattr(record, field):
            missing_fields.append(field)

    if missing_fields:
        print(f"❌ 누락된 포맷 필드: {missing_fields}")
        return False

    # 컴포넌트 자동 라벨링 확인
    if record.component != "learning":
        print(f"❌ 컴포넌트 라벨링 실패: {record.component}")
        return False

    print("✅ 로깅 포맷 확인")
    return True


def test_multiprocess_safety():
    """멀티프로세스 안전성 테스트"""
    print("🔍 멀티프로세스 안전성 테스트 시작...")

    from DuRiCore.bootstrap import bootstrap_logging

    # 첫 번째 부트스트랩
    bootstrap_logging()

    # 두 번째 부트스트랩 (중복 호출)
    bootstrap_logging()

    # 강제 재설정
    bootstrap_logging(force=True)

    print("✅ 멀티프로세스 안전성 확인")
    return True


def run_all_tests():
    """모든 통합 테스트를 실행합니다."""
    print("🚀 DuRi 로깅 시스템 통합 테스트 시작")
    print("=" * 60)

    tests = [
        ("RULES 매칭 정확도", test_rules_matching_accuracy),
        ("컨텍스트 필드 존재성", test_context_fields),
        ("PII 마스킹 유효성", test_pii_masking),
        ("샘플링 기능", test_sampling_functionality),
        ("로깅 포맷", test_logging_format),
        ("멀티프로세스 안전성", test_multiprocess_safety),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 실행 중...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 통과")
            else:
                print(f"❌ {test_name} 실패")
        except Exception as e:
            print(f"❌ {test_name} 오류: {e}")

    print("\n" + "=" * 60)
    print(f"📊 통합 테스트 결과: {passed}/{total} 통과")

    if passed == total:
        print("🎉 모든 통합 테스트 통과! DuRi 로깅 시스템이 안정합니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 추가 수정이 필요합니다.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
