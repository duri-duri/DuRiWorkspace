#!/usr/bin/env bash
# Textfile heartbeat generator
# Writes a timestamp metric to ensure textfile collector is active
# Usage: Called by cron every 5 minutes

set -euo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-./reports/textfile}"
mkdir -p "$TEXTFILE_DIR"

tmp=$(mktemp "${TEXTFILE_DIR}/.duri_textfile_heartbeat.prom.XXXXXX")
ts=$(date +%s)

{
  echo "# HELP duri_textfile_heartbeat Textfile collector heartbeat timestamp"
  echo "# TYPE duri_textfile_heartbeat gauge"
  echo "duri_textfile_heartbeat $ts"
} > "$tmp"

chmod 644 "$tmp"
mv -f "$tmp" "${TEXTFILE_DIR}/duri_textfile_heartbeat.prom"

