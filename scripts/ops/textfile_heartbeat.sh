#!/usr/bin/env bash
# Textfile heartbeat generator v2
# Writes a timestamp metric + monotonic seq + writer pid + last_success_exit
# Usage: Called by cron every 5 minutes (or 1 minute for high-frequency)
# Single source of truth: /home/duri/DuRiWorkspace/reports/textfile
# Lock-protected to prevent concurrent writes

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

# Source config (TEXTFILE_DIR)
if [ -f "$ROOT/config/duri.env" ]; then
  source "$ROOT/config/duri.env"
fi

# Single source of truth: Always use reports/textfile
TEXTFILE_DIR="${TEXTFILE_DIR:-$ROOT/reports/textfile}"
METRIC="$TEXTFILE_DIR/duri_textfile_heartbeat.prom"
SEQ_FILE="${TEXTFILE_DIR}/duri_textfile_heartbeat_seq.prom"
TS_FILE="${TEXTFILE_DIR}/duri_textfile_heartbeat_ts.prom"
LOCK="${TEXTFILE_DIR}/.hb.lock"
TMP="$METRIC.$$"

mkdir -p "$TEXTFILE_DIR"

# Lock-protected write (flock prevents concurrent execution)
exec 9>"${LOCK}"
if ! flock -n 9; then
  # Another process is writing, skip silently
  exit 0
fi

# Current seq reading (from existing file if available)
SEQ=0
if [ -f "$SEQ_FILE" ]; then
  SEQ=$(awk '/^duri_textfile_heartbeat_seq{metric_realm="prod"} /{print $2}' "$SEQ_FILE" 2>/dev/null || \
        awk '/^duri_textfile_heartbeat_seq /{print $2}' "$SEQ_FILE" 2>/dev/null || echo 0)
fi
NEW=$((SEQ + 1))

ts=$(date +%s)
pid=$$

# Atomic write: tmp → mv
# Write sequence counter separately for freshness guard
{
  echo "# HELP duri_textfile_heartbeat_seq Monotonic sequence counter"
  echo "# TYPE duri_textfile_heartbeat_seq gauge"
  echo "duri_textfile_heartbeat_seq{metric_realm=\"prod\"} $NEW"
} > "${SEQ_FILE}.$$"
mv -f "${SEQ_FILE}.$$" "$SEQ_FILE"

# Write timestamp separately for freshness guard
{
  echo "# HELP duri_textfile_heartbeat_ts Timestamp of last heartbeat write"
  echo "# TYPE duri_textfile_heartbeat_ts gauge"
  echo "duri_textfile_heartbeat_ts{metric_realm=\"prod\"} $ts"
} > "${TS_FILE}.$$"
mv -f "${TS_FILE}.$$" "$TS_FILE"

# Write full heartbeat file (backward compatibility)
{
  echo "# HELP duri_textfile_heartbeat Textfile collector heartbeat timestamp"
  echo "# TYPE duri_textfile_heartbeat gauge"
  echo "duri_textfile_heartbeat{metric_realm=\"prod\"} $ts"
  echo ""
  echo "# HELP duri_textfile_heartbeat_seq Monotonic sequence counter"
  echo "# TYPE duri_textfile_heartbeat_seq gauge"
  echo "duri_textfile_heartbeat_seq{metric_realm=\"prod\"} $NEW"
  echo ""
  echo "# HELP duri_textfile_writer_pid Writer process PID"
  echo "# TYPE duri_textfile_writer_pid gauge"
  echo "duri_textfile_writer_pid{metric_realm=\"prod\"} $pid"
  echo ""
  echo "# HELP duri_textfile_last_success_exit Last success exit code (0=success, 1=failure)"
  echo "# TYPE duri_textfile_last_success_exit gauge"
  echo "duri_textfile_last_success_exit{metric_realm=\"prod\"} 0"
} > "$TMP"

chmod 644 "$TMP" "$SEQ_FILE" "$TS_FILE"
mv -f "$TMP" "$METRIC"

# Release lock
exec 9>&-

# Exit with success
exit 0
