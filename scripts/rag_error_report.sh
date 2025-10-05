#!/usr/bin/env bash
set -euo pipefail

# --- Locale guard: ko_KR 없어도 경고 안 나게 고정 ---
if locale -a 2>/dev/null | grep -qi '^c\.utf-8$'; then
  export LC_ALL=C.UTF-8 LANG=C.UTF-8
else
  export LC_ALL=C LANG=C
fi

GT="${1:-.reports/day62/ground_truth_clean.tsv}"
K="${K:-3}"
SEARCH_SCRIPT="${SEARCH:-scripts/rag_search.sh}"

printf "query\tFN_count\tFP_count\n"

# FD로 안전 파싱 (+ CR 제거)
exec 3<"$GT"
IFS= read -r _header <&3 || true
while IFS= read -r line <&3 || [[ -n "${line:-}" ]]; do
  line=${line%$'\r'}
  [[ -z "${line//[[:space:]]/}" ]] && continue

  q=$(printf '%s' "$line" | cut -f1)
  gold_csv=$(printf '%s' "$line" | cut -f4)

  E=$(mktemp); G=$(mktemp)
  printf '%s\n' "$gold_csv" \
    | tr ',' '\n' \
    | sed -E 's/^[[:space:]]+|[[:space:]]+$//g;/^$/d' \
    | LC_ALL=C sort -u > "$E"

  "$SEARCH_SCRIPT" "$q" --rank --k "$K" --format ids 2>/dev/null \
    | LC_ALL=C sort -u > "$G" || : >"$G"

  fn=$(comm -23 "$E" "$G" | wc -l | tr -d ' ')
  fp=$(comm -13 "$E" "$G" | wc -l | tr -d ' ')
  printf "%s\t%s\t%s\n" "$q" "$fn" "$fp"

  rm -f "$E" "$G"
done
exec 3<&-
