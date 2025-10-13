#!/usr/bin/env bash
# CI: PR 게이트 (엄격 - 회귀 시 실패)
set -euo pipefail

echo "🚪 CI: PR 게이트 (엄격 - 회귀 시 실패)"

# CI 도구 부트스트랩 (노이즈 제로)
make ci-bootstrap-tools

# PR 게이트 실행 (회귀 시 실패)
GUARD_STRICT=1 bash scripts/pr_gate_day63.sh

# promtool 검증 (라벨 정합성 보장)
echo "🔍 promtool 검증..."
bash scripts/metrics/validate_prom.sh .reports/metrics/day66_metrics.tsv

# CI 로그 파서용 아티팩트 저장
mkdir -p artifacts
bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv 3 > artifacts/guard.out 2>&1 || true

echo "✅ PR 게이트 통과"
