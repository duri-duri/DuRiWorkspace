#!/usr/bin/env bash
# Textfile heartbeat generator v2
# Writes a timestamp metric + monotonic seq + writer pid + last_success_exit
# Usage: Called by cron every 5 minutes (or 1 minute for high-frequency)
# Single source of truth: /home/duri/DuRiWorkspace/reports/textfile

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
TMP="$METRIC.$$"

mkdir -p "$TEXTFILE_DIR"

# Current seq reading (from existing file if available)
SEQ=0
if [ -f "$METRIC" ]; then
  SEQ=$(awk '/^duri_textfile_heartbeat_seq /{print $2}' "$METRIC" 2>/dev/null || echo 0)
fi
NEW=$((SEQ + 1))

ts=$(date +%s)
pid=$$

# Atomic write: tmp → mv
{
  echo "# HELP duri_textfile_heartbeat Textfile collector heartbeat timestamp"
  echo "# TYPE duri_textfile_heartbeat gauge"
  echo "duri_textfile_heartbeat $ts"
  echo ""
  echo "# HELP duri_textfile_heartbeat_seq Monotonic sequence counter"
  echo "# TYPE duri_textfile_heartbeat_seq gauge"
  echo "duri_textfile_heartbeat_seq $NEW"
  echo ""
  echo "# HELP duri_textfile_writer_pid Writer process PID"
  echo "# TYPE duri_textfile_writer_pid gauge"
  echo "duri_textfile_writer_pid $pid"
  echo ""
  echo "# HELP duri_textfile_last_success_exit Last success exit code (0=success, 1=failure)"
  echo "# TYPE duri_textfile_last_success_exit gauge"
  echo "duri_textfile_last_success_exit 0"
} > "$TMP"

chmod 644 "$TMP"
mv -f "$TMP" "$METRIC"

# Exit with success
exit 0
