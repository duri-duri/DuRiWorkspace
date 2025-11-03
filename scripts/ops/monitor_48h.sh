#!/usr/bin/env bash
# 관제·판독 루틴(48-72h) - 주요 판독식(원라이너)
# B. monitor_48h.sh 결손 보수
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 주요 판독식 (원라이너) ==="
echo ""

echo "[1] 24h detect ratio (효과적 EV 비율):"
grep -h '^duri_ab_effective_ev' var/evolution/*/ab_effective_ev.prom 2>/dev/null | awk '{s+=$NF; n++} END{if(n>0) print s/n; else print 0}' || echo "0"

echo ""
echo "[2] EV/h(60m):"
evv() {
    if [ -f /home/duri/DuRiWorkspace/scripts/ev_velocity.sh ]; then
        bash /home/duri/DuRiWorkspace/scripts/ev_velocity.sh 2>/dev/null | awk '{print $1}' || echo "N/A"
    elif [ -f /home/duri/DuRiWorkspace/scripts/ev_velocity.sh ]; then
        bash /home/duri/DuRiWorkspace/scripts/ev_velocity.sh 2>/dev/null | awk '{print $1}' || echo "N/A"
    else
        echo "N/A (/home/duri/DuRiWorkspace/scripts/ev_velocity.sh not found)"
    fi
}
evv

echo ""
echo "[3] p-value 표준편차(2h):"
pstd() {
    bash scripts/ab_pvalue_stats.sh "2 hours" 2>/dev/null | grep "표준편차" || echo "N/A"
}
pstd

echo ""
echo "[4] p-value 표준편차(24h):"
bash scripts/ab_pvalue_stats.sh "24 hours" 2>/dev/null | grep "표준편차" || echo "N/A"

echo ""
echo "[5] 목표함수 (success_rate, latency_p50_ms):"
if [ -f .reports/synth/target.prom ]; then
    grep -E "duri_(success_rate|latency_p50_ms)" .reports/synth/target.prom || echo "N/A"
else
    echo "[WARN] target.prom not found (미수집)"
fi

echo ""
echo "[6] TS 라우팅 분배:"
if [ -f .reports/synth/routes.json ]; then
    cat .reports/synth/routes.json || echo "N/A"
else
    echo "[WARN] routes.json not found"
fi

echo ""
echo "[7] Route apply 상태:"
if [ -f .reports/synth/route_apply.prom ]; then
    grep "ab_route_apply_success" .reports/synth/route_apply.prom || echo "N/A"
else
    echo "[WARN] route_apply.prom not found"
fi

echo ""
echo "=== 판정 기준 ==="
echo "  - 72h 내 detect_ratio ≥ 0.10 또는 목표함수 동일 방향 추세 12h 이상 → 개선 증거 채택 (P≈0.7~0.8)"
echo "  - detect_ratio < 0.05 12h 지속 + 목표함수 정체/역행 → 실험 재설계"

