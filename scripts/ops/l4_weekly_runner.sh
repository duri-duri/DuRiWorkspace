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

# 4) 48h 스톱룰 체크 (의미 있는 관찰 확보)
if bash scripts/ops/l4_stop_rule.sh 2>&1 | tee -a "${summary_log}"; then
  stop_result=$?
  if [[ $stop_result -eq 1 ]]; then
    echo "[STOP_RULE] ACT - Shadow replay triggered" >> "${summary_log}"
    # Shadow replay 트리거 (graceful skip)
    python3 scripts/evolution/shadow_runner.py 2>/dev/null || true
  elif [[ $stop_result -eq 2 ]]; then
    echo "[STOP_RULE] STOP - All recent decisions are HOLD (72h+)" >> "${summary_log}"
    # 중단 신호 (로그만 기록, 실제 중단은 수동 확인)
  else
    echo "[STOP_RULE] KEEP - Continue observation" >> "${summary_log}"
  fi
fi

# 5) 로그 롤링은 이제 l4_post_decision.sh 내부에서 디렉터리 락으로 원자 처리됨
# (별도 회전 로직 불필요 - append 시점에 자동 처리)

# 산출 확인용(실패해도 runner 실패로 간주하지 않음)
ls -1t var/audit/logs/weekly_*.log 2>/dev/null | head -1 || true
tail -n +1 var/audit/recommendations.log 2>/dev/null | tail -5 || true

exit 0

