#!/usr/bin/env bash
# 마지막 체크리스트 (당장 해볼 6줄)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 마지막 체크리스트 (당장 해볼 6줄) ==="
echo ""

# 1) 2-worker 가동
echo "[1] 2-worker 가동..."
bash scripts/start_shadow_2worker.sh

# 2) 2시간 창으로 분산 재계산
echo ""
echo "[2] 2시간 창으로 분산 재계산..."
bash scripts/ab_pvalue_stats.sh "2 hours"

# 3) 고유값 ≥2 확인
echo ""
echo "[3] 고유값 ≥2 확인..."
UNIQUE_COUNT=$(grep -h '^duri_ab_p_value' var/evolution/*/ab_eval.prom 2>/dev/null | awk '{print $NF}' | sort -u | wc -l || echo "0")
echo "고유 p-value 개수: $UNIQUE_COUNT (기대: ≥2)"
if [ "${UNIQUE_COUNT:-0}" -ge 2 ]; then
    echo "[OK] 고유값 ≥2 확인됨"
else
    echo "[WARN] 고유값 < 2 (상수화 의심)"
fi

# 4) epoch END 라인 존재 확인
echo ""
echo "[4] epoch END 라인 존재 확인..."
END_COUNT=$(grep -c 'SHADOW_EPOCH_END' var/logs/shadow.log 2>/dev/null || echo "0")
echo "END 로그 개수: $END_COUNT"
if [ "${END_COUNT:-0}" -gt 0 ]; then
    echo "[OK] END 로그 존재"
else
    echo "[WARN] END 로그 없음 (다음 실행 시 기록 예정)"
fi

# 5) EV 속도
echo ""
echo "[5] EV 속도..."
bash scripts/ev_velocity.sh

# 6) 알람 룰: ABPValueConstant(2h) 추가 확인
echo ""
echo "[6] 알람 룰: ABPValueConstant(2h) 추가 확인..."
if grep -q 'ABPValueConstant2H' prometheus/rules/duri-ab-test.rules.yml; then
    echo "[OK] ABPValueConstant2H 알람 룰 존재"
    grep -n 'ABPValueConstant2H' prometheus/rules/duri-ab-test.rules.yml | head -3
else
    echo "[WARN] ABPValueConstant2H 알람 룰 없음"
fi

echo ""
echo "=== 체크리스트 완료 ==="

