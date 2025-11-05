#!/usr/bin/env bash
# L4 Sentinel Gauge - 폐쇄 루프 완결성 신호 생성
# Purpose: 모든 자동화 루프가 완전히 닫혔는지 단일 신호로 표시
# Usage: Called by l4-selftest.service ExecStartPost

set -euo pipefail

WORK="${WORK:-/home/duri/DuRiWorkspace}"
OUT_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
mkdir -p "$OUT_DIR"

# Check if all components are healthy
ok=1

# 1. Check decisions in last 24h
if [[ -f "${WORK}/var/audit/decisions.ndjson" ]]; then
  decisions_24h=$(jq -r '
    select(type=="object" and .ts and .decision) 
    | select(.decision | IN("GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"))
    | ( .ts | fromdateiso8601 ) 
    | select(. > (now - 86400))
  ' "${WORK}/var/audit/decisions.ndjson" 2>/dev/null | wc -l | tr -d " ")
  if [[ "${decisions_24h:-0}" -lt 1 ]]; then
    ok=0
  fi
else
  ok=0
fi

# 2. Check selftest pass
if [[ ! -f "$OUT_DIR/l4_selftest.pass.prom" ]]; then
  ok=0
else
  selftest_val=$(grep 'l4_selftest_pass' "$OUT_DIR/l4_selftest.pass.prom" | awk '{print $2}' || echo "0")
  if [[ "$selftest_val" != "1" ]]; then
    ok=0
  fi
fi

# 3. Check weekly decision freshness (allow first-create exception)
if [[ ! -f "$OUT_DIR/l4_weekly_decision.prom" ]]; then
  # First-create exception: warn only
  ok=$((ok & 1))  # Don't fail completely
else
  age=$(($(date +%s) - $(stat -c %Y "$OUT_DIR/l4_weekly_decision.prom" 2>/dev/null || echo 0)))
  if [[ $age -gt 612000 ]]; then  # > 7d
    ok=0
  fi
fi

# 4. Check timers are enabled
if ! systemctl --user is-enabled l4-weekly.timer >/dev/null 2>&1; then
  ok=0
fi

# Export sentinel gauge
cat > "$OUT_DIR/l4_closed_loop_ok.prom" <<EOF
# HELP l4_closed_loop_ok L4 closed loop completeness (1=all OK, 0=degraded)
# TYPE l4_closed_loop_ok gauge
l4_closed_loop_ok $ok
EOF

chmod 0644 "$OUT_DIR/l4_closed_loop_ok.prom" 2>/dev/null || true
bash "${WORK}/scripts/ops/inc/_export_timestamp.sh" "closed_loop_ok" 2>/dev/null || true

exit 0

