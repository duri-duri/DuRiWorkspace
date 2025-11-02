#!/usr/bin/env bash
# Shadow 병렬 워커 런처 (A: flock 정상화)
set -euo pipefail

cd "$(dirname "$0")/.."

# A) flock 정상화: 락 파일 FD 9 오픈
LOCKFILE="var/run/shadow_worker.lock"
mkdir -p "$(dirname "$LOCKFILE")"
exec 9>"$LOCKFILE"

: "${WORKERS:=2}"
DELAY="${1:-0}"

if [ "$DELAY" -gt 0 ]; then
    sleep "$DELAY"
fi

# A) flock FD 9 오픈 후 병렬 실행 보장
for i in $(seq 1 "$WORKERS"); do
    (
        flock -n 9 || { echo "[SKIP] Shadow worker $i already running"; exit 0; }
        echo "[START] Shadow worker $i ($(date))"
        bash scripts/shadow_duri_integration_final.sh || true
        echo "[END] Shadow worker $i ($(date))"
    ) 9>&- &
done

# 모든 워커 종료 대기 (wait -n 루프)
while kill -0 $(jobs -p) >/dev/null 2>&1; do
    wait -n || true
done
