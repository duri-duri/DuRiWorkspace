#!/usr/bin/env bash
set -euo pipefail
TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
mkdir -p "$TEXTFILE_DIR"
bash scripts/ev_velocity.sh > "$TEXTFILE_DIR/duri_ev.prom.$$"
mv "$TEXTFILE_DIR/duri_ev.prom.$$" "$TEXTFILE_DIR/duri_ev.prom"
echo "[OK] duri_ev_velocity exported to $TEXTFILE_DIR/duri_ev.prom"
