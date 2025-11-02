#!/usr/bin/env bash
# 3) 검증 루틴(즉시 실행용)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 6단계 패치 검증 루틴 ==="
echo ""

# A. EV 속도(목표: 2.5/h → 4.0/h 수렴)
echo "[A] EV 속도:"
bash scripts/ev_velocity.sh
echo ""

# B. AB 분산(2h 창, n>=1만 집계, 고유값 ≥2, σ>0)
echo "[B] AB 분산 (2h 창):"
bash scripts/ab_pvalue_stats.sh "2 hours"
echo ""

# C. Epoch duration 통계(p50 ≤ 6m, p95 ≤ 12m)
echo "[C] Epoch duration 통계:"
bash scripts/epoch_duration_stats.sh var/logs/shadow.log 2>&1 | head -20 || echo "[INFO] Duration 데이터 부족"
echo ""

# D. 경보 상태(ABPValueConstant, EVVelocityLow, ShadowEpochDelay)
echo "[D] 경보 상태:"
grep -E "ABPValueConstant|EVVelocityLow|ShadowEpochDelay" prometheus/rules/duri-ab-test.rules.yml || echo "[INFO] 경보 룰 없음"
echo ""

echo "=== 검증 완료 ==="

