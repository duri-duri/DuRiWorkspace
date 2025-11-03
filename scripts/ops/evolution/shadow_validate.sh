#!/usr/bin/env bash
# Shadow Validator: Validate patch candidates with sandbox + statistical tests
# Purpose: L3 pipeline - estimate ΔKS_p, Δunique, Δσ, and P(break)
# Usage: Called by evolution pipeline with patch candidate file

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PATCH_FILE="${1:-}"
if [ -z "$PATCH_FILE" ] || [ ! -f "$PATCH_FILE" ]; then
  echo "Usage: $0 <patch_candidates.json>" >&2
  exit 1
fi

SANDBOX_NAME="prom-validator-$$"
SANDBOX_PORT="${SANDBOX_PORT:-9092}"

cleanup() {
  docker rm -f "$SANDBOX_NAME" 2>/dev/null || true
}
trap cleanup EXIT

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# 1) Start sandbox Prometheus
log "Starting sandbox Prometheus..."
docker run -d --name "$SANDBOX_NAME" \
  -v "$(pwd)/prometheus:/etc/prometheus:ro" \
  -p "$SANDBOX_PORT:9090" \
  prom/prometheus:v2.54.1 \
  --config.file=/etc/prometheus/prometheus.yml.minimal \
  --storage.tsdb.path=/tmp/prometheus \
  --web.listen-address=0.0.0.0:9090 >/dev/null 2>&1

# Wait for readiness
for i in $(seq 1 30); do
  if curl -sf "http://localhost:$SANDBOX_PORT/-/ready" >/dev/null 2>&1; then
    log "[OK] Sandbox ready"
    break
  fi
  sleep 2
done

# 2) Run validation checks
VALIDATION_RESULT="${PATCH_FILE%.json}.validation.json"

# Check rules loaded
rules_loaded=$(curl -sf "http://localhost:$SANDBOX_PORT/api/v1/rules" | \
  jq -r '.data.groups | length' || echo "0")

# Check representative query
query_status=$(curl -sf --get "http://localhost:$SANDBOX_PORT/api/v1/query" \
  --data-urlencode 'query=up' | jq -r '.status' || echo "fail")

# Run promtool check
promtool_pass=0
if docker run --rm --entrypoint /bin/sh \
  -v "$(pwd)/prometheus:/etc/prometheus:ro" \
  prom/prometheus:v2.54.1 -lc \
  'promtool check config /etc/prometheus/prometheus.yml.minimal && promtool check rules /etc/prometheus/rules/*.yml' >/dev/null 2>&1; then
  promtool_pass=1
fi

# Calculate P(break) estimate
P_BREAK=0.0
if [ "$rules_loaded" -eq 0 ] || [ "$query_status" != "success" ] || [ "$promtool_pass" -eq 0 ]; then
  P_BREAK=1.0
fi

# Estimated improvements (placeholder - would use actual A/B test results)
DELTA_KS_P=0.0
DELTA_UNIQUE=0.0
DELTA_SIGMA=0.0

# Calculate odds ratio (OR) - minimum threshold > 1.05
OR=1.0
if [ "$P_BREAK" -lt 0.01 ]; then
  # If no break risk, estimate improvement
  OR=$(echo "scale=2; 1.0 + ($DELTA_KS_P * 0.35 + $DELTA_UNIQUE * 0.30 + $DELTA_SIGMA * 0.20)" | bc -l 2>/dev/null || echo "1.0")
fi

cat > "$VALIDATION_RESULT" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "sandbox_checks": {
    "rules_loaded": $rules_loaded,
    "query_status": "$query_status",
    "promtool_pass": $promtool_pass
  },
  "risk_estimate": {
    "p_break": $P_BREAK
  },
  "improvement_estimate": {
    "delta_ks_p": $DELTA_KS_P,
    "delta_unique": $DELTA_UNIQUE,
    "delta_sigma": $DELTA_SIGMA,
    "odds_ratio": $OR
  },
  "validation": {
    "passed": $(if (( $(echo "$P_BREAK < 0.01" | bc -l 2>/dev/null || echo "0") )) && (( $(echo "$OR > 1.05" | bc -l 2>/dev/null || echo "0") )); then echo "true"; else echo "false"; fi)
  }
}
EOF

log "[VALIDATION] Result: $VALIDATION_RESULT"
echo "$VALIDATION_RESULT"

# Exit with validation result
if [ "$P_BREAK" -lt 0.01 ] && (( $(echo "$OR > 1.05" | bc -l 2>/dev/null || echo "0") )); then
  exit 0
else
  exit 1
fi

