#!/usr/bin/env bash
# 하드닝 #6: 라운딩/시드 정책 고정 테스트
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 라운딩/시드 정책 고정 테스트 ==="
echo ""

export DURI_AB_ROUND=1e-6
export DURI_AB_SEED_MODE=ev_ts

echo "[INFO] 환경변수 설정:"
echo "  DURI_AB_ROUND=$DURI_AB_ROUND"
echo "  DURI_AB_SEED_MODE=$DURI_AB_SEED_MODE"
echo ""

# 프로듀서 스키마 계약 테스트 실행
if bash tests/test_producer_schema.sh 2>&1 | tail -3; then
    echo "[OK] 라운딩/시드 정책 테스트 통과"
else
    echo "[FAIL] 라운딩/시드 정책 테스트 실패"
    exit 1
fi

echo ""

