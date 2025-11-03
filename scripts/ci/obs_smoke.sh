#!/usr/bin/env bash
# CI Observability Smoke Test
# Purpose: Seed heartbeat metrics via Pushgateway and verify recording rules
# Usage: bash scripts/ci/obs_smoke.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PG="http://localhost:9091"
PR="http://localhost:9090"
JOB="node_exporter"
INST="ci"
REALM="prod"

log() {
  echo "[CI] $*" >&2
}

log "Bring up stack"
docker compose -f compose.observation.ci.yml up -d --wait

log "Seed heartbeat x2 via pushgateway"
curl -s --data-binary "duri_textfile_heartbeat_seq{metric_realm=\"${REALM}\"} 1" \
  "${PG}/metrics/job/${JOB}/instance/${INST}" >/dev/null || true
sleep 2
curl -s --data-binary "duri_textfile_heartbeat_seq{metric_realm=\"${REALM}\"} 2" \
  "${PG}/metrics/job/${JOB}/instance/${INST}" >/dev/null || true

# Also push timestamp
TS=$(date +%s)
curl -s --data-binary "duri_textfile_heartbeat_ts{metric_realm=\"${REALM}\"} ${TS}" \
  "${PG}/metrics/job/${JOB}/instance/${INST}" >/dev/null || true

log "Wait for rule evaluation"
sleep 18  # 15~20s

log "Verify heartbeat metrics"
ok=$(curl -sf --get "${PR}/api/v1/query" --data-urlencode "query=duri_heartbeat_ok{metric_realm=\"${REALM}\"}" \
     | jq -r '.data.result[]?.value[1] // "0"')
chg=$(curl -sf --get "${PR}/api/v1/query" --data-urlencode "query=duri_heartbeat_changes_6m{metric_realm=\"${REALM}\"}" \
     | jq -r '.data.result[]?.value[1] // "0"')
fresh=$(curl -sf --get "${PR}/api/v1/query" --data-urlencode "query=duri_heartbeat_fresh_120s{metric_realm=\"${REALM}\"}" \
     | jq -r '.data.result[]?.value[1] // "0"')

log "ok=${ok} chg=${chg} fresh=${fresh}"

if [ "${ok}" != "1" ]; then
  log "FAIL: heartbeat_ok not 1 (got: ${ok})"
  exit 1
fi

log "PASS"
exit 0
