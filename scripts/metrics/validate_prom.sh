#!/usr/bin/env bash
# promtool로 Textfile 포맷 정적 검증
set -euo pipefail

IN="${1:-.reports/metrics/day66_metrics.tsv}"
OUT="/tmp/duri.prom"

echo "🔍 promtool로 Textfile 포맷 정적 검증"

# 메트릭 생성
bash scripts/metrics/export_prom.sh "$IN" > "$OUT"

# 포맷 검사
if command -v promtool >/dev/null 2>&1; then
  echo "1. promtool 포맷 검사..."
  promtool check metrics "$OUT"
  echo "✅ promtool 포맷 검사 통과"
else
  echo "⚠️ promtool 없음 - 포맷 검사 건너뜀"
fi

# 추가 스모크: k 라벨에 콤마가 끼었는지, domain이 '-' 그대로인지
echo "2. 라벨 정규화 검사..."
if grep -q 'k="[^"]*,' "$OUT"; then
  echo "❌ k label ends with comma"
  exit 1
fi

if grep -q 'domain="-"' "$OUT"; then
  echo "❌ domain is raw '-'"
  exit 1
fi

# guard 도메인은 반드시 ALL (긍정 매치로 강제)
if ! grep -q 'duri_guard_last_exit_code{[^}]*domain="ALL"' "$OUT"; then
  echo "❌ guard domain must be ALL"
  exit 1
fi

# guard 라인 중복 방지(있다면 정확히 1줄이어야 함)
guard_count=$(grep -c '^duri_guard_last_exit_code{' "$OUT")
if [ "$guard_count" -ne 1 ]; then
  echo "❌ guard metric should appear exactly once, found $guard_count"
  exit 1
fi

# MRR 라벨 정책 검증 (k 라벨 없어야 함)
if grep -Eq '^duri_mrr\{[^}]*k=' "$OUT"; then
  echo "❌ duri_mrr must not have k label" >&2
  exit 1
fi

echo "✅ exporter labels look good"
echo "✅ 모든 검증 통과"
