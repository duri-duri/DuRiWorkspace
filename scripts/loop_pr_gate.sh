#!/usr/bin/env bash
set -Eeuo pipefail
RELOAD=0
trap 'RELOAD=1' HUP

# 루프 공통화 라이브러리 사용
source scripts/lib/loop_common.sh
lock_and_stamp pr_gate

# 주기 환경변수화
SLEEP_SECS="${SLEEP_SECS:-7200}"
# 기본값 보존 + 숫자 유효성
[[ "$SLEEP_SECS" =~ ^[0-9]+$ ]] || { echo "[err] invalid SLEEP_SECS: $SLEEP_SECS" >&2; exit 2; }

while true; do
  if (( RELOAD )); then
    # 서비스별 환경파일(이미 unit에 EnvironmentFile= 설정됨)
    . /etc/default/duri-rag-eval 2>/dev/null || true
    . /etc/default/duri-workspace 2>/dev/null || true
    RELOAD=0
  fi
  TS=$(date +%Y%m%d_%H%M)
  echo "[$(date)] PR 게이트 점검 시작 (Shadow Mode)" >> var/logs/loop_pr_gate.log
  bash scripts/pr_gate_day63.sh > var/logs/pr_gate_${TS}.log 2>&1
  echo "[$(date)] PR 게이트 점검 완료: var/logs/pr_gate_${TS}.log" >> var/logs/loop_pr_gate.log
  ln -sfn "var/logs/pr_gate_${TS}.log" var/logs/pr_gate_LATEST.log
  sleep "$SLEEP_SECS"
done
