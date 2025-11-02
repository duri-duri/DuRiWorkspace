#!/usr/bin/env bash
# (A) 파일계수 기반 EV/h 산출
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

EV_DIR="$ROOT/var/evolution"

count_in_window() { # mins
    local mins="$1"
    find "$EV_DIR" -maxdepth 1 -type d -name "EV-*" -mmin "-$mins" 2>/dev/null | wc -l | awk '{print $1}'
}

ev_60m=$(count_in_window 60)
ev_6h=$(count_in_window 360)

# EV/h
rate_60m=$(awk -v n="$ev_60m" 'BEGIN{printf "%.2f", (60>0? n/1.0 : 0)}')   # 60m 창은 그대로 EV/1h
rate_6h=$(awk -v n="$ev_6h" 'BEGIN{printf "%.2f", (n/6.0)}')               # 6h 창은 6으로 나눔

echo "$rate_60m $rate_6h"
