from DuRiCore.trace import emit_trace
import asyncio
import logging
import time
from typing import Any, Dict
from .errors import ValidationError, TransientError, SystemError
from .config import load_thresholds
logger = logging.getLogger(__name__)

class RunnerEngine:

    def __init__(self, validator, metrics, clock, rng, cfg=None):
        self.validator = validator
        self.metrics = metrics
        self.clock = clock
        self.rng = rng
        self.cfg = cfg or load_thresholds()

    async def _attempt_once(self, request_id: int, payload: Dict[str, Any]):
        """단일 시도 - per_attempt_ms 타임아웃 적용"""
        per_attempt = self.cfg.timeouts.per_attempt_ms / 1000.0
        try:
            return await asyncio.wait_for(self.validator.validate(request_id, payload), timeout=per_attempt)
        except asyncio.TimeoutError as e:
            raise TransientError('timeout', code='timeout') from e
        except asyncio.CancelledError as e:
            raise TransientError('timeout-cancelled', code='timeout') from e

    async def _validate_with_retry(self, request_id: int, payload: Dict[str, Any]):
        """리트라이 정책 적용 - TransientError만 리트라이"""
        attempts = self.cfg.retry.transient_max_attempts
        backoffs = self.cfg.retry.backoff_ms or []
        jitter = self.cfg.retry.jitter_ms
        for attempt in range(attempts):
            start = self.clock.time()
            try:
                res = await self._attempt_once(request_id, payload)
                latency = self.clock.time() - start
                self.metrics.add_success(latency)
                return True
            except ValidationError as e:
                latency = self.clock.time() - start
                self.metrics.add_validation_failure(latency)
                logger.info(f'[validation-fail] req_id={request_id} attempt={attempt + 1} elapsed_ms={latency * 1000:.1f}')
                return False
            except TransientError as e:
                latency = self.clock.time() - start
                if attempt < attempts - 1:
                    base = backoffs[attempt] if attempt < len(backoffs) else backoffs[-1] if backoffs else 0
                    sleep_ms = base + (self.rng.randint(0, jitter) if jitter > 0 else 0)
                    logger.debug(f'[retry] req_id={request_id} attempt={attempt + 1} backoff={sleep_ms}ms')
                    await asyncio.sleep(sleep_ms / 1000.0)
                    continue
                else:
                    self.metrics.add_transient_failure(latency)
                    logger.warning(f'[transient-fail] req_id={request_id} attempts={attempt + 1} elapsed_ms={latency * 1000:.1f} err={e}')
                    return False
            except SystemError as e:
                latency = self.clock.time() - start
                self.metrics.add_system_failure(latency)
                if self.cfg.alerting.on_system_error:
                    logger.error(f'[system-error] req_id={request_id} attempt={attempt + 1} elapsed_ms={latency * 1000:.1f} err={e} :: alert=on')
                else:
                    logger.error(f'[system-error] req_id={request_id} attempt={attempt + 1} elapsed_ms={latency * 1000:.1f} err={e}')
                return False
            except Exception as e:
                latency = self.clock.time() - start
                self.metrics.add_system_failure(latency)
                logger.exception(f'[system-fail-unexpected] req_id={request_id} attempt={attempt + 1} elapsed_ms={latency * 1000:.1f} err={e}')
                return False
        return False

    async def run_scenario(self, name: str, num_requests: int, concurrency: int):
        """시나리오 실행 - 동시성 제한 + 메트릭 집계"""
        self.metrics.reset()
        sem = asyncio.Semaphore(concurrency)

        async def worker(i: int):
            async with sem:
                payload = {'value': i}
                await self._validate_with_retry(i, payload)
        t0 = self.clock.time()
        tasks = [asyncio.create_task(worker(i)) for i in range(num_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        dur = max(self.clock.time() - t0, 1e-09)
        summary = self.metrics.get_summary()
        if self.cfg.stress.slo.availability_excludes_validation:
            total = summary.total
            non_avail = summary.error_breakdown.get('transient', 0) + summary.error_breakdown.get('system', 0)
            availability = (total - non_avail) / total if total else 1.0
            from dataclasses import replace
            summary = replace(summary, availability_success_rate=availability)
        return summary
StressRunner = RunnerEngine