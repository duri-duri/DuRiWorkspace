#!/usr/bin/env bash
set -Eeuo pipefail

# DuRi 캐스케이드 스캔 및 큐잉 시스템
# 목적: HDD 백업 변화를 감지하고 연쇄반응 트리거

source .ops.env 2>/dev/null || true

USB_ROOT="${USB_ROOT:-/mnt/g/DuRiSync}"
HANDOFF_ROOT="${HANDOFF_ROOT:-/mnt/g/두리백업}"
LOG_FILE="/var/log/duri2-backup/cascade_scan_$(date +%Y%m%d_%H%M%S).log"

TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

log "=== DuRi 캐스케이드 스캔 시작 ===" | tee -a "$LOG_FILE"

# HDD 백업 디렉토리 모니터링
HDD_BACKUP_DIR="/mnt/hdd/ARCHIVE/FULL"
if [[ ! -d "$HDD_BACKUP_DIR" ]]; then
    log "❌ HDD 백업 디렉토리가 없음: $HDD_BACKUP_DIR" | tee -a "$LOG_FILE"
    exit 1
fi

# 최근 백업 파일 확인
RECENT_FILES=$(find "$HDD_BACKUP_DIR" -name "*.tar.zst" -type f -mtime -1 | wc -l)
log "📊 최근 1일 내 백업 파일 수: $RECENT_FILES" | tee -a "$LOG_FILE"

if [[ "$RECENT_FILES" -gt 0 ]]; then
    log "🔄 새로운 백업 감지됨 - 연쇄반응 트리거" | tee -a "$LOG_FILE"

    # USB 미러 실행
    if [[ -x "scripts/usb_incremental_sync.sh" ]]; then
        log "📤 USB 미러 실행 중..." | tee -a "$LOG_FILE"
        scripts/usb_incremental_sync.sh export | tee -a "$LOG_FILE"

        # 핸드오프 시그널 확인
        if [[ -f "$HANDOFF_ROOT/.handoff_READY" ]]; then
            log "✅ 핸드오프 시그널 생성 완료" | tee -a "$LOG_FILE"
        else
            log "❌ 핸드오프 시그널 생성 실패" | tee -a "$LOG_FILE"
        fi
    else
        log "❌ USB 미러 스크립트를 찾을 수 없음" | tee -a "$LOG_FILE"
    fi
else
    log "ℹ️ 새로운 백업 없음 - 스캔 완료" | tee -a "$LOG_FILE"
fi

log "=== DuRi 캐스케이드 스캔 완료 ===" | tee -a "$LOG_FILE"
