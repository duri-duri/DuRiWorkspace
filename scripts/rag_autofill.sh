#!/usr/bin/env bash
set -euo pipefail

# 공통 상수 로드
source "$(dirname "$0")/_rag_constants.sh"
tmp="$(mktemp)"
while IFS= read -r -d '' f; do
  : > "$tmp"
  while IFS= read -r line; do
    j="$line"
    cat="$(jq -r '.category // empty' <<<"$j")"
    id="$(jq -r '.id // empty' <<<"$j")"
    body="$(jq -r '.body // ""' <<<"$j")"
    if [ -z "$cat" ]; then echo "$j" >> "$tmp"; continue; fi
    min="${MIN_LEN[$cat]:-$MIN_LEN_DEFAULT}"
    len="$(printf "%s" "$body" | wc -m)"
    if (( len < min )); then
      pad="${PAD_TEXT[$cat]:- }"
      # triage.*는 policy라도 triage 톤으로 오버라이드
      if [[ "$id" == triage.* ]]; then pad="${PAD_TEXT[triage]}"; fi
      need=$((min - len))

      add=""
      while (( ${#add} < need )); do
        chunk="${pad:0:$((need - ${#add}))}"
        # pad가 need보다 짧으면 여러 번 이어붙음
        add="$add$chunk"
        # pad가 너무 짧으면 반복해서 누적 (보수적)
        if [[ -z "$chunk" ]]; then add="$add$pad"; fi
      done
      j="$(jq --arg add " $add" '.body = (.body // "" + $add)' <<<"$j")"
    fi
    echo "$j" >> "$tmp"
  done < "$f"
  mv "$tmp" "$f"
done < <(find rag/ -name "*.jsonl" -print0)
