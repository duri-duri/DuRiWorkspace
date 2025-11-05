#!/usr/bin/env bash
# Wait for Prom File - Prometheus 파일 생성 대기
# Purpose: Prometheus 텍스트파일이 생성될 때까지 대기
# Usage: wait_for_prom.sh <file> <timeout_sec>

set -euo pipefail

f="$1"
timeout="${2:-15}"

for i in $(seq 1 "$timeout"); do
  if [[ -s "$f" ]]; then
    exit 0
  fi
  sleep 1
done

echo "[ERR] prom file not generated: $f" >&2
exit 1

