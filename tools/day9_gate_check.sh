#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
: "${GITHUB_WORKSPACE:=$(pwd)}"

echo "=== Day 9 Gate: Alert Latency & Reliability (Enhanced) ==="
echo "[DEBUG] pwd=$(pwd)"
echo "[DEBUG] workspace=$GITHUB_WORKSPACE"
echo "[Gate] Mode=${GATE_SET:-normal}"
echo "[INFO] Seed-matrix: ${DURI_SEEDS:-17,42,123}"
ls -la "$GITHUB_WORKSPACE/tools" || true

# 결과 디렉토리 보장
mkdir -p "$GITHUB_WORKSPACE/var/reports"

# 항상 절대경로로 실행
python3 "$GITHUB_WORKSPACE/tools/day9_latency_measure.py" \
  --seeds "${DURI_SEEDS:-17,42,123}" \
  --mode "${GATE_SET:-normal}" \
  --out "$GITHUB_WORKSPACE/var/reports/day9.json"

echo "Done."