#!/bin/bash
set -Eeuo pipefail
INPUT=${1:-/mnt/usb/CORE_PROTECTED/META/INDEX.full.jsonl}
OUTPUT=${2:-/mnt/usb/CORE_PROTECTED/META/INDEX.full.normalized.jsonl}

if [ ! -f "$INPUT" ]; then
  echo "❌ 입력 파일 없음: $INPUT"
  exit 1
fi

echo " 정규화 시작..."
echo "입력 파일: $INPUT"

# 정규화 실행
jq -c '{
    src: (.src // .file),
    bytes: (.bytes // .size),
    sha256: .sha256
} | select(.sha256 != null)' "$INPUT" > "$OUTPUT"

echo "✅ 정규화 완료!"
echo "출력 파일: $OUTPUT"
echo "원본 라인 수: $(wc -l < "$INPUT")"
echo "정규화 후 라인 수: $(wc -l < "$OUTPUT")"
echo "제거된 NULL 항목: $(( $(wc -l < "$INPUT") - $(wc -l < "$OUTPUT") ))"
