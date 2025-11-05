#!/usr/bin/env bash
# L4 Weekly Runner (with lock and logging)
# Purpose: Wrapper for l4_weekly_summary.sh with flock lock and logging
# Usage: Called by systemd timer

set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "${ROOT}"

mkdir -p var/audit/logs

exec 9>var/audit/.l4_weekly.lock
flock -n 9 || { echo "[skip] already running"; exit 0; }

ts=$(date +%Y%m%d_%H%M%S)

# 1) 주간 요약 산출
bash scripts/ops/l4_weekly_summary.sh 2>&1 | tee "var/audit/logs/weekly_${ts}.log"

# 2) 최신 weekly_* 로그 및 점수 파싱
summary_log="var/audit/logs/weekly_${ts}.log"
score="$(grep -E '^\[.*\] Score:' -m1 "${summary_log}" | awk '{print $NF}' || true)"
if [[ -z "${score}" ]]; then
  # 백업: 파일 상단의 Score: X.Y 형식(골든 로그 스타일)
  score="$(grep -E '^Score:' -m1 "${summary_log}" | awk '{print $2}' || echo 0)"
fi

# 3) 후처리(판정/가이드/추천로그/옵션 중단) – 명시 인자 전달
summary="${summary_log}" score="${score}" AUTO_SUSPEND_ON_REVIEW="${AUTO_SUSPEND_ON_REVIEW:-0}" \
bash scripts/ops/inc/l4_post_decision.sh || true

# 산출 확인용(실패해도 runner 실패로 간주하지 않음)
ls -1t var/audit/logs/weekly_*.log 2>/dev/null | head -1 || true
tail -n +1 var/audit/recommendations.log 2>/dev/null | tail -5 || true

exit 0

