#!/usr/bin/env bash
# Δt95 롤링(6h) 메트릭 계산 및 출력
set -euo pipefail

cd /home/duri/DuRiWorkspace

# 롤링 윈도우 크기 (6시간 = 21600초)
ROLLING_WINDOW=21600
NOW=$(date +%s)
WINDOW_START=$((NOW - ROLLING_WINDOW))

# 6시간 이내 EV 목록 필터링
EV_TIMES=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@\n' 2>/dev/null | \
    awk -v ws="$WINDOW_START" '$1 >= ws {print $1}' | sort -n)

# Δt95 계산
DT95=$(echo "$EV_TIMES" | \
    awk 'NR>1{print $1-prev}{prev=$1}' | \
    sort -n | \
    awk '{a[NR]=$1} END{
        if(NR==0){print "NO_DATA"; exit 1}
        p=0.95*(NR-1)+1; i=int(p); f=p-i;
        val=(f==0)?a[i]:(a[i]*(1-f)+a[i+1]*f);
        printf "%.0f", val
    }')

if [ -z "$DT95" ] || [ "$DT95" = "NO_DATA" ]; then
    echo "duri_pilot_dt95_rolling{window=\"6h\"} -1"
else
    echo "duri_pilot_dt95_rolling{window=\"6h\"} $DT95"
fi

# 파일에 저장 (Prometheus 텍스트 형식)
mkdir -p var/metrics
echo "# HELP duri_pilot_dt95_rolling Δt95 rolling window (6h)" > var/metrics/dt95_rolling.prom
echo "# TYPE duri_pilot_dt95_rolling gauge" >> var/metrics/dt95_rolling.prom
if [ -z "$DT95" ] || [ "$DT95" = "NO_DATA" ]; then
    echo "duri_pilot_dt95_rolling{window=\"6h\"} -1" >> var/metrics/dt95_rolling.prom
else
    echo "duri_pilot_dt95_rolling{window=\"6h\"} $DT95" >> var/metrics/dt95_rolling.prom
fi

