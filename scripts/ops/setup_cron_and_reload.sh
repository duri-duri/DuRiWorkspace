#!/usr/bin/env bash
# Setup Script: Cron Registration + Prometheus Reload
# Purpose: Register cron jobs and reload Prometheus
# Usage: bash scripts/ops/setup_cron_and_reload.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# 1) Cron 등록
log "=== Registering cron jobs ==="

# Textfile heartbeat (every 5 minutes)
(crontab -l 2>/dev/null | grep -v "textfile_heartbeat.sh" || true; \
  echo "*/5 * * * * bash $ROOT/scripts/ops/textfile_heartbeat.sh") | crontab -

log "[OK] textfile_heartbeat.sh registered (every 5 minutes)"

# DR rehearsal (daily at 02:00)
(crontab -l 2>/dev/null | grep -v "dr_rehearsal.sh" || true; \
  echo "0 2 * * * bash $ROOT/scripts/ops/dr_rehearsal.sh") | crontab -

log "[OK] dr_rehearsal.sh registered (daily at 02:00)"

# Verify
log ""
log "Current cron entries:"
crontab -l | grep -E "(textfile_heartbeat|dr_rehearsal)" || log "[WARN] No entries found"

# 2) Prometheus 리로드
log ""
log "=== Reloading Prometheus ==="

if curl -sf --max-time 5 -X POST http://localhost:9090/-/reload >/dev/null 2>&1; then
  log "[OK] Prometheus reloaded"
else
  log "[WARN] Prometheus reload failed (may not be running)"
fi

# 3) Verification
log ""
log "=== Verification ==="
log "Run 'bash scripts/ops/l4_dryrun_decision.sh' to verify setup"

