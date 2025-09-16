#!/usr/bin/env bash
set -euo pipefail

# 설정
BASELINE_JSON="${BASELINE_JSON:-var/reports/bench/0001_baseline.json}"   # 필요 시 경로 조정
NOW_JSON="${NOW_JSON:-var/reports/bench_now.json}"
THRESH_PCT="${THRESH_PCT:-10}"

mkdir -p "$(dirname "$NOW_JSON")"

echo "[1/2] running benchmarks → $NOW_JSON"
# 벤치 실행(예시: tests/benchmarks 패턴은 환경에 맞게 조정)
pytest -q tests -k "bench" --benchmark-only --benchmark-json="$NOW_JSON"

echo "[2/2] guarding (only-fail-on-regression, threshold ${THRESH_PCT}%)"
scripts/bench_guard.py "$BASELINE_JSON" "$NOW_JSON" "$THRESH_PCT"
