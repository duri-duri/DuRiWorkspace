from DuRiCore.trace import emit_trace
"""
Hybrid test runner implementing TestRunnerPort interface.
Supports both synchronous and asynchronous execution modes.
"""
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime
from .ports import TestRunnerPort, ValidatorPort, MetricsPort, ClockPort, ValidationResult, MetricsSnapshot

class HybridTestRunner(TestRunnerPort):
    """
    Hybrid test runner that can operate in different execution modes.
    Provides isolation between test scenarios and flexible concurrency control.
    """

    def __init__(self, validator: ValidatorPort, metrics: MetricsPort, clock: ClockPort, use_subprocess: bool=False, max_retries: int=3, retry_delay_ms: float=100.0):
        """
        Initialize hybrid test runner.
        
        Args:
            validator: Validator implementation to use
            metrics: Metrics collection implementation
            clock: Clock implementation for timing
            use_subprocess: Whether to use subprocess isolation
            max_retries: Maximum number of retries for failed requests
            retry_delay_ms: Delay between retries in milliseconds
        """
        self.validator = validator
        self.metrics = metrics
        self.clock = clock
        self.use_subprocess = use_subprocess
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms
        self.validator.reset_request_count()

    async def run_scenario(self, name: str, n_requests: int, max_concurrent: int) -> MetricsSnapshot:
        """Run a single test scenario and return metrics snapshot"""
        emit_trace('info', ' '.join(map(str, [f'🚀 Starting scenario: {name}'])))
        emit_trace('info', ' '.join(map(str, [f'   Requests: {n_requests}, Max Concurrent: {max_concurrent}'])))
        self.metrics.reset()
        self.validator.reset_request_count()
        self.metrics.start_timing()
        start_time = self.clock.time()
        try:
            if max_concurrent == 1:
                await self._run_sequential(n_requests)
            else:
                await self._run_concurrent(n_requests, max_concurrent)
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ Error in scenario {name}: {e}'])))
            self.metrics.record_failure(0.0, str(e))
        self.metrics.stop_timing()
        end_time = self.clock.time()
        snapshot = self.metrics.snapshot()
        duration = end_time - start_time
        emit_trace('info', ' '.join(map(str, [f'✅ Scenario {name} completed:'])))
        emit_trace('info', ' '.join(map(str, [f'   Duration: {duration:.2f}s'])))
        emit_trace('info', ' '.join(map(str, [f'   Success Rate: {snapshot.success_rate:.2%}'])))
        emit_trace('info', ' '.join(map(str, [f'   P95 Response Time: {snapshot.p95_response_time:.2f}ms'])))
        emit_trace('info', ' '.join(map(str, [f'   Requests/sec: {snapshot.requests_per_second:.1f}'])))
        return snapshot

    async def run_scenarios(self, scenarios: Dict[str, Dict[str, int]]) -> Dict[str, MetricsSnapshot]:
        """Run multiple test scenarios and return results"""
        results = {}
        for (scenario_name, config) in scenarios.items():
            n_requests = config.get('n_requests', 100)
            max_concurrent = config.get('max_concurrent', 10)
            if self.use_subprocess:
                result = await self._run_scenario_in_subprocess(scenario_name, n_requests, max_concurrent)
            else:
                result = await self._run_scenario_with_new_loop(scenario_name, n_requests, max_concurrent)
            results[scenario_name] = result
            await asyncio.sleep(0.1)
        return results

    async def _run_sequential(self, n_requests: int) -> None:
        """Run requests sequentially"""
        for i in range(n_requests):
            request_id = i + 1
            data = {'request_id': request_id, 'sequential': True}
            start_time = self.clock.time()
            try:
                result = await self.validator.validate(request_id, data)
                response_time = (self.clock.time() - start_time) * 1000
                if result.valid:
                    self.metrics.record_success(response_time)
                else:
                    self.metrics.record_failure(response_time, result.error)
            except Exception as e:
                response_time = (self.clock.time() - start_time) * 1000
                self.metrics.record_failure(response_time, str(e))

    async def _run_concurrent(self, n_requests: int, max_concurrent: int) -> None:
        """Run requests with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def make_request(request_id: int):
            async with semaphore:
                data = {'request_id': request_id, 'concurrent': True}
                start_time = self.clock.time()
                try:
                    result = await self.validator.validate(request_id, data)
                    response_time = (self.clock.time() - start_time) * 1000
                    if result.valid:
                        self.metrics.record_success(response_time)
                    else:
                        self.metrics.record_failure(response_time, result.error)
                except Exception as e:
                    response_time = (self.clock.time() - start_time) * 1000
                    self.metrics.record_failure(response_time, str(e))
        tasks = [make_request(i + 1) for i in range(n_requests)]
        await asyncio.gather(*tasks)

    async def _run_scenario_with_new_loop(self, scenario_name: str, n_requests: int, max_concurrent: int) -> MetricsSnapshot:
        """Run scenario with new event loop for isolation"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = await self.run_scenario(scenario_name, n_requests, max_concurrent)
            return result
        finally:
            loop.close()

    async def _run_scenario_in_subprocess(self, scenario_name: str, n_requests: int, max_concurrent: int) -> MetricsSnapshot:
        """Run scenario in subprocess for complete isolation"""
        emit_trace('info', ' '.join(map(str, [f'⚠️  Subprocess mode not yet implemented, using event loop isolation'])))
        return await self._run_scenario_with_new_loop(scenario_name, n_requests, max_concurrent)

    def get_scenario_summary(self, snapshot: MetricsSnapshot) -> Dict[str, any]:
        """Get human-readable summary of scenario results"""
        return {'total_requests': snapshot.total_requests, 'success_rate': f'{snapshot.success_rate:.2%}', 'avg_response_time': f'{snapshot.avg_response_time:.2f}ms', 'p95_response_time': f'{snapshot.p95_response_time:.2f}ms', 'p99_response_time': f'{snapshot.p99_response_time:.2f}ms', 'requests_per_second': f'{snapshot.requests_per_second:.1f}', 'duration': f'{(snapshot.end_time - snapshot.start_time).total_seconds():.2f}s'}