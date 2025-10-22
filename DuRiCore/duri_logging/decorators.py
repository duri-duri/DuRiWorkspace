#!/usr/bin/env python3
"""
DuRi 로깅 데코레이터

함수/메서드 자동 로깅을 제공합니다.
"""

import functools
import os
import random
import threading
import time
from typing import Any, Callable, Optional

from .adapter import get_logger

# 스레드별 RNG를 위한 로컬 스토리지
_tls = threading.local()


def _parse_rate(default: str = "1.0") -> float:
    """환경변수에서 샘플링 비율을 안전하게 파싱합니다."""
    try:
        v = float(os.environ.get("LOG_SAMPLE_RATE", default))
    except Exception:
        v = 1.0
    return max(0.0, min(1.0, v))


def _get_rng(seed: Optional[int], env_seed: Optional[str]) -> random.Random:
    """스레드별 안전한 RNG를 반환합니다."""
    if not hasattr(_tls, "rng"):
        _tls.rng = random.Random(
            seed if seed is not None else (int(env_seed) if env_seed else None)
        )
    return _tls.rng


def log_calls(
    sample_rate: Optional[float] = None,
    component: Optional[str] = None,
    seed: Optional[int] = None,
):
    """
    함수 호출을 자동으로 로깅하는 데코레이터.

    우선순위: explicit arg > env(LOG_SAMPLE_RATE) > 1.0
    env LOG_SAMPLE_SEED 로 재현성 제어

    Args:
        sample_rate: 샘플링 비율 (0.0~1.0, None이면 환경변수 또는 1.0)
        component: 강제로 지정할 컴포넌트
        seed: 랜덤 시드 (재현성 확보용)
    """
    # 재현성 확보: 인자 seed > 환경변수(LOG_SAMPLE_SEED) > 시스템랜덤
    env_seed = os.environ.get("LOG_SAMPLE_SEED")

    def decorator(func: Callable) -> Callable:
        # --- 핵심 개선: arg 우선권 고정 및 진단용 노출 ---
        effective_sr = sample_rate if sample_rate is not None else _parse_rate()
        setattr(func, "__log_sample_rate__", effective_sr)

        log = get_logger(func.__module__, component)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # --- 샘플링 게이트 (최상단, 로깅 이전) ---
            sr = effective_sr  # arg가 있으면 env 무시(명시적 우선)

            if sr <= 0.0:
                # 샘플링 비율이 0이면 로그 없이 함수만 실행
                return func(*args, **kwargs)

            if sr < 1.0:
                # 스레드별 안전한 RNG 사용
                rng = _get_rng(seed, env_seed)
                if rng.random() > sr:
                    # 로그 전체를 건너뛰고 함수만 실행
                    return func(*args, **kwargs)

            # 시작 시간 기록
            start_time = time.perf_counter()

            # 시작 로그
            log.info(f"→ {func.__name__} 시작")

            try:
                # 함수 실행
                result = func(*args, **kwargs)

                # 완료 시간 계산
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # 성공 로그
                log.info(f"← {func.__name__} 완료 ({elapsed_ms:.1f}ms)")

                return result

            except Exception as e:
                # 완료 시간 계산
                elapsed_ms = (time.perf_counter() - start_time) * 1000

                # 오류 로그
                log.error(f"✗ {func.__name__} 실패 ({elapsed_ms:.1f}ms): {type(e).__name__}: {e}")

                # 원본 예외 재발생
                raise

        return wrapper

    return decorator


def log_exceptions(component: Optional[str] = None):
    """
    예외만 로깅하는 데코레이터.

    Args:
        component: 강제로 지정할 컴포넌트
    """

    def decorator(func: Callable) -> Callable:
        log = get_logger(func.__module__, component)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"✗ {func.__name__}: {type(e).__name__}: {e}")
                raise

        return wrapper

    return decorator


def timed(component: Optional[str] = None):
    """
    실행 시간만 로깅하는 데코레이터.

    Args:
        component: 강제로 지정할 컴포넌트
    """

    def decorator(func: Callable) -> Callable:
        log = get_logger(func.__module__, component)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            log.info(f"⏱️ {func.__name__} 실행 시간: {elapsed_ms:.1f}ms")

            return result

        return wrapper

    return decorator


def log_performance(threshold_ms: float = 100.0, component: Optional[str] = None):
    """
    성능 임계값을 초과하는 함수를 로깅하는 데코레이터.

    Args:
        threshold_ms: 임계값 (밀리초)
        component: 강제로 지정할 컴포넌트
    """

    def decorator(func: Callable) -> Callable:
        log = get_logger(func.__module__, component)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if elapsed_ms > threshold_ms:
                log.warning(
                    f"🐌 {func.__name__} 느림: {elapsed_ms:.1f}ms (임계값: {threshold_ms}ms)"
                )

            return result

        return wrapper

    return decorator


def test_decorators():
    """데코레이터 시스템을 테스트합니다."""
    from .setup import setup_logging

    # 로깅 시스템 초기화
    setup_logging()

    # 1. 기본 로깅 테스트
    @log_calls()
    def test_function():
        time.sleep(0.01)  # 10ms 지연
        return "success"

    result = test_function()
    assert result == "success"

    # 2. 예외 로깅 테스트
    @log_exceptions()
    def error_function():
        raise ValueError("테스트 오류")

    try:
        error_function()
    except ValueError:
        pass  # 예외가 정상적으로 로깅됨

    # 3. 시간 측정 테스트
    @timed()
    def timed_function():
        time.sleep(0.01)
        return "timed"

    result = timed_function()
    assert result == "timed"

    # 4. 성능 임계값 테스트
    @log_performance(threshold_ms=5.0)
    def slow_function():
        time.sleep(0.01)  # 10ms > 5ms 임계값
        return "slow"

    result = slow_function()
    assert result == "slow"

    # 5. 샘플링 테스트 (환경변수 설정)
    os.environ["LOG_SAMPLE_SEED"] = "42"

    @log_calls(sample_rate=0.5, seed=42)
    def sampled_function():
        return "sampled"

    # 진단용: 유효 샘플링 비율 확인
    effective_sr = getattr(sampled_function, "__log_sample_rate__", None)
    print(f"진단: EFFECTIVE_SR = {effective_sr}")

    # 여러 번 호출하여 샘플링 확인
    for _ in range(10):
        sampled_function()

    print("✅ 데코레이터 시스템 테스트 통과")
    return True


if __name__ == "__main__":
    test_decorators()
