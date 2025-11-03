#!/usr/bin/env bash
# 10-30분 빠른 검증 체크리스트
set -euo pipefail

cd /home/duri/DuRiWorkspace

echo "=== 빠른 검증 체크리스트 ==="
echo ""

# A) 최근 1시간 EV 개수 (목표 ≥4)
EV_1H=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -newermt '-1 hour' 2>/dev/null | wc -l)
echo "A) EV_1h: $EV_1H (목표: ≥4, 기대값: ≈6)"
if [ "$EV_1H" -ge 4 ]; then
    echo "   ✅ 충족"
else
    echo "   ❌ 미충족"
fi

# B) Δt_now (프리-알람 >1800s, 롤백 >7200s)
DT_NOW=$(curl -fsS localhost:9109/metrics 2>/dev/null | awk '/^duri_last_ev_unixtime/{t=$2} END{now=systime(); dt=now-int(t); print dt}' || echo "0")
echo ""
echo "B) Δt_now: ${DT_NOW}s"
if [ "$DT_NOW" -gt 7200 ]; then
    echo "   🚨 롤백 조건 (Δt_now > 7200s)"
elif [ "$DT_NOW" -gt 1800 ]; then
    echo "   ⚠️ 프리-알람 (Δt_now > 1800s)"
elif [ "$DT_NOW" -le 1200 ]; then
    echo "   ✅ 수락 범위 (Δt_now ≤ 1200s)"
else
    echo "   ⚠️ 경계선 (1200s < Δt_now ≤ 1800s)"
fi

# C) 6h 롤링 Δt95 (목표 ≤1800s, 가드 2400s)
DT95_6H=$(awk '/^duri_pilot_dt95_rolling{window="6h"}/{print $2;exit}' var/metrics/dt95_rolling.prom 2>/dev/null || echo "N/A")
echo ""
echo "C) Δt95(6h): ${DT95_6H}s"
if [ "$DT95_6H" != "N/A" ] && [ "$DT95_6H" != "-1" ]; then
    if (( $(echo "$DT95_6H <= 1800" | bc -l 2>/dev/null || awk -v d="$DT95_6H" 'BEGIN{if (d <= 1800) print 1; else print 0}') )); then
        echo "   ✅ 목표 달성 (Δt95 ≤ 1800s)"
    elif (( $(echo "$DT95_6H > 2400" | bc -l 2>/dev/null || awk -v d="$DT95_6H" 'BEGIN{if (d > 2400) print 1; else print 0}') )); then
        echo "   🚨 가드 초과 (Δt95 > 2400s) → 미세 조정 필요"
    else
        echo "   ⚠️ 경계선 (1800s < Δt95 ≤ 2400s)"
    fi
else
    echo "   ⚠️ 데이터 부족 (계산 중)"
fi

echo ""
echo "=== 수락/조정 기준 ==="
echo ""
echo "✅ 수락 (그대로 유지/승격):"
echo "   EV_1h ≥ 4 AND Δt_now ≤ 1200s AND Δt95(6h) ≤ 1800s 중 2개 이상 충족"
echo ""
echo "⚠️ 미세 조정:"
echo "   2시간 내 Δt95(6h) > 2400s 지속 → 주기 480s(8분)로 고정 전환 + 첫 30분간 burst 1회"
echo ""
echo "🚨 즉시 롤백:"
echo "   Δt_now > 7200s OR exporter_up==0 ≥300s OR drift>1e-9 연속 2회"

