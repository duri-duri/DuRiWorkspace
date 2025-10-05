#!/usr/bin/env bash
set -euo pipefail

# 드리프트 감시 스트립트 - 두 JSONL 파일의 micro_p 비교

if [[ $# -ne 2 ]]; then
  echo "Usage: $(basename "$0") <jsonl_a> <jsonl_b>" >&2
  exit 1
fi

a="$1"; b="$2"

# JSONL 파일 유무 확인
for file in "$a" "$b"; do
  [[ -f "$file" ]] || { echo "File not found: $file" >&2; exit 2; }
done

# micro_p 추출
mp_a=$(tail -1 "$a" | jq -r .micro_p)
mp_b=$(tail -1 "$b" | jq -r .micro_p)

# 드리프트 계산 및 출력
diff=$(awk -v x="$mp_a" -v y="$mp_b" 'BEGIN{printf "%.4f", x-y}')
printf "Δ micro_p = %+0.4f (new=%0.4f, old=%0.4f)\n" "$diff" "$mp_a" "$mp_b"

# 임계값 체크 (경고)
threshold=0.05
if (( $(echo "$diff > $threshold || $diff < -$threshold" | bc -l) )); then
  echo "⚠️  WARNING: Significant drift detected (>±${threshold})"
fi
