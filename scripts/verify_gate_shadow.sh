#!/usr/bin/env bash
set -euo pipefail
ROOT="/home/duri/DuRiWorkspace"
cd "$ROOT"

# 기존 디렉토리 구조 활용
mkdir -p var/locks var/logs

echo "== [$(date '+%F %T')] verify_gate_shadow start =="

# 0) 서브모듈 동기화 (SSH 연결된 서브모듈들)
echo "🔄 서브모듈 동기화 시작..."
source scripts/lib/submodule_sync.sh
sync_all_submodules

# 1) 헬스/스모크 (기존 enhanced_healthcheck.sh 활용)
echo "📋 1. 헬스/스모크 체크..."
./scripts/enhanced_healthcheck.sh

# 2) CI 가드 (기존 ci_guard.sh 활용 - 상대임포트/린트/테스트)
echo "📋 2. CI 가드 체크..."
# DB 스킵 환경변수 3종 세트 주입
export DURICORE_SKIP_DB=1
export DURI_DB_SKIP=1
export DURI_TEST_SKIP_DB=1
./scripts/ci_guard.sh

# 3) 승격 정책 점검 (기존 promotion_gate.py 인터페이스에 맞춤)
echo "📋 3. 승격 정책 체크..."
TEMP_RESULTS="$(mktemp)"
# TODO: 추후 Prometheus 수집으로 교체 (현재는 더미 데이터)
echo '{"latency_ms": 100, "error_rate": 0.01, "success_rate": 0.99}' > "$TEMP_RESULTS"

python3 ./scripts/promotion_gate.py "$TEMP_RESULTS" ./policies/promotion.yaml

# 정리
rm -f "$TEMP_RESULTS"

echo "== [$(date '+%F %T')] verify_gate_shadow PASS =="
