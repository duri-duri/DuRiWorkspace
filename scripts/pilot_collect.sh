#!/usr/bin/env bash
# 24h 파일럿 증거 자동 수집 (스냅샷 보고서 생성)
set -euo pipefail

cd /home/duri/DuRiWorkspace

out="var/reports/pilot_24h_snapshot-$(date +%Y%m%d-%H%M%S).md"
mkdir -p var/reports

PH=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_ab_p_value[[:space:]]/{print $2;exit}' || echo "0")
PF=$(awk '/^duri_ab_p_value[[:space:]]/{print $2;exit}' var/metrics/ab_eval.prom 2>/dev/null || echo "0")

DT=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_last_ev_unixtime[[:space:]]/{print $2;exit}' || echo "0")
NOW=$(date +%s)
if [ "$DT" != "0" ]; then
    DELTA=$(( NOW - ${DT%.*} ))
else
    DELTA=999999
fi

EV1H=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -newermt '-1 hour' 2>/dev/null | wc -l)
EV24H=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -newermt '-24 hours' 2>/dev/null | wc -l)
LATEST=$(readlink -f var/evolution/LATEST 2>/dev/null || echo "")

{
    echo "# 24h 파일럿 스냅샷 ($(date))"
    echo "- p_value_http=$PH"
    echo "- p_value_file=$PF"
    python3 - <<PY "$PH" "$PF"
import sys,math
ph=float(sys.argv[1])
pf=float(sys.argv[2])
print(f"- drift_abs={abs(ph-pf):.12g}")
PY
    echo "- Δt_last_EV=${DELTA}s"
    echo "- EV_1h=${EV1H}, EV_24h=${EV24H}"
    echo "- LATEST=${LATEST}"
    echo
    echo "## 최근 EV Top3"
    find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %f\n' 2>/dev/null | sort -nr | head -3 | awk '{printf "- %s (epoch %.0f)\n",$2,$1}'
    
    if [ -n "$LATEST" ] && [ -f "$LATEST/summary.txt" ]; then
        echo
        echo "## LATEST/summary.txt (상위 50줄)"
        head -50 "$LATEST/summary.txt"
    else
        echo
        echo "## LATEST/summary.txt (없음)"
    fi
} > "$out"

echo "[OK] $out"

