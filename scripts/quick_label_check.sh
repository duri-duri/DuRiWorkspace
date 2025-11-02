#!/usr/bin/env bash
# 빠른 체크리스트 (복붙)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 빠른 체크리스트 ==="
echo ""

# 1) 레거시 정리 + 재계산
echo "[1] 레거시 정리 + 재계산..."
bash scripts/fix_legacy_prom.sh
echo ""

# evidence_bundle.sh는 --ev all --force 옵션을 지원하지 않을 수 있으므로 확인
if grep -q "\-\-ev\|--force" scripts/evolution/evidence_bundle.sh 2>/dev/null; then
    bash scripts/evolution/evidence_bundle.sh --ev all --force 2>/dev/null || echo "[INFO] evidence_bundle.sh 재계산 스킵 (옵션 미지원)"
else
    echo "[INFO] evidence_bundle.sh는 --ev all --force 옵션 미지원"
fi
echo ""

# 2) 라벨 무결성=0 확인
echo "[2] 라벨 무결성 확인..."
LABELESS_COUNT=$(find var/evolution -name "ab_eval.prom" -newermt "-2 hours" \
  -exec grep -l '^duri_ab_p_value ' {} \; 2>/dev/null | wc -l || echo "0")
echo "  라벨 없는 p라인 개수: $LABELESS_COUNT (기대: 0)"
if [ "$LABELESS_COUNT" -eq 0 ]; then
    echo "  [OK] 라벨 무결성 통과"
else
    echo "  [FAIL] 라벨 없는 p라인 발견: $LABELESS_COUNT (fix_legacy_prom.sh 재실행 필요)"
fi
echo ""

# 3) 2h 창 집계
echo "[3] 2h 창 집계:"
bash scripts/ab_pvalue_stats.sh "2 hours"
echo ""

# 4) EV/h + Epoch 분포
echo "[4] EV/h:"
bash scripts/ev_velocity.sh
echo ""

echo "[5] Epoch 분포:"
if [ -f "var/logs/shadow.log" ]; then
    bash scripts/epoch_duration_stats.sh var/logs/shadow.log 2>&1 | head -20 || echo "[INFO] Duration 데이터 부족"
else
    echo "  [INFO] Shadow 로그 없음"
fi
echo ""

echo "=== 체크리스트 완료 ==="

