#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/mnt/h/ARCHIVE"
REPORT="$ROOT/reports/verify_$(date +%F_%H%M).md"
: > "$REPORT"

echo "## HASH verify" | tee -a "$REPORT"
# 1) .sha256 파일이 있는 항목은 openssl/sha256sum으로 즉시 검증
find "$ROOT" -type f -name "*.sha256" -printf "%h/%f\n" | while read -r sf; do
  f="${sf%.sha256}"
  [[ -f "$f" ]] || { echo "MISSING: $f" | tee -a "$REPORT"; continue; }
  v1=$(awk '{print $1}' "$sf")
  v2=$(sha256sum "$f" | awk '{print $1}')
  if [[ "$v1" == "$v2" ]]; then echo "OK  $f" | tee -a "$REPORT"; else echo "FAIL $f" | tee -a "$REPORT"; fi
done

echo -e "\n## LINK sanity (same inode if deduped)" | tee -a "$REPORT"
# 2) DEDUPE 샘플 검사: 같은 sha256 그룹 1~2개 무작위 추출해 inode 비교
META="$ROOT/META/sha256_index.tsv"
awk -F'\t' '{print $1"\t"$3}' "$META" | sort -k1,1 | awk -F'\t' '
  NR==1{prev=$1; paths=$2; next}
  {
    if($1==prev){ paths=paths"||"$2 }
    else { if(paths~/\|\|/){ print prev"\t"paths } prev=$1; paths=$2 }
  }
' | head -20 | while IFS=$'\t' read -r _ pls; do
  a=$(echo "$pls" | cut -d'|' -f1-1); b=$(echo "$pls" | cut -d'|' -f3-3)
  [[ -f "$a" && -f "$b" ]] || continue
  ia=$(stat -c%i "$a"); ib=$(stat -c%i "$b")
  if [[ "$ia" == "$ib" ]]; then echo "OK  inode same: $a == $b" | tee -a "$REPORT"
  else echo "WARN inode differ: $a != $b" | tee -a "$REPORT"; fi
done
