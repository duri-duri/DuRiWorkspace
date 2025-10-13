#!/usr/bin/env bash
set -Eeuo pipefail

want="${1:-${RUN_PATH:-}}"

is_tsv() {
  local f="$1"
  [[ -s "$f" ]] || return 1
  local header
  header=$(head -n1 "$f" 2>/dev/null || true)
  [[ -n "$header" ]] || return 1

  # 필수 컬럼들이 모두 있는지 확인
  echo "$header" | grep -q -w "query_id" || return 1
  echo "$header" | grep -q -w "domain" || return 1
  echo "$header" | grep -q -w "rank" || return 1
  echo "$header" | grep -q -w "is_correct" || return 1
  return 0
}

pick_latest_run() {
  local base="$1"
  ls -1t "$base"/run_*.tsv 2>/dev/null | head -1 || true
}

candidates=()
# 우선순위: 명시된 경로 → day66 LATEST → day66 최신 run_* → day64 LATEST → day64 최신 run_*
[[ -n "${want:-}" ]] && candidates+=("$want")
candidates+=(".reports/train/day66/LATEST.tsv")
candidates+=("$(pick_latest_run .reports/train/day66)")
candidates+=(".reports/train/day64/LATEST.tsv")
candidates+=("$(pick_latest_run .reports/train/day64)")

for c in "${candidates[@]}"; do
  [[ -n "${c:-}" && -e "$c" ]] || continue
  if is_tsv "$c"; then
    readlink -f "$c"
    exit 0
  fi
done

echo "[err] could not resolve a valid TSV dataset. Checked:" >&2
printf '  - %s\n' "${candidates[@]}" >&2
exit 2
