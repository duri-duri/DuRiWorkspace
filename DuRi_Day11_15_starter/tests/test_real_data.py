# tests/test_real_data.py
"""
실제 실험 데이터 기반 테스트
"""
import json
import pathlib

import pytest

from scripts.promotion_gate import evaluate, load_policy


def test_day36_variantA_real():
    """Day36 Variant A 실제 데이터 테스트"""
    results_path = pathlib.Path("outputs/day36/var_A/results.json")
    policy_path = pathlib.Path("policies/promotion.yaml")

    if not results_path.exists():
        pytest.skip("Day36 A 결과 파일이 없습니다")

    results = json.loads(results_path.read_text())
    policy = load_policy(policy_path)

    ok, reasons = evaluate(results, policy)
    assert ok, f"Day36 A 실패: {reasons}"


def test_day36_variantB_real():
    """Day36 Variant B 실제 데이터 테스트"""
    results_path = pathlib.Path("outputs/day36/var_B/results.json")
    policy_path = pathlib.Path("policies/promotion.yaml")

    if not results_path.exists():
        pytest.skip("Day36 B 결과 파일이 없습니다")

    results = json.loads(results_path.read_text())
    policy = load_policy(policy_path)

    ok, reasons = evaluate(results, policy)
    # B는 의도적으로 실패해야 함
    assert not ok, f"Day36 B는 실패해야 하는데 통과됨: {reasons}"


def test_results_schema():
    """결과 파일 스키마 검증"""
    results_path = pathlib.Path("outputs/day36/var_A/results.json")

    if not results_path.exists():
        pytest.skip("결과 파일이 없습니다")

    results = json.loads(results_path.read_text())

    # 필수 필드 검증
    required_fields = {
        "objective_delta",
        "p_value",
        "t_stat",
        "gate_pass",
        "gate_reasons",
    }
    assert required_fields.issubset(
        results.keys()
    ), f"필수 필드 누락: {required_fields - set(results.keys())}"

    # 데이터 타입 검증
    assert isinstance(results["objective_delta"], (int, float))
    assert isinstance(results["p_value"], (int, float))
    assert isinstance(results["t_stat"], (int, float))
    assert isinstance(results["gate_pass"], (bool, type(None)))
    assert isinstance(results["gate_reasons"], list)

    # 선택적 확장 필드 검증 (있으면 타입 체킹)
    optional_fields = {
        "ci_low": (int, float),
        "ci_high": (int, float),
        "power": (int, float),
        "n_A": int,
        "n_B": int,
        "policy_version": str,
    }

    for field, expected_type in optional_fields.items():
        if field in results:
            if isinstance(expected_type, tuple):
                assert isinstance(
                    results[field], expected_type
                ), f"{field} 타입 오류: {type(results[field])}"
            else:
                assert isinstance(
                    results[field], expected_type
                ), f"{field} 타입 오류: {type(results[field])}"
