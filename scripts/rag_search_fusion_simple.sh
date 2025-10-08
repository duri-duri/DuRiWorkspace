#!/usr/bin/env bash
set -euo pipefail

# stderr 출력 제거한 간단한 RRF fusion
QUERY="${1:-}"
K="${K:-3}"

# 매개변수 파싱 (rag_eval.sh 호환)
while [[ $# -gt 0 ]]; do
  case "$1" in
    --k) K="$2"; shift 2;;
    --format) FORMAT="$2"; shift 2;;
    --rank) RANK=1; shift;;
    --cat) CAT="$2"; shift 2;;
    --pf) PF="$2"; shift 2;;
    *) shift;;
  esac
done

# tuned 스크립트에서 ID만 추출 (stderr 출력 없이)
K="$K" scripts/rag_search_tuned.sh "$QUERY" 2>/dev/null | \
sed -n 's/^📄[[:space:]]*\([^:]*\):.*/\1/p' | \
head -n "$K"
