#!/usr/bin/env bash
# Lyapunov Control Function Evaluator
# Purpose: Calculate control function V(t) and trigger corrective actions
# Usage: Called periodically (e.g., every 5 minutes) to monitor system stability

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

PROM_URL="${PROM_URL:-http://localhost:9090}"
STATE_FILE="${STATE_FILE:-.reports/obs/lyapunov_state.json}"

# Control function coefficients (from user's specification)
ALPHA="${ALPHA:-0.4}"  # GREEN_uptime weight
BETA="${BETA:-0.25}"   # AlertRate weight
GAMMA="${GAMMA:-0.20}" # MTTR weight
DELTA="${DELTA:-0.10}" # DR_success weight
EPSILON="${EPSILON:-0.05}"  # EV/h target weight

EV_TARGET="${EV_TARGET:-4.0}"  # Target EV/h

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

# Query Prometheus for metrics
query_prom() {
  local query="$1"
  curl -sf --max-time 3 --get "$PROM_URL/api/v1/query" \
    --data-urlencode "query=$query" 2>/dev/null | \
    jq -r '.data.result[0].value[1] // "0"' || echo "0"
}

# 1) Collect current metrics
log "Collecting metrics for Lyapunov control function..."

GREEN_UPTIME=$(query_prom 'duri_green_uptime_ratio')
ALERT_RATE=$(query_prom 'duri_alert_rate_per_hour')
MTTR=$(query_prom 'duri_mttr_seconds')
DR_SUCCESS=$(query_prom 'duri_dr_success_ratio_7d')
EV_H=$(query_prom 'rate(duri_ev_created_total[1h])')

# Normalize MTTR (convert seconds to minutes, then normalize 0-1 scale)
MTTR_NORM=$(echo "scale=4; $MTTR / 600" | bc -l 2>/dev/null || echo "0.1")  # 10 minutes = 0.1

# Calculate EV/h deficit
EV_DEFICIT=$(echo "scale=4; if ($EV_H < $EV_TARGET) then ($EV_TARGET - $EV_H) / $EV_TARGET else 0" | bc -l 2>/dev/null || echo "0")

# 2) Calculate control function V(t)
V_TERM1=$(echo "scale=6; $ALPHA * (1 - $GREEN_UPTIME)^2" | bc -l 2>/dev/null || echo "0")
V_TERM2=$(echo "scale=6; $BETA * $ALERT_RATE / 10" | bc -l 2>/dev/null || echo "0")  # Normalize alert rate
V_TERM3=$(echo "scale=6; $GAMMA * $MTTR_NORM" | bc -l 2>/dev/null || echo "0")
V_TERM4=$(echo "scale=6; $DELTA * (1 - $DR_SUCCESS)" | bc -l 2>/dev/null || echo "0")
V_TERM5=$(echo "scale=6; $EPSILON * $EV_DEFICIT" | bc -l 2>/dev/null || echo "0")

V_TOTAL=$(echo "scale=6; $V_TERM1 + $V_TERM2 + $V_TERM3 + $V_TERM4 + $V_TERM5" | bc -l 2>/dev/null || echo "0")

log "[METRICS] GREEN_uptime=$GREEN_UPTIME, AlertRate=$ALERT_RATE, MTTR=${MTTR}s, DR_success=$DR_SUCCESS, EV/h=$EV_H"
log "[CONTROL] V(t)=$V_TOTAL (terms: $V_TERM1 + $V_TERM2 + $V_TERM3 + $V_TERM4 + $V_TERM5)"

# 3) Determine corrective actions
ACTIONS=()

if (( $(echo "$ALERT_RATE > 5" | bc -l 2>/dev/null || echo "0") )); then
  ACTIONS+=("throttle_merges")
  ACTIONS+=("enhance_rules")
fi

if (( $(echo "$MTTR > 300" | bc -l 2>/dev/null || echo "0") )); then
  ACTIONS+=("increase_retry_rate")
  ACTIONS+=("improve_rollback")
fi

if (( $(echo "$DR_SUCCESS < 0.995" | bc -l 2>/dev/null || echo "0") )); then
  ACTIONS+=("block_merges")
  ACTIONS+=("fix_dr_procedures")
fi

if (( $(echo "$EV_DEFICIT > 0.1" | bc -l 2>/dev/null || echo "0") )); then
  ACTIONS+=("increase_l3_cycle")
fi

# 4) Write state
mkdir -p "$(dirname "$STATE_FILE")"
cat > "$STATE_FILE" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "metrics": {
    "green_uptime": $GREEN_UPTIME,
    "alert_rate": $ALERT_RATE,
    "mttr_seconds": $MTTR,
    "dr_success": $DR_SUCCESS,
    "ev_per_hour": $EV_H
  },
  "control_function": {
    "v_total": $V_TOTAL,
    "terms": {
      "green_uptime": $V_TERM1,
      "alert_rate": $V_TERM2,
      "mttr": $V_TERM3,
      "dr_success": $V_TERM4,
      "ev_deficit": $V_TERM5
    }
  },
  "actions": $(printf '%s\n' "${ACTIONS[@]}" | jq -R . | jq -s .)
}
EOF

# 5) Export metrics
METRICS_DIR="${METRICS_DIR:-.reports/textfile}"
mkdir -p "$METRICS_DIR"
tmp_metrics=$(mktemp "${METRICS_DIR}/.duri_lyapunov.prom.XXXXXX")
{
  echo "# HELP duri_lyapunov_v Control function value V(t)"
  echo "# TYPE duri_lyapunov_v gauge"
  echo "duri_lyapunov_v $V_TOTAL"
  echo ""
  echo "# HELP duri_alert_rate_per_hour Alert rate (alerts per hour)"
  echo "# TYPE duri_alert_rate_per_hour gauge"
  echo "duri_alert_rate_per_hour $ALERT_RATE"
  echo ""
  echo "# HELP duri_mttr_seconds Mean time to recovery in seconds"
  echo "# TYPE duri_mttr_seconds gauge"
  echo "duri_mttr_seconds $MTTR"
} > "$tmp_metrics"
chmod 644 "$tmp_metrics"
mv -f "$tmp_metrics" "${METRICS_DIR}/duri_lyapunov.prom"

# 6) Log actions
if [ ${#ACTIONS[@]} -gt 0 ]; then
  log "[ACTIONS] Triggered: ${ACTIONS[*]}"
else
  log "[OK] No corrective actions needed"
fi

echo "$V_TOTAL"

