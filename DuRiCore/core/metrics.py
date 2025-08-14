from DuRiCore.trace import emit_trace
from dataclasses import dataclass, field
from typing import List, Dict
import statistics
import time

@dataclass(frozen=True)
class Summary:
    total: int
    successes: int
    failures: int
    success_rate: float
    availability_success_rate: float
    p95_ms: float
    duration_s: float
    requests_per_second: float
    error_breakdown: Dict[str, int] = field(default_factory=dict)

class StressTestMetrics:

    def __init__(self):
        self.reset()

    def reset(self):
        self.successes = 0
        self.failures = 0
        self.latencies: List[float] = []
        self.error_breakdown = {'validation': 0, 'transient': 0, 'system': 0}
        self._start_time = None
        self._end_time = None

    def start_timing(self):
        """타이밍 시작"""
        self._start_time = time.perf_counter()

    def stop_timing(self):
        """타이밍 종료"""
        self._end_time = time.perf_counter()

    def add_success(self, latency_s: float):
        """성공 추가"""
        self.successes += 1
        self.latencies.append(latency_s)

    def add_validation_failure(self, latency_s: float):
        """검증 실패 추가"""
        self.failures += 1
        self.error_breakdown['validation'] += 1
        self.latencies.append(latency_s)

    def add_transient_failure(self, latency_s: float):
        """일시적 실패 추가"""
        self.failures += 1
        self.error_breakdown['transient'] += 1
        self.latencies.append(latency_s)

    def add_system_failure(self, latency_s: float):
        """시스템 실패 추가"""
        self.failures += 1
        self.error_breakdown['system'] += 1
        self.latencies.append(latency_s)

    def add_failure(self, latency_s: float, kind: str):
        """일반 실패 추가 (하위 호환성)"""
        self.failures += 1
        if kind in self.error_breakdown:
            self.error_breakdown[kind] += 1
        else:
            self.error_breakdown[kind] = 1
        self.latencies.append(latency_s)

    def get_summary(self) -> Summary:
        """요약 통계 반환"""
        total = self.successes + self.failures
        if total == 0:
            return Summary(total=0, successes=0, failures=0, success_rate=1.0, availability_success_rate=1.0, p95_ms=0.0, duration_s=0.0, requests_per_second=0.0, error_breakdown=self.error_breakdown.copy())
        success_rate = self.successes / total
        duration_s = self._end_time - self._start_time if self._start_time and self._end_time else 0.0
        if self.latencies:
            latencies_ms = [lat * 1000.0 for lat in self.latencies]
            p95_ms = statistics.quantiles(latencies_ms, n=20)[18] if len(latencies_ms) >= 20 else latencies_ms[-1]
        else:
            p95_ms = 0.0
        requests_per_second = total / duration_s if duration_s > 0 else 0.0
        validation_failures = self.error_breakdown.get('validation', 0)
        availability_denominator = total - validation_failures
        availability_success_rate = self.successes / availability_denominator if availability_denominator > 0 else 1.0
        return Summary(total=total, successes=self.successes, failures=self.failures, success_rate=success_rate, availability_success_rate=availability_success_rate, p95_ms=p95_ms, duration_s=duration_s, requests_per_second=requests_per_second, error_breakdown=self.error_breakdown.copy())

    @property
    def total(self) -> int:
        """총 요청 수 (읽기 전용)"""
        return self.successes + self.failures
        availability_success_rate = success_rate
        return Summary(total=total, successes=self.successes, failures=self.failures, success_rate=success_rate, availability_success_rate=availability_success_rate, p95_ms=p95_ms, duration_s=duration_s, requests_per_second=requests_per_second, error_breakdown=self.error_breakdown.copy())