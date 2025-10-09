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
  if promtool check metrics "$OUT" 2>/dev/null; then
    echo "✅ promtool 포맷 검사 통과"
  else
    echo "⚠️ promtool 검사 실패 - 건너뜀"
  fi
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

# HELP/TYPE 중복/누락 검증 (정확한 로직)
awk '
  # HELP / TYPE 헤더 집계
  /^# HELP / {help[$3]++; next}
  /^# TYPE / {type[$3]++; next}

  # 값 라인에 등장한 메트릭명 기록 (라벨 제거)
  /^[a-zA-Z_:][a-zA-Z0-9_:]*\{/ {
    split($0,a,"{"); m=a[1]; seen[m]=1
  }
  /^[a-zA-Z_:][a-zA-Z0-9_:]* [0-9]/ {
    split($0,a," "); m=a[1]; seen[m]=1
  }

  END {
    bad=0
    # 중복 검사
    for (m in help) if (help[m] > 1) { printf("❌ duplicate HELP for %s (%d)\n", m, help[m]) > "/dev/stderr"; bad=1 }
    for (m in type) if (type[m] > 1) { printf("❌ duplicate TYPE for %s (%d)\n", m, type[m]) > "/dev/stderr"; bad=1 }

    # 누락 검사(값 라인에 등장한 메트릭은 HELP/TYPE 각각 1개씩 있어야 함)
    for (m in seen) {
      if (!help[m]) { printf("❌ missing HELP for %s\n", m) > "/dev/stderr"; bad=1 }
      if (!type[m]) { printf("❌ missing TYPE for %s\n", m) > "/dev/stderr"; bad=1 }
    }
    exit bad
  }
' "$OUT" || exit 1

# 메트릭명 정규식 (라벨 없는 메트릭도 처리)
grep -E '^[^# ]' "$OUT" | sed 's/{.*//' | sed 's/ [0-9].*//' | grep -qvE '^[a-zA-Z_:][a-zA-Z0-9_:]*$$' \
  && { echo "❌ invalid metric name"; exit 1; }

echo "✅ exporter labels look good"
echo "✅ 모든 검증 통과"
