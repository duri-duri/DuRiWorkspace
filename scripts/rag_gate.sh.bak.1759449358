#!/usr/bin/env bash
set -Eeuo pipefail
LC_ALL=C

GT="${1:-.reports/day62/ground_truth.tsv}"
K="${K:-3}"
THRESH_P="${THRESH_P:-0.70}"
THRESH_R="${THRESH_R:-}"

TMP="$(mktemp)"; trap 'rm -f "$TMP"' EXIT
bash scripts/rag_eval.sh "$GT" > "$TMP"

mp="$(awk -F'\t' '$1 ~ /^micro_p@/ {print $2}' "$TMP" | tail -n1)"
mr="$(awk -F'\t' '$1 ~ /^micro_r@/ {print $2}' "$TMP" | tail -n1)"

echo "[gate] micro_p@${K}=${mp} (threshold=${THRESH_P})"
[[ -n "$THRESH_R" ]] && echo "[gate] micro_r@${K}=${mr} (threshold=${THRESH_R})"

awk -v mp="$mp" -v th="$THRESH_P" 'BEGIN{ if( (mp+0) < (th+0) ) exit 1 }'
if [[ -n "$THRESH_R" ]]; then
  awk -v mr="$mr" -v th="$THRESH_R" 'BEGIN{ if( (mr+0) < (th+0) ) exit 1 }'
fi
