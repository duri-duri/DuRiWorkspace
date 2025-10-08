#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

# 경로 고정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_EXTRACT="$SCRIPT_DIR/lib/extract_ids.awk"
readonly SCRIPT_DIR REPO_ROOT LIB_EXTRACT

# 추출기 존재 확인
[[ -r "$LIB_EXTRACT" ]] || { echo "❌ missing extractor: $LIB_EXTRACT" >&2; exit 1; }

# v1 호환 인자
QUERY=""; K=3; FORMAT="ids"; CAT=""; PF=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --k) K="${2:-3}"; shift 2;;
    --format) FORMAT="${2:-ids}"; shift 2;;
    ---rank|--rank) shift;;
    --cat) CAT="${2:-}"; shift 2;;
    --pf)  PF="${2:-}"; shift 2;;
    --) shift; break;;
    -*) shift;;
    *) [[ -z "$QUERY" ]] && QUERY="$1"; shift;;
  esac
done
[[ -n "$QUERY" ]] || exit 0

PRE_K="${PRE_K:-20}"
RRF_K="${RRF_K:-10}"
SYNONYMS_TSV="${SYNONYMS_TSV:-$REPO_ROOT/.reports/day64/synonyms.tsv}"

# 동의어 파일 존재 빠른 체크
[[ -n "${SYNONYMS_TSV:-}" && ! -f "$SYNONYMS_TSV" ]] && \
  echo "[warn] SYNONYMS_TSV not found: $SYNONYMS_TSV" >&2

# === DRY 추출기 (경로 고정, 중복 제거 내장) ===
extract_ids() { awk -f "$LIB_EXTRACT"; }

# 쿼리 확장
declare -a QLIST; QLIST+=("$QUERY")
if [[ -f "$SYNONYMS_TSV" ]]; then
  while IFS=$'\t' read -r k syn; do
    [[ -z "$k" || -z "$syn" ]] && continue
    [[ "$QUERY" == *"$k"* ]] && QLIST+=("${QUERY/$k/$syn}")
  done < "$SYNONYMS_TSV"
fi
declare -A SEENQ; declare -a QU
for q in "${QLIST[@]}"; do [[ -z "${SEENQ[$q]:-}" ]] && SEENQ[$q]=1 && QU+=("$q"); done

# 2단계: 쿼리 확장 + tuned + enhanced RRF
tmp="$(mktemp)"; tmp_sorted="$(mktemp)"; trap 'rm -f "$tmp" "$tmp_sorted"' EXIT

for q in "${QU[@]}"; do
  # tuned 결과 수집 (절대경로)
  { K="$PRE_K" "$SCRIPT_DIR/rag_search_tuned.sh" "$q" 2>/dev/null; } | extract_ids | head -n "$PRE_K" \
  | awk '{printf("%s\t%d\n", $0, NR)}' >> "$tmp"

  # enhanced 결과 수집 (절대경로)
  { K="$PRE_K" "$SCRIPT_DIR/rag_search_enhanced.sh" "$q" 2>/dev/null; } | extract_ids | head -n "$PRE_K" \
  | awk '{printf("%s\t%d\n", $0, NR)}' >> "$tmp"
done

# RRF 계산
if [[ -s "$tmp" ]]; then
  awk -v rrfk="$RRF_K" '{ id=$1; r=$2+0; S[id]+=1/(rrfk+r) } END{ for(id in S) printf("%.9f\t%s\n",S[id],id) }' "$tmp" \
  | LC_ALL=C sort -rg > "$tmp_sorted"
head -n "$K" "$tmp_sorted" | cut -f2
else
  # 폴백: tuned만 (절대경로)
  { K="$K" "$SCRIPT_DIR/rag_search_tuned.sh" "$QUERY" 2>/dev/null; } | awk -v MAXN="$K" -f "$LIB_EXTRACT"
fi
