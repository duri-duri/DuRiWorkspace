#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="${ROOT:-/mnt/h/ARCHIVE}"
TRASH="$ROOT/.TRASH"
SAMPLE="${SAMPLE:-8}"   # 0이면 해시 스킵
ZSTD_LONG="${ZSTD_LONG:-31}"
MODE="${MODE:-self}"    # self=동일 폴더 옆에 동명 폴더로 추출, central=DEST_ROOT 사용
DEST_ROOT="${DEST_ROOT:-$ROOT/.UNWRAP/extracted}"

pick_next(){
  find "$ROOT" \
    \( -path "$TRASH" -o -path "$TRASH/*" -o -path "$ROOT/SECURITY*" \) -prune -o \
    -type f \( -name '*.tar' -o -name '*.tar.gz' -o -name '*.tgz' -o -name '*.tar.zst' \) \
    -print | head -20 | while read -r file; do echo "$(stat -c%s "$file") $file"; done | sort -nr | head -1 | cut -d' ' -f2-
}

arc="${1:-}"
[[ -n "${arc}" ]] || arc="$(pick_next)"
[[ -n "${arc}" && -f "${arc}" ]] || { echo "대상 아카이브 없음"; exit 0; }

arcbase="${arc##*/}"
base="${arcbase%.tar.zst}"; base="${base%.tar.gz}"; base="${base%.tgz}"; base="${base%.tar}"
arcdir="$(dirname -- "$arc")"
if [[ "$MODE" == "self" ]]; then dest="$arcdir/$base"; else dest="$DEST_ROOT/$base"; fi
mkdir -p -- "$dest"

echo "[*] 대상: $arc"
echo "[*] 추출 폴더: $dest"

# 1) 추출 (이미 있으면 스킵)
if [[ -z "$(find "$dest" -type f -mindepth 1 -print -quit 2>/dev/null)" ]]; then
  case "$arc" in
    *.tar.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -xf - -C "$dest" ;;
    *.tar.gz|*.tgz) gzip -dc -- "$arc" | tar -xf - -C "$dest" ;;
    *.tar)     tar -xf "$arc" -C "$dest" ;;
  esac
else
  echo "[i] 이미 추출됨 → 검증만 진행"
fi

# 2) 목록 대조
a=$(mktemp); b=$(mktemp)
case "$arc" in
  *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -tf - ;;
  *.gz|*.tgz) gzip -dc -- "$arc" | tar -tf - ;;
  *.tar)  tar -tf "$arc" ;;
esac | sed 's#^\./##' | grep -v '/$' | LC_ALL=C sort -u >"$a"
( cd "$dest" && find . -type f -printf '%P\n' | LC_ALL=C sort -u >"$b" )

if ! diff -q "$a" "$b" >/dev/null 2>&1; then
  echo "[!] 목록 불일치 → 원본 보존"; rm -f "$a" "$b"; exit 2
fi

# 3) 샘플 해시(옵션)
if (( SAMPLE > 0 )); then
  mapfile -t samples < <(shuf -n "$SAMPLE" "$a" 2>/dev/null || head -n "$SAMPLE" "$a")
  for rel in "${samples[@]}"; do
    ah=$(case "$arc" in
           *.zst)  zstd -dc --long="$ZSTD_LONG" -- "$arc" | tar -xO -f - -- "$rel" ;;
           *.gz|*.tgz) gzip -dc -- "$arc" | tar -xO -f - -- "$rel" ;;
           *.tar)  tar -xO -f "$arc" -- "$rel" ;;
         esac | sha256sum | awk '{print $1}') || { echo "[X] 샘플 추출 실패: $rel"; exit 3; }
    bh=$(sha256sum -- "$dest/$rel" 2>/dev/null | awk '{print $1}') || { echo "[X] 디스크 샘플 없음: $rel"; exit 3; }
    [[ "$ah" == "$bh" ]] || { echo "[X] 해시 불일치: $rel"; exit 3; }
  done
  echo "[OK] 목록/샘플 검증 통과"
else
  echo "[OK] 목록만 검증 통과 (SAMPLE=0)"
fi
rm -f "$a" "$b"

# 4) 원본 TRASH로 이동(경로 보존)
rel="${arc#"$ROOT/"}"
mkdir -p -- "$TRASH/$(dirname "$rel")"
mv -vn -- "$arc" "$TRASH/$rel"
echo "[DONE] 이동 완료 → 필요 시 TRASH에서 최종 삭제하세요."
