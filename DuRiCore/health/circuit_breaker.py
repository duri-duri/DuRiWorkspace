#!/usr/bin/env python3
"""
DuRi Circuit Breaker - Day 76 Canary 엔드포인트 탄력성
"""

import time
from enum import Enum
from threading import RLock
from typing import Dict, Any, Optional, Callable
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("circuit_breaker")

class CircuitState(Enum):
    """서킷 브레이커 상태"""
    CLOSED = "closed"      # 정상 동작
    OPEN = "open"          # 차단 상태
    HALF_OPEN = "half_open"  # 테스트 상태

class CircuitBreaker:
    """서킷 브레이커 구현"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        """
        Args:
            failure_threshold: 실패 임계치 (연속 실패 횟수)
            recovery_timeout: 복구 타임아웃 (초)
            expected_exception: 예상되는 예외 타입
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
        self.lock = RLock()
        
        logger.info(f"CircuitBreaker 초기화: threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        함수 호출 (서킷 브레이커 적용)
        
        Args:
            func: 호출할 함수
            *args: 함수 인자
            **kwargs: 함수 키워드 인자
            
        Returns:
            함수 결과
            
        Raises:
            Exception: 서킷 브레이커가 열려있거나 함수 실행 실패
        """
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("서킷 브레이커 HALF_OPEN으로 전환")
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """리셋 시도 여부 확인"""
        return time.time() - self.last_failure_time >= self.recovery_timeout
    
    def _on_success(self):
        """성공 시 처리"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("서킷 브레이커 CLOSED로 전환")
    
    def _on_failure(self):
        """실패 시 처리"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"서킷 브레이커 OPEN으로 전환 (실패 횟수: {self.failure_count})")
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        with self.lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout
            }

class BackpressureController:
    """백프레셔 컨트롤러"""
    
    def __init__(self, max_concurrent: int = 10, queue_size: int = 100):
        """
        Args:
            max_concurrent: 최대 동시 처리 수
            queue_size: 큐 크기
        """
        self.max_concurrent = max_concurrent
        self.queue_size = queue_size
        self.current_concurrent = 0
        self.queue_length = 0
        self.lock = RLock()
        
        logger.info(f"BackpressureController 초기화: max_concurrent={max_concurrent}, queue_size={queue_size}")
    
    def acquire(self) -> bool:
        """
        리소스 획득 시도
        
        Returns:
            성공하면 True, 실패하면 False
        """
        with self.lock:
            if self.current_concurrent >= self.max_concurrent:
                return False
            
            self.current_concurrent += 1
            return True
    
    def release(self):
        """리소스 해제"""
        with self.lock:
            self.current_concurrent = max(0, self.current_concurrent - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        with self.lock:
            return {
                "max_concurrent": self.max_concurrent,
                "current_concurrent": self.current_concurrent,
                "queue_size": self.queue_size,
                "queue_length": self.queue_length,
                "utilization": self.current_concurrent / self.max_concurrent
            }

class ParameterValidator:
    """파라미터 검증기"""
    
    @staticmethod
    def validate_thresholds(latency_threshold: Optional[int] = None,
                          error_threshold: Optional[float] = None,
                          readiness_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        임계치 파라미터 검증
        
        Args:
            latency_threshold: 지연시간 임계치
            error_threshold: 오류율 임계치
            readiness_threshold: Readiness 임계치
            
        Returns:
            검증 결과
        """
        errors = []
        
        # 지연시간 임계치 검증
        if latency_threshold is not None:
            if not isinstance(latency_threshold, (int, float)):
                errors.append("latency_threshold must be numeric")
            elif latency_threshold <= 0:
                errors.append("latency_threshold must be positive")
            elif latency_threshold > 10000:  # 10초
                errors.append("latency_threshold too high (max 10000ms)")
        
        # 오류율 임계치 검증
        if error_threshold is not None:
            if not isinstance(error_threshold, (int, float)):
                errors.append("error_threshold must be numeric")
            elif error_threshold < 0 or error_threshold > 1:
                errors.append("error_threshold must be between 0 and 1")
        
        # Readiness 임계치 검증
        if readiness_threshold is not None:
            if not isinstance(readiness_threshold, (int, float)):
                errors.append("readiness_threshold must be numeric")
            elif readiness_threshold < 0 or readiness_threshold > 1:
                errors.append("readiness_threshold must be between 0 and 1")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def validate_window_params(window: Optional[int] = None, 
                             step: Optional[int] = None) -> Dict[str, Any]:
        """
        윈도우 파라미터 검증
        
        Args:
            window: 윈도우 크기 (초)
            step: 스텝 크기 (초)
            
        Returns:
            검증 결과
        """
        errors = []
        
        # 윈도우 크기 검증
        if window is not None:
            if not isinstance(window, int):
                errors.append("window must be integer")
            elif window <= 0:
                errors.append("window must be positive")
            elif window > 86400:  # 24시간
                errors.append("window too large (max 86400s)")
        
        # 스텝 크기 검증
        if step is not None:
            if not isinstance(step, int):
                errors.append("step must be integer")
            elif step <= 0:
                errors.append("step must be positive")
            elif step > 3600:  # 1시간
                errors.append("step too large (max 3600s)")
        
        # 윈도우와 스텝 관계 검증
        if window is not None and step is not None:
            if step > window:
                errors.append("step cannot be larger than window")
            elif window // step > 1000:  # 최대 1000개 버킷
                errors.append("too many buckets (window/step > 1000)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

# 전역 인스턴스
canary_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception
)

canary_backpressure = BackpressureController(
    max_concurrent=10,
    queue_size=100
)

def with_circuit_breaker(func: Callable) -> Callable:
    """서킷 브레이커 데코레이터"""
    def wrapper(*args, **kwargs):
        return canary_circuit_breaker.call(func, *args, **kwargs)
    return wrapper

def with_backpressure(func: Callable) -> Callable:
    """백프레셔 데코레이터"""
    def wrapper(*args, **kwargs):
        if not canary_backpressure.acquire():
            raise Exception("Backpressure limit exceeded")
        try:
            return func(*args, **kwargs)
        finally:
            canary_backpressure.release()
    return wrapper

def get_resilience_stats() -> Dict[str, Any]:
    """탄력성 통계 반환"""
    return {
        "circuit_breaker": canary_circuit_breaker.get_state(),
        "backpressure": canary_backpressure.get_stats(),
        "timestamp": time.time()
    }
