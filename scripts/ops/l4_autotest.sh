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

# [G] Check promfile freshness (cadence-aware SLA)
echo "[G] Check promfile freshness (cadence-aware)"
prom_dir="$dir"
now=$(date +%s)

# 산출물별 신선도 기준 (초)
SLA_WEEKLY=$((8*24*3600))      # 8일 (주간 산출물)
SLA_DAILY=$((26*3600))          # 26시간 (일일 산출물)
SLA_QUICK=$((3*3600))           # 3시간 (퀵 체크)
SLA_CANON=$((2*3600))           # 2시간 (정규화)
SLA_BOOT=$((26*3600))           # 26시간 (부팅 상태)
SLA_FRESH=600                   # 10분 (일반 메트릭)

check_age() {
  local f="$1"
  local max="$2"
  local label="$3"
  local warn_only="${4:-0}"
  
  if [[ ! -f "$f" ]]; then
    if [[ $warn_only -eq 1 ]]; then
      echo "⚠️  WARN: $label missing (tolerated)"
      return 0
    else
      echo "❌ MISSING: $label ($f)"
      return 1
    fi
  fi
  
  local mtime
  mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0)
  local age=$((now - mtime))
  
  echo "  $label age: ${age}s (limit: ${max}s)"
  
  if [[ $age -gt $max ]]; then
    if [[ $warn_only -eq 1 ]]; then
      echo "⚠️  WARN: $label older than limit (${max}s)"
      return 0
    else
      echo "❌ FAIL: $label stale (>${max}s)"
      return 1
    fi
  fi
  
  return 0
}

# 주간 산출물: 8일 허용
if ! check_age "$prom_dir/l4_weekly_decision.prom" "$SLA_WEEKLY" "weekly_decision"; then
  fail=1
fi

# 부팅 상태: 26시간 허용
if ! check_age "$prom_dir/l4_boot_status.prom" "$SLA_BOOT" "boot_status" 1; then
  # 경고만, 실패로 처리하지 않음 (부팅 후 26시간 내 업데이트되지 않아도 정상일 수 있음)
  :
fi

# 자체검증 메트릭: 10분 허용 (자체검증 실행 후 즉시 생성되어야 함)
if ! check_age "$prom_dir/l4_selftest.pass.prom" "$SLA_FRESH" "selftest_pass" 1; then
  # 첫 실행이거나 아직 실행되지 않았을 수 있으므로 경고만
  :
fi

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
