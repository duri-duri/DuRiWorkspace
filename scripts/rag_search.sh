#!/usr/bin/env bash
set -euo pipefail

# 간단한 RAG 검색 스크립트 (find + grep + jq)
# 사용법: bash scripts/rag_search.sh "검색어" [카테고리] [환자용여부]

query="${1:-}"
category="${2:-}"
patient_facing="${3:-}"

if [ -z "$query" ]; then
  echo "사용법: $0 '검색어' [카테고리] [patient_facing:true/false]"
  echo "예시: $0 '요통' 'intake' 'false'"
  exit 1
fi

echo "🔍 RAG 검색: '$query'"
if [ -n "$category" ]; then echo "   카테고리: $category"; fi
if [ -n "$patient_facing" ]; then echo "   환자용: $patient_facing"; fi
echo ""

# find + grep으로 검색 후 jq로 필터링
find rag/ -name "*.jsonl" -exec grep -l "$query" {} \; | while read -r file; do
  while IFS= read -r line; do
    # JSON 파싱 및 검색어 매칭
    if echo "$line" | jq -e "select(.title | test(\"$query\"; \"i\")) or
                            select(.body | test(\"$query\"; \"i\")) or
                            select(.bullets[]? | test(\"$query\"; \"i\")) or
                            select(.tags[]? | test(\"$query\"; \"i\"))" >/dev/null 2>&1; then

      # 추가 필터 적용
      if [ -n "$category" ]; then
        if ! echo "$line" | jq -e "select(.category == \"$category\")" >/dev/null 2>&1; then
          continue
        fi
      fi

      if [ -n "$patient_facing" ]; then
        if ! echo "$line" | jq -e "select(.patient_facing == $patient_facing)" >/dev/null 2>&1; then
          continue
        fi
      fi

      # 결과 출력
      echo "📄 $(echo "$line" | jq -r '.id'): $(echo "$line" | jq -r '.title')"
      echo "   카테고리: $(echo "$line" | jq -r '.category')"
      echo "   환자용: $(echo "$line" | jq -r '.patient_facing')"
      echo "   내용: $(echo "$line" | jq -r '.body' | head -c 100)..."
      echo ""
    fi
  done < "$file"
done
