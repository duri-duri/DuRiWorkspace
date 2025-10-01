#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AXIS="${AXIS:-/mnt/hdd/ARCHIVE/backup_phase5_day8_day15}"
OUT="$ROOT/verify_out"; mkdir -p "$OUT"

declare -a DAYS=({8..34})
RESULTS=()

echo "Starting verification sweep for Days 8-34..."

for d in "${DAYS[@]}"; do
  echo "Verifying Day $d..."
  r="$( "$ROOT/scripts/verify_day.sh" "$d" | sed 's/}},/},/' )"
  echo "$r" > "$OUT/day_${d}.json"
  RESULTS+=("$OUT/day_${d}.json")
done

echo "Generating summary report..."

# 집계 + 손실함수(hinge) 계산
python3 -c "
import json, sys, os
from datetime import datetime

# Load all day results
day_results = []
for i in range(8, 35):
    file_path = f'$OUT/day_{i}.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                day_results.append(json.load(f))
        except json.JSONDecodeError as e:
            print(f'Error parsing day_{i}.json: {e}')
            continue

# Calculate pass rate
pass_count = sum(1 for r in day_results if r.get('status') == 'PASS')
pass_rate = pass_count / len(day_results) if day_results else 0

# Calculate average metrics
metrics_sum = {'pou_success_rate': 0, 'safety_score_avg': 0, 'error_rate_avg': 0, 'latency_ms_avg': 0}
metrics_count = 0

for result in day_results:
    metrics = result.get('metrics', {})
    if metrics:
        for key in metrics_sum:
            metrics_sum[key] += metrics.get(key, 0)
        metrics_count += 1

if metrics_count > 0:
    metrics_avg = {k: v/metrics_count for k, v in metrics_sum.items()}
else:
    metrics_avg = {'pou_success_rate': 0, 'safety_score_avg': 0, 'error_rate_avg': 0, 'latency_ms_avg': 0}

# Calculate loss function (hinge)
def hinge(x, threshold):
    return max(0, threshold - x)

loss = (0.30 * hinge(metrics_avg['pou_success_rate'], 0.80) +
        0.25 * hinge(metrics_avg['safety_score_avg'], 0.95) +
        0.25 * hinge(1 - metrics_avg['error_rate_avg'], 1 - 0.01) +
        0.20 * hinge((1000 - metrics_avg['latency_ms_avg'])/1000, 0))

summary = {
    'as_of': datetime.now().isoformat(),
    'days': day_results,
    'pass_rate': pass_rate,
    'metrics_avg': metrics_avg,
    'loss': loss
}

with open('$OUT/summary_day08_34.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f'Summary report generated: $OUT/summary_day08_34.json')
print(f'Pass rate: {pass_rate:.2%}')
print(f'Loss: {loss:.4f}')
print(f'Total days processed: {len(day_results)}')
"

# 축에 보관(가역)
mkdir -p "$AXIS/day34"
cp "$OUT"/day_*.json "$OUT/summary_day08_34.json" "$AXIS/day34/" 2>/dev/null || true
echo "[OK] Verification sweep complete → $AXIS/day34/summary_day08_34.json"
