from DuRiCore.trace import emit_trace
"""
Phase 4B 데모 스크립트 - 최적화된 버전
에러 모델, 정책 기반 리트라이, 정확한 처리량 측정
"""
import asyncio
import time
from core.metrics import StressTestMetrics
from adapters.mock.mock_validator import DeterministicMockValidator
from core.runner_engine import RunnerEngine
from core.config import load_thresholds
from adapters.clock.system_clock import SystemClock
from adapters.random.system_random import SystemRandom
CONCURRENCY = 5
TOTAL_REQ = 50

async def run_scenario():
    """시나리오 실행 - 정확한 벽시계 시간 측정"""
    emit_trace('info', ' '.join(map(str, ['🚀 Phase 4B 데모 시작'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    emit_trace('info', ' '.join(map(str, ['\n🔍 에러 모델 데모'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    validator = DeterministicMockValidator(success_rate=0.7)
    test_cases = [(1, {'value': 10}, '정상 케이스'), (2, {'value': -1}, 'ValidationError (음수)'), (3, {'value': 'timeout'}, 'TransientError (타임아웃)'), (4, {'value': 'boom'}, 'SystemError (시스템 오류)')]
    for (req_id, data, desc) in test_cases:
        try:
            result = await validator.validate(req_id, data)
            emit_trace('info', ' '.join(map(str, [f'✅ {desc}: 성공 (valid={result.valid})'])))
        except Exception as e:
            error_type = type(e).__name__
            emit_trace('info', ' '.join(map(str, [f'❌ {desc}: {error_type} - {e}'])))
    emit_trace('info', ' '.join(map(str, ['\n🔄 리트라이 정책 데모'])))
    emit_trace('info', ' '.join(map(str, ['=' * 50])))
    cfg = load_thresholds()
    emit_trace('info', ' '.join(map(str, [f'리트라이 설정: 최대 {cfg.retry.transient_max_attempts}회, 백오프 {cfg.retry.backoff_ms}ms, 지터 {cfg.retry.jitter_ms}ms'])))
    validator = DeterministicMockValidator(success_rate=0.3)
    metrics = StressTestMetrics()
    clock = SystemClock()
    rng = SystemRandom()
    engine = RunnerEngine(validator, metrics, clock, rng, cfg)
    emit_trace('info', ' '.join(map(str, [f'\n🚀 시나리오 실행: {TOTAL_REQ}개 요청, 동시성 {CONCURRENCY}'])))
    t0 = time.perf_counter()
    summary = await engine.run_scenario('demo_phase4b', TOTAL_REQ, CONCURRENCY)
    t1 = time.perf_counter()
    wall_s = max(1e-06, t1 - t0)
    throughput = summary.total / wall_s
    p95 = summary.p95_ms
    overall_success = summary.successes / max(1, summary.total)
    avail_den = max(1, summary.total - summary.error_breakdown.get('validation', 0))
    availability_success = summary.availability_success_rate if hasattr(summary, 'availability_success_rate') else summary.successes / avail_den
    emit_trace('info', ' '.join(map(str, [f'\n📊 결과 요약:'])))
    emit_trace('info', ' '.join(map(str, [f'   총 요청: {summary.total}'])))
    emit_trace('info', ' '.join(map(str, [f'   성공: {summary.successes}'])))
    emit_trace('info', ' '.join(map(str, [f'   실패: {summary.failures}'])))
    emit_trace('info', ' '.join(map(str, [f'   전체 성공률: {overall_success:.3f}'])))
    emit_trace('info', ' '.join(map(str, [f'   가용성 성공률(Validation 제외): {availability_success:.3f}'])))
    emit_trace('info', ' '.join(map(str, [f'   p95 지연: {p95:.2f}ms'])))
    emit_trace('info', ' '.join(map(str, [f'   처리량: {throughput:.2f} req/s'])))
    emit_trace('info', ' '.join(map(str, [f'   에러 분류:'])))
    for (k, v) in summary.error_breakdown.items():
        emit_trace('info', ' '.join(map(str, [f'     {k}: {v}'])))
    emit_trace('info', ' '.join(map(str, ['\n✅ 임계값 검증:'])))
    overall_ok = overall_success >= cfg.stress.success_rate_min
    availability_ok = availability_success >= cfg.stress.availability_min
    p95_budget = cfg.stress.p95_ms.medium
    p95_ok = p95 <= p95_budget
    emit_trace('info', ' '.join(map(str, [f"   전체 성공률 {('✅' if overall_ok else '❌')} {overall_success:.3f} {('>=' if overall_ok else '<')} {cfg.stress.success_rate_min}"])))
    emit_trace('info', ' '.join(map(str, [f"   가용성 성공률 {('✅' if availability_ok else '❌')} {availability_success:.3f} {('>=' if availability_ok else '<')} {cfg.stress.availability_min}"])))
    emit_trace('info', ' '.join(map(str, [f"   p95 지연 {('✅' if p95_ok else '❌')} {p95:.2f}ms {('<=' if p95_ok else '>')} {p95_budget}ms"])))
    if summary.error_breakdown.get('transient', 0) > 0:
        emit_trace('info', ' '.join(map(str, [f"\n🔄 리트라이 효과: TransientError {summary.error_breakdown['transient']}건 발생, 리트라이로 일부 복구"])))
    emit_trace('info', ' '.join(map(str, ['\n🎉 Phase 4B 데모 완료!'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
if __name__ == '__main__':
    asyncio.run(run_scenario())