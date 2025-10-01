#!/usr/bin/env bash
set -euo pipefail

# 진짜 중복 파일 찾기 및 정리 스크립트
ROOT="/mnt/h/ARCHIVE"
MIN_SIZE="+1G"
WORK="$ROOT/.UNWRAP/DEDUP_REAL"
mkdir -p "$WORK"

CAND="$WORK/candidates.tsv"
CAND2="$WORK/candidates.size_dups.tsv"
HASHED="$WORK/hashed.tsv"
PLAN="$WORK/plan.tsv"
LOG="$WORK/actions.log"

echo "=== 1) 후보 수집 (1GB 이상 파일) ==="
find "$ROOT" -type f -size $MIN_SIZE \
  -not -path '*/.UNWRAP/*' -not -path '*/.git/*' \
  -printf '%s\t%i\t%p\n' > "$CAND"

echo "총 후보 파일 수: $(wc -l < "$CAND")"

echo "=== 2) 같은 크기 파일들만 추려서 해시 계산량 최소화 ==="
awk -F'\t' '{c[$1]++} END{for (s in c) if (c[s]>1) print s}' "$CAND" \
  | grep -F -f - "$CAND" > "$CAND2"

echo "같은 크기 그룹 파일 수: $(wc -l < "$CAND2")"

echo "=== 3) 해시 계산 (같은 크기 후보만) ==="
: > "$HASHED"
while IFS=$'\t' read -r size inode path; do
  echo "해시 계산 중: $(basename "$path")"
  hash=$(sha256sum "$path" | awk '{print $1}')
  printf "%s\t%s\t%s\t%s\n" "$size" "$inode" "$hash" "$path" >> "$HASHED"
done < "$CAND2"

echo "=== 4) 해시 같지만 inode 다른 그룹에서 기준 파일 고르기 ==="
awk -F'\t' '
{
  key = $3 ":" $1;
  inode=$2; path=$4;
  if (!(key in canon)) {
    canon[key] = path;
  }
  if (path ~ /\/두리백업\//) canon[key] = path;
  if (seen[key, inode]++) next;
  group[key] = group[key] ? group[key] RS $0 : $0;
}
END{
  for (k in group) {
    split(group[k], arr, RS);
    if (length(arr) < 2) continue;
    base = canon[k];
    for (i in arr) {
      split(arr[i], f, "\t");
      p=f[4]; ino=f[2];
      if (!(k in baseino)) {
        cmd="stat -c %i \"" base "\"";
        cmd | getline baseino[k];
        close(cmd);
      }
      if (p != base && ino != baseino[k]) {
        print k "\t" base "\t" p;
      }
    }
  }
}' "$HASHED" > "$PLAN"

echo "=== 5) 드라이런: 실제로 무엇을 치환할지 보여주기 ==="
echo "치환 예정 건수: $(wc -l < "$PLAN")"
if [ -s "$PLAN" ]; then
  echo "처음 20개 계획:"
  head -20 "$PLAN" | sed 's/^/PLAN: /'
else
  echo "진짜 중복 파일이 없습니다!"
fi

echo "=== 6) 실행 여부 확인 ==="
RUN=0
if [ "$RUN" -eq 1 ]; then
  echo "=== 실행 시작 ===" | tee "$LOG"
  BEFORE=$(df -h /mnt/h | awk 'NR==2{print $4}')
  while IFS=$'\t' read -r key base victim; do
    rm -f -- "$victim" && ln -- "$base" "$victim" \
      && echo "[OK] LINK  base=$base  -> victim=$victim" | tee -a "$LOG" \
      || echo "[ERR] $victim" | tee -a "$LOG"
  done < "$PLAN"
  sync
  AFTER=$(df -h /mnt/h | awk 'NR==2{print $4}')
  echo "여유공간: before=$BEFORE → after=$AFTER" | tee -a "$LOG"
else
  echo "실행은 하지 않았습니다. 검토 후 아래 한 줄만 바꿔서 재실행하세요:"
  echo "sed -i 's/RUN=0/RUN=1/' find_real_duplicates.sh && ./find_real_duplicates.sh"
fi

echo "=== 완료 ==="
