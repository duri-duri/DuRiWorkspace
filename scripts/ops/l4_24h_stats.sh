#!/usr/bin/env bash
# L4 24-Hour Monitor Statistics Analyzer
# Purpose: Analyze 24-hour monitoring logs and generate statistics report
# Usage: bash scripts/ops/l4_24h_stats.sh [log_file]

set -euo pipefail

LOG_FILE="${1:-var/logs/l4_24h_monitor.log}"

if [ ! -f "$LOG_FILE" ]; then
  echo "[ERROR] Log file not found: $LOG_FILE"
  exit 1
fi

echo "=== L4 24-Hour Monitoring Statistics ==="
echo "Log file: $LOG_FILE"
echo ""

# Extract Lyapunov V values
echo "=== Lyapunov V Analysis ==="
LYAPUNOV_VALUES=$(grep "lyapunov_V:" "$LOG_FILE" | awk '{print $NF}' | grep -v "N/A" | grep -v "target")

if [ -n "$LYAPUNOV_VALUES" ]; then
  echo "$LYAPUNOV_VALUES" | awk '
    {
      sum += $1
      sumsq += $1 * $1
      n++
      if ($1 > max) max = $1
      if (n == 1 || $1 < min) min = $1
    }
    END {
      if (n > 0) {
        mean = sum / n
        variance = (sumsq / n) - (mean * mean)
        stddev = sqrt(variance)
        printf "Samples: %d\n", n
        printf "Mean: %.4f\n", mean
        printf "Std Dev: %.4f\n", stddev
        printf "Min: %.4f\n", min
        printf "Max: %.4f\n", max
        printf "\n"
        if (mean <= 0.2) {
          printf "[L4.9] Autonomous stability verified\n"
        } else if (mean <= 0.3) {
          printf "[L4.7] Stable but monitoring recommended\n"
        } else {
          printf "[L4.5] Unstable, requires investigation\n"
        }
      }
    }
  '
else
  echo "No Lyapunov V data found"
fi

echo ""
echo "=== Heartbeat Analysis ==="
HEARTBEAT_OK_COUNT=$(grep "heartbeat_ok:" "$LOG_FILE" | grep -c " 1 " || echo "0")
HEARTBEAT_STALL_COUNT=$(grep "heartbeat_stall:" "$LOG_FILE" | grep -c " 1 " || echo "0")
TOTAL_SAMPLES=$(grep -c "heartbeat_ok:" "$LOG_FILE" || echo "0")

if [ "$TOTAL_SAMPLES" -gt 0 ]; then
  OK_RATIO=$(echo "scale=2; $HEARTBEAT_OK_COUNT * 100 / $TOTAL_SAMPLES" | bc)
  echo "Total samples: $TOTAL_SAMPLES"
  echo "Heartbeat OK: $HEARTBEAT_OK_COUNT ($OK_RATIO%)"
  echo "Heartbeat Stall: $HEARTBEAT_STALL_COUNT"
else
  echo "No heartbeat data found"
fi

echo ""
echo "=== Violation Summary ==="
VIOLATION_COUNT=$(grep -c "\[VIOLATION\]" "$LOG_FILE" || echo "0")
ABORT_COUNT=$(grep -c "\[ABORT\]" "$LOG_FILE" || echo "0")

echo "Total violations: $VIOLATION_COUNT"
echo "Abort events: $ABORT_COUNT"

echo ""
echo "=== Time Range ==="
FIRST_LOG=$(head -1 "$LOG_FILE" | grep -oP '\[\K[^\]]+' | head -1)
LAST_LOG=$(tail -1 "$LOG_FILE" | grep -oP '\[\K[^\]]+' | head -1)
echo "Start: $FIRST_LOG"
echo "End: $LAST_LOG"

echo ""
echo "=== Recommendation ==="
if [ "$ABORT_COUNT" -eq 0 ] && [ "$VIOLATION_COUNT" -eq 0 ]; then
  echo "[SUCCESS] No violations detected - L4.9 certification recommended"
elif [ "$ABORT_COUNT" -eq 0 ] && [ "$VIOLATION_COUNT" -lt 3 ]; then
  echo "[OK] Minor violations - L4.7 status maintained"
else
  echo "[WARN] Significant violations detected - L4.5 status, investigation required"
fi

