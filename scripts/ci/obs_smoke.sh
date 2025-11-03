#!/usr/bin/env bash
# CI Observability Smoke Test
# Purpose: Seed heartbeat metrics via Pushgateway and verify recording rules
# Usage: bash scripts/ci/obs_smoke.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PUSHGATEWAY_URL="${PUSHGATEWAY_URL:-http://localhost:9091}"

log() {
  echo "[CI] $*" >&2
}

log "Bring up stack"
docker compose -f compose.observation.ci.yml up -d --wait

log "Seed heartbeat x2 via pushgateway"
for i in 1 2; do
  TS=$(date +%s)
  SEQ=$i
  cat <<EOF | curl -sf --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/duri_heartbeat/instance/local"
# TYPE duri_textfile_heartbeat_seq gauge
duri_textfile_heartbeat_seq{metric_realm="prod"} ${SEQ}
# TYPE duri_textfile_heartbeat_ts gauge
duri_textfile_heartbeat_ts{metric_realm="prod"} ${TS}
EOF
  log "Pushed heartbeat seq=$SEQ, ts=$TS"
  sleep 2
done

log "Wait for rule evaluation"
sleep 10

log "Verify heartbeat metrics"
ok=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_ok{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "0"')

chg=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_changes_6m{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "0"')

fresh=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_fresh_120s{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "0"')

log "ok=$ok chg=$chg fresh=$fresh"

# Validation
if [ "$ok" != "1" ]; then
  log "FAIL: heartbeat_ok not 1 (got: $ok)"
  exit 1
fi

# fresh should be 0 or 1 (boolean)
if [ "$fresh" = "N/A" ] || [ -z "$fresh" ]; then
  log "FAIL: freshness N/A or empty"
  exit 1
fi

# Check if fresh is valid (0 or 1, or reasonable timestamp difference < 120)
if ! echo "$fresh" | grep -qE '^[01]$'; then
  # If it's a timestamp difference, check if it's reasonable (< 120)
  if ! awk -v v="$fresh" 'BEGIN{exit (v >= 0 && v < 120) ? 0 : 1}'; then
    log "FAIL: freshness invalid (got: $fresh)"
    exit 1
  fi
fi

# Check changes_6m >= 1 (should have at least 1 increase from 2 pushes)
if ! awk -v v="$chg" 'BEGIN{exit (v > 0) ? 0 : 1}'; then
  log "FAIL: changes_6m <= 0 (got: $chg)"
  exit 1
fi

log "OK: All heartbeat metrics verified"
exit 0
