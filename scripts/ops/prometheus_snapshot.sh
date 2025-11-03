#!/usr/bin/env bash
# Prometheus TSDB Snapshot Script (Hardened)
# Purpose: Create Prometheus TSDB snapshot with proper validation
# Usage: bash scripts/ops/prometheus_snapshot.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"
BACKUP_DIR="${BACKUP_DIR:-/home/duri/BACKUP/prometheus}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Prometheus TSDB Snapshot (Hardened) ==="

# Step 1: Check if admin API is enabled
log "Step 1: Checking admin API availability..."
if ! curl -sf "${PROM_URL}/api/v1/status/config" >/dev/null 2>&1; then
  log "[FAIL] Prometheus not accessible"
  exit 1
fi

# Step 2: Create snapshot
log "Step 2: Creating TSDB snapshot..."
SNAP_JSON=$(curl -sfS -XPOST "${PROM_URL}/api/v1/admin/tsdb/snapshot?skip_head=false" 2>&1)

if [ $? -ne 0 ]; then
  log "[FAIL] Snapshot API call failed"
  log "[INFO] Check if --web.enable-admin-api is enabled in Prometheus"
  exit 1
fi

SNAP_ID=$(printf '%s' "$SNAP_JSON" | jq -r '.data.name // empty' 2>/dev/null || echo "")

# Step 3: Validate snapshot ID (3-level check)
log "Step 3: Validating snapshot ID..."
if [ -z "$SNAP_ID" ] || [ "$SNAP_ID" = "null" ] || [ "$SNAP_ID" = "NULL" ]; then
  log "[FAIL] TSDB snapshot name is null/empty"
  log "[INFO] Response: $SNAP_JSON"
  log "[INFO] Check if --web.enable-admin-api is enabled in Prometheus compose file"
  exit 2
fi

log "[OK] Snapshot ID: $SNAP_ID"

# Step 4: Verify snapshot directory exists in container
log "Step 4: Verifying snapshot directory in container..."
if ! docker exec "$PROM_CONTAINER" test -d "/prometheus/snapshots/$SNAP_ID" 2>/dev/null; then
  log "[FAIL] Snapshot directory missing in container: snapshots/$SNAP_ID"
  log "[INFO] Available snapshots:"
  docker exec "$PROM_CONTAINER" ls -la /prometheus/snapshots/ 2>/dev/null || true
  exit 3
fi

log "[OK] Snapshot directory exists in container"

# Step 5: Export snapshot
log "Step 5: Exporting snapshot..."
mkdir -p "$BACKUP_DIR"
SNAP_FILE="${BACKUP_DIR}/prom_tsdb_${SNAP_ID}_$(date +%Y%m%d-%H%M).tar.gz"

if docker exec "$PROM_CONTAINER" tar -C /prometheus -czf - "snapshots/$SNAP_ID" > "$SNAP_FILE" 2>&1; then
  log "[OK] Snapshot exported: $SNAP_FILE"
else
  log "[FAIL] Snapshot export failed"
  exit 4
fi

# Step 6: Verify exported file
if [ ! -f "$SNAP_FILE" ] || [ ! -s "$SNAP_FILE" ]; then
  log "[FAIL] Exported file missing or empty: $SNAP_FILE"
  exit 5
fi

FILE_SIZE=$(ls -lh "$SNAP_FILE" | awk '{print $5}')
log "[OK] Exported file size: $FILE_SIZE"

# Step 7: Create SHA256 checksum
log "Step 7: Creating SHA256 checksum..."
sha256sum "$SNAP_FILE" | tee -a "${BACKUP_DIR}/SHA256SUMS"
log "[OK] Checksum created"

log "[OK] Prometheus TSDB snapshot completed successfully"
log "[INFO] Snapshot: $SNAP_FILE"
exit 0

