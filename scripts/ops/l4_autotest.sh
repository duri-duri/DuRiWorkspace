#!/usr/bin/env bash
# L4 Autotest - 통합 자동화 검증 스크립트
# Purpose: 자동화가 개입 없이 정상 동작하는지 검증
# Usage: Called by systemd timer or manual execution

set -euo pipefail

WORK="/home/duri/DuRiWorkspace"
LOG="/tmp/l4_autotest.$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

# 로그 출력용 타임존 (계산은 epoch UTC 사용)
export TZ=Asia/Seoul

echo "=== L4 AUTOTEST START $(date) ==="

fail=0

# [A] Timers & Services
echo "[A] Timers & Services"
systemctl --user list-timers --all | grep -E 'l4-(daily|weekly|canonicalize|shadow-replay|daily-quick)' || true

if systemctl --user is-enabled l4-weekly.timer >/dev/null 2>&1; then
  echo "✅ l4-weekly.timer enabled"
else
  echo "❌ l4-weekly.timer NOT enabled"
  fail=1
fi

for s in l4-weekly l4-daily l4-canonicalize l4-shadow-replay l4-daily-quick; do
  env=$(systemctl --user show "${s}.service" | grep '^Environment=' | sed -n '1p' || echo "no env")
  echo "  ${s}: ${env}"
done

# [B] Check NODE_EXPORTER_TEXTFILE_DIR
echo "[B] Check NODE_EXPORTER_TEXTFILE_DIR"
dir=$(systemctl --user show l4-weekly.service | sed -n 's/.*NODE_EXPORTER_TEXTFILE_DIR=\([^ ]*\).*/\1/p' | head -1 || true)
[ -n "$dir" ] || dir="/tmp/test_textfile"
echo "prom dir: $dir"

if [[ ! -d "$dir" ]]; then
  echo "❌ WARN: prom dir not present: $dir"
  fail=1
fi

# [C] Run canonicalize (safe)
echo "[C] Run canonicalize (safe)"
bash "${WORK}/scripts/ops/inc/l4_canonicalize_ndjson.sh" || echo "⚠️  canonicalize non-fatal"

# [D] Run one shadow replay
echo "[D] Run one shadow replay"
systemctl --user start l4-shadow-replay.service || echo "⚠️  shadow start non-fatal"
sleep 3

# [E] Run validation
echo "[E] Run validation"
if bash "${WORK}/scripts/ops/l4_validation.sh" >/tmp/l4_validation.autotest.log 2>&1; then
  echo "✅ VALIDATION OK"
else
  echo "❌ VALIDATION FAIL"
  fail=1
fi

# [F] Check latest decisions
echo "[F] Check latest decisions"
if [[ -f "${WORK}/var/audit/decisions.ndjson" ]]; then
  jq -cr '. | {ts,decision,score}' "${WORK}/var/audit/decisions.ndjson" 2>/dev/null | tail -3 || {
    echo "❌ decisions missing or invalid"
    fail=1
  }
else
  echo "❌ decisions.ndjson missing"
  fail=1
fi

# [F2] Check decisions in last 24h (activity check)
echo "[F2] Decisions in last 24h"
if [[ -f "${WORK}/var/audit/decisions.ndjson" ]]; then
  cutoff_ts=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)
  if jq -e --arg ts "$cutoff_ts" 'select((.ts // "") >= $ts)' "${WORK}/var/audit/decisions.ndjson" 2>/dev/null | head -1 >/dev/null; then
    echo "✅ Recent decisions found in last 24h"
  else
    echo "⚠️  WARN: no decisions in last 24h"
    # 경고만, 실패로 처리하지 않음 (주간 실행일 수 있음)
  fi
fi

# [G] Check promfile freshness (cadence-aware)
# [G] START GENERATED - DO NOT EDIT MANUALLY
# Generated from config/l4_spec.yml using: python3 scripts/ops/gen_l4_from_spec.py
if [[ -f "${WORK}/scripts/ops/inc/_gen_freshness_block.sh" ]]; then
  prom_dir="$dir"
  now=$(date +%s)
  . "${WORK}/scripts/ops/inc/_gen_freshness_block.sh"
else
  echo "⚠️  WARN: Generated freshness block not found, using fallback"
  # Fallback to basic check
  if [[ -f "$dir/l4_weekly_decision.prom" ]]; then
    age=$(($(date +%s) - $(stat -c %Y "$dir/l4_weekly_decision.prom" 2>/dev/null || echo 0)))
    echo "  weekly_decision age: ${age}s (limit: 691200s)"
    if [[ $age -gt 691200 ]]; then
      echo "❌ FAIL: weekly_decision stale (>691200s)"
      fail=1
    fi
  else
    echo "❌ MISSING: weekly_decision"
    fail=1
  fi
fi
# [G] END GENERATED

# [H] Generate selftest metric
echo "[H] Generate selftest metric"
if [[ $fail -eq 0 ]]; then
  echo "l4_selftest_pass{component=\"autotest\"} 1 $(date +%s)" > "${dir}/l4_selftest.pass.prom"
  echo "✅ L4 AUTOTEST PASS $(date)"
  exit 0
else
  echo "l4_selftest_pass{component=\"autotest\"} 0 $(date +%s)" > "${dir}/l4_selftest.pass.prom"
  echo "❌ L4 AUTOTEST FAIL $(date)"
  exit 2
fi
