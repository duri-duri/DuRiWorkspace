#!/usr/bin/env bash
# Γ6: 한 방 실행 & 검증 루틴
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Γ6: 한 방 실행 & 검증 루틴 ==="
echo ""

# 1) 재시작
echo "[1] Docker 재시작..."
docker compose up -d || echo "[WARN] docker compose 실패"

# 2) 캐시 제거 (Γ3)
echo "[2] 캐시 제거 (Γ3)..."
rm -f var/evolution/*/ab_eval.prom var/evolution/*/.ab_cache 2>/dev/null || true
echo "[OK] 과거 캐시 삭제 완료"

# 3) 2-worker 가동 (Γ1)
echo "[3] 2-worker 가동 (Γ1)..."
WORKERS=2 bash scripts/start_shadow_2worker.sh || echo "[WARN] 워커 시작 실패"

# 4) 즉시 확인 루틴
echo ""
echo "[4] 즉시 확인 루틴..."
echo ""

echo "A) EV 생성 속도:"
bash scripts/ev_velocity.sh 2>&1 || echo "[WARN] ev_velocity.sh 실패"
echo ""

echo "B) AB p-value 통계:"
bash scripts/ab_pvalue_stats.sh 2>&1 || echo "[WARN] ab_pvalue_stats.sh 실패"
echo ""

echo "C) Shadow Epoch 로그:"
grep -E "SHADOW_EPOCH_(START|END)" var/logs/shadow.log 2>/dev/null | tail -4 || echo "[INFO] Epoch 로그 없음"
echo ""

echo "D) 최근 AB 평가 파일:"
find var/evolution -name "ab_eval.prom" -newermt "-2 hours" -exec awk '/^duri_ab_p_value/{print FILENAME": "$0}' {} \; 2>/dev/null | head -5 || echo "[INFO] 최근 AB 평가 없음"
echo ""

# 5) 게이트
echo "[5] 게이트 체크..."
echo ""
bash scripts/doctor.sh 2>&1 | head -40
echo ""
bash scripts/gate_check.sh 2>&1 | tail -15
echo ""

# 6) 테스트 (선택적)
echo "[6] 테스트 실행..."
python3 -m pytest tests/test_ab_variance.py tests/test_ev_cadence.py -v 2>&1 | tail -10 || echo "[INFO] pytest 실패 또는 의존성 필요"
echo ""

echo "=== Γ6 완료 ==="
echo ""
echo "기대 변화:"
echo "  - EV cadence: 1.04/h → ≥2.5/h (초기) → ≥4.0/h"
echo "  - AB p-value: 고유값 ≥ 2, 표준편차 > 0"
echo "  - Shadow epoch: END/Duration 기록 생성 → p50≤6m, p95≤12m 모니터링 가능"

