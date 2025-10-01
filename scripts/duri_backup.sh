#!/usr/bin/env bash
set -Eeuo pipefail

TS(){ date "+%F %T"; }
log(){ echo "[$(TS)] $*"; }
die(){ log "[FATAL] $*"; exit 1; }

# === 정책 ===
# 기본은 '증분'; 필요할 때만 'full' 수행
SRC="${SRC:-/home/duri/DuRiWorkspace}"
MODE="${1:-incr}"          # full | incr
SRC_DIR="${SRC_DIR:-$SRC}"

# 산출/상태 경로
HOST="${HOSTNAME:-host}"
ARCH_BASE="/mnt/hdd/ARCHIVE"                         # HDD 보관 루트
DEST_FULL_DIR="${ARCH_BASE}/FULL"
DEST_INCR_DIR="${ARCH_BASE}/INCR"
RUNLOG="/var/log/duri2-backup/backup_$(date +%Y%m%d_%H%M%S).log"
EXC="/var/log/duri2-backup/tar.exclude"
SNAP_DIR="/var/lib/duri-backup/snapshots"
SNAP="${SNAP_DIR}/duri_ws.snar"

# USB/HOSP/HOME 연쇄 트리거용
USB_ROOT="/mnt/usb/두리백업/latest"
USB_HAN_READY="${USB_ROOT}/.handoff_READY"
USB_HAN_SEQ="${USB_ROOT}/.handoff.seq"
HOSP_SYNC="/usr/local/bin/coldsync_hosp_from_usb.sh"   # 있으면 후크로 실행

mkdir -p "$(dirname "$RUNLOG")" "$SNAP_DIR" "$DEST_FULL_DIR" "$DEST_INCR_DIR" || true

log "=== DuRi 백업 시작 ===" | tee -a "$RUNLOG"
log "SRC=$SRC_DIR"          | tee -a "$RUNLOG"
log "MODE=${MODE}"          | tee -a "$RUNLOG"

# --- 제외 규칙 파일(없으면 생성/보완) ---
if [[ ! -s "$EXC" ]]; then
  cat >"$EXC" <<'EOF'
# 안전 센티넬
.duri_guard
# 런타임/볼라틸
data/prometheus/**
data/**/wal/**
data/**/queries.active
# VCS/캐시/대용량 잡음
**/.git/ **/.github/ **/.venv/ **/__pycache__/ **/node_modules/ **/logs/
ARCHIVE/ backup_repository/ duri_snapshots/
*.tar.zst *.sha256 .DS_Store Thumbs.db
EOF
fi

# --- 스냅샷 관리 ---
if [[ "$MODE" == "full" ]]; then
  : > "$SNAP"    # level-0 스냅샷 리셋
else
  [[ -f "$SNAP" ]] || { echo "[FATAL] snapshot 없음: 먼저 'scripts/duri_backup.sh full' 로 기준 생성 필요"; exit 2; }
fi

# --- 산출 파일명/경로 ---
STAMP="$(date +%F__%H%M)"
if [[ "$MODE" == "full" ]]; then
  OUT="${DEST_FULL_DIR}/FULL__${STAMP}__${HOST}.tar.zst"
else
  OUT="${DEST_INCR_DIR}/INCR__${STAMP}__${HOST}.tar.zst"
fi

# --- tar 실행 (증분은 --listed-incremental) ---
log "PRIMARY 백업 시작: $OUT"        | tee -a "$RUNLOG"

# 주의: tar는 아카이브 파일만 HDD(예: NTFS)에 쓰므로 심링크/권한 이슈에 둔감
tar --zstd -cpf "$OUT" \
  --listed-incremental="$SNAP" \
  --xattrs --acls --numeric-owner --one-file-system \
  --exclude-from="$EXC" \
  -C "$SRC_DIR" . 2>&1 | tee -a "$RUNLOG" || die "tar 실패"

sha256sum "$OUT" > "${OUT}.sha256"
log "PRIMARY 백업 완료: $(basename "$OUT")" | tee -a "$RUNLOG"

# ──────────────────────────────────────────────────────────────────────────────
# 1) Desktop_Mirror(선택) — 필요 시 유지
#   (기존 미러 스텝이 있다면 여기에 source 하거나 함수 호출)
# source scripts/duri_backup.dest.sh || true

# 2) USB 미러 (워크스페이스 → USB/latest)  — 심링크/런타임 제외 반영
if mountpoint -q /mnt/usb; then
  log "USB 라이브 미러 시작" | tee -a "$RUNLOG"
  # 링크는 내용 복사, 깨진 링크/볼라틸 제외
  RSYNC_OPTS=(-aHL --copy-unsafe-links --safe-links
              --delete --delete-delay --mkpath --modify-window=2
              --no-perms --no-owner --no-group
              --exclude-from="$EXC")
  ionice -c2 -n7 nice -n19 rsync "${RSYNC_OPTS[@]}" "$SRC_DIR/" "$USB_ROOT/" \
    >>"$RUNLOG" 2>&1 || log "[warn] USB 미러 경고"

  # handoff 마커/시퀀스 갱신
  seq=$(( $(cat "$USB_HAN_SEQ" 2>/dev/null || echo 0) + 1 ))
  echo "$seq" > "$USB_HAN_SEQ"
  : > "$USB_HAN_READY"
  log "USB handoff 갱신: seq=$seq" | tee -a "$RUNLOG"

  # 병원 콜드 후크(있을 때만)
  if [[ -x "$HOSP_SYNC" ]]; then
    log "HOSP cold 연쇄 트리거" | tee -a "$RUNLOG"
    "$HOSP_SYNC" >>"$RUNLOG" 2>&1 || log "[warn] HOSP 연쇄 경고"
  fi
else
  log "[skip] USB 미러: USB 미마운트" | tee -a "$RUNLOG"
fi

log "=== 백업 체인 완료 ===" | tee -a "$RUNLOG"
