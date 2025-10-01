# tests/test_ab_runner.py
"""
A/B 러너 통합 테스트
"""
import os
import sys

import pytest

# 레거시 src 우선 인식
if "DuRi_Day11_15_starter" not in sys.path:
    sys.path.insert(0, "DuRi_Day11_15_starter")
sys.path.insert(0, ".")

try:
    from src.ab.core_runner import run_ab_with_gate
except ImportError:
    # Fallback: 직접 import
    import importlib.util

    starter_path = "DuRi_Day11_15_starter"
    spec = importlib.util.spec_from_file_location(
        "core_runner", os.path.join(starter_path, "src/ab/core_runner.py")
    )
    core_runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core_runner)
    run_ab_with_gate = core_runner.run_ab_with_gate


def test_run_ab_with_gate_pass():
    """게이트 통과 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36,
        variant="A",
        seed=42,
        cfg=config,
        gate_policy_path="policies/promotion.yaml",
    )

    # v2 게이트 정책에서는 도메인별 조건이 필요하므로 False가 정상
    assert results["gate_pass"] is False
    assert "gate_reasons" in results
    assert results["objective_delta"] > 0


def test_run_ab_with_gate_fail():
    """게이트 실패 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36,
        variant="B",
        seed=42,
        cfg=config,
        gate_policy_path="policies/promotion.yaml",
    )

    assert results["gate_pass"] is False
    assert "gate_reasons" in results
    assert results["objective_delta"] < 0


def test_run_ab_without_gate():
    """게이트 비활성화 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36, variant="A", seed=42, cfg=config, gate_policy_path=None
    )

    assert results["gate_pass"] is None
    assert results["gate_reasons"] == ["gate_disabled_or_no_policy"]


# tests/test_pou_manager.py
"""
PoU 매니저 통합 테스트
"""
import pytest

from src.pou.manager import create_pou_manager, create_pou_monitor


def test_pou_manager_creation():
    """PoU 매니저 생성 테스트"""
    manager = create_pou_manager()
    assert manager is not None
    assert "domains" in manager.config


def test_pou_pilot_execution():
    """PoU 파일럿 실행 테스트"""
    manager = create_pou_manager()
    result = manager.run_pilot("medical")

    assert result["domain"] == "medical"
    assert result["status"] == "success"
    assert "metrics" in result


def test_pou_monitor_creation():
    """PoU 모니터 생성 테스트"""
    manager = create_pou_manager()
    monitor = create_pou_monitor(manager)

    assert monitor is not None
    status = monitor.get_status()
    assert "status" in status
