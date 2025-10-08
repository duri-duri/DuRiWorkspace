#!/usr/bin/env bash
# CI: PR 게이트 (엄격 - 회귀 시 실패)
set -euo pipefail

echo "🚪 CI: PR 게이트 (엄격 - 회귀 시 실패)"

# PR 게이트 실행 (회귀 시 실패)
GUARD_STRICT=1 make pr-gate

# CI 로그 파서용 아티팩트 저장
mkdir -p artifacts
bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3 > artifacts/guard.out 2>&1 || true

echo "✅ PR 게이트 통과"
