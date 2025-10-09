#!/usr/bin/env bash
# promtool로 Textfile 포맷 정적 검증
set -euo pipefail
: "${LC_ALL:=C}"; export LC_ALL

IN="${1:-.reports/metrics/day66_metrics.tsv}"
OUT="/tmp/duri.prom"

echo "🔍 promtool로 Textfile 포맷 정적 검증"

# 메트릭 생성
bash scripts/metrics/export_prom.sh "$IN" > "$OUT"

# CRLF(윈도 줄끝) 감지
if grep -q $'\r' "$OUT"; then
  echo "❌ CRLF detected (\\r present). Convert to LF only." >&2
  exit 1
fi

# 텍스트파일 폭주 방지
MAX_BYTES="${MAX_PROM_SIZE:-1048576}"  # 1 MiB 기본
sz=$(wc -c < "$OUT")
if [ "$sz" -gt "$MAX_BYTES" ]; then
  echo "❌ metrics text too large: ${sz} bytes (limit=${MAX_BYTES})" >&2
  exit 1
fi

# 포맷 검사
if command -v promtool >/dev/null 2>&1; then
  echo "1. promtool 포맷 검사..."

  # GA에서만 강제, 로컬/비엄격은 스킵
  : "${GA_ENFORCE:=0}"
  if [ "$GA_ENFORCE" != "1" ]; then
    echo "ℹ️ non-GA: promtool 스킵"
  else
    # promtool 능력 탐지(진짜 동작 프로브)
    if printf '# HELP _probe dummy\n# TYPE _probe gauge\n_probe 1\n' \
       | promtool check metrics >/dev/null 2>&1; then
      # promtool stdin 개행 보증
      tail -c1 "$OUT" | read -r _ || printf '\n' >> "$OUT"
      # 파이프 실패 전파
      promtool check metrics < "$OUT" || { echo "❌ promtool check failed"; exit 1; }
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
    # PCRE → POSIX ERE
    NUM = "([+-]?(([0-9]+(\\.[0-9]*)?)|(\\.[0-9]+))([eE][+-]?[0-9]+)?|[+-]?(Inf|NaN))"
  }
  # 모든 레코드 공통 전처리: BOM/CR 제거
  { sub(/^\xEF\xBB\xBF/,"",$0); sub(/\r$/,"",$0) }

  /^# HELP /{help[$3]++}
  /^# TYPE /{type[$3]++}

  # 값 라인(라벨 有): name{...} <num>
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*\\{[^}]*\\}[[:space:]]+" NUM "$" {
    split($0,a,"{"); seen[a[1]]=1; next
  }
  # 값 라인(라벨 無): name <num>
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*[[:space:]]+" NUM "$" {
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

# HELP/TYPE 순서 보장 (샘플보다 앞)
echo "4. HELP/TYPE 순서 보장 검증..."
awk '
  # 모든 레코드 공통 전처리: BOM/CR 제거
  { sub(/^\xEF\xBB\xBF/,"",$0); sub(/\r$/,"",$0) }

  /^# HELP /{h[$3]=NR}
  /^# TYPE /{t[$3]=NR}
  /^[A-Za-z_:][A-Za-z0-9_:]*([[:space:]]|{)/{
    m=$1; sub(/\{.*/,"",m)   # 라벨 있으면 제거
    if (m in seen_first == 0) seen_first[m]=NR
  }
  END{
    bad=0
    for (m in seen_first){
      if (!(m in h)){ printf("❌ missing HELP before samples for %s\n", m) > "/dev/stderr"; bad=1 }
      if (!(m in t)){ printf("❌ missing TYPE before samples for %s\n", m) > "/dev/stderr"; bad=1 }
      if ((m in h) && seen_first[m] < h[m]){ printf("❌ HELP after samples for %s\n", m) > "/dev/stderr"; bad=1 }
      if ((m in t) && seen_first[m] < t[m]){ printf("❌ TYPE after samples for %s\n", m) > "/dev/stderr"; bad=1 }
    }
    exit bad
  }
' "$OUT" || exit 1

# 라벨 이름 규칙 + 동일 키 중복 금지
echo "5. 라벨 이름 규칙 + 중복키 검증..."
awk '
function check_labels(lbls,   i,k,seen){
  n=split(lbls, a, /,/)
  for(i=1;i<=n;i++){
    # key="value" 또는 key="" 형태
    split(a[i], kv, /=/)
    k=kv[1]
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", k)
    if (k in seen){ printf("❌ duplicate label key: %s\n", k) > "/dev/stderr"; return 1 }
    if (k !~ /^[A-Za-z_][A-Za-z0-9_]*$/){ printf("❌ invalid label name: %s\n", k) > "/dev/stderr"; return 1 }
    seen[k]=1
  }
  return 0
}
# 모든 레코드 공통 전처리: BOM/CR 제거
{ sub(/^\xEF\xBB\xBF/,"",$0); sub(/\r$/,"",$0) }

# 라벨이 있는 샘플만 검사
/^[A-Za-z_:][A-Za-z0-9_:]*\{/{
  s=$0
  sub(/^[^{]*\{/, "", s); sub(/\}[[:space:]].*$/, "", s)  # {...}만 추출
  if (check_labels(s)) { bad=1 }
}
END{ exit bad }
' "$OUT" || exit 1

# 메트릭명 정규식 검증: HELP/TYPE/샘플에 등장한 모든 name 대상
echo "6. 메트릭명 정규식 검증..."
awk '
  # 모든 레코드 공통 전처리: BOM/CR 제거
  { sub(/^\xEF\xBB\xBF/,"",$0); sub(/\r$/,"",$0) }

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
