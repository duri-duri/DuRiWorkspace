from DuRiCore.trace import emit_trace
import asyncio
import statistics as stats
import random
from adapters.mock.mock_validator import DeterministicMockValidator
from adapters.clock.system_clock import SystemClock
from adapters.random.system_random import SystemRandom

async def test_failrate_converges():
    """실패율 수렴성 검증 - 프로퍼티 테스트"""
    clock = SystemClock()
    rng = SystemRandom()
    rng.seed(42)
    v = DeterministicMockValidator(success_rate=0.95, base_latency_ms=10.0, latency_variance_ms=5.0, seed=42)
    N = 1000
    ok = 0
    for i in range(N):
        try:
            res = await v.validate(i, {'value': i % 100})
            ok += bool(res.valid)
        except Exception:
            pass
    sr = ok / N
    assert 0.92 <= sr <= 0.98
    emit_trace('info', ' '.join(map(str, [f'✅ test_failrate_converges: PASSED (success_rate: {sr:.3f})'])))

async def run_property_tests():
    """프로퍼티 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🚀 Running Property Tests...'])))
    await test_failrate_converges()
    emit_trace('info', ' '.join(map(str, ['🎉 All property tests passed!'])))
if __name__ == '__main__':
    asyncio.run(run_property_tests())