#!/usr/bin/env bash
set -Eeuo pipefail

LC_ALL=C
GT="${1:-.reports/day62/ground_truth.tsv}"   # query\tcat\tpf\texpected_csv
K="${K:-3}"
SEARCH="${SEARCH:-scripts/rag_search.sh}"
RANK_FLAG="${RANK_FLAG:---rank}"

OUT="${OUT:-.reports/day62/eval_$(date +%F_%H%M).tsv}"
mkdir -p "$(dirname "$OUT")"

echo -e "query\tk\thits\tp@k\tr@k" > "$OUT"

total_q=0; sum_hits=0; sum_k=0; sum_exp=0
sum_p=0; sum_r=0

while IFS=$'\t' read -r query cat pf expected || [[ -n "${query:-}" ]]; do
  [[ -z "${query// }" ]] && continue
  [[ "${query:0:1}" == "#" ]] && continue

  E="$(mktemp)"; G="$(mktemp)"
  trap 'rm -f "$E" "$G"' RETURN

  printf "%s" "${expected:-}" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u > "$E"
  bash "$SEARCH" "$query" "${cat:-}" "${pf:-}" $RANK_FLAG --k "$K" --format ids \
    | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u > "$G"

  hits="$(comm -12 "$E" "$G" | wc -l | tr -d ' ')"
  exp_cnt="$(wc -l < "$E" | tr -d ' ')"

  p="$(awk -v h="$hits" -v k="$K" 'BEGIN{printf("%.4f", (k? h/k : 0))}')"
  r="$(awk -v h="$hits" -v e="$exp_cnt" 'BEGIN{printf("%.4f", (e? h/e : 0))}')"

  echo -e "${query}\t${K}\t${hits}\t${p}\t${r}" >> "$OUT"

  total_q=$((total_q+1))
  sum_hits=$((sum_hits+hits))
  sum_k=$((sum_k+K))
  sum_exp=$((sum_exp+exp_cnt))
  sum_p=$(awk -v a="$sum_p" -v b="$p" 'BEGIN{printf("%.6f", a + b)}')
  sum_r=$(awk -v a="$sum_r" -v b="$r" 'BEGIN{printf("%.6f", a + b)}')
done < "$GT"

micro_p="$(awk -v h="$sum_hits" -v k="$sum_k" 'BEGIN{printf("%.4f", (k? h/k:0))}')"
micro_r="$(awk -v h="$sum_hits" -v e="$sum_exp" 'BEGIN{printf("%.4f", (e? h/e:0))}')"
macro_p="$(awk -v s="$sum_p" -v n="$total_q" 'BEGIN{printf("%.4f", (n? s/n:0))}')"
macro_r="$(awk -v s="$sum_r" -v n="$total_q" 'BEGIN{printf("%.4f", (n? s/n:0))}')"

{
  echo "----"
  echo -e "queries\t${total_q}"
  echo -e "micro_p@${K}\t${micro_p}"
  echo -e "micro_r@${K}\t${micro_r}"
  echo -e "macro_p@${K}\t${macro_p}"
  echo -e "macro_r@${K}\t${macro_r}"
} >> "$OUT"

cat "$OUT"
