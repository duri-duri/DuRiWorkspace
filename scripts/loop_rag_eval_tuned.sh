#!/usr/bin/env bash
set -Eeuo pipefail
RELOAD=0
trap 'RELOAD=1' HUP

# 루프 공통화 라이브러리 사용
source scripts/lib/loop_common.sh
lock_and_stamp rag_eval_tuned

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
  mkdir -p .reports/train/day64_tuned
  TS=$(date +%Y%m%d_%H%M)
  echo "[$(date)] RAG(튜닝) 시작" >> var/logs/loop_rag_eval_tuned.log
  HYBRID_ALPHA=0.5 K=3 THRESH_P=0.45 SEARCH=scripts/rag_search_enhanced.sh \
    bash scripts/rag_gate.sh .reports/day62/ground_truth_clean.tsv \
    > .reports/train/day64_tuned/run_${TS}.log 2>&1
  echo "[$(date)] RAG(튜닝) 완료: .reports/train/day64_tuned/run_${TS}.log" >> var/logs/loop_rag_eval_tuned.log
  ln -sfn ".reports/train/day64_tuned/run_${TS}.log" .reports/train/day64_tuned/LATEST.log
  sleep "$SLEEP_SECS"
done
