#!/usr/bin/env bash
set -Eeuo pipefail

IN="${1:-.reports/train/day64/LATEST.tsv}"
OUT=".reports/metrics/day66_hygiene.tsv"
mkdir -p .reports/metrics

printf "check\tresult\tinfo\n" > "$OUT"

# 1) 파일 존재
if [[ ! -s "$IN" ]]; then
  printf "source_exists\tFAIL\t%s not found or empty\n" "$IN" >> "$OUT"
  exit 1
fi
printf "source_exists\tOK\tfound\n" >> "$OUT"

# 2) 필수 컬럼
header="$(head -1 "$IN" | sed '1s/^\xEF\xBB\xBF//' | tr -d '\r' || true)"
for col in query_id domain rank is_correct; do
  grep -q -w "$col" <<<"$header" || { printf "columns\tFAIL\tmissing_required\n" >> "$OUT"; exit 2; }
done
printf "columns\tOK\tall_present\n" >> "$OUT"

# 3) (query_id,rank) 중복
dups=$(awk -F'\t' 'NR>1{k=$1 FS $3; c[k]++} END{for(k in c) if(c[k]>1) d++; print 0+d}' "$IN")
if (( dups>0 )); then
  printf "dup.query_rank\tFAIL\t%d duplicates\n" "$dups" >> "$OUT"
else
  printf "dup.query_rank\tOK\tno-dup\n" >> "$OUT"
fi

# 4) domain 누락/unknown
unk=$(awk -F'\t' 'NR>1{if($2==""||$2=="unknown") c++} END{print c+0}' "$IN")
if (( unk>0 )); then
  printf "domain.missing\tWARN\t%d rows\n" "$unk" >> "$OUT"
else
  printf "domain.missing\tOK\t0\n" >> "$OUT"
fi

# 5) is_correct 값 검증
bad=$(awk -F'\t' 'NR>1{if($4 !~ /^(0|1|true|false|True|False)$/) c++} END{print c+0}' "$IN")
if (( bad>0 )); then
  printf "label.valid\tFAIL\t%d bad labels\n" "$bad" >> "$OUT"
else
  printf "label.valid\tOK\tall_valid\n" >> "$OUT"
fi

echo "[hygiene] report written to $OUT"
