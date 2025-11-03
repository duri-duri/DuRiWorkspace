#!/usr/bin/env bash
# Textfile Directory Auto-Detection & Synchronization
# Purpose: Detect node_exporter textfile directory and sync all metrics
# Usage: bash scripts/ops/sync_textfile_dir.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

# Source config
if [ -f "$ROOT/config/duri.env" ]; then
  source "$ROOT/config/duri.env"
fi

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# 1) Detect node_exporter textfile directory
log "=== Detecting node_exporter textfile directory ==="

# Check running node_exporter process
NODE_EXPORTER_CMD=$(ps aux | grep -E "[n]ode_exporter" | head -1 | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}' || echo "")

if [ -n "$NODE_EXPORTER_CMD" ]; then
  # Extract directory from command line
  TEXTFILE_DIR_DETECTED=$(echo "$NODE_EXPORTER_CMD" | sed -n 's/.*--collector.textfile.directory=\([^ ]*\).*/\1/p' | head -1 || echo "")
  
  if [ -n "$TEXTFILE_DIR_DETECTED" ]; then
    log "[OK] Detected from process: $TEXTFILE_DIR_DETECTED"
    TEXTFILE_DIR="$TEXTFILE_DIR_DETECTED"
  fi
fi

# Check docker container
if [ -z "${TEXTFILE_DIR:-}" ]; then
  DOCKER_MOUNT=$(docker inspect node-exporter 2>/dev/null | jq -r '.[0].Mounts[]? | select(.Destination=="/textfile") | .Source' | head -1 || echo "")
  
  if [ -n "$DOCKER_MOUNT" ]; then
    log "[OK] Detected from docker: $DOCKER_MOUNT"
    TEXTFILE_DIR="$DOCKER_MOUNT"
  fi
fi

# Fallback to config or default
: "${TEXTFILE_DIR:=${HOME}/DuRiWorkspace/.reports/textfile}"
log "[INFO] Using TEXTFILE_DIR: $TEXTFILE_DIR"

# 2) Ensure directory exists (use container mount path, no sudo)
log "=== Ensuring directory exists ==="

# Use container mount path if available
if [ -n "${DOCKER_MOUNT:-}" ]; then
  TEXTFILE_DIR="$DOCKER_MOUNT"
  log "[OK] Using container mount path: $TEXTFILE_DIR"
fi

# Try to create directory without sudo first
if ! mkdir -p "$TEXTFILE_DIR" 2>/dev/null; then
  log "[WARN] Cannot create $TEXTFILE_DIR without sudo"
  log "[INFO] Please ensure container mount path is accessible or run with appropriate permissions"
  log "[INFO] Container mount should be: ./.reports/textfile:/textfile:ro"
  exit 1
fi

# Ensure permissions (user should own the directory)
chmod 755 "$TEXTFILE_DIR" 2>/dev/null || true

# 3) Sync existing metrics from .reports/textfile
SOURCE_DIR="$ROOT/.reports/textfile"
if [ -d "$SOURCE_DIR" ] && [ "$SOURCE_DIR" != "$TEXTFILE_DIR" ]; then
  log "=== Syncing metrics from $SOURCE_DIR to $TEXTFILE_DIR ==="
  find "$SOURCE_DIR" -maxdepth 1 -type f -name '*.prom' -print0 | while IFS= read -r -d '' file; do
    base=$(basename "$file")
    log "  Copying $base"
    cp -f "$file" "$TEXTFILE_DIR/"
  done
fi

# 4) Set permissions
chmod 644 "$TEXTFILE_DIR"/*.prom 2>/dev/null || true
chown "$USER:$USER" "$TEXTFILE_DIR"/*.prom 2>/dev/null || true

# 5) Update config/duri.env
if [ -f "$ROOT/config/duri.env" ]; then
  if ! grep -q "^TEXTFILE_DIR=" "$ROOT/config/duri.env"; then
    sed -i "1i TEXTFILE_DIR=\"$TEXTFILE_DIR\"" "$ROOT/config/duri.env"
  else
    sed -i "s|^TEXTFILE_DIR=.*|TEXTFILE_DIR=\"$TEXTFILE_DIR\"|" "$ROOT/config/duri.env"
  fi
fi

log "[OK] TEXTFILE_DIR synchronized: $TEXTFILE_DIR"

# 6) Verify node_exporter can see metrics
log ""
log "=== Verification ==="
sleep 2
METRIC_COUNT=$(curl -s http://localhost:9100/metrics 2>/dev/null | grep -c '^duri_' || echo "0")
log "  Metrics visible at localhost:9100: $METRIC_COUNT"

if [ "$METRIC_COUNT" -eq 0 ]; then
  log "[WARN] No duri_ metrics found. Check node_exporter configuration."
  exit 1
fi

log "[OK] Textfile directory synchronized successfully"

