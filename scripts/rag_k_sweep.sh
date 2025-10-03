#!/usr/bin/env bash
set -euo pipefail

# k-스윕 유틸리티 - 여러 k값으로 한 번에 평가

GT="${1:?usage: rag_k_sweep.sh GT_TSV [k1] [k2] ... [kN]}"
shift
ks="${@:-1 3 5}"

echo "Running k-sweep: GT=$GT, k_values=[$ks]"
echo "---"

for k in $ks; do
  echo -n "k=$k: "
  K=$k bash scripts/rag_eval.sh "$GT" | awk -F'\t' -v k=$k '$1==("micro_p@" k){print "micro_p=" $2; exit}'
done
