#!/usr/bin/env bash
# C) Shadow epoch Duration 통계 (p50/p95 계산)
set -euo pipefail

LOG_FILE="${1:-var/logs/shadow.log}"

if [ ! -f "$LOG_FILE" ]; then
    echo "[WARN] Shadow log file not found: $LOG_FILE"
    exit 1
fi

# START/END 매칭하여 duration 계산 (dur= 필드 우선 파싱)
durations=$(awk '
/SHADOW_EPOCH_START/ {
    if (match($0, /ev=([^ ]+)/, arr)) {
        ev=arr[1]
    }
    if (match($0, /ts=([0-9]+)/, arr)) {
        start[ev]=arr[1]
    }
}
/SHADOW_EPOCH_END/ {
    if (match($0, /ev=([^ ]+)/, arr)) {
        ev=arr[1]
    }
    # dur= 필드 우선 확인
    if (match($0, /dur=([0-9]+)/, arr)) {
        dur=arr[1]
        if (dur > 0) {
            print dur
        }
    }
    # dur= 없으면 ts= 차이로 계산
    else if (match($0, /ts=([0-9]+)/, arr)) {
        end_ts=arr[1]
        if (start[ev] && end_ts > start[ev]) {
            print (end_ts - start[ev])
            delete start[ev]
        }
    }
}
' "$LOG_FILE" | sort -n)

if [ -z "$durations" ]; then
    echo "[WARN] No epoch durations found in $LOG_FILE"
    exit 1
fi

n=$(echo "$durations" | wc -l)
if [ "$n" -lt 2 ]; then
    echo "[WARN] Insufficient samples: $n < 2"
    exit 1
fi

# p50, p95 계산
p50_idx=$((n * 50 / 100))
p95_idx=$((n * 95 / 100))
p50=$(echo "$durations" | sed -n "${p50_idx}p")
p95=$(echo "$durations" | sed -n "${p95_idx}p")

# 평균 계산
avg=$(echo "$durations" | awk '{sum+=$1; count++} END{if(count>0) print sum/count; else print 0}')

# 분포 히스토그램 (1분 bin)
echo "$durations" | awk '
{
    b=int($1/60)
    h[b]++
}
END {
    for(k in h)
        printf "%3dm~%3dm: %d\n", k*1, (k+1)*1, h[k]
}' | sort -n

echo ""
echo "통계 (샘플 수: $n):"
echo "  p50: ${p50}s (목표: ≤360s)"
echo "  p95: ${p95}s (목표: ≤720s)"
echo "  평균: ${avg}s"

# Prometheus textfile 노출
TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
mkdir -p "$TEXTFILE_DIR" 2>/dev/null || true
if [ -d "$TEXTFILE_DIR" ]; then
    printf 'duri_shadow_epoch_duration_p50_seconds %d\n' "$p50" \
        > "${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom.$$"
    printf 'duri_shadow_epoch_duration_p95_seconds %d\n' "$p95" >> "${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom.$$"
    printf 'duri_shadow_epoch_duration_avg_seconds %d\n' "${avg%.*}" >> "${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom.$$"
    mv "${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom.$$" \
       "${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom" 2>/dev/null || true
    echo "[OK] Prometheus textfile 노출: ${TEXTFILE_DIR}/duri_shadow_epoch_stats.prom"
fi
