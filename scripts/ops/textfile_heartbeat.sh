#!/usr/bin/env bash
# Textfile Heartbeat Generator (Pushgateway + Textfile Dual Mode)
# Purpose: Generate heartbeat metrics and push to Pushgateway + write to textfile
# Usage: bash scripts/ops/textfile_heartbeat.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

# Source config (TEXTFILE_DIR)
if [ -f "$ROOT/config/duri.env" ]; then
  source "$ROOT/config/duri.env"
fi

# Single source of truth: Always use reports/textfile
TEXTFILE_DIR="${TEXTFILE_DIR:-$ROOT/reports/textfile}"
PUSHGATEWAY_URL="${PUSHGATEWAY_URL:-http://localhost:9091}"
SEQ_FILE="${TEXTFILE_DIR}/.hb_seq"
LOCK="${TEXTFILE_DIR}/.hb.lock"

mkdir -p "${TEXTFILE_DIR}"

# Lock-protected write (flock prevents concurrent execution)
exec 9>"${LOCK}"
if ! flock -n 9; then
  # Another process is writing, skip silently
  exit 0
fi

# Current seq reading (from existing file if available)
SEQ=$(cat "${SEQ_FILE}" 2>/dev/null || echo 0)
SEQ=$((SEQ + 1))
echo "$SEQ" > "${SEQ_FILE}"

ts=$(date +%s)

# Push to Pushgateway
# Format: job=duri_heartbeat, instance=local
# Metric labels: metric_realm="prod"
# honor_labels: true ensures job="duri_heartbeat" is preserved
cat <<EOF | curl -sf --data-binary @- "${PUSHGATEWAY_URL}/metrics/job/duri_heartbeat/instance/local" >/dev/null 2>&1 || true
# TYPE duri_textfile_heartbeat_seq gauge
duri_textfile_heartbeat_seq{metric_realm="prod"} ${SEQ}
# TYPE duri_textfile_heartbeat_ts gauge
duri_textfile_heartbeat_ts{metric_realm="prod"} ${ts}
EOF

# Also write to textfile for backward compatibility (if node-exporter is available)
SEQ_FILE_TXT="${TEXTFILE_DIR}/duri_textfile_heartbeat_seq.prom"
TS_FILE_TXT="${TEXTFILE_DIR}/duri_textfile_heartbeat_ts.prom"

cat > "${SEQ_FILE_TXT}.$$" <<EOF
duri_textfile_heartbeat_seq{metric_realm="prod"} ${SEQ}
EOF

cat > "${TS_FILE_TXT}.$$" <<EOF
duri_textfile_heartbeat_ts{metric_realm="prod"} ${ts}
EOF

mv -f "${SEQ_FILE_TXT}.$$" "${SEQ_FILE_TXT}"
mv -f "${TS_FILE_TXT}.$$" "${TS_FILE_TXT}"

# Release lock
exec 9>&-

# Exit with success
exit 0
