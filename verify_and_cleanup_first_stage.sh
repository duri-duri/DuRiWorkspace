#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob

# === 설정 ===
MOUNT="/mnt/h"  # 4TB HDD 마운트 지점
ARCHIVE_PAT='\( -name "*.tar.zst" -o -name "*.tar.gz" -o -name "*.tgz" -o -name "*.tar" \)'
EXTRACT_ROOTS=(
  "__SELF__"                           # 아카이브와 같은 위치의 동명 디렉터리
  "$MOUNT/ARCHIVE/.UNWRAP/extracted"   # 별도 추출 스테이지(있으면 사용)
)
DRYRUN=1  # 1: 동작만 출력, 0: 실제 이동
TRASH="$MOUNT/.TRASH"

mkdir -p "$TRASH"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

delete_archive() {
  local arc="$1"
  if (( DRYRUN )); then
    echo "[DRYRUN] would move to trash: $arc"
  else
    mv -vn -- "$arc" "$TRASH/"
  fi
}

verify_and_cleanup() {
  local arc="$1"
  local arcdir filename base dest="" sha
  arcdir=$(dirname "$arc")
  filename=$(basename "$arc")
  base="$filename"
  base="${base%.zst}"; base="${base%.gz}"
  base="${base%.tgz}"; base="${base%.tar}"

  # 추출 대상 디렉터리 찾기
  if [[ " ${EXTRACT_ROOTS[*]} " == *" __SELF__ "* ]] && [[ -d "$arcdir/$base" ]]; then
    dest="$arcdir/$base"
  fi
  if [[ -z "$dest" ]]; then
    for root in "${EXTRACT_ROOTS[@]}"; do
      [[ "$root" == "__SELF__" ]] && continue
      if [[ -d "$root/$base" ]]; then dest="$root/$base"; break; fi
    done
  fi
  if [[ -z "$dest" ]]; then
    echo "[-] 추출 디렉터리 없음: $filename"
    return
  fi

  echo "[*] 검증 시작: $filename  ->  $dest"

  # 원본 목록(아카이브) & 추출 목록(디스크)
  tar -tf "$arc" >"$tmpdir/raw.lst" || { echo "[!] tar -tf 실패(가능: zstd long window)"; return; }
  sed 's#^\./##' "$tmpdir/raw.lst" | grep -v '/$' | LC_ALL=C sort -u >"$tmpdir/a.lst"
  (cd "$dest" && find . -type f -printf '%P\n' | LC_ALL=C sort -u) >"$tmpdir/b.lst"

  if ! diff -u "$tmpdir/a.lst" "$tmpdir/b.lst" >/dev/null; then
    echo "[!] 파일 목록 불일치: $filename"
    return
  fi

  sha="$arc.inputtree.sha256"
  if [[ -f "$sha" ]]; then
    echo "[i] inputtree 해시 존재 → 전체 해시 대조 시도"
    LC_ALL=C sort -k2,2 "$sha" >"$tmpdir/a.sha" || true
    (cd "$dest" && find . -type f -print0 \
      | xargs -0 sha256sum -b \
      | sed 's#^\./##' \
      | LC_ALL=C sort -k2,2) >"$tmpdir/b.sha"
    if ! diff -u "$tmpdir/a.sha" "$tmpdir/b.sha" >/dev/null; then
      echo "[!] SHA256 불일치(또는 inputtree 포맷 불일치): $filename"
      return
    fi
  else
    echo "[i] inputtree 없음 → 샘플 64개 해시 대조"
    mapfile -t sample_raw < <(grep -v '/$' "$tmpdir/raw.lst" | shuf -n 64 2>/dev/null || head -n 64 "$tmpdir/raw.lst")
    for name_in_tar in "${sample_raw[@]}"; do
      rel="${name_in_tar#./}"
      a_hash=$(tar -Oxf "$arc" "$name_in_tar" | sha256sum | awk '{print $1}') || { echo "[!] 샘플 추출 실패: $name_in_tar"; return; }
      b_hash=$(sha256sum "$dest/$rel" | awk '{print $1}') || { echo "[!] 샘플 파일 없음: $dest/$rel"; return; }
      [[ "$a_hash" == "$b_hash" ]] || { echo "[!] 샘플 해시 불일치: $rel"; return; }
    done
  fi

  echo "[OK] 검증 통과: $filename"
  delete_archive "$arc"
}

while IFS= read -r -d '' arc; do
  verify_and_cleanup "$arc"
done < <(eval "find \"$MOUNT\" -type f $ARCHIVE_PAT -print0")

echo "완료. (TRASH: $TRASH)"




