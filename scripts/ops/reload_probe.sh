#!/usr/bin/env bash
set -Eeuo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
mkdir -p "$TEXTFILE_DIR"

out="$TEXTFILE_DIR/reload_probe.prom"

rc=0
curl -fsS --max-time 3 -X POST http://localhost:9090/-/reload >/dev/null || rc=$?

ts=$(date +%s)

{
  echo "duri_prom_reload_success $((rc==0))"
  echo "duri_prom_reload_timestamp $ts"
} > "$out"

exit "$rc"

