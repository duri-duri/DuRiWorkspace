from DuRiCore.trace import emit_trace
"""
In-memory metrics adapter implementing MetricsPort interface.
Provides immutable snapshots and thread-safe metrics collection.
"""
import time
import threading
from typing import List, Optional
from datetime import datetime
from statistics import mean, quantiles
from core.ports import MetricsPort, MetricsSnapshot

class InMemoryMetrics(MetricsPort):
    """
    Thread-safe in-memory metrics implementation.
    Maintains mutable internal state but provides immutable snapshots.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._reset_state()

    def _reset_state(self) -> None:
        """Reset internal state to initial values"""
        self._total_requests = 0
        self._successes = 0
        self._failures = 0
        self._latencies: List[float] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

    def record_success(self, response_time: float) -> None:
        """Record a successful request with response time"""
        with self._lock:
            self._total_requests += 1
            self._successes += 1
            self._latencies.append(response_time)

    def record_failure(self, response_time: float, error: Optional[str]=None) -> None:
        """Record a failed request with response time and optional error"""
        with self._lock:
            self._total_requests += 1
            self._failures += 1
            self._latencies.append(response_time)

    def record_latency(self, response_time: float) -> None:
        """Record response time (called for both success and failure)"""
        pass

    def start_timing(self) -> None:
        """Start timing for a test scenario"""
        with self._lock:
            self._start_time = datetime.utcnow()

    def stop_timing(self) -> None:
        """Stop timing for a test scenario"""
        with self._lock:
            self._end_time = datetime.utcnow()

    def snapshot(self) -> MetricsSnapshot:
        """Take immutable snapshot of current metrics"""
        with self._lock:
            if not self._latencies:
                return MetricsSnapshot(total_requests=0, successes=0, failures=0, latencies=(), start_time=datetime.utcnow(), end_time=datetime.utcnow(), success_rate=0.0, avg_response_time=0.0, p50_response_time=0.0, p95_response_time=0.0, p99_response_time=0.0, requests_per_second=0.0)
            latencies = sorted(self._latencies)
            total_time = 0.0
            if self._start_time and self._end_time:
                total_time = (self._end_time - self._start_time).total_seconds()
            if len(latencies) >= 4:
                p50_idx = int(len(latencies) * 0.5)
                p95_idx = int(len(latencies) * 0.95)
                p99_idx = int(len(latencies) * 0.99)
                p50_response_time = latencies[p50_idx]
                p95_response_time = latencies[p95_idx]
                p99_response_time = latencies[p99_idx]
            else:
                p50_response_time = latencies[0] if latencies else 0.0
                p95_response_time = latencies[-1] if latencies else 0.0
                p99_response_time = latencies[-1] if latencies else 0.0
            success_rate = self._successes / self._total_requests if self._total_requests > 0 else 0.0
            avg_response_time = mean(latencies) if latencies else 0.0
            requests_per_second = self._total_requests / total_time if total_time > 0 else 0.0
            return MetricsSnapshot(total_requests=self._total_requests, successes=self._successes, failures=self._failures, latencies=tuple(latencies), start_time=self._start_time or datetime.utcnow(), end_time=self._end_time or datetime.utcnow(), success_rate=success_rate, avg_response_time=avg_response_time, p50_response_time=p50_response_time, p95_response_time=p95_response_time, p99_response_time=p99_response_time, requests_per_second=requests_per_second)

    def reset(self) -> None:
        """Reset metrics to initial state"""
        with self._lock:
            self._reset_state()

    def get_current_state(self) -> dict:
        """Get current internal state for debugging (not part of interface)"""
        with self._lock:
            return {'total_requests': self._total_requests, 'successes': self._successes, 'failures': self._failures, 'latency_count': len(self._latencies), 'start_time': self._start_time, 'end_time': self._end_time}