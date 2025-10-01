#!/usr/bin/env bash
set -euo pipefail

# Day 8~10 통합 검증 스윕 스크립트
# Usage: ./run_verification_sweep.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$WORKSPACE_DIR/verify_out"

# 출력 디렉토리 생성
mkdir -p "$OUTPUT_DIR"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

# JSON 집계 함수 (Python 사용)
aggregate_results() {
    python3 -c "
import json
import sys
from datetime import datetime

results = []
for line in sys.stdin:
    if line.strip():
        try:
            result = json.loads(line.strip())
            results.append(result)
        except json.JSONDecodeError:
            continue

# 통계 계산
total_days = len(results)
pass_count = sum(1 for r in results if r.get('status') == 'PASS')
fail_count = sum(1 for r in results if r.get('status') == 'FAIL')
skip_count = sum(1 for r in results if r.get('status') == 'SKIP')

pass_rate = (pass_count / total_days * 100) if total_days > 0 else 0

# 메트릭 집계
metrics = {}
if results:
    for key in ['pou_success_rate', 'safety_score_avg', 'error_rate_avg', 'latency_ms_avg']:
        values = [r.get('metrics', {}).get(key, 0) for r in results if r.get('metrics', {}).get(key) is not None]
        if values:
            metrics[key] = sum(values) / len(values)

# 손실 함수 계산 (Hinge Loss)
target_pou = 0.85
target_safe = 0.90
target_err = 0.05
target_lat = 1000

loss = 0
if 'pou_success_rate' in metrics:
    loss += max(0, target_pou - metrics['pou_success_rate'])
if 'safety_score_avg' in metrics:
    loss += max(0, target_safe - metrics['safety_score_avg'])
if 'error_rate_avg' in metrics:
    loss += max(0, metrics['error_rate_avg'] - target_err)
if 'latency_ms_avg' in metrics:
    loss += max(0, metrics['latency_ms_avg'] - target_lat)

# 결과 출력
summary = {
    'verification_summary': {
        'total_days': total_days,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'skip_count': skip_count,
        'pass_rate': round(pass_rate, 2),
        'loss_function': round(loss, 4)
    },
    'average_metrics': metrics,
    'day_results': results,
    'timestamp': datetime.now().isoformat()
}

print(json.dumps(summary, indent=2, ensure_ascii=False))
"
}

# 메인 실행
log "Starting Day 8~10 verification sweep..."

# 각 Day 검증 실행
results_file="$OUTPUT_DIR/temp_results.jsonl"
> "$results_file"  # 파일 초기화

for day in 8 9 10; do
    log "Verifying Day $day..."
    "$SCRIPT_DIR/verify_day.sh" "$day" >> "$results_file"
done

# 결과 집계
cat "$results_file" | aggregate_results > "$OUTPUT_DIR/summary_day08_10.json"

log "Verification sweep completed. Results saved to $OUTPUT_DIR/summary_day08_10.json"

# 결과 요약 출력
echo "=== Day 8~10 Verification Summary ==="
python3 -c "
import json
with open('$OUTPUT_DIR/summary_day08_10.json', 'r') as f:
    data = json.load(f)

summary = data['verification_summary']
print(f'Total Days: {summary[\"total_days\"]}')
print(f'Pass: {summary[\"pass_count\"]}')
print(f'Fail: {summary[\"fail_count\"]}')
print(f'Skip: {summary[\"skip_count\"]}')
print(f'Pass Rate: {summary[\"pass_rate\"]}%')
print(f'Loss Function: {summary[\"loss_function\"]}')

if 'average_metrics' in data and data['average_metrics']:
    print('\\nAverage Metrics:')
    for key, value in data['average_metrics'].items():
        print(f'  {key}: {value:.3f}')
"
