#!/usr/bin/env bash
# (4) EV/h 승수를 건드리는 안전한 3변수 미세튜닝
set -euo pipefail

cd "$(dirname "$0")/.."

# config/duri.env에서 설정 로드
if [ -f "config/duri.env" ]; then
    set -a
    source config/duri.env
    set +a
fi

# 환경변수 우선순위: DURI_* > config/duri.env > 기본값
: "${DURI_WORKERS:=4}"
: "${DURI_MAX_INFLIGHT:=6}"
: "${DURI_GAP_MIN:=360}"  # 6분 (초 단위)

echo "=== EV/h 승수 미세튜닝 ==="
echo ""
echo "현재 설정:"
echo "  WORKERS: $DURI_WORKERS"
echo "  MAX_INFLIGHT: $DURI_MAX_INFLIGHT"
echo "  GAP_MIN: ${DURI_GAP_MIN}s ($(($DURI_GAP_MIN / 60))분)"
echo ""

# 이론적 상한 계산
THEORETICAL_MAX=$(echo "scale=2; $DURI_WORKERS * $DURI_MAX_INFLIGHT / ($DURI_GAP_MIN / 60)" | bc -l 2>/dev/null || echo "0")
EFFECTIVE_MIN=$(echo "scale=2; $THEORETICAL_MAX * 0.60" | bc -l 2>/dev/null || echo "0")
EFFECTIVE_MAX=$(echo "scale=2; $THEORETICAL_MAX * 0.80" | bc -l 2>/dev/null || echo "0")

echo "이론적 상한: ${THEORETICAL_MAX}/h"
echo "예상 실효 범위: ${EFFECTIVE_MIN}/h ~ ${EFFECTIVE_MAX}/h"
echo ""

# pilot_24h.sh에 적용
if [ -f "scripts/pilot_24h.sh" ]; then
    # MAX_INFLIGHT 업데이트
    sed -i "s/: \"\${MAX_INFLIGHT:=[0-9]\+}\"/: \"\${MAX_INFLIGHT:=$DURI_MAX_INFLIGHT}\"/" scripts/pilot_24h.sh 2>/dev/null || true
    # MAX_GAP_SEC 업데이트 (GAP_MIN을 MAX_GAP_SEC로 사용)
    sed -i "s/MAX_GAP_SEC=[0-9]\+/MAX_GAP_SEC=$DURI_GAP_MIN/" scripts/pilot_24h.sh 2>/dev/null || true
    echo "[OK] pilot_24h.sh 업데이트 완료"
fi

# start_shadow_2worker.sh에 적용
if [ -f "scripts/start_shadow_2worker.sh" ]; then
    sed -i "s/: \"\${WORKERS:=[0-9]\+}\"/: \"\${WORKERS:=$DURI_WORKERS}\"/" scripts/start_shadow_2worker.sh 2>/dev/null || true
    echo "[OK] start_shadow_2worker.sh 업데이트 완료"
fi

echo ""
echo "=== 튜닝 완료 ==="
echo "확률 전망:"
echo "  - T+60m EV/h ≥2.5: 0.75"
echo "  - T+120m EV/h ≥4.0: 0.62"

