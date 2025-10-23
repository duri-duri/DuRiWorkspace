#!/usr/bin/env python3
"""
품질 게이트 스코어 평가 스크립트
베이스라인 대비 품질 지표 변화를 측정하고 게이트 통과 여부 결정
"""

import json
import pathlib
import sys
from statistics import mean
from typing import Any, Dict, Optional


def load_metrics(file_path: pathlib.Path) -> Optional[Dict[str, Any]]:
    """메트릭 파일 로드"""
    if not file_path.exists():
        return None

    try:
        return json.loads(file_path.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def calculate_mi_average(metrics: Dict[str, Any]) -> float:
    """Maintainability Index 평균 계산"""
    mi_data = metrics.get("maintainability_index", {})
    if not mi_data:
        return 100.0

    mi_values = []
    for file_path, data in mi_data.items():
        if isinstance(data, dict) and "mi" in data:
            mi_values.append(data["mi"])

    return mean(mi_values) if mi_values else 100.0


def calculate_cc_average(metrics: Dict[str, Any]) -> float:
    """Cyclomatic Complexity 평균 계산"""
    cc_data = metrics.get("cyclomatic_complexity", {})
    if not cc_data:
        return 1.0

    cc_values = []
    for file_path, data in cc_data.items():
        if isinstance(data, dict) and "complexity" in data:
            cc_values.append(data["complexity"])

    return mean(cc_values) if cc_values else 1.0


def count_high_complexity_functions(
    metrics: Dict[str, Any], threshold: int = 10
) -> int:
    """높은 복잡도 함수 개수 계산"""
    cc_data = metrics.get("cyclomatic_complexity", {})
    if not cc_data:
        return 0

    high_complexity_count = 0
    for file_path, data in cc_data.items():
        if isinstance(data, dict) and "complexity" in data:
            if data["complexity"] > threshold:
                high_complexity_count += 1

    return high_complexity_count


def evaluate_gate(
    baseline: Optional[Dict[str, Any]], current: Dict[str, Any]
) -> Dict[str, Any]:
    """게이트 평가 수행"""
    # 현재 메트릭 계산
    curr_mi = calculate_mi_average(current)
    curr_cc = calculate_cc_average(current)
    curr_high_cc = count_high_complexity_functions(current)

    # 베이스라인 메트릭 계산 (없으면 현재값 사용)
    base_mi = calculate_mi_average(baseline) if baseline else curr_mi
    base_cc = calculate_cc_average(baseline) if baseline else curr_cc
    base_high_cc = (
        count_high_complexity_functions(baseline) if baseline else curr_high_cc
    )

    # 델타 계산
    delta_mi = curr_mi - base_mi
    delta_cc = curr_cc - base_cc
    delta_high_cc = curr_high_cc - base_high_cc

    # 게이트 규칙 적용
    gate_results = {
        "maintainability": {
            "current": curr_mi,
            "baseline": base_mi,
            "delta": delta_mi,
            "passed": delta_mi >= -2.0,  # MI 하락 2점 이내 허용
            "threshold": -2.0,
        },
        "complexity": {
            "current": curr_cc,
            "baseline": base_cc,
            "delta": delta_cc,
            "passed": delta_cc <= 1.0,  # CC 증가 1점 이내 허용
            "threshold": 1.0,
        },
        "high_complexity": {
            "current": curr_high_cc,
            "baseline": base_high_cc,
            "delta": delta_high_cc,
            "passed": delta_high_cc <= 2,  # 높은 복잡도 함수 2개 이내 증가 허용
            "threshold": 2,
        },
    }

    # 전체 게이트 통과 여부
    overall_passed = all(result["passed"] for result in gate_results.values())

    return {
        "overall_passed": overall_passed,
        "gate_results": gate_results,
        "summary": {
            "maintainability_delta": delta_mi,
            "complexity_delta": delta_cc,
            "high_complexity_delta": delta_high_cc,
        },
    }


def main():
    """메인 실행 함수"""
    metrics_dir = pathlib.Path("metrics")
    baseline_file = metrics_dir / "baseline.json"
    current_file = metrics_dir / "current.json"

    # 메트릭 로드
    baseline = load_metrics(baseline_file)
    current = load_metrics(current_file)

    if not current:
        print("❌ No current metrics found. Run collect_static_metrics.py first.")
        sys.exit(1)

    if not baseline:
        print("⚠️ No baseline metrics found. Using current metrics as baseline.")
        baseline = current

    # 게이트 평가
    evaluation = evaluate_gate(baseline, current)

    # 결과 출력
    print("🎯 Quality Gate Evaluation Results:")
    print(f"  Overall: {'✅ PASSED' if evaluation['overall_passed'] else '❌ FAILED'}")
    print()

    for gate_name, result in evaluation["gate_results"].items():
        status = "✅" if result["passed"] else "❌"
        print(f"  {gate_name.title()}: {status}")
        print(f"    Current: {result['current']:.2f}")
        print(f"    Baseline: {result['baseline']:.2f}")
        print(f"    Delta: {result['delta']:+.2f}")
        print(f"    Threshold: {result['threshold']}")
        print()

    # 상세 실패 정보
    if not evaluation["overall_passed"]:
        print("🚨 Gate failures:")
        for gate_name, result in evaluation["gate_results"].items():
            if not result["passed"]:
                print(
                    f"  - {gate_name}: {result['delta']:+.2f} (threshold: {result['threshold']})"
                )

    # 종료 코드 설정
    sys.exit(0 if evaluation["overall_passed"] else 1)


if __name__ == "__main__":
    main()
