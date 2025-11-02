#!/usr/bin/env bash
# USB 미러링부터 콜드백업까지 연쇄 실행 스크립트
set -Eeuo pipefail

cd /home/duri/DuRiWorkspace

TS(){ date "+%F %T"; }
log(){ echo "[$(TS)] $*"; }

source scripts/duri_backup.sh 2>/dev/null || true

# G: 드라이브 경로 설정
USB_ROOT="/mnt/g/두리백업/latest"
USB_HAN_READY="${USB_ROOT}/.handoff_READY"
USB_HAN_SEQ="${USB_ROOT}/.handoff.seq"
SRC_DIR="/home/duri/DuRiWorkspace"
EXC="/var/log/duri2-backup/tar.exclude"

log "=== USB 미러링부터 콜드백업까지 연쇄 실행 ==="

# 1) G: 드라이브 마운트 확인 및 마운트
ensure_g_ventoy_mounted || { log "[FATAL] G: 드라이브 마운트 실패"; exit 1; }

if ! mountpoint -q /mnt/g || [ "$(df -P /mnt/g 2>/dev/null | tail -1 | awk '{print $1}')" = "/dev/sdb" ]; then
  log "[FATAL] G: 드라이브가 올바르게 마운트되지 않음"; exit 1
fi

log "[OK] G: 드라이브 마운트 확인 완료"

# 2) USB 미러 (워크스페이스 → USB/latest)
log "2️⃣ USB 미러 시작: 워크스페이스 → $USB_ROOT"
mkdir -p "$USB_ROOT" "$(dirname "$EXC")" 2>/dev/null || true

RSYNC_OPTS=(-aHL --copy-unsafe-links --safe-links
            --delete --delete-delay --delete-excluded --mkpath --modify-window=2
            --no-perms --no-owner --no-group
            --exclude-from="$EXC")

# 제외 규칙 파일 확인
if [[ ! -s "$EXC" ]]; then
  mkdir -p "$(dirname "$EXC")" 2>/dev/null || true
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

log "rsync 시작..."
ionice -c2 -n7 nice -n19 rsync "${RSYNC_OPTS[@]}" "$SRC_DIR/" "$USB_ROOT/" \
  || log "[WARN] USB 미러 경고 (일부 실패 가능)"

log "[OK] USB 미러 완료"

# 3) handoff 마커/시퀀스 갱신
log "3️⃣ Handoff 마커 생성"
mkdir -p "$(dirname "$USB_HAN_SEQ")" 2>/dev/null || true
seq=$(( $(cat "$USB_HAN_SEQ" 2>/dev/null || echo 0) + 1 ))
echo "$seq" > "$USB_HAN_SEQ"
: > "$USB_HAN_READY"
log "[OK] USB handoff 갱신: seq=$seq"

# 4) HOSP 콜드 백업 연쇄 트리거
log "4️⃣ HOSP 콜드 백업 시작: USB → HOSP"
HOSP_SYNC="/usr/local/bin/coldsync_hosp_from_usb.sh"
if [[ -x "$HOSP_SYNC" ]]; then
  log "HOSP cold 연쇄 트리거 실행..."
  "$HOSP_SYNC" && log "[OK] HOSP 콜드 백업 완료" || log "[WARN] HOSP 콜드 백업 경고"
else
  log "[WARN] HOSP 콜드 백업 스크립트 없음: $HOSP_SYNC"
fi

log "=== USB 미러링부터 콜드백업까지 연쇄 실행 완료 ==="

