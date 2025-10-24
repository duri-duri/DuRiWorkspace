import importlib.util
import pathlib
import sys

import pytest


def _load_orch():
    """기존 tests/smoke/test_modules_import.py 패턴 활용 + 강력한 캐시 클리어"""
    p = pathlib.Path("scripts/core/phase11/orchestrator.py")

    # 모든 관련 모듈 캐시 클리어 (강력한 방법)
    modules_to_clear = [name for name in sys.modules.keys() if "phase11" in name or "orchestrator" in name]
    for module_name in modules_to_clear:
        del sys.modules[module_name]

    # 파일 타임스탬프 기반 모듈명 (고유성 보장)
    import time

    module_name = f"phase11_orchestrator_{int(time.time() * 1000000)}"

    spec = importlib.util.spec_from_file_location(module_name, str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_turn(user_text: str):
    """오케스트레이터 턴 실행"""
    mod = _load_orch()
    ctx = mod.TurnContext(conv_id="t", messages=[mod.Message(role="user", content=user_text)])
    oc = mod.Orchestrator()
    ctx = oc.run_turn(ctx)
    return ctx


def _roles(ctx):
    return [m.role for m in ctx.messages]


def _assistant(ctx):
    return next(m for m in ctx.messages if m.role == "assistant").content


def _inner(ctx):
    return next(m for m in ctx.messages if m.role == "inner").content


@pytest.mark.parametrize("text", ["오늘 계획 세워줘", "plan please", "todo 추천", "스케줄 만들어줘"])
def test_golden_plan_requests(text):
    """골든 케이스: 계획 요청에 대한 적절한 응답"""
    ctx = run_turn(text)
    assert "assistant" in _roles(ctx)
    a = _assistant(ctx)
    assert "- " in a or "계획" in a or "plan" in a
    i = _inner(ctx)
    assert "OK" in i or "개선" in i or "성찰" in i


@pytest.mark.parametrize("text", ["...", "???", "무", "", "   "])
def test_failure_ambiguous_requests(text):
    """실패 케이스: 애매한 요청에 대한 안전한 처리"""
    ctx = run_turn(text)
    a = _assistant(ctx)
    # 최소한 에코가 아닌 안내문 형태이어야 함
    assert "[core]" in a and ("입력" in a or "요청" in a or "목표" in a)


def test_telemetry_artifacts():
    """텔레메트리 아티팩트 생성 확인"""
    ctx = run_turn("테스트")  # noqa: F841

    # JSONL 파일 생성 확인
    events_file = pathlib.Path("DuRiCore/memory/phase11_traces/events.jsonl")
    assert events_file.exists(), "events.jsonl 파일이 생성되어야 합니다"

    # 스냅샷 파일 생성 확인
    snapshot_file = pathlib.Path("DuRiCore/memory/phase11_traces/last_context.json")
    assert snapshot_file.exists(), "컨텍스트 스냅샷 파일이 생성되어야 합니다"
