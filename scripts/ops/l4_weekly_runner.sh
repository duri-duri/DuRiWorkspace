#!/usr/bin/env bash
# L4 Weekly Runner (with lock and logging)
# Purpose: Wrapper for l4_weekly_summary.sh with flock lock and logging
# Usage: Called by systemd timer

set -euo pipefail

cd /home/duri/DuRiWorkspace

mkdir -p var/audit/logs

exec 9>var/audit/.l4_weekly.lock
flock -n 9 || { echo "[skip] already running"; exit 0; }

ts=$(date +%Y%m%d_%H%M%S)

bash scripts/ops/l4_weekly_summary.sh 2>&1 | tee "var/audit/logs/weekly_${ts}.log"

# === [AUTO] L4 주간 후처리: 판정 + 인간 행동 가이드 + (옵션) 자동 중단 ===
# post-decision 모듈 실행 (읽기 전용 로깅; 관찰 중단은 AUTO_SUSPEND_ON_REVIEW=1 로 명시적 허용 시만)
summary="var/audit/logs/weekly_${ts}.log"
AUTO_SUSPEND_ON_REVIEW="${AUTO_SUSPEND_ON_REVIEW:-0}" \
bash scripts/ops/inc/l4_post_decision.sh || true

# 산출 확인용(실패해도 runner 실패로 간주하지 않음)
ls -1t var/audit/logs/weekly_*.log 2>/dev/null | head -1 || true
tail -n +1 var/audit/recommendations.log 2>/dev/null | tail -5 || true

exit 0

