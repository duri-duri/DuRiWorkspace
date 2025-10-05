#!/usr/bin/env bash
set -euo pipefail

# 원클릭 FN/FP 진단 스크립트

q="${1:?usage: rag_diagnose.sh <query> [gt_file]}"
gt="${2:-.reports/day62/ground_truth_clean.tsv}"

echo "[diagnosis] Query: $q"
echo "[diagnosis] GT file: $gt"

E=$(mktemp); G=$(mktemp)
trap 'rm -f "$E" "$G"' EXIT

# Expected results
awk -F'\t' -v q="$q" '$1==q{print $4}' "$gt" | tr ',' '\n' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | LC_ALL=C sort -u > "$E"

# Search engine
: "${SEARCH:=scripts/rag_search_enhanced.sh}"
echo "[diagnosis] Search engine: $SEARCH"
"$SEARCH" "$q" | LC_ALL=C sort -u > "$G"

echo ""
echo "[FN] Misses (expected but not found):"
comm -23 "$E" "$G" | sed 's/^/  - /' || echo "  (none)"

echo ""
echo "[FP] False Positives (found but not expected):"
comm -13 "$E" "$G" | sed 's/^/  - /' || echo "  (none)"

echo ""
echo "Expected (${q}):"
[[ -s "$E" ]] && cat "$E" | sed 's/^/  - /' || echo "  (no expected results)"

echo ""
echo "Got (${q}):"
[[ -s "$G" ]] && cat "$G" | sed 's/^/  - /' || echo "  (no results)"
