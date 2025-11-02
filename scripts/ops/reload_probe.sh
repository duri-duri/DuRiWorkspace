#!/usr/bin/env bash
set -Eeuo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
mkdir -p "$TEXTFILE_DIR"

out="$TEXTFILE_DIR/reload_probe.prom"
tmp="$(mktemp)"

rc=0
curl -fsS --max-time 3 -X POST http://localhost:9090/-/reload >/dev/null || rc=$?

ts=$(date +%s)

{
  echo "duri_prom_reload_timestamp $ts"
  if [ "$rc" -eq 0 ]; then
    echo "duri_prom_reload_success 1"
  else
    echo "duri_prom_reload_success 0"
  fi
} > "$tmp"

mv "$tmp" "$out"

# 즉시 노출 확인(있으면 1줄 출력, 없으면 빈출력)
curl -s http://localhost:9100/metrics 2>/dev/null | grep '^duri_prom_reload_' || true

exit "$rc"

