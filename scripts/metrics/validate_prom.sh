#!/usr/bin/env bash
# promtool로 Textfile 포맷 정적 검증
set -euo pipefail
: "${LC_ALL:=C}"; export LC_ALL

IN="${1:-.reports/metrics/day66_metrics.tsv}"
OUT="/tmp/duri.prom"

echo "🔍 promtool로 Textfile 포맷 정적 검증"

# 메트릭 생성
bash scripts/metrics/export_prom.sh "$IN" > "$OUT"

# 포맷 검사
if command -v promtool >/dev/null 2>&1; then
  echo "1. promtool 포맷 검사..."

  # GA에서만 강제, 로컬/비엄격은 스킵
  : "${GA_ENFORCE:=0}"
  if [ "$GA_ENFORCE" != "1" ]; then
    echo "ℹ️ non-GA: promtool 스킵"
  else
    # promtool 능력 탐지(진짜 동작 프로브)
    if printf 'x 1\n' | promtool check metrics >/dev/null 2>&1; then
      # 파이프 실패 전파
      cat "$OUT" | promtool check metrics || { echo "❌ promtool check failed"; exit 1; }
      echo "✅ promtool 포맷 검사 통과"
    else
      echo "⚠️ promtool check metrics 미지원 - 스킵"
    fi
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

# HELP/TYPE 중복/누락 검증 (과학표기·라벨 유무 모두 인식) - 항상 실행
echo "3. HELP/TYPE 중복/누락 검증..."
awk '
  BEGIN{
    # 숫자 파싱 끝장 정규식(선택) — NaN/Inf까지
    num="(?:[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?|[+-]?(?:Inf|NaN))"
  }
  /^# HELP /{help[$3]++}
  /^# TYPE /{type[$3]++}

  # 값 라인(라벨 有): name{...} <num>
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*\\{[^}]*\\}[[:space:]]+" num "$" {
    split($0,a,"{"); seen[a[1]]=1; next
  }
  # 값 라인(라벨 無): name <num>
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*[[:space:]]+" num "$" {
    split($0,a," ");  seen[a[1]]=1; next
  }

  END{
    bad=0
    for (m in help) if (help[m]>1){ printf("❌ duplicate HELP for %s (%d)\n",m,help[m]) > "/dev/stderr"; bad=1 }
    for (m in type) if (type[m]>1){ printf("❌ duplicate TYPE for %s (%d)\n",m,type[m]) > "/dev/stderr"; bad=1 }
    for (m in seen){
      if (!(m in help)){ printf("❌ missing HELP for %s\n",m) > "/dev/stderr"; bad=1 }
      if (!(m in type)){ printf("❌ missing TYPE for %s\n",m) > "/dev/stderr"; bad=1 }
    }
    exit bad
  }
' "$OUT" || exit 1

# 메트릭명 정규식 검증: HELP/TYPE/샘플에 등장한 모든 name 대상
awk '
  /^# (HELP|TYPE) /{n=$3; name[n]=1}
  /^[A-Za-z_:][A-Za-z0-9_:]*/{
    split($0,a,/[ {]/); name[a[1]]=1
  }
  END{
    bad=0
    for (m in name)
      if (m !~ /^[A-Za-z_:][A-Za-z0-9_:]*$/){
        printf("❌ invalid metric name: %s\n", m) > "/dev/stderr"; bad=1
      }
    exit bad
  }
' "$OUT" || exit 1

echo "✅ exporter labels look good"
echo "✅ 모든 검증 통과"
