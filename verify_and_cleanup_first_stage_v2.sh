#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

# ===== 설정 =====
MOUNT="/mnt/h"  # 4TB HDD 마운트 지점 (1차 압축이 있는 곳)
ARCHIVE_PAT='\( -name "*.tar.zst" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar" \)'

EXTRACT_ROOTS=(
  "__SELF__"                             # 아카이브와 같은 폴더의 동명 디렉터리
  "$MOUNT/ARCHIVE/.UNWRAP/extracted"     # 네가 쓰던 스테이지 경로
)

DRYRUN=1          # 1: 시뮬레이션(이동하지 않음), 0: 실제 .TRASH로 이동
SAMPLE=12         # 내용 샘플 해시 대조 개수 (0 이면 목록 대조만)
TRASH="$MOUNT/.TRASH"

tar_list() {  # 아카이브 파일 목록(파일만)
  local arc="$1"
  case "$arc" in
    *.zst)  zstd -dc --long=31 -- "$arc" | tar -tf - ;;
    *.gz)   gzip -dc -- "$arc"   | tar -tf - ;;
    *.tgz)  gzip -dc -- "$arc"   | tar -tf - ;;
    *.tar)  tar -tf -- "$arc" ;;
    *)      echo "지원하지 않는 형식: $arc" >&2; return 2 ;;
  esac | sed 's#^\./##' | grep -v '/$'
}

tar_cat() {   # 아카이브에서 단일 파일의 바이트 스트림 추출
  local arc="$1" rel="$2"
  case "$arc" in
    *.zst)  zstd -dc --long=31 -- "$arc" | tar -xO -f - -- "$rel" ;;
    *.gz|*.tgz) gzip -dc -- "$arc"      | tar -xO -f - -- "$rel" ;;
    *.tar)  tar -xO -f "$arc" -- "$rel" ;;
  esac
}

detect_dest_dir() {  # 동명 추출 디렉터리 탐색
  local arc="$1" arcdir base filename
  arcdir=$(dirname -- "$arc")
  filename=$(basename -- "$arc")
  base="$filename"; base="${base%.zst}"; base="${base%.gz}"; base="${base%.tgz}"; base="${base%.tar}"

  if [[ " ${EXTRACT_ROOTS[*]} " == *" __SELF__ "* ]] && [[ -d "$arcdir/$base" ]]; then
    printf '%s\n' "$arcdir/$base"; return 0
  fi
  for root in "${EXTRACT_ROOTS[@]}"; do
    [[ "$root" == "__SELF__" ]] && continue
    if [[ -d "$root/$base" ]]; then printf '%s\n' "$root/$base"; return 0; fi
  done
  return 1
}

move_to_trash() {
  local p="$1"
  mkdir -p -- "$TRASH"
  if (( DRYRUN )); then
    echo "[DRYRUN] → .TRASH 이동 예정: $p"
  else
    mv -vn -- "$p" "$TRASH/"
  fi
}

ok_cnt=0 ; skip_cnt=0 ; bytes_sum=0

while IFS= read -r -d '' arc; do
  dest=""
  if ! dest=$(detect_dest_dir "$arc"); then
    echo "[-] 추출 디렉터리 미발견 → 보류: $arc"
    ((skip_cnt++))
    continue
  fi

  echo "[*] 검증 시작"
  echo "    ARC : $arc"
  echo "    DEST: $dest"

  # 1) 목록 대조
  a_list=$(mktemp) ; b_list=$(mktemp)
  trap 'rm -f "$a_list" "$b_list"' RETURN

  if ! tar_list "$arc" | LC_ALL=C sort -u >"$a_list"; then
    echo "[!] 아카이브 목록 읽기 실패 → 보류"
    ((skip_cnt++)); continue
  fi
  ( cd "$dest" && find . -type f -printf '%P\n' | LC_ALL=C sort -u ) >"$b_list"

  if ! diff -u "$a_list" "$b_list" >/dev/null; then
    echo "[!] 파일 목록 불일치 → 보류"
    ((skip_cnt++)); continue
  fi

  # 2) 내용 샘플 해시 대조(옵션)
  if (( SAMPLE > 0 )); then
    mapfile -t samples < <(shuf -n "$SAMPLE" "$a_list" 2>/dev/null || head -n "$SAMPLE" "$a_list")
    mismatch=0
    for rel in "${samples[@]}"; do
      if ! a_hash=$(tar_cat "$arc" "$rel" | sha256sum | awk '{print $1}'); then
        echo "[!] 샘플 추출 실패: $rel" ; mismatch=1 ; break
      fi
      if ! b_hash=$(sha256sum -- "$dest/$rel" | awk '{print $1}'); then
        echo "[!] 디스크 샘플 없음: $rel" ; mismatch=1 ; break
      fi
      if [[ "$a_hash" != "$b_hash" ]]; then
        echo "[!] 샘플 해시 불일치: $rel" ; mismatch=1 ; break
      fi
    done
    if (( mismatch )); then
      echo "[!] 샘플 대조 실패 → 보류"
      ((skip_cnt++)); continue
    fi
  fi

  echo "[OK] 검증 통과 → 아카이브 정리 대상"
  move_to_trash "$arc"
  ((ok_cnt++))
  bytes_sum=$(( bytes_sum + $(stat -c '%s' -- "$arc") ))

done < <(eval "find \"$MOUNT\" -type f $ARCHIVE_PAT -print0")

echo
echo "==== 요약 ===="
echo "검증 통과: $ok_cnt 개  |  보류: $skip_cnt 개"
printf '회수 가능 용량(아카이브 합): %.2f GB\n' "$(awk -v b="$bytes_sum" 'BEGIN{printf b/1024/1024/1024}')"
echo "TRASH 위치: $TRASH"