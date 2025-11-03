#!/usr/bin/env bash
set -Eeuo pipefail

# === USB mount auto-detection ===
find_usb_ventoy() {
  local cand base
  # Check saved config first
  [ -f "$HOME/.config/duri/backup_env" ] && source "$HOME/.config/duri/backup_env" 2>/dev/null
  [ -n "${USB_BASE:-}" ] && [ -d "$USB_BASE" ] && echo "$USB_BASE" && return 0
  # Search candidates
  for cand in /mnt/g /mnt/usb /mnt/{g,G,usb,USB}; do
    [ ! -d "$cand" ] && continue
    df -P "$cand" 2>/dev/null | grep -q "G:" && echo "$cand" && return 0
    [ -d "$cand/두리백업" ] && echo "$cand" && return 0
  done
  df -h 2>/dev/null | awk '$NF ~ //mnt/[gG]|G:/ {print $NF; exit}' || true
}
USB_BASE_AUTO=$(find_usb_ventoy)
[ -n "$USB_BASE_AUTO" ] && USB_ROOT="$USB_BASE_AUTO/두리백업/latest"

# === G: Ventoy 드라이브 마운트 확인 및 자동 마운트 ===
ensure_g_ventoy_mounted() {
  # /mnt/g가 실제 G: 드라이브인지 확인 (/dev/sdb가 루트이므로 이것이면 마운트 안 된 것)
  if ! mountpoint -q /mnt/g || [ "$(df -P /mnt/g 2>/dev/null | tail -1 | awk '{print $1}')" = "/dev/sdb" ]; then
    echo "[INFO] G: 드라이브가 마운트되지 않음 - 자동 마운트 시도" >&2
    sudo "$HOME/DuRiWorkspace/scripts/_umount_g.sh" 2>/dev/null || true
    if sudo "$HOME/DuRiWorkspace/scripts/_mount_g.sh" 2>/dev/null; then
      echo "[OK] G: 드라이브를 /mnt/g에 마운트 성공" >&2
    else
      echo "[WARN] G: 드라이브 마운트 실패 - WSL 재시작 필요: wsl --shutdown" >&2
      return 1
    fi
  fi
  # 마운트 확인: /mnt/g가 실제 G: 드라이브인지 (Windows 경로 확인)
  if df -P /mnt/g 2>/dev/null | tail -1 | awk '{print $1}' | grep -q "^/dev/sdb$"; then
    echo "[WARN] /mnt/g가 여전히 루트를 가리킴 - G: 드라이브 마운트 확인 필요" >&2
    return 1
  fi
  return 0
}

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
USB_ROOT="/mnt/g/두리백업/latest"
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
# G: 드라이브 마운트 확인 및 자동 마운트
ensure_g_ventoy_mounted || log "[WARN] G: 드라이브 마운트 실패 - USB 미러 스킵"
if mountpoint -q /mnt/g && [ "$(df -P /mnt/g 2>/dev/null | tail -1 | awk '{print $1}')" != "/dev/sdb" ]; then
  log "USB 라이브 미러 시작" | tee -a "$RUNLOG"
  # 링크는 내용 복사, 깨진 링크/볼라틸 제외
  # USB는 drvfs 마운트이므로 타임스탬프/권한 설정 제한 → --no-times 사용
  # 큰 디렉토리 명시적 제외로 rsync 성능 최적화
  RSYNC_OPTS=(-aHL --copy-unsafe-links --safe-links
              --delete --delete-delay --mkpath --modify-window=2
              --no-perms --no-owner --no-group --no-times
              --exclude-from="$EXC"
              --exclude='.git/'
              --exclude='**/.git/'
              --exclude='**/.github/'
              --exclude='**/.venv/'
              --exclude='**/__pycache__/'
              --exclude='**/node_modules/'
              --exclude='**/logs/'
              --exclude='ARCHIVE/'
              --exclude='*.tar.zst'
              --exclude='*.sha256'
              --max-size=100M
              --info=progress2 --human-readable)
  ionice -c2 -n7 nice -n19 rsync "${RSYNC_OPTS[@]}" "$SRC_DIR/" "$USB_ROOT/" \
    2>>"$RUNLOG" | tee -a "$RUNLOG" | grep -E "(total size|sent|received|speed)" || true
  RSYNC_EXIT=${PIPESTATUS[0]}
  
  if [ "$RSYNC_EXIT" -eq 0 ] || [ "$RSYNC_EXIT" -eq 23 ]; then  # 23 = partial transfer OK
    log "USB 미러 완료 (exit=$RSYNC_EXIT)" | tee -a "$RUNLOG"
    
    # handoff 마커/시퀀스 갱신 (rsync 성공 시에만)
    seq=$(( $(cat "$USB_HAN_SEQ" 2>/dev/null || echo 0) + 1 ))
    echo "$seq" > "$USB_HAN_SEQ" 2>/dev/null || true
    : > "$USB_HAN_READY" 2>/dev/null || true
    log "USB handoff 갱신: seq=$seq" | tee -a "$RUNLOG"

    # 병원 콜드 후크(있을 때만)
    if [[ -x "$HOSP_SYNC" ]]; then
      log "HOSP cold 연쇄 트리거" | tee -a "$RUNLOG"
      "$HOSP_SYNC" >>"$RUNLOG" 2>&1 || log "[warn] HOSP 연쇄 경고" | tee -a "$RUNLOG"
    fi
  else
    log "[warn] USB 미러 경고 (exit=$RSYNC_EXIT) - handoff 마커 생성 안 함" | tee -a "$RUNLOG"
  fi
else
  log "[skip] USB 미러: USB 미마운트" | tee -a "$RUNLOG"
fi

log "=== 백업 체인 완료 ===" | tee -a "$RUNLOG"
