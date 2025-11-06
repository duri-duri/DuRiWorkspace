#!/usr/bin/env bash
# L4 Heartbeat - 결정 스트림 하트비트 생성
# Purpose: 24시간 내 최소 1건의 결정 보장
# Usage: Called by l4-daily-quick.service or l4_post_decision.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
DECISIONS_NDJSON="${ROOT}/var/audit/decisions.ndjson"

# Load spec
HEARTBEAT_INTERVAL="${HEARTBEAT_INTERVAL:-23h}"
cutoff_sec=$(python3 <<PYTHON
import sys
s = "${HEARTBEAT_INTERVAL}"
u = {"m": 60, "h": 3600, "d": 86400}
n = int(s[:-1])
unit = s[-1]
print(n * u.get(unit, 1))
PYTHON
)

# Get last decision timestamp
if [[ -f "${DECISIONS_NDJSON}" ]]; then
  last_ts=$(jq -r '.[-1].ts // empty' "${DECISIONS_NDJSON}" 2>/dev/null | tail -1 || true)
else
  last_ts=""
fi

now=$(date -u +%s)

if [[ -z "$last_ts" ]]; then
  # No decisions yet, create heartbeat
  ts_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  heartbeat='{"ts":"'$ts_iso'","decision":"HEARTBEAT","score":0,"reason":"no_previous_decisions"}'
  echo "$heartbeat" >> "${DECISIONS_NDJSON}"
  echo "[HEARTBEAT] Created initial heartbeat"
elif [[ -n "$last_ts" ]]; then
  last_epoch=$(date -u -d "$last_ts" +%s 2>/dev/null || echo 0)
  age=$((now - last_epoch))
  
  if [[ $age -gt $cutoff_sec ]]; then
    ts_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    heartbeat='{"ts":"'$ts_iso'","decision":"HEARTBEAT","score":0,"reason":"gap_filler","age_sec":'$age'}'
    echo "$heartbeat" >> "${DECISIONS_NDJSON}"
    echo "[HEARTBEAT] Created heartbeat (gap: ${age}s)"
  fi
fi

# Export decision timestamp
bash "${ROOT}/scripts/ops/inc/_export_timestamp.sh" "decision" || true

exit 0

