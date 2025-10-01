#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

# ===== 설정 =====
ROOT="/mnt/h/ARCHIVE"          # 원본 아카이브들이 위치한 최상위
ACTION="trash"                 # "delete"=즉시 삭제, "trash"=.TRASH 이동
TRASH="$ROOT/.TRASH"
SAMPLE=8                       # 0=목록만, >0=샘플 해시 대조 개수 (초기엔 8, 최종엔 32 권장)
ZSTD_LONG=31                   # zstd long window (너의 백업과 동일)

# 추출물이 있을 법한 루트들(필요시 추가/삭제)
EXTRACT_ROOTS=(
  "__SELF__"                   # 아카이브와 같은 폴더의 동명 디렉터리
  "$ROOT/.UNWRAP/STAGE1"
  "$ROOT/.UNWRAP/STAGE2"
  "$ROOT/.UNWRAP/STAGE3"
  "$ROOT/.UNWRAP/extracted"
  "$ROOT/.UNWRAP/FIRST"
  "$ROOT/.UNWRAP/SECOND"
)

# ===== 유틸 =====
require(){ command -v "$1" >/dev/null || { echo "필요 명령어 없음: $1"; exit 127; }; }
require tar; require sha256sum; require find; require awk; require sort
command -v zstd >/dev/null || true
command -v gzip >/dev/null || true

tar_list(){ # 아카이브 내 "파일" 목록
  case "$1" in
    *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$1" | tar -tf - ;;
    *.gz|*.tgz) gzip -dc -- "$1" | tar -tf - ;;
    *.tar)  tar -tf -- "$1" ;;
    *)      return 2 ;;
  esac | sed 's#^\./##' | grep -v '/$'
}

tar_cat(){  # 아카이브에서 단일 파일 바이트 스트림
  local arc="$1" rel="$2"
  case "$arc" in
    *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -xO -f - -- "$rel" ;;
    *.gz|*.tgz) gzip -dc -- "$arc" | tar -xO -f - -- "$rel" ;;
    *.tar)  tar -xO -f "$arc" -- "$rel" ;;
  esac
}

# dest 경로 후보 찾기: 동명/루트 하위에서 이름 검색
find_dest_candidates(){
  local arc="$1" arcdir base root
  arcdir=$(dirname -- "$arc")
  base=$(basename -- "$arc"); base="${base%.zst}"; base="${base%.gz}"; base="${base%.tgz}"; base="${base%.tar}"
  # 1) 같은 폴더 동명
  if [[ " ${EXTRACT_ROOTS[*]} " == *" __SELF__ "* ]] && [[ -d "$arcdir/$base" ]]; then
    printf '%s\0' "$arcdir/$base"
  fi
  # 2) 지정 루트들에서 이름으로 탐색 (깊이 3까지)
  for root in "${EXTRACT_ROOTS[@]}"; do
    [[ "$root" == "__SELF__" ]] && continue
    [[ -d "$root" ]] || continue
    while IFS= read -r -d '' d; do printf '%s\0' "$d"; done < <(
      find "$root" -maxdepth 3 -type d -name "$base" -print0 2>/dev/null
    )
  done
}

