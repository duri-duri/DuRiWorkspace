#!/usr/bin/env bash
set -euo pipefail

echo "🧪 결정론 스모크 테스트"
out1="$(scripts/rag_search_fusion.sh '요통' ---rank --k 3 --format ids)"
out2="$(scripts/rag_search_fusion.sh '요통' ---rank --k 3 --format ids)"
if diff -u <(printf "%s" "$out1") <(printf "%s" "$out2") >/dev/null; then
  echo "✅ 결정론: 동일 쿼리 2회 결과 일치"
else
  echo "❌ 결정론: 동일 쿼리 2회 결과 불일치"
  exit 1
fi
