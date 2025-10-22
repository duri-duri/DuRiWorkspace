import os
from importlib import reload

from DuRiCore.unified.reasoning import router as R


def _call():
    return R.process({"query": "1+1", "context": "math"})


def test_rollout_0_uses_base(monkeypatch):
    monkeypatch.setenv("DURI_UNIFIED_REASONING_MODE", "auto")
    monkeypatch.setenv("DURI_UNIFIED_REASONING_ROLLOUT", "0")
    reload(R)
    out = _call()
    assert out.get("result") in (2, "2")


def test_rollout_force_unified(monkeypatch):
    monkeypatch.setenv("DURI_UNIFIED_REASONING_MODE", "force")
    reload(R)
    out = _call()
    assert out.get("confidence", 0) >= 0.9
