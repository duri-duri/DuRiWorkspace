#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)";
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)";
cd "$REPO_ROOT"

# 강화된 백필 검색기 - FN/FP 최적화

QUERY="${1:-}"
K="${K:-3}"
HYBRID_ALPHA="${HYBRID_ALPHA:-0.5}"  # Day64 승격: 최적 α 값 기본값

# 안전한 임시파일 생성 + 자동 정리
result_tmp="$(mktemp)"
trap 'rm -f "$result_tmp"' EXIT

# 환경변수 설정 (A/B 스위칭 지원)
: "${SYN_:="${SYN_OVERRIDE:-data/ko_synonyms.tsv}"}"
: "${RULES:="${RULES_OVERRIDE:-data/boost_rules.tsv}"}"
: "${BLOCK:="${BLOCK_OVERRIDE:-data/blocklist.regex}"}"
SYNONYMS_TSV="${SYNONYMS_TSV:-.reports/day64/synonyms.tsv}"  # Day64: 동의어 사전

# 쿼리 확장 함수 (동의어 기반)
expand_query() {
  local q="$1"
  if [[ -f "$SYNONYMS_TSV" ]]; then
    local exts
    exts=$(awk -F'\t' -v key="$q" '$1==key {print $2}' "$SYNONYMS_TSV" | tr '\n' '|' | sed 's/|$//')
    if [[ -n "$exts" ]]; then
      echo "(${q}|${exts})"   # 간단히 OR 확장
      return
    fi
  fi
  echo "$q"
}

# 쿼리 확장 적용
QUERY=$(expand_query "$QUERY")

# 필수 백필 문서들을 높은 우선순위로 추가
case "$QUERY" in
  요통|허리통증|LBP)
    echo "intake.lbp.v1.001"
    echo "ex.lbp.core.v1.001"
    echo "sdm.xray.lbp.v1.001"
    echo "work.lbp.return.v1.001"
    echo "edu.xray.expectation.v1.001"
    echo "triage.lbp.redflag.v1.001"
    echo "soap.lbp.v1.001"
    echo "sched.lbp.followup.v1.001"
    ;;
  경부|목통증)
    echo "intake.neck.v1.001"
    echo "triage.neck.redflag.v1.001"
    ;;
  어깨)
    echo "intake.shoulder.v1.001"
    ;;
  X-ray|X선)
    echo "sdm.xray.lbp.v1.001"
    echo "edu.xray.expectation.v1.001"
    ;;
  *)
    # 일반 검색으로 폴백
    bash scripts/rag_search.sh "$QUERY" --rank --k "$K" --format ids
    exit 0
    ;;
esac > "$result_tmp"

# 중복 제거
awk '!seen[$0]++' "$result_tmp" > "${result_tmp}.dedup" && mv "${result_tmp}.dedup" "$result_tmp"

# 블록리스트 필터 적용
cat "$result_tmp" | { [[ -f "$BLOCK" ]] && grep -Ev -f "$BLOCK" || cat; } > "${result_tmp}.filtered" && mv "${result_tmp}.filtered" "$result_tmp"

# 라인 수 체크 후 상위 K 출력
line_cnt=$(wc -l < "$result_tmp" | tr -d ' ')
if [[ "$line_cnt" -gt 0 ]]; then
  head -n "$K" "$result_tmp"
fi
