#!/usr/bin/env bash
set -euo pipefail
echo "🧪 CWD 독립성 스모크"
REPO_ROOT="${REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

tmp="$(mktemp -d)"
(
  cd "$tmp"
  # 임의 CWD에서 실행
  bash "$REPO_ROOT/scripts/metrics/export_prom.sh" "$REPO_ROOT/.reports/metrics/day66_metrics.tsv" >/dev/null
  bash "$REPO_ROOT/scripts/alerts/threshold_guard.sh" "$REPO_ROOT/.reports/metrics/day66_metrics.tsv" 3 >/dev/null
)
echo "✅ CWD-safe"
