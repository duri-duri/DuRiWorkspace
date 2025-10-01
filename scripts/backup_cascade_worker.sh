#!/usr/bin/env bash
set -Eeuo pipefail

# DuRi 캐스케이드 워커 시스템
# 목적: 백업 연쇄반응 실행

source .ops.env 2>/dev/null || true

USB_ROOT="${USB_ROOT:-/mnt/usb/DuRiSync}"
HANDOFF_ROOT="${HANDOFF_ROOT:-/mnt/usb/두리백업}"
LOG_FILE="/var/log/duri2-backup/cascade_worker_$(date +%Y%m%d_%H%M%S).log"

LOCK="/var/lock/cascade_worker.lock"
exec 9>"$LOCK"; flock -n 9 || { echo "[skip] cascade_worker running"; exit 0; }

TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

log "=== DuRi 캐스케이드 워커 시작 ===" | tee -a "$LOG_FILE"

# 1단계: HDD → Desktop_Mirror
log "🔄 1단계: HDD → Desktop_Mirror" | tee -a "$LOG_FILE"
DESKTOP_MIRROR="/mnt/hdd/ARCHIVE/Desktop_Mirror"
if [[ -d "$DESKTOP_MIRROR" ]]; then
    rsync -a --ignore-existing "$DESKTOP_MIRROR/" "/mnt/usb/두리백업/" | tee -a "$LOG_FILE" || true
    log "✅ Desktop_Mirror 동기화 완료" | tee -a "$LOG_FILE"
else
    log "❌ Desktop_Mirror 디렉토리 없음" | tee -a "$LOG_FILE"
fi

# 2단계: USB 미러
log "🔄 2단계: USB 미러" | tee -a "$LOG_FILE"
if [[ -x "scripts/usb_incremental_sync.sh" ]]; then
    scripts/usb_incremental_sync.sh export | tee -a "$LOG_FILE"
    log "✅ USB 미러 완료" | tee -a "$LOG_FILE"
else
    log "❌ USB 미러 스크립트 없음" | tee -a "$LOG_FILE"
fi

# 3단계: 핸드오프 시그널 확인
log "🔄 3단계: 핸드오프 시그널 확인" | tee -a "$LOG_FILE"
if [[ -f "$HANDOFF_ROOT/.handoff_READY" ]]; then
    SEQ=$(cat "$HANDOFF_ROOT/.handoff.seq" 2>/dev/null || echo 0)
    log "✅ 핸드오프 시그널 확인됨 (seq=$SEQ)" | tee -a "$LOG_FILE"

    # 병원 콜드 동기 (백스톱)
    if [[ -x "/usr/local/bin/coldsync_hosp_from_usb.sh" ]]; then
        log "🔄 병원 콜드 동기 실행" | tee -a "$LOG_FILE"
        /usr/local/bin/coldsync_hosp_from_usb.sh | tee -a "$LOG_FILE" || true
    fi
else
    log "❌ 핸드오프 시그널 없음" | tee -a "$LOG_FILE"
fi

log "=== DuRi 캐스케이드 워커 완료 ===" | tee -a "$LOG_FILE"
