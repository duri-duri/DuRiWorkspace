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
