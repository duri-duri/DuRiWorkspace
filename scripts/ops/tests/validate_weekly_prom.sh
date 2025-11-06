#!/usr/bin/env bash
# Validate Weekly Prom - Prometheus 메트릭 파일 검증
# Purpose: l4_weekly_decision.prom 파일의 형식, 라벨, 타임스탬프 검증
# Usage: validate_weekly_prom.sh <prom_file>

set -euo pipefail

FILE="${1:-$HOME/.cache/node_exporter/textfile/l4_weekly_decision.prom}"

if [[ ! -f "$FILE" ]] || [[ ! -s "$FILE" ]]; then
  echo "[FAIL] File not found or empty: $FILE" >&2
  exit 1
fi

# 1) 형식: 단 1행의 gauge 시계열과 라벨 1개
if ! grep -q '^l4_weekly_decision_ts{decision="[^"]\+"} [0-9]\+$' "$FILE"; then
  echo "[FAIL] Bad prom format" >&2
  exit 1
fi

# 2) 라벨 값 집합 검증
val=$(sed -n 's/^l4_weekly_decision_ts{decision="\([^"]\+\)".*/\1/p' "$FILE" | head -n1)

if [[ -z "$val" ]]; then
  echo "[FAIL] No decision label found" >&2
  exit 2
fi

case "$val" in
  GO|NO-GO|REVIEW|HOLD|HEARTBEAT|APPROVED|CONTINUE) : ;;
  *) echo "[FAIL] Invalid decision: $val" >&2; exit 2 ;;
esac

# 3) 타임스탬프 신선도(UTC <=120s)
now=$(date -u +%s)
ts=$(awk '/^l4_weekly_decision_ts/{print $NF}' "$FILE" | head -n1)

if [[ -z "$ts" ]] || ! [[ "$ts" =~ ^[0-9]+$ ]]; then
  echo "[FAIL] No valid timestamp found" >&2
  exit 3
fi

delta=$(( now - ts ))

# ζ: scrape_interval + 1s (보통 15s + 1s = 16s)
ZETA=16
effective_delta=$(( delta > ZETA ? delta - ZETA : 0 ))

if [[ "$delta" -lt 0 ]] || [[ "$effective_delta" -gt 120 ]]; then
  echo "[FAIL] staleness or clock drift: Δ=${delta}s, ζ=${ZETA}s, effective=${effective_delta}s" >&2
  exit 3
fi

echo "[PASS] prom validated: decision=$val, Δ=${delta}s, ζ=${ZETA}s, effective=${effective_delta}s"

