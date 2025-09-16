#!/usr/bin/env bash
set -euo pipefail

# --- 입력/출력 경로 설정 ---
WORKSPACE="/home/duri/DuRiWorkspace"
STAMP="$(date +'%Y-%m-%d__%H%M')"
OUT_DIR="/mnt/c/Users/admin/Desktop/두리백업/$(date +'%Y/%m/%d')"
HOSTN="$(hostname)"
mkdir -p "$OUT_DIR"

OUT="${OUT_DIR}/FULL__${STAMP}__host-${HOSTN}.tar.zst"
TMPDIR="/tmp/duri_backup"; mkdir -p "$TMPDIR"
TMP="${TMPDIR}/$(basename "$OUT").partial"

FILELIST_TMP="${TMPDIR}/filelist.FULL.${STAMP}.txt.partial"
HASHLIST_TMP="${TMPDIR}/HASHLIST.FULL.${STAMP}.txt.partial"
SHA_TMP="${TMPDIR}/SHA256SUMS.FULL.${STAMP}.txt.partial"

# --- 총량 계산(안정) ---
TOTAL_FILES="$(find "$WORKSPACE" -xdev -type f -print0 | awk -v RS='\0' 'END{print NR}')"
TOTAL_BYTES="$(du -sb --apparent-size "$WORKSPACE" | awk '{print $1}')"
export TOTAL_FILES TOTAL_BYTES

echo "[FULL] 시작 → $OUT"
echo " - 총 파일: $TOTAL_FILES"
echo " - 총 크기 : $TOTAL_BYTES bytes"

# --- 시그널 안전화 ---
cleanup(){ rm -f "$TMP" "$FILELIST_TMP" "$HASHLIST_TMP" "$SHA_TMP" 2>/dev/null || true; }
trap cleanup INT TERM

# --- 메타(원자적 생성) ---
find "$WORKSPACE" -xdev -type f -print0 \
 | tee >(tr '\0' '\n' > "$FILELIST_TMP") \
 | xargs -0 -I{} sha256sum "{}" > "$HASHLIST_TMP"

# --- 본 백업(파이프 단일화, 이중확장자 차단) ---
#  TIP(WSL): tmp(ext4)에 먼저 쓰고 마지막에 mv로 NTFS(C:) 이동
tar --posix --no-xattrs --no-acls -C "$WORKSPACE" -cf - . \
 | pv -s "$TOTAL_BYTES" \
 | zstd -T0 -19 -q -o "$TMP"

# --- 산출물 확정(원자 치환) ---
mv -f "$TMP" "$OUT"
mv -f "$FILELIST_TMP" "${OUT_DIR}/filelist.FULL.${STAMP}.txt"
mv -f "$HASHLIST_TMP"  "${OUT_DIR}/HASHLIST.FULL.${STAMP}.txt"
sha256sum "$OUT" > "$SHA_TMP" && mv -f "$SHA_TMP" "${OUT_DIR}/SHA256SUMS.FULL.${STAMP}.txt"

echo "[OK] FULL 완료 → $OUT"
