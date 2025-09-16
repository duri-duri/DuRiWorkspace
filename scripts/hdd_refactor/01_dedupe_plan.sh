#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/mnt/h/ARCHIVE"
META="$ROOT/META"
IN="$META/sha256_index.tsv"
PLAN="$META/DEDUPE_PLAN.jsonl"

: > "$PLAN"
# sha256 동일 + size 동일 -> 같은 파일로 간주
# 첫 번째 항목을 "대표(canonical)"로 삼고 나머지는 대표로 링크 치환
awk -F'\t' '{print $1"\t"$2"\t"$3}' "$IN" \
 | sort -k1,1 -k2,2n -k3,3 \
 | awk -F'\t' '
   BEGIN{prev=""; canon=""}
   {
     key=$1"\t"$2
     if(key!=prev){ # 새 그룹
        if(canon!=""){ canon="" }
        canon=$3; prev=key; next
     } else {
        printf("{\"sha256\":\"%s\",\"size\":%s,\"from\":\"%s\",\"to\":\"%s\"}\n",$1,$2,$3,canon)
     }
 }' >> "$PLAN"

wc -l "$PLAN"
