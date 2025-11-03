#!/usr/bin/env bash
# Shadow 2-worker 병렬화 시작 스크립트 (워커 PID/로그 파일 분리)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[START] Shadow 2-worker 병렬화 시작 ($(date))"

# (2) 워커+인플라이트를 보수적으로 +1씩 올려 스루풋 경사 확보
: "${WORKERS:=4}"

# 워커 PID/로그 파일 분리 (worker-1.log, worker-2.log)
mkdir -p var/logs

# Worker 1: 즉시 시작
bash scripts/shadow_parallel_worker.sh 1 0 > var/logs/shadow_worker-1.log 2>&1 &
WORKER1_PID=$!
echo "[INFO] Worker 1 PID: $WORKER1_PID"

# Worker 2: 5초 지연 후 시작
if [ "$WORKERS" -ge 2 ]; then
    bash scripts/shadow_parallel_worker.sh 2 5 > var/logs/shadow_worker-2.log 2>&1 &
    WORKER2_PID=$!
    echo "[INFO] Worker 2 PID: $WORKER2_PID"
fi

# 워커 확인 (5초 후)
sleep 6
echo "[CHECK] 실행 중인 Shadow 워커:"
pgrep -fa "shadow_duri_integration_final\|shadow_parallel_worker" || echo "[INFO] 워커 없음"

# FD 9 열림 확인 (flock 정상화 검증)
if [ -f "var/run/shadow_worker.lock" ]; then
    echo "[OK] 락 파일 생성 확인: var/run/shadow_worker.lock"
    lsof var/run/shadow_worker.lock 2>/dev/null | grep -q "FD.*9" && echo "[OK] FD 9 오픈 확인됨" || echo "[WARN] FD 9 오픈 확인 실패"
else
    echo "[WARN] 락 파일 없음"
fi

echo "[OK] Shadow ${WORKERS}-worker 시작 완료 (로그: var/logs/shadow_worker-{1,2}.log)"
