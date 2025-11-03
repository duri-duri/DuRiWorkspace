#!/usr/bin/env bash
# CI Observability Smoke Test
# Purpose: Seed heartbeat metrics via Pushgateway and verify recording rules
# Usage: bash scripts/ci/obs_smoke.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PG="${PG:-http://localhost:9091}"
PR="${PR:-http://localhost:9090}"
REALM="${REALM:-prod}"
JOB="${JOB:-duri_heartbeat}"
INSTANCE="${INSTANCE:-local}"

# Scrape/eval intervals from config (default 15s)
SCRAPE="${SCRAPE:-15}"
EVAL="${EVAL:-15}"
# Wait formula: 3×scrape + 1×eval + 3s buffer = 63s for default 15s intervals
WAIT=$(( 3*SCRAPE + 1*EVAL + 3 ))

log() {
  echo "[CI] $*" >&2
}

log "Bring up stack"
docker compose -f compose.observation.ci.yml up -d --wait

log "Seed heartbeat x2 via pushgateway (job=${JOB}, instance=${INSTANCE}, realm=${REALM})"
ts=$(date +%s)
seq1=1
seq2=2

cat <<EOF | curl -sS --data-binary @- "${PG}/metrics/job/${JOB}/instance/${INSTANCE}/"
duri_textfile_heartbeat_seq{metric_realm="${REALM}"} ${seq1}
duri_textfile_heartbeat_ts{metric_realm="${REALM}"} ${ts}
EOF

sleep 2

ts2=$((ts+2))

cat <<EOF | curl -sS --data-binary @- "${PG}/metrics/job/${JOB}/instance/${INSTANCE}/"
duri_textfile_heartbeat_seq{metric_realm="${REALM}"} ${seq2}
duri_textfile_heartbeat_ts{metric_realm="${REALM}"} ${ts2}
EOF

log "Wait for rule evaluation (${WAIT}s = 3×scrape + 1×eval + buffer)"
sleep ${WAIT}

log "Verify heartbeat metrics (labels: job=${JOB}, instance=${INSTANCE}, realm=${REALM})"
QBASE="${PR}/api/v1/query"
realm="metric_realm=\"${REALM}\",job=\"${JOB}\",instance=\"${INSTANCE}\""

ok=$(curl -sf --get "${QBASE}" --data-urlencode "query=duri_heartbeat_ok{${realm}}" \
     | jq -r '.data.result[0]?.value[1] // "0"')
chg=$(curl -sf --get "${QBASE}" --data-urlencode "query=duri_heartbeat_changes_6m{${realm}}" \
     | jq -r '.data.result[0]?.value[1] // "0"')
fresh=$(curl -sf --get "${QBASE}" --data-urlencode "query=duri_heartbeat_fresh_120s{${realm}}" \
     | jq -r '.data.result[0]?.value[1] // "0"')

log "ok=${ok} chg=${chg} fresh=${fresh}"

if [ "${ok}" != "1" ]; then
  log "FAIL: heartbeat_ok not 1 (got: ${ok})"
  log "DEBUG: Check if metrics exist with labels"
  curl -sf --get "${PR}/api/v1/series" --data-urlencode "match[]=duri_textfile_heartbeat_seq{${realm}}" | jq '.data | length' || echo "0"
  exit 1
fi

log "PASS"
exit 0
