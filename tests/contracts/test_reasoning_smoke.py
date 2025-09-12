import time
import pytest

# --- Import with fallbacks (robust to path changes) ---
try:
    # 권장 파사드
    from logical_reasoning_engine import ReasoningEngine
except Exception:
    try:
        # 백업 경로 1
        from DuRiCore.reasoning_engine.core.logical_reasoning_engine import (
            LogicalReasoningEngine as ReasoningEngine
        )
    except Exception:
        # 백업 경로 2
        from duri_core.reasoning_engine.core.logical_reasoning_engine import (
            LogicalReasoningEngine as ReasoningEngine
        )

# 공통 입력 케이스
INP_MATH = {"query": "1+1", "context": "math"}
INP_WEATHER = {"query": "weather", "context": "general"}

@pytest.fixture(scope="module")
def eng():
    return ReasoningEngine()

# 1) 입력 검증: 타입/키 오류는 예외 또는 안전한 실패 반환
@pytest.mark.parametrize("bad", [
    {"query": 123, "context": "math"},
    {"query": None, "context": "math"},
    {"context": "math"},                # query 없음
    {"query": "hi"},                    # context 없음
])
def test_input_validation(eng, bad):
    try:
        out = eng.process(bad)  # 구현에 따라 예외 또는 안전 실패
    except (ValueError, KeyError, TypeError, AssertionError):
        return
    # 예외를 던지지 않는 구현이라면 안전 실패를 강제
    assert isinstance(out, dict)
    assert "result" in out and "confidence" in out

# 2) 결정성(재현성): 동일 입력 → 동일 출력
def test_deterministic_outputs(eng):
    a = eng.process(INP_MATH)
    b = eng.process(INP_MATH)
    assert a == b

# 3) 성능 예산(P95 대용): 단일 호출 지연이 예산 내(예: 50ms)
def test_latency_budget(eng):
    t0 = time.perf_counter()
    _ = eng.process(INP_MATH)
    dt = time.perf_counter() - t0
    assert dt < 0.05  # 50ms 예산, 필요시 조정

# 4) 경계값: 빈 문자열/초장문도 안전 동작
@pytest.mark.parametrize("query", ["", "x" * 10000])
def test_boundary_inputs(eng, query):
    out = eng.process({"query": query, "context": "general"})
    assert isinstance(out, dict)
    assert "result" in out and "confidence" in out

# 5) 회귀 가드(핵심 시나리오): 현재 기대 행동 고정
def test_core_scenarios(eng):
    math_out = eng.process(INP_MATH)
    assert math_out["result"] in (2, "2")  # 구현 차이 허용
    assert math_out["confidence"] == pytest.approx(0.95, abs=0.1)

    gen_out = eng.process(INP_WEATHER)
    assert isinstance(gen_out["result"], (str, type(None)))
    # 기존 기대치 근처(±0.1)
    assert gen_out["confidence"] == pytest.approx(0.3, abs=0.1)
