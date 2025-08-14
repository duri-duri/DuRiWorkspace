from DuRiCore.trace import emit_trace
import asyncio
from core.config import load_thresholds

async def test_thresholds_load_dev():
    """개발 환경 임계값 로드 및 검증"""
    cfg = load_thresholds('dev', 'config/thresholds.yaml')
    assert cfg.stress.success_rate_min >= 0.9
    assert cfg.stress.p95_ms['light'] <= 15
    assert cfg.retry.transient_max_attempts in (1, 2, 3)
    assert len(cfg.retry.backoff_ms) >= 1
    emit_trace('info', ' '.join(map(str, ['✅ test_thresholds_load_dev: PASSED'])))

async def run_policy_tests():
    """정책 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🚀 Running Policy Tests...'])))
    await test_thresholds_load_dev()
    emit_trace('info', ' '.join(map(str, ['🎉 All policy tests passed!'])))
if __name__ == '__main__':
    asyncio.run(run_policy_tests())