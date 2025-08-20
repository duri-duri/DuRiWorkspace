#!/usr/bin/env bash
set -euo pipefail

# ---- 설정 ----
WORKSPACE="/home/duri/DuRiWorkspace"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
STAMP="$(date +'%Y-%m-%d__%H%M')"
DATE_DIR="$(date +'%Y')/$(date +'%m')/$(date +'%d')"
OUT_DIR="${DEST_ROOT}/${DATE_DIR}"
HOSTN="$(hostname | tr '[:space:]' '-')"

TMP_ROOT="/tmp/duri_full_backup"
mkdir -p "$TMP_ROOT" "$OUT_DIR"
OUT="${OUT_DIR}/FULL__${STAMP}__host-${HOSTN}.tar.zst"
TMP="${TMP_ROOT}/FULL__${STAMP}__host-${HOSTN}.tar.zst.partial"

echo "[FULL] 시작 → $OUT"
echo " - 작업공간: $WORKSPACE"
echo " - 임시 디렉토리: $TMP_ROOT"

# ---- SIGINT/TERM 핸들러 ----
cleanup() {
  echo "[CLEANUP] partial 제거"
  rm -f "$TMP"
}
trap cleanup INT TERM

# ---- 본 백업: ext4에 먼저 쓰기 ----
echo "[STEP] tar→zstd (tmp로) ..."
(
  cd "$WORKSPACE"
  tar --posix --no-xattrs --no-acls --numeric-owner --owner=0 --group=0 \
      --exclude=.git \
      --exclude=__pycache__ --exclude=.pytest_cache --exclude=.cache \
      --exclude=node_modules --exclude=logs --exclude=temp_* \
      --exclude=var/tmp --exclude=var/run --exclude=var/cache \
      --sort=name --mtime='@0' \
      -cf - \
      DuRiCore duri_brain duri_core duri_common core tools tests configs scripts docs \
      models artifacts var/checkpoints var/prom_data var/metadata \
  | pv -pterb \
  | zstd -T2 -15 -q -o "$TMP"
)

# ---- 원자적 확정(move) ----
echo "[STEP] 최종 이동 ..."
mv -f "$TMP" "$OUT"
sync

# ---- 해시 생성 ----
echo "[STEP] SHA256 ..."
( cd "$OUT_DIR" && sha256sum "$(basename "$OUT")" > "SHA256SUMS.FULL.${STAMP}.txt" )

echo "[OK] FULL 완료 → $OUT"
echo " - 최종 크기: $(du -h "$OUT" | awk '{print $1}')"
