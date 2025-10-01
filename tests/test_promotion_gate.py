# tests/test_promotion_gate.py
from scripts.promotion_gate import evaluate

BASE_POLICY = {
    "delta": {"op": "gt", "value": 0},
    "p_value": {"op": "le", "value": 0.05},
}


def test_pass_on_boundary_p_equal_0_05():
    results = {"objective_delta": 0.01, "p_value": 0.05}
    ok, reasons = evaluate(results, BASE_POLICY)
    assert ok, reasons


def test_fail_on_negative_delta():
    results = {"objective_delta": -0.01, "p_value": 0.001}
    ok, reasons = evaluate(results, BASE_POLICY)
    assert not ok


def test_mes_and_n_min_hold():
    policy = {
        **BASE_POLICY,
        "mes": {"op": "ge", "value": 0.02},
        "n_A": {"min": 10},
        "n_B": {"min": 10},
    }
    results_good = {"objective_delta": 0.03, "p_value": 0.02, "n_A": 12, "n_B": 11}
    ok1, _ = evaluate(results_good, policy)
    assert ok1

    results_bad_n = {"objective_delta": 0.03, "p_value": 0.02, "n_A": 9, "n_B": 11}
    ok2, _ = evaluate(results_bad_n, policy)
    assert not ok2


def test_ci_width_gate_fail():
    policy = {
        "delta": {"op": "gt", "value": 0},
        "p_value": {"op": "le", "value": 0.05},
        "ci_width": {"op": "le", "value": 0.01},
    }
    results = {
        "objective_delta": 0.02,
        "p_value": 0.04,
        "ci_low": 0.01,
        "ci_high": 0.035,
    }  # width=0.025
    ok, _ = evaluate(results, policy)
    assert not ok


def test_boundary_delta_zero_fail():
    """경계값 delta=0 → FAIL"""
    results = {"objective_delta": 0.0, "p_value": 0.01}
    ok, reasons = evaluate(results, BASE_POLICY)
    assert not ok
    assert "delta fail" in " ".join(reasons)


def test_policy_key_missing_protection():
    """정책 키 누락 시 보호 로직"""
    results = {"objective_delta": 0.01, "p_value": 0.05}
    empty_policy = {}
    ok, reasons = evaluate(results, empty_policy)
    # 빈 정책이면 기본 정책 사용되어야 함
    assert ok  # 기본 정책으로 PASS
