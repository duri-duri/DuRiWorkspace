from DuRiCore.trace import emit_trace
"""
Core ports for clean architecture implementation.
Defines abstract interfaces that adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass(frozen=True)
class ValidationResult:
    """Immutable validation result"""
    valid: bool
    request_id: int
    timestamp: datetime
    data: Dict[str, Any]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class MetricsSnapshot:
    """Immutable metrics snapshot"""
    total_requests: int
    successes: int
    failures: int
    latencies: Tuple[float, ...]
    start_time: datetime
    end_time: datetime
    success_rate: float
    avg_response_time: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float

class ValidatorPort(ABC):
    """Abstract interface for validators"""

    @abstractmethod
    async def validate(self, request_id: int, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a request and return immutable result
        
        May raise:
          - ValidationError: 도메인 규칙 위반 (재시도 없음)
          - TransientError: 일시적 실패 (재시도 가능)  
          - SystemError: 시스템 오류 (재시도 없음 + 알람)
        """
        pass

    @abstractmethod
    def reset_request_count(self) -> None:
        """Reset internal request counter (for testing)"""
        pass

class MetricsPort(ABC):
    """Abstract interface for metrics collection"""

    @abstractmethod
    def record_success(self, response_time: float) -> None:
        """Record a successful request with response time"""
        pass

    @abstractmethod
    def record_failure(self, response_time: float, error: Optional[str]=None) -> None:
        """Record a failed request with response time and optional error"""
        pass

    @abstractmethod
    def record_latency(self, response_time: float) -> None:
        """Record response time (called for both success and failure)"""
        pass

    @abstractmethod
    def start_timing(self) -> None:
        """Start timing for a test scenario"""
        pass

    @abstractmethod
    def stop_timing(self) -> None:
        """Stop timing for a test scenario"""
        pass

    @abstractmethod
    def snapshot(self) -> MetricsSnapshot:
        """Take immutable snapshot of current metrics"""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset metrics to initial state"""
        pass

class ClockPort(ABC):
    """Abstract interface for time operations"""

    @abstractmethod
    def now(self) -> datetime:
        """Get current UTC timestamp"""
        pass

    @abstractmethod
    def time(self) -> float:
        """Get current time as float (for performance measurements)"""
        pass

class RandomPort(ABC):
    """Abstract interface for random operations"""

    @abstractmethod
    def seed(self, seed_value: int) -> None:
        """Set random seed for reproducibility"""
        pass

    @abstractmethod
    def random(self) -> float:
        """Generate random float between 0.0 and 1.0"""
        pass

    @abstractmethod
    def choice(self, choices: List[Any]) -> Any:
        """Choose random element from choices"""
        pass

    def randint(self, a: int, b: int) -> int:
        """Generate random integer between a and b (inclusive)"""
        pass

class TestRunnerPort(ABC):
    """Abstract interface for test runners"""

    @abstractmethod
    async def run_scenario(self, name: str, n_requests: int, max_concurrent: int) -> MetricsSnapshot:
        """Run a single test scenario and return metrics snapshot"""
        pass

    @abstractmethod
    async def run_scenarios(self, scenarios: Dict[str, Dict[str, int]]) -> Dict[str, MetricsSnapshot]:
        """Run multiple test scenarios and return results"""
        pass