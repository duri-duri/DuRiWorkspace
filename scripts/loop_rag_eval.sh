#!/usr/bin/env bash
set -Eeuo pipefail
RELOAD=0
trap 'RELOAD=1' HUP

# 루프 공통화 라이브러리 사용
source scripts/lib/loop_common.sh
lock_and_stamp rag_eval

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
  mkdir -p .reports/train/day64
  TS=$(date +%Y%m%d_%H%M)
  echo "[$(date)] RAG 평가 시작 (Shadow Mode)" >> var/logs/loop_rag_eval.log
  bash scripts/rag_eval_day62.sh > .reports/train/day64/run_${TS}.tsv 2>&1
  echo "[$(date)] RAG 평가 완료: .reports/train/day64/run_${TS}.tsv" >> var/logs/loop_rag_eval.log
  ln -sfn ".reports/train/day64/run_${TS}.tsv" .reports/train/day64/LATEST.tsv
  sleep "$SLEEP_SECS"
done
