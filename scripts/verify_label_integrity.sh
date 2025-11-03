#!/usr/bin/env bash
# 검증 체크리스트 (10분 내 수행)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 라벨 무결성 검증 체크리스트 ==="
echo ""

# 1. 라벨 없는 p라인 존재 여부 = 0 확인
echo "[1] 라벨 없는 p라인 존재 여부:"
LABELESS_COUNT=$(grep -h '^duri_ab_p_value ' var/evolution/*/ab_eval.prom 2>/dev/null | wc -l || echo "0")
echo "  라벨 없는 p라인 개수: $LABELESS_COUNT (기대: 0)"
if [ "$LABELESS_COUNT" -eq 0 ]; then
    echo "  [OK] 라벨 없는 p라인 없음"
else
    echo "  [FAIL] 라벨 없는 p라인 발견: $LABELESS_COUNT"
    grep -h '^duri_ab_p_value ' var/evolution/*/ab_eval.prom 2>/dev/null | head -3
fi
echo ""

# 2. 라벨형 p라인·samples 쌍 일관성
echo "[2] 라벨형 p라인·samples 쌍 일관성:"
BAD_FILES=0
for f in var/evolution/*/ab_eval.prom; do
    if [ ! -f "$f" ]; then
        continue
    fi
    p=$(grep -c '^duri_ab_p_value{' "$f" 2>/dev/null || echo "0")
    s=$(grep -c '^duri_ab_samples{' "$f" 2>/dev/null || echo "0")
    if [ "$p" -gt 0 ] && [ "$s" -lt 1 ]; then
        echo "  [BAD] $f: p라인=$p, samples라인=$s"
        BAD_FILES=$((BAD_FILES + 1))
    fi
done
if [ "$BAD_FILES" -eq 0 ]; then
    echo "  [OK] 모든 ev에서 p라인·samples 쌍 일관성 확인"
else
    echo "  [FAIL] 불일치 파일: $BAD_FILES"
fi
echo ""

# 3. 2h 창 통계(유효샘플만)
echo "[3] 2h 창 통계(유효샘플만):"
bash scripts/ab_pvalue_stats.sh "2 hours"
echo ""

# 4. Epoch duration 분포 생성
echo "[4] Epoch duration 분포:"
if [ -f "var/logs/shadow.log" ]; then
    bash scripts/epoch_duration_stats.sh var/logs/shadow.log 2>&1 | head -20 || echo "[INFO] Duration 데이터 부족"
else
    echo "  [INFO] Shadow 로그 없음 (30-60분 후 실행)"
fi
echo ""

# 5. EV cadence
echo "[5] EV cadence:"
bash scripts/ev_velocity.sh
echo ""

echo "=== 검증 완료 ==="

