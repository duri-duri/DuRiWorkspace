from DuRiCore.trace import emit_trace
import asyncio
from core.errors import ValidationError, TransientError, SystemError
from adapters.mock.mock_validator import DeterministicMockValidator
from adapters.clock.system_clock import SystemClock
from adapters.random.system_random import SystemRandom

async def test_validator_contract_ok():
    """ValidatorPort 계약 검증 - 정상 케이스"""
    clock = SystemClock()
    rng = SystemRandom()
    rng.seed(42)
    v = DeterministicMockValidator(success_rate=0.95, base_latency_ms=10.0, latency_variance_ms=5.0, seed=42)
    out = await v.validate(1, {'value': 10})
    assert hasattr(out, 'valid')
    assert hasattr(out, 'error')
    assert hasattr(out, 'request_id')
    assert hasattr(out, 'timestamp')
    assert hasattr(out, 'data')
    emit_trace('info', ' '.join(map(str, ['✅ test_validator_contract_ok: PASSED'])))

async def test_validator_contract_errors():
    """ValidatorPort 계약 검증 - 에러 케이스"""
    clock = SystemClock()
    rng = SystemRandom()
    rng.seed(42)
    v = DeterministicMockValidator(success_rate=0.95, base_latency_ms=10.0, latency_variance_ms=5.0, seed=42)
    try:
        await v.validate(10001, {'value': -1})
        assert False, 'ValidationError should have been raised'
    except ValidationError:
        emit_trace('info', ' '.join(map(str, ['✅ ValidationError raised correctly'])))
    try:
        await v.validate(20001, {'value': 'timeout'})
        assert False, 'TransientError should have been raised'
    except TransientError:
        emit_trace('info', ' '.join(map(str, ['✅ TransientError raised correctly'])))
    try:
        await v.validate(30001, {'value': 'boom'})
        assert False, 'SystemError should have been raised'
    except SystemError:
        emit_trace('info', ' '.join(map(str, ['✅ SystemError raised correctly'])))
    emit_trace('info', ' '.join(map(str, ['✅ test_validator_contract_errors: PASSED'])))

async def run_contract_tests():
    """계약 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🚀 Running ValidatorPort Contract Tests...'])))
    await test_validator_contract_ok()
    await test_validator_contract_errors()
    emit_trace('info', ' '.join(map(str, ['🎉 All contract tests passed!'])))
if __name__ == '__main__':
    asyncio.run(run_contract_tests())