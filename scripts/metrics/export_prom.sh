#!/usr/bin/env bash
set -Eeuo pipefail
IN="${1:-.reports/metrics/day66_metrics.tsv}"

hdr="$(head -1 "$IN" 2>/dev/null || true)"
[[ -z "$hdr" ]] && exit 0

# k 추출 (ndcg@3 같은 헤더에서 k를 읽음)
k="3"  # 기본값
if echo "$hdr" | grep -q "ndcg@"; then
  k="$(echo "$hdr" | grep -o "ndcg@[0-9]\+" | sed 's/ndcg@//')"
fi

cat <<EOF
# HELP duri_ndcg_at_k NDCG@k
# TYPE duri_ndcg_at_k gauge
# HELP duri_mrr Mean Reciprocal Rank
# TYPE duri_mrr gauge
# HELP duri_oracle_recall_at_k Oracle recall@k
# TYPE duri_oracle_recall_at_k gauge
EOF

# columns: scope  domain  count  ndcg@k  mrr  oracle_recall@k
awk -F'\t' -v k="$k" 'NR>1{
  gsub(/\r$/,""); # CRLF 보호
  scope=$1; domain=$2; ndcg=$4; mrr=$5; oracle=$6;
  printf "duri_ndcg_at_k{k=\"%s\",scope=\"%s\",domain=\"%s\"} %s\n", k, scope, domain, ndcg;
  printf "duri_mrr{scope=\"%s\",domain=\"%s\"} %s\n", scope, domain, mrr;
  printf "duri_oracle_recall_at_k{k=\"%s\",scope=\"%s\",domain=\"%s\"} %s\n", k, scope, domain, oracle;
}' "$IN"
