#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C

# 경로 고정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LIB_EXTRACT="$SCRIPT_DIR/lib/extract_ids.awk"
readonly SCRIPT_DIR REPO_ROOT LIB_EXTRACT

# 디버그 가독성 강화
if [[ -n "${DEBUG_RAG:-}" ]]; then
  # shellcheck source=scripts/lib/debug_trace.sh
  source scripts/lib/debug_trace.sh
  set -x
fi
# shellcheck source=scripts/lib/debug_trace.sh
source scripts/lib/debug_trace.sh

# v1 CLI: bash $SEARCH "<query>" ---rank --k N --format ids [--cat C] [--pf P]
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
    *)  [[ -z "$QUERY" ]] && QUERY="$1"; shift;;
  esac
done

# 예약 옵션을 한 번 참조해 ShellCheck SC2034 경고 제거 + 기본값 세팅
: "${FORMAT:=ids}" "${CAT:=}" "${PF:=}"

[[ -n "$QUERY" ]] || exit 0

# repo-root에서 tuned 실행 (CWD 독립성 확보) + 조건부 에러 숨김
if [[ -n "${DEBUG_RAG:-}" ]]; then
  ( cd "$REPO_ROOT" && K="$K" "$SCRIPT_DIR/rag_search_tuned.sh" "$QUERY" ) \
    | awk -v MAXN="$K" -f "$LIB_EXTRACT"
else
  ( cd "$REPO_ROOT" && K="$K" "$SCRIPT_DIR/rag_search_tuned.sh" "$QUERY" ${RAG_QUIET:+2>/dev/null} ) \
    | awk -v MAXN="$K" -f "$LIB_EXTRACT"
fi
