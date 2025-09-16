# tests/test_promotion_gate.py
from scripts.promotion_gate import evaluate

BASE_POLICY = {
    "delta":   {"op": "gt", "value": 0},
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
    policy = {"delta":{"op":"gt","value":0},"p_value":{"op":"le","value":0.05},"ci_width":{"op":"le","value":0.01}}
    results = {"objective_delta": 0.02, "p_value": 0.04, "ci_low": 0.01, "ci_high": 0.035}  # width=0.025
    ok, _ = evaluate(results, policy)
    assert not ok
