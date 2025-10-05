#!/usr/bin/env bash
set -euo pipefail

# 부스팅 규칙 파일 린터

file="${1:-data/boost_rules.tsv}"

echo "Linting boost rules: $file"
awk -F'\t' '
  NF != 3 {print "ERROR: bad columns (expected 3):", $0; exit 2}
  {
    query=$1; weight=$2; pattern=$3
    if(weight !~ /^[+-]?[0-9]+(\.[0-9]+)?$/) {
      print "ERROR: bad weight format:", $0; exit 3
    }
    if(query == "" || pattern == "") {
      print "ERROR: empty query or pattern:", $0; exit 4
    }
    count++
  }
  END {
    print "OK: rules lint passed (" count " rules)"
  }
' "$file"

echo ""
echo "Linting blocklist: data/blocklist.regex"
# 블록리스트 정규식 검증
grep -nP '\s$|\t' data/blocklist.regex && { echo "[blocklist] trailing ws/tab"; exit 5; } || true
blocklist_count=$(awk 'length($0)>0 && $0 !~ /^[#[:space:]]*$/ {c++} END{print c+0}' data/blocklist.regex)
echo "OK: blocklist lines: $blocklist_count"
