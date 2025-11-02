#!/usr/bin/env bash
# 원클릭 판정 스크립트 (최종 스모크 3지표)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 최종 스모크 3지표 판정 ==="
echo ""

# 1) 분산 정상화: unique_p(2h) ≥ 2 AND sigma(2h) > 0
echo "[1] 분산 정상화 체크..."
UNIQUE_P=$(find var/evolution -name ab_eval.prom -newermt "-2 hours" -exec awk '/^duri_ab_p_value{/{print $NF}' {} \; 2>/dev/null | sort -u | wc -l)
echo "  unique_p(2h): $UNIQUE_P (목표: ≥2)"

# sigma는 ab_pvalue_stats.sh에서 계산하므로 스킵 (doctor.sh에서 확인)
if [ "$UNIQUE_P" -ge 2 ]; then
    echo "  [OK] unique_p ≥ 2"
else
    echo "  [FAIL] unique_p < 2"
fi
echo ""

# 2) 속도(EV/h): ≥ 2.5/h → ≥ 4.0/h
echo "[2] 속도(EV/h) 체크..."
EV_60M=$(find var/evolution -maxdepth 1 -type d -name "EV-*" -newermt "-60 minutes" 2>/dev/null | wc -l)
EV_H=$(echo "scale=2; $EV_60M * 60 / 60" | bc -l 2>/dev/null || echo "$EV_60M")
echo "  EV/h (직전 60m): $EV_H (목표: ≥2.5/h, 최종: ≥4.0/h)"

if (( $(echo "$EV_H >= 2.5" | bc -l 2>/dev/null || echo "0") )); then
    if (( $(echo "$EV_H >= 4.0" | bc -l 2>/dev/null || echo "0") )); then
        echo "  [OK] EV/h ≥ 4.0/h (최종 목표 달성)"
    else
        echo "  [OK] EV/h ≥ 2.5/h (1단계 목표 달성)"
    fi
else
    echo "  [FAIL] EV/h < 2.5/h"
fi
echo ""

# 3) Epoch 지연: p50 ≤ 6m, p95 ≤ 12m
echo "[3] Epoch 지연 체크..."
EPOCH_LOGS=$(grep -E "SHADOW_EPOCH_(START|END|DURATION)" var/logs/shadow.log 2>/dev/null | tail -20 || true)
if [ -n "$EPOCH_LOGS" ]; then
    DURATIONS=$(echo "$EPOCH_LOGS" | grep "SHADOW_EPOCH_DURATION\|dur=" | awk '{print $NF}' | sed 's/s$//' | sort -n)
    if [ -n "$DURATIONS" ]; then
        D_COUNT=$(echo "$DURATIONS" | wc -l)
        D_P50=$(echo "$DURATIONS" | awk -v n="$D_COUNT" 'NR==int(n*0.5+0.5) {print}')
        D_P95=$(echo "$DURATIONS" | awk -v n="$D_COUNT" 'NR==int(n*0.95+0.5) {print}')
        echo "  p50: ${D_P50}s (목표: ≤360s), p95: ${D_P95}s (목표: ≤720s)"
        
        if [ "${D_P95:-9999}" -le 720 ] && [ "${D_P50:-9999}" -le 360 ]; then
            echo "  [OK] Epoch 지연 정상"
        else
            echo "  [WARN] Epoch 지연 초과"
        fi
    else
        echo "  [INFO] Duration 데이터 부족"
    fi
else
    echo "  [INFO] Epoch 로그 없음"
fi
echo ""

# 4) 라벨 무결성 (최종 확인)
echo "[4] 라벨 무결성 (최종 확인)..."
LABELESS=$(find var/evolution -name "ab_eval.prom" -newermt "-2 hours" -exec grep -l '^duri_ab_p_value ' {} \; 2>/dev/null | wc -l)
if [ "$LABELESS" -eq 0 ]; then
    echo "  [OK] 라벨 무결성 통과 (0)"
else
    echo "  [FAIL] 라벨 없는 p라인: $LABELESS"
fi
echo ""

echo "=== 판정 완료 ==="

