#!/usr/bin/env python3
"""
Day41~43: PoU Pilot Metrics Rollup
실제 파일럿 로그에서 메트릭을 산출하여 기존 대시보드와 연결합니다.
"""

import argparse
import json
import pathlib
from typing import Any, Dict, List, Optional

# 도메인별 P95 타임아웃 기준 (ms)
P95_TIMEOUT_THRESHOLDS = {"medical": 1500, "rehab": 1200, "coding": 2000}


def load_logs(log_path: str) -> List[Dict[str, Any]]:
    """로그 파일 로드 (존재하지 않으면 빈 리스트)"""
    if not pathlib.Path(log_path).exists():
        return []

    logs = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return logs


def normalize_domain(domain: str) -> str:
    """도메인 정규화"""
    domain_lower = domain.lower()
    if domain_lower in ["medical", "medicine", "med"]:
        return "medical"
    elif domain_lower in ["rehab", "rehabilitation"]:
        return "rehab"
    elif domain_lower in ["coding", "developer", "code"]:
        return "coding"
    return domain_lower


def calculate_metrics(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """로그에서 메트릭 계산"""
    if not logs:
        return {
            "p_error": None,
            "p_timeout": None,
            "explain_score": None,
            "source": "rollup-empty",
            "total_entries": 0,
        }

    # task_complete 이벤트만 평가 대상 (없으면 전부 사용)
    task_logs = [log for log in logs if log.get("event_type") == "task_complete"]
    if not task_logs:
        task_logs = logs

    total_entries = len(task_logs)

    # 에러율 계산
    error_count = sum(
        1 for log in task_logs if log.get("metrics", {}).get("error_count", 0) > 0
    )
    p_error = error_count / total_entries if total_entries > 0 else 0

    # 타임아웃율 계산 (도메인별 임계값 적용)
    timeout_count = 0
    for log in task_logs:
        domain = normalize_domain(log.get("domain", ""))
        latency_ms = log.get("metrics", {}).get("latency_ms", 0)
        threshold = P95_TIMEOUT_THRESHOLDS.get(domain, 2000)
        if latency_ms > threshold:
            timeout_count += 1

    p_timeout = timeout_count / total_entries if total_entries > 0 else 0

    # 설명성 점수 계산 (quality_score를 0~1로 정규화)
    explain_scores = []
    for log in task_logs:
        metrics = log.get("metrics", {})
        if "explain_score" in metrics:
            explain_scores.append(metrics["explain_score"])
        elif "quality_score" in metrics:
            # 0~100을 0~1로 정규화
            explain_scores.append(metrics["quality_score"] / 100.0)

    explain_score = (
        (sum(explain_scores) / len(explain_scores)) if explain_scores else None
    )

    return {
        "p_error": round(p_error, 4),
        "p_timeout": round(p_timeout, 4),
        "explain_score": round(explain_score, 4) if explain_score is not None else None,
        "source": "rollup-from-logs",
        "total_entries": total_entries,
        "error_count": error_count,
        "timeout_count": timeout_count,
    }


def main():
    parser = argparse.ArgumentParser(description="PoU Pilot Metrics Rollup")
    parser.add_argument(
        "--output",
        default="slo_sla_dashboard_v1/metrics.json",
        help="Output metrics file path",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # 모든 도메인 로그 수집
    all_logs = []

    # SSOT 매핑: 도메인별 가능한 모든 경로 (첫 존재 파일만 채택)
    DOMAIN_ALIASES = {
        "medical": ["medical_pilot_v2_logs/logs.jsonl", "med_pilot_v2_logs/logs.jsonl"],
        "rehab": [
            "rehab_pilot_v2_logs/logs.jsonl",
            "rehabilitation_pilot_v2_logs/logs.jsonl",
        ],
        "coding": ["coding_pilot_v2_logs/logs.jsonl", "code_pilot_v2_logs/logs.jsonl"],
    }

    log_paths = []
    for domain, paths in DOMAIN_ALIASES.items():
        for path in paths:
            if pathlib.Path(path).exists():
                log_paths.append(path)
                break  # 첫 존재 파일만 채택

    for log_path in log_paths:
        logs = load_logs(log_path)
        if logs:
            all_logs.extend(logs)
            if args.verbose:
                print(f"Loaded {len(logs)} entries from {log_path}")

    # 메트릭 계산
    metrics = calculate_metrics(all_logs)

    # 출력 디렉토리 생성
    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 메트릭 저장
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"✅ Metrics written to {args.output}")
    total = metrics.get("total_entries") or 0

    def fmt(x):
        try:
            return f"{float(x):.3f}"
        except Exception:
            return "0.000"

    print(f"   Total entries: {total}")
    print(f"   Error rate: {fmt(metrics.get('p_error'))}")
    print(f"   Timeout rate: {fmt(metrics.get('p_timeout'))}")
    print(f"   Explain score: {fmt(metrics.get('explain_score'))}")


if __name__ == "__main__":
    main()
