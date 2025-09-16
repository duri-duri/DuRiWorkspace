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

LOG="${TMP_ROOT}/full_${STAMP}.log"
touch "$LOG"

# ---- 프리플라이트 ----
command -v zstd >/dev/null || { echo "zstd 필요"; exit 2; }
command -v tar  >/dev/null || { echo "tar 필요";  exit 2; }

# 용량 추정(대략치): FULL 대상 디렉터리만 합산
estimate_bytes() {
  du -sb --apparent-size \
     "${WORKSPACE}/DuRiCore" \
     "${WORKSPACE}/duri_brain" \
     "${WORKSPACE}/duri_core" \
     "${WORKSPACE}/duri_common" \
     "${WORKSPACE}/core" \
     "${WORKSPACE}/tools" \
     "${WORKSPACE}/tests" \
     "${WORKSPACE}/configs" \
     "${WORKSPACE}/scripts" \
     "${WORKSPACE}/docs" \
     "${WORKSPACE}/models" \
     "${WORKSPACE}/artifacts" \
     "${WORKSPACE}/var/checkpoints" \
     "${WORKSPACE}/var/prom_data" \
     "${WORKSPACE}/var/metadata" 2>/dev/null | awk '{s+=$1} END{print s+0}'
}

EST=$(estimate_bytes || echo 0)
FREE_TMP=$(df -P /tmp | awk 'NR==2{print $4*1024}')
FREE_DEST=$(df -P "$DEST_ROOT" | awk 'NR==2{print $4*1024}')
NEED=$(( EST / 3 ))  # zstd -15 기준 대략 3:1 가정(보수적으로 1/3)

echo "[FULL] 시작 → $OUT" | tee -a "$LOG"
echo " - 추정 원본: ${EST} bytes, 필요 임시공간(추정): ≥${NEED} bytes" | tee -a "$LOG"
echo " - /tmp free: ${FREE_TMP}, DEST free: ${FREE_DEST}" | tee -a "$LOG"

# 공간 체크 (임계치 완화: 추정치의 1.1배)
if (( FREE_TMP < NEED + NEED/10 )); then
  echo "❌ /tmp 공간 부족" | tee -a "$LOG"; exit 3
fi
if (( FREE_DEST < NEED + NEED/5 )); then
  echo "❌ 목적지 드라이브 공간 부족" | tee -a "$LOG"; exit 3
fi

# FD 여유
UL=$(ulimit -n || echo 1024)
if (( UL < 4096 )); then
  ulimit -n 8192 || true
fi

# ---- SIGINT/TERM 핸들러 ----
cleanup() {
  echo "[CLEANUP] partial 제거" | tee -a "$LOG"
  rm -f "$TMP"
}
trap cleanup INT TERM

# ---- 압축 파라미터(WSL 안전값) ----
# 메모리 절약: 스레드 2, 레벨 15(필요시 12로 낮추면 더 안전)
ZSTD_THREADS="${ZSTD_THREADS:-2}"
ZSTD_LEVEL="${ZSTD_LEVEL:-15}"

# ---- tar include/exclude ----
# NTFS 특성 고려: xattrs/acls 끔, 결정적 옵션 일부 유지
EXCLUDES=(
  "--exclude=.git"
  "--exclude=__pycache__" "--exclude=.pytest_cache" "--exclude=.cache"
  "--exclude=node_modules" "--exclude=logs" "--exclude=temp_*"
  "--exclude=var/tmp" "--exclude=var/run" "--exclude=var/cache" "--exclude=var/ephemeral_logs"
  "--exclude=.DS_Store"
)

# ---- 진행률(pv) 옵션: 있으면 쓰고, 없으면 생략 ----
PVOPT=()
if command -v pv >/dev/null; then
  # 원본 전체크기 모르면 pv -pterb만 사용
  PVOPT=(pv -pterb)
fi

# ---- 본 백업: ext4에 먼저 쓰기 ----
echo "[STEP] tar→zstd (tmp로) ..." | tee -a "$LOG"
(
  cd "$WORKSPACE"
  tar --posix --no-xattrs --no-acls --numeric-owner --owner=0 --group=0 \
      "${EXCLUDES[@]}" \
      --sort=name --mtime='@0' \
      -cf - \
      DuRiCore duri_brain duri_core duri_common core tools tests configs scripts docs \
      models artifacts var/checkpoints var/prom_data var/metadata \
  | "${PVOPT[@]}" \
  | zstd -T"${ZSTD_THREADS}" -"${ZSTD_LEVEL}" -q -o "$TMP"
)

# ---- 원자적 확정(move) ----
mv -f "$TMP" "$OUT"
sync

# ---- 해시(사후 단일 패스) ----
echo "[STEP] SHA256 ..." | tee -a "$LOG"
( cd "$OUT_DIR" && sha256sum "$(basename "$OUT")" > "SHA256SUMS.FULL.${STAMP}.txt" )

echo "[OK] FULL 완료 → $OUT" | tee -a "$LOG"
