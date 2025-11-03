#!/usr/bin/env bash
# Rollback & Restart One-Liner
# Purpose: Immediate rollback and observation loop restart
# Usage: bash scripts/ops/rollback_restart.sh <bad_sha>

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

BAD_SHA="${1:-HEAD}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Rollback & Restart ==="

# Rollback
log "Reverting $BAD_SHA..."
git revert --no-edit "$BAD_SHA" || log "[WARN] Revert failed"
git push origin HEAD:main || log "[WARN] Push failed"

# Restart Prometheus
log "Restarting Prometheus..."
if systemctl --user is-active prometheus >/dev/null 2>&1; then
  systemctl --user restart prometheus || log "[WARN] Systemd restart failed"
elif docker ps --format '{{.Names}}' | grep -q prometheus; then
  docker restart prometheus || log "[WARN] Docker restart failed"
else
  log "[WARN] Prometheus not found (systemd or docker)"
fi

# Restart heartbeat
log "Restarting heartbeat..."
bash scripts/ops/textfile_heartbeat.sh || log "[WARN] Heartbeat restart failed"

log "[OK] Rollback and restart completed"

