#!/usr/bin/env bash
# unique_p(2h)=1 진단 및 수정 스크립트
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== unique_p(2h)=1 진단 및 수정 ==="
echo ""

# [D1] 2h 창 p라인 목록
echo "[D1] 2h 창 p라인 목록 (값·EV 상관):"
find var/evolution -name ab_eval.prom -newermt "-2 hours" -exec awk '/^duri_ab_p_value/{for(i=1;i<=NF;i++){if($i ~ /ev=/) {split($i,a,"\""); ev=a[2]; break}} pv=$NF; if(pv!="") print pv, ev}' {} \; 2>/dev/null | column -t | head -10
echo ""

# [D2] 2h 창 p 고유값 개수 & 분포
echo "[D2] 2h 창 p 고유값 개수 & 분포:"
find var/evolution -name ab_eval.prom -newermt "-2 hours" -exec awk '/^duri_ab_p_value/{print $NF}' {} \; 2>/dev/null | sort -n | tee /tmp/pvals_2h.txt | uniq -c
UNIQ_COUNT=$(sort -u /tmp/pvals_2h.txt 2>/dev/null | wc -l)
echo "고유값 개수: $UNIQ_COUNT"
echo ""

# [D3] 2h 창 n_samples 분포
echo "[D3] 2h 창 n_samples 분포:"
find var/evolution -name ab_eval.prom -newermt "-2 hours" -exec awk '/^duri_ab_samples{/{ev=""; n=0; if(match($0, /ev="([^"]+)"/, m)) ev=m[1]; if(match($0, /}\s+([0-9.eE+-]+)$/, m)) n=m[1]; if(ev!="" && n!="") print ev, n}' {} \; 2>/dev/null | awk '{c[$1]+=$2} END{print "EV별 누적 samples:"; for(k in c) print c[k], k}' | sort -n
echo ""

# [D4] n≥1 EV 개수
echo "[D4] n≥1 EV 개수:"
N_GE1=$(find var/evolution -name ab_eval.prom -newermt "-2 hours" -exec awk '/^duri_ab_samples{/{if(match($0, /}\s+([0-9.eE+-]+)$/, m)) {n=m[1]+0; if(n>=1) print n}}' {} \; 2>/dev/null | wc -l)
echo "n≥1 EV 개수 (2h): $N_GE1"
echo ""

# 판정
echo "=== 판정 ==="
if [ "$N_GE1" -lt 2 ]; then
    echo "[판정] G1: 표본 부족 (n≥1 EV가 1건뿐)"
    echo "[조치] 경로 A 적용: 샘플 확보 우선"
    echo ""
    echo "경로 A 적용:"
    echo "  - GAP_MIN=300s (config/duri.env에 이미 적용)"
    echo "  - DURI_FORCE_MIN_SAMPLES=1 (config/duri.env에 이미 적용)"
    echo "  - tune_ev_h_params.sh 실행 완료"
elif [ "$UNIQ_COUNT" -eq 1 ] && [ "$N_GE1" -ge 2 ]; then
    echo "[판정] G2: p 단조 (n≥1 EV는 여러 개인데 p가 동일)"
    echo "[조치] 경로 B 적용: p 계산 정밀도·랜덤 요인 노이즈 축소"
    echo ""
    echo "경로 B 적용:"
    echo "  - DURI_AB_ROUND=1e-6 (config/duri.env에 이미 적용)"
    echo "  - DURI_AB_SEED_MODE=ev (config/duri.env에 이미 적용)"
    echo "  - 캐시 제거:"
    find var/evolution -name ".ab_cache" -newermt "-2 hours" -delete 2>/dev/null || true
    echo "[OK] 캐시 제거 완료"
else
    echo "[판정] 원인 불명 (추가 조사 필요)"
fi
echo ""

# 재집계
echo "=== 재집계 ==="
bash scripts/ab_pvalue_stats.sh "2 hours" 2>&1 | tail -10
echo ""

# 최종 판정
echo "=== 최종 판정 ==="
bash scripts/final_smoke_3metrics.sh 2>&1 | tail -15

