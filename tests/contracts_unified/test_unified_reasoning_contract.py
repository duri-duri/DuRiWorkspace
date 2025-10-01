import pytest

from DuRiCore.unified.reasoning.service import UnifiedReasoningService


@pytest.fixture(scope="module")
def svc():
    return UnifiedReasoningService()


def test_unified_reasoning_default_process(svc):
    out = svc.process({"query": "1+1", "context": "math"})
    assert out["result"] in (2, "2")


def test_unified_reasoning_strategy_route(svc):
    out = svc.process({"query": "1+1", "context": "math", "strategy": "deductive"})
    assert out["confidence"] >= 0.9
