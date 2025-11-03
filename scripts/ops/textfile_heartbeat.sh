#!/usr/bin/env bash
# Textfile heartbeat generator v2
# Writes a timestamp metric + monotonic seq + writer pid + last_success_exit
# Usage: Called by cron every 5 minutes

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

# Source config (TEXTFILE_DIR)
if [ -f "$ROOT/config/duri.env" ]; then
  source "$ROOT/config/duri.env"
fi

# Default to workspace textfile directory
: "${TEXTFILE_DIR:=${HOME}/DuRiWorkspace/.reports/textfile}"
mkdir -p "$TEXTFILE_DIR"

tmp=$(mktemp "${TEXTFILE_DIR}/.duri_textfile_heartbeat.prom.XXXXXX")
ts=$(date +%s)
pid=$$
seq_file="${TEXTFILE_DIR}/.heartbeat_seq"

# Monotonic sequence (increment on each successful write)
seq=0
if [ -f "$seq_file" ]; then
  seq=$(cat "$seq_file" 2>/dev/null || echo "0")
fi
seq=$((seq + 1))

# Last success exit (0 = success, 1 = failure)
last_success_exit=0

{
  echo "# HELP duri_textfile_heartbeat Textfile collector heartbeat timestamp"
  echo "# TYPE duri_textfile_heartbeat gauge"
  echo "duri_textfile_heartbeat $ts"
  echo ""
  echo "# HELP duri_textfile_heartbeat_seq Monotonic sequence counter"
  echo "# TYPE duri_textfile_heartbeat_seq counter"
  echo "duri_textfile_heartbeat_seq $seq"
  echo ""
  echo "# HELP duri_textfile_writer_pid Writer process PID"
  echo "# TYPE duri_textfile_writer_pid gauge"
  echo "duri_textfile_writer_pid $pid"
  echo ""
  echo "# HELP duri_textfile_last_success_exit Last success exit code (0=success, 1=failure)"
  echo "# TYPE duri_textfile_last_success_exit gauge"
  echo "duri_textfile_last_success_exit $last_success_exit"
} > "$tmp"

chmod 644 "$tmp"
mv -f "$tmp" "${TEXTFILE_DIR}/duri_textfile_heartbeat.prom"
echo "$seq" > "$seq_file"

# Exit with success
exit 0


