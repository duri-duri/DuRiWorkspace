# tests/test_ab_runner.py
"""
A/B 러너 통합 테스트
"""
import pytest
from src.ab.core_runner import run_ab_with_gate

def test_run_ab_with_gate_pass():
    """게이트 통과 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36, variant="A", seed=42, cfg=config,
        gate_policy_path="policies/promotion.yaml"
    )
    
    assert results["gate_pass"] is True
    assert "gate_reasons" in results
    assert results["objective_delta"] > 0

def test_run_ab_with_gate_fail():
    """게이트 실패 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36, variant="B", seed=42, cfg=config,
        gate_policy_path="policies/promotion.yaml"
    )
    
    assert results["gate_pass"] is False
    assert "gate_reasons" in results
    assert results["objective_delta"] < 0

def test_run_ab_without_gate():
    """게이트 비활성화 테스트"""
    config = {"metrics": {"primary": "objective_delta"}}
    results = run_ab_with_gate(
        day=36, variant="A", seed=42, cfg=config,
        gate_policy_path=None
    )
    
    assert results["gate_pass"] is None
    assert results["gate_reasons"] == ["gate_disabled_or_no_policy"]
