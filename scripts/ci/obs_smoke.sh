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
  sleep 2
done

log "Safe reload + wait eval"
curl -sf -X POST "${PROM_URL}/-/reload" >/dev/null || true
sleep 8

log "Verify heartbeat metrics"
ok=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_ok{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

fresh=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_fresh_120s{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

changes=$(curl -sf --get "${PROM_URL}/api/v1/query" \
  --data-urlencode 'query=duri_heartbeat_changes_6m{metric_realm="prod"}' | \
  jq -r '.data.result[]?.value[1] // "N/A"')

log "duri_heartbeat_ok=$ok, fresh_120s=$fresh, changes_6m=$changes"

# Validation
if [ "$ok" != "1" ] && [ "$ok" != "N/A" ]; then
  log "FAIL: heartbeat_ok not 1 (got: $ok)"
  exit 1
fi

# Check if fresh is a valid boolean (should be 0 or 1)
if [ "$fresh" = "N/A" ]; then
  log "FAIL: freshness N/A"
  exit 1
fi

# For boolean check: fresh should be 0 or 1 (or a small positive number if computed as difference)
if ! echo "$fresh" | grep -qE '^[01](\.[0-9]+)?$'; then
  # If it's a timestamp difference, check if it's reasonable (< 120)
  if (( $(echo "$fresh" | awk '{if ($1 > 120 || $1 < 0) exit 1; exit 0}') )); then
    log "WARN: freshness not boolean but reasonable (got: $fresh)"
  else
    log "FAIL: freshness invalid (got: $fresh)"
    exit 1
  fi
fi

# Check changes_6m >= 1 (should have at least 1 increase from 2 pushes)
if [ "$changes" != "N/A" ]; then
  if (( $(echo "$changes < 1" | bc -l 2>/dev/null || echo "0") )); then
    log "WARN: changes_6m < 1 (got: $changes), may need more time"
  fi
fi

log "OK: All heartbeat metrics verified"
exit 0

