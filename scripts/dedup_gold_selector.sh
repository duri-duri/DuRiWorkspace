#!/bin/bash
INPUT=${1:-/mnt/usb/CORE_PROTECTED/META/INDEX.full.normalized.jsonl}
OUTPUT_DIR=${2:-/mnt/usb/CORE_PROTECTED/META}

if [ ! -f "$INPUT" ]; then
  echo "❌ 정규화된 INDEX 파일 없음: $INPUT"
  exit 1
fi

echo " Dedup 및 GOLD 선택 시작..."

# 1. 중복 탐지
echo " 중복 파일 분석..."
jq -s '
  group_by(.sha256) |
  map(select(.[0].sha256 != null and length > 1)) |
  map({
    sha256: .[0].sha256,
    count: length,
    keep: (max_by(.bytes) | .src),
    dups: (map(.src) - [(max_by(.bytes) | .src)])
  })
' "$INPUT" > "$OUTPUT_DIR/REPORT.dedup.json"

# 2. GOLD 선택 (일자별 최고 품질)
echo "🏆 GOLD 백업 선택..."
jq -s '
  [.[] | 
    (.src | capture("(?<day>\\d{4}-\\d{2}-\\d{2}).*__(?<hm>\\d{4})")) as $t |
    {day: $t.day, hm: ($t.hm | tonumber), bytes, src}
  ] |
  group_by(.day) |
  map({
    day: .[0].day,
    gold: (max_by(.hm * 1000000000 + .bytes) | .src),
    size: (max_by(.hm * 1000000000 + .bytes) | .bytes)
  })
' "$INPUT" > "$OUTPUT_DIR/REPORT.gold.json"

echo "✅ Dedup 및 GOLD 선택 완료!"
echo "📁 생성된 파일들:"
echo "  - REPORT.dedup.json"
echo "  - REPORT.gold.json"
