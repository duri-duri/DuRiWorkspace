#!/usr/bin/env bash
# A) flock FD9 열림 스모크 테스트
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[TEST] flock FD9 열림 확인"

# shadow_parallel_worker.sh 백그라운드 실행
bash scripts/shadow_parallel_worker.sh 1 0 &
WORKER_PID=$!

# 1초 대기
sleep 1

# FD 9이 잡혀야 정상
if lsof -p "$WORKER_PID" 2>/dev/null | grep -q "shadow_worker.lock.*FD.*9"; then
    echo "[OK] FD 9 오픈 확인됨 (PID: $WORKER_PID)"
    kill "$WORKER_PID" 2>/dev/null || true
    exit 0
else
    echo "[FAIL] FD 9 오픈 확인 실패 (PID: $WORKER_PID)"
    lsof -p "$WORKER_PID" 2>/dev/null | grep -E "lock|FD" || echo "[INFO] lsof 실패"
    kill "$WORKER_PID" 2>/dev/null || true
    exit 1
fi

