#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${LOG_FILE:-.reports/day62/search_history.tsv}"
SEARCH_SCRIPT="scripts/rag_search_day62_final.sh"

echo "📝 RAG 검색 로그 시스템 (Day 62)"
echo "로그 파일: $LOG_FILE"
echo

# 로그 파일 초기화
mkdir -p "$(dirname "$LOG_FILE")"
[[ -f "$LOG_FILE" ]] || printf "timestamp\tquery\tcat\tpf\tk\tranking\thit_ids\tcount\n" > "$LOG_FILE"

# 테스트 검색 실행 및 로깅
echo "🔍 테스트 검색 실행..."

queries=("요통" "경부" "어깨" "레드플래그" "스테로이드")

for query in "${queries[@]}"; do
  echo "  📋 검색: '$query'..."

  # 검색 실행
  timestamp="$(date --iso-8601=seconds 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)"
  results=$(bash "$SEARCH_SCRIPT" "$query" "" "" "3" "1" 2>/dev/null || echo "")

  if [[ -n "$results" ]]; then
    hit_ids=$(echo "$results" | grep "📄 " | sed 's/📄 \([^: (]*\).*/\1/' | tr '\n' ',' | sed 's/,$//')
    hit_count=$(echo "$results" | grep "📄 " | wc -l)
  else
    hit_ids=""
    hit_count=0
  fi

  # 로그 기록
  printf "%s\t%s\t\t\ttrue\t3\t1\t%s\t%d\n" "$timestamp" "$query" "$hit_ids" "$hit_count" >> "$LOG_FILE"

  echo "    📝 기록: hits=${hit_count}, ids=${hit_ids}"
done

echo
echo "📊 로그 분석 결과:"

# 상위 쿼리 분석
echo "🔥 가장 많이 검색된 쿼리 TOP 3:"
tail -n +2 "$LOG_FILE" | sort | uniq -c | sort -nr | head -3 | while read count query; do
  echo "  $count회: $query"
done

# 무결과 쿼리 체크
echo
echo "🚫 무결과 쿼리:"
awk -F'\t' '$NF == 0 {print $2}' "$LOG_FILE" | tail -n +2 | sort | uniq -c | sort -nr

echo
echo "📝 전체 로그 (최근 10개):"
tail -10 "$LOG_FILE" | column -t -s$'\t'