list_exact(){ (cd "$1" && find . -type f -printf '%P\n'); }
list_strip_top(){
  mapfile -t tops < <(find "$1" -mindepth 1 -maxdepth 1 -type d -printf '%f\n')
  (( ${#tops[@]} == 1 )) || return 3
  (cd "$1/${tops[0]}" && find . -type f -printf '%P\n')
}

do_trash(){
  local f="$1" rel
  rel="${f#$ROOT/}"                         # ROOT 기준 상대경로
  mkdir -p -- "$TRASH/$(dirname "$rel")"
  mv -vn -- "$f" "$TRASH/$rel"
}
do_delete(){ rm -v -- "$1"; }

# ===== 메인 =====
ok=0; skip=0; bytes=0

# .TRASH / .QUAR* / QUARANTINE / SECURITY / 격리/임시 디렉터리는 프룬
mapfile -t ARCS < <(
  find "$ROOT" \
    \( -path "$TRASH" -o -path "$ROOT/.TRASH/*" \
       -o -path "$ROOT/.QUAR*" -o -path "$ROOT/QUARANTINE*" -o -path "$ROOT/SECURITY*" \
       -o -path "$ROOT/.QUAR_FAIL" -o -path "$ROOT/.QUAR_FAIL/*" \
       -o -path "$ROOT/.UNWRAP/D/_trash_inner_*" -o -path "$ROOT/.UNWRAP/quarantine*" -o -path "$ROOT/.UNWRAP/.quarantine*" \
    \) -prune -o \
    -type f \( -name '*.tar.zst' -o -name '*.tar.gz' -o -name '*.tgz' -o -name '*.tar' \) -print |
  LC_ALL=C sort
)

(( ${#ARCS[@]} )) || { echo "대상 아카이브 없음 (ROOT=$ROOT)"; exit 0; }

for arc in "${ARCS[@]}"; do
  echo -e "\n[*] 검사: $arc"

  # 1) 아카이브 목록
  a=$(mktemp)
  if ! tar_list "$arc" | LC_ALL=C sort -u >"$a"; then
    echo "[!] 아카이브 목록 읽기 실패 → 보류"; rm -f "$a"; ((skip++)); continue
  fi

  # 2) 후보 dest들 중 목록 일치하는 곳 찾기
  matched=""; mode=""
  while IFS= read -r -d '' dest; do
    b=$(mktemp)
    # exact
    list_exact "$dest" | LC_ALL=C sort -u >"$b" || true
    if diff -q "$a" "$b" >/dev/null 2>&1; then matched="$dest"; mode="exact"; rm -f "$b"; break; fi
    rm -f "$b"
    # strip-top (dest 안에 상위 1폴더)
    b=$(mktemp)
    list_strip_top "$dest" 2>/dev/null | LC_ALL=C sort -u >"$b" || true
    if [[ -s "$b" ]] && diff -q "$a" "$b" >/dev/null 2>&1; then matched="$dest"; mode="strip-top"; rm -f "$b"; break; fi
    rm -f "$b"
  done < <(find_dest_candidates "$arc")

  [[ -n "$matched" ]] || { echo "[!] 매칭되는 추출 디렉터리 없음 → 보류"; ((skip++)); rm -f -- "$a"; continue; }
  echo "    ↳ 매칭: $matched (모드: $mode)"

  # 3) 내용 샘플 해시 대조(옵션)
  if (( SAMPLE > 0 )); then
    mapfile -t samples < <(shuf -n "$SAMPLE" "$a" 2>/dev/null || head -n "$SAMPLE" "$a")
    for rel in "${samples[@]}"; do
      ah=$(tar_cat "$arc" "$rel" | sha256sum | awk '{print $1}') || { echo "[!] 샘플 추출 실패: $rel"; matched=""; break; }
      case "$mode" in
        exact)     disk="$matched/$rel" ;;
        strip-top) top=$(find "$matched" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | head -n1); disk="$matched/$top/$rel" ;;
      esac
      bh=$(sha256sum -- "$disk" 2>/dev/null | awk '{print $1}') || { echo "[!] 디스크 샘플 없음: $disk"; matched=""; break; }
      [[ "$ah" == "$bh" ]] || { echo "[!] 해시 불일치: $rel"; matched=""; break; }
    done
    [[ -n "$matched" ]] || { echo "[!] 샘플 대조 실패 → 보류"; ((skip++)); rm -f -- "$a"; continue; }
  fi

  size=$(stat -c '%s' -- "$arc" || echo 0)
  echo "[OK] 검증 통과 → 원본 정리 대상"

  if [[ "$ACTION" == "delete" ]]; then do_delete "$arc"; else do_trash "$arc"; fi
  ((ok++)); bytes=$((bytes + size))

  # 임시 파일 정리
  rm -f -- "$a"
done

echo -e "\n==== 요약 ===="
echo "정리(삭제/이동): $ok  |  보류: $skip"
printf '회수 용량 합계: %.2f GB\n' "$(awk -v b="$bytes" 'BEGIN{printf b/1024/1024/1024}')"
[[ "$ACTION" == "trash" ]] && echo "TRASH: $TRASH"
