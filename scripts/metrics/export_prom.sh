#!/usr/bin/env bash
set -Eeuo pipefail
IN="${1:-.reports/metrics/day66_metrics.tsv}"

# 라벨 정규화 함수들
sanitize_label() {
  local s="$1"
  # '-' → ALL, 그 외 비문자는 '_' 로
  [ "$s" = "-" ] && echo "ALL" && return 0
  printf '%s' "$s" | sed 's/[^A-Za-z0-9_]/_/g'
}

sanitize_k() {
  # 숫자만 통과
  printf '%s' "$1" | tr -cd '0-9'
}

hdr="$(head -1 "$IN" 2>/dev/null || true)"
[[ -z "$hdr" ]] && exit 0

# k 추출 (ndcg@3 같은 헤더에서 k를 읽음)
k="3"  # 기본값
if echo "$hdr" | grep -q "ndcg@"; then
  k="$(echo "$hdr" | grep -o "ndcg@[0-9]\+" | sed 's/ndcg@//')"
fi
: "${k:=3}"   # set -u에서도 안전

cat <<EOF
# HELP duri_ndcg_at_k NDCG@k
# TYPE duri_ndcg_at_k gauge
# HELP duri_mrr Mean Reciprocal Rank
# TYPE duri_mrr gauge
# HELP duri_oracle_recall_at_k Oracle recall@k
# TYPE duri_oracle_recall_at_k gauge
# HELP duri_guard_last_exit_code Guard script last exit code (0 ok, 1 infra, 2 regression)
# TYPE duri_guard_last_exit_code gauge
EOF

# columns: scope  domain  count  ndcg@k  mrr  oracle_recall@k
awk -F'\t' -v k="$k" 'NR>1{
  gsub(/\r$/,""); # CRLF 보호
  scope=$1; domain=$2; ndcg=$4; mrr=$5; oracle=$6;

  # 라벨 정규화
  if(domain == "-") dom = "ALL"; else dom = domain; gsub(/[^A-Za-z0-9_]/, "_", dom);
  if(scope == "-") sc = "ALL"; else sc = scope; gsub(/[^A-Za-z0-9_]/, "_", sc);
  kk = k; gsub(/[^0-9]/, "", kk);

  printf "duri_ndcg_at_k{k=\"%s\",scope=\"%s\",domain=\"%s\"} %s\n", kk, sc, dom, ndcg;
  printf "duri_mrr{scope=\"%s\",domain=\"%s\"} %s\n", sc, dom, mrr;
  printf "duri_oracle_recall_at_k{k=\"%s\",scope=\"%s\",domain=\"%s\"} %s\n", kk, sc, dom, oracle;
}' "$IN"

# 마지막 가드 exit 코드 (회귀 발생 시 2로 갱신)
guard_exit_code=0
if [[ -f ".reports/metrics/day66_metrics.tsv" ]]; then
  # 가드 실행하여 exit 코드 확인
  bash scripts/alerts/threshold_guard.sh .reports/metrics/day66_metrics.tsv "$k" >/dev/null 2>&1 || guard_exit_code=$?
fi

# guard 메트릭: 라벨 순서(k, scope, domain)를 다른 메트릭과 맞춰 가독성 ↑
# guard는 "전체 집계"를 대표 → domain은 항상 "ALL"이 명확
printf "duri_guard_last_exit_code{k=\"%s\",scope=\"all\",domain=\"ALL\"} %d\n" "$k" "$guard_exit_code"
