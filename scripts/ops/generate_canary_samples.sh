#!/usr/bin/env bash
# Canary Sample Generation Helper
# Purpose: Generate samples for canary quorum when traffic is low
# Usage: bash scripts/ops/generate_canary_samples.sh [n_samples]

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

N_SAMPLES="${1:-300}"
RPS="${RPS:-2}"
DURATION=$((N_SAMPLES / RPS))

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== Canary Sample Generation ==="
log "Target samples: $N_SAMPLES"
log "RPS: $RPS"
log "Duration: ${DURATION}s"

# Check if sandbox traffic generator exists
if [ -f "scripts/ops/sandbox/smoke_traffic.sh" ]; then
  log "Using sandbox traffic generator..."
  bash scripts/ops/sandbox/smoke_traffic.sh --rps "$RPS" --duration "$DURATION" || {
    log "[WARN] Traffic generator failed, using manual method"
  }
else
  log "[INFO] Traffic generator not found, using manual shadow generation..."
  
  # Use shadow generator if available
  if [ -f "scripts/ops/evolution/shadow_generate.sh" ]; then
    log "Using shadow generator..."
    for i in $(seq 1 $((N_SAMPLES / 10))); do
      bash scripts/ops/evolution/shadow_generate.sh --smoke --tag dryrun --n 10 || true
      sleep 1
    done
  else
    log "[WARN] No traffic generation method available"
    log "  Please ensure canary traffic is routed to generate samples"
  fi
fi

# Wait for metrics to propagate
log "Waiting for metrics to propagate..."
sleep 10

# Check canary samples
SAMPLES=$(curl -sf --max-time 3 --get 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=duri_canary_samples' 2>/dev/null | \
  jq -r '.data.result[0].value[1] // "0"' || echo "0")

log "Current canary samples: $SAMPLES"

if [ "$SAMPLES" -ge "$N_SAMPLES" ]; then
  log "[OK] Quorum reached: $SAMPLES >= $N_SAMPLES"
  exit 0
else
  log "[WARN] Quorum not reached: $SAMPLES < $N_SAMPLES"
  log "  Run canary evaluation again after more traffic"
  exit 1
fi

