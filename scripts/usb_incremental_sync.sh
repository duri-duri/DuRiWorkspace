#!/usr/bin/env bash
set -Eeuo pipefail
TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }

# === DuRi USB 증분 동기화 시스템 ===
# 목적: USB를 매개체로 병원용과 집용 콜드 백업 동기화
# 사용법: ./scripts/usb_incremental_sync.sh [export|import]

MODE="${1:-export}"  # export: 병원→USB, import: USB→집
USB_ROOT="/mnt/g/DuRiSync"
HOSP_ROOT="/mnt/e/DuRiSafe_HOSP"
HOME_ROOT="/mnt/f/DuRiSafe_HOME"
LOG_FILE="/var/log/duri2-backup/usb_sync_$(date +%Y%m%d_%H%M%S).log"

# 로그 디렉토리 준비
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true

log "=== DuRi USB 증분 동기화 시작 ===" | tee -a "$LOG_FILE"
log "모드: $MODE" | tee -a "$LOG_FILE"
log "USB: $USB_ROOT" | tee -a "$LOG_FILE"

# USB 마운트 확인
if ! mountpoint -q "/mnt/g"; then
    log "❌ USB가 마운트되지 않음: /mnt/g" | tee -a "$LOG_FILE"
    exit 1
fi

# USB 동기화 디렉토리 생성
mkdir -p "$USB_ROOT"/{metadata,increments,logs} 2>/dev/null || true

if [[ "$MODE" == "export" ]]; then
    # === 병원용 → USB 내보내기 ===
    log "📤 병원용 콜드 백업 → USB 내보내기" | tee -a "$LOG_FILE"
    
    if ! mountpoint -q "/mnt/e"; then
        log "❌ 병원용 콜드 백업 드라이브가 마운트되지 않음: /mnt/e" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 1) 메타데이터 내보내기 (파일 목록, 크기, 해시, 타임스탬프)
    log "📋 메타데이터 내보내기 중..." | tee -a "$LOG_FILE"
    
    METADATA_FILE="$USB_ROOT/metadata/hosp_metadata_$(date +%Y%m%d_%H%M%S).json"
    
    # JSON 형태로 메타데이터 생성
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"source\": \"hosp\","
        echo "  \"files\": ["
        
        first=true
        find "$HOSP_ROOT/FULL" -name "*.tar.zst" -type f | while read -r file; do
            if [[ "$first" == true ]]; then
                first=false
            else
                echo ","
            fi
            
            basename_file=$(basename "$file")
            size=$(stat -c %s "$file")
            mtime=$(stat -c %Y "$file")
            
            echo -n "    {"
            echo -n "\"name\": \"$basename_file\","
            echo -n "\"size\": $size,"
            echo -n "\"mtime\": $mtime,"
            echo -n "\"path\": \"$file\""
            echo -n "}"
        done
        
        echo ""
        echo "  ]"
        echo "}"
    } > "$METADATA_FILE"
    
    log "✅ 메타데이터 내보내기 완료: $METADATA_FILE" | tee -a "$LOG_FILE"
    
    # 2) 최신 백업 파일들만 USB로 복사 (크기 제한)
    log "📁 최신 백업 파일들 복사 중..." | tee -a "$LOG_FILE"
    
    # 최근 7일 이내의 파일들만 복사
    find "$HOSP_ROOT/FULL" -name "*.tar.zst" -type f -mtime -7 | while read -r file; do
        basename_file=$(basename "$file")
        dest_file="$USB_ROOT/increments/$basename_file"
        
        if [[ ! -f "$dest_file" ]]; then
            log "복사 중: $basename_file" | tee -a "$LOG_FILE"
            if cp "$file" "$dest_file"; then
                log "✅ 복사 완료: $basename_file" | tee -a "$LOG_FILE"
            else
                log "❌ 복사 실패: $basename_file" | tee -a "$LOG_FILE"
            fi
        else
            log "⏭️ 이미 존재: $basename_file" | tee -a "$LOG_FILE"
        fi
    done
    
    # 3) SHA256 파일들도 복사
    find "$HOSP_ROOT/FULL" -name "*.sha256" -type f -mtime -7 | while read -r file; do
        basename_file=$(basename "$file")
        dest_file="$USB_ROOT/increments/$basename_file"
        
        if [[ ! -f "$dest_file" ]]; then
            cp "$file" "$dest_file"
            log "✅ SHA256 복사: $basename_file" | tee -a "$LOG_FILE"
        fi
    done
    
    # 4) 상태 파일 생성
    echo "$(date -Iseconds)" > "$USB_ROOT/last_export.txt"
    echo "hosp" > "$USB_ROOT/source_location.txt"
    
    log "✅ 병원용 → USB 내보내기 완료" | tee -a "$LOG_FILE"
    
elif [[ "$MODE" == "import" ]]; then
    # === USB → 집용 가져오기 ===
    log "📥 USB → 집용 콜드 백업 가져오기" | tee -a "$LOG_FILE"
    
    if ! mountpoint -q "/mnt/f"; then
        log "❌ 집용 콜드 백업 드라이브가 마운트되지 않음: /mnt/f" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    # 1) 메타데이터 확인
    METADATA_FILES=($(find "$USB_ROOT/metadata" -name "hosp_metadata_*.json" -type f 2>/dev/null | sort -r))
    if [[ ${#METADATA_FILES[@]} -eq 0 ]]; then
        log "❌ USB에 메타데이터가 없습니다" | tee -a "$LOG_FILE"
        exit 1
    fi
    
    LATEST_METADATA="${METADATA_FILES[0]}"
    log "📋 최신 메타데이터: $(basename "$LATEST_METADATA")" | tee -a "$LOG_FILE"
    
    # 2) 집용 현재 상태 확인
    log "🔍 집용 현재 상태 확인 중..." | tee -a "$LOG_FILE"
    
    HOME_METADATA="$USB_ROOT/metadata/home_current_$(date +%Y%m%d_%H%M%S).json"
    {
        echo "{"
        echo "  \"timestamp\": \"$(date -Iseconds)\","
        echo "  \"source\": \"home\","
        echo "  \"files\": ["
        
        first=true
        find "$HOME_ROOT/FULL" -name "*.tar.zst" -type f | while read -r file; do
            if [[ "$first" == true ]]; then
                first=false
            else
                echo ","
            fi
            
            basename_file=$(basename "$file")
            size=$(stat -c %s "$file")
            mtime=$(stat -c %Y "$file")
            
            echo -n "    {"
            echo -n "\"name\": \"$basename_file\","
            echo -n "\"size\": $size,"
            echo -n "\"mtime\": $mtime,"
            echo -n "\"path\": \"$file\""
            echo -n "}"
        done
        
        echo ""
        echo "  ]"
        echo "}"
    } > "$HOME_METADATA"
    
    # 3) 증분 파일들 복사
    log "📁 증분 파일들 복사 중..." | tee -a "$LOG_FILE"
    
    COPIED_COUNT=0
    find "$USB_ROOT/increments" -name "*.tar.zst" -type f | while read -r file; do
        basename_file=$(basename "$file")
        dest_file="$HOME_ROOT/FULL/$basename_file"
        
        if [[ ! -f "$dest_file" ]]; then
            log "복사 중: $basename_file" | tee -a "$LOG_FILE"
            if cp "$file" "$dest_file"; then
                log "✅ 복사 완료: $basename_file" | tee -a "$LOG_FILE"
                COPIED_COUNT=$((COPIED_COUNT + 1))
            else
                log "❌ 복사 실패: $basename_file" | tee -a "$LOG_FILE"
            fi
        else
            log "⏭️ 이미 존재: $basename_file" | tee -a "$LOG_FILE"
        fi
    done
    
    # 4) SHA256 파일들도 복사
    find "$USB_ROOT/increments" -name "*.sha256" -type f | while read -r file; do
        basename_file=$(basename "$file")
        dest_file="$HOME_ROOT/FULL/$basename_file"
        
        if [[ ! -f "$dest_file" ]]; then
            cp "$file" "$dest_file"
            log "✅ SHA256 복사: $basename_file" | tee -a "$LOG_FILE"
        fi
    done
    
    # 5) 상태 파일 업데이트
    echo "$(date -Iseconds)" > "$USB_ROOT/last_import.txt"
    echo "home" > "$USB_ROOT/target_location.txt"
    
    log "✅ USB → 집용 가져오기 완료" | tee -a "$LOG_FILE"
    log "복사된 파일 수: $COPIED_COUNT" | tee -a "$LOG_FILE"
    
else
    log "❌ 잘못된 모드: $MODE (export 또는 import 사용)" | tee -a "$LOG_FILE"
    exit 1
fi

log "=== DuRi USB 증분 동기화 완료 ===" | tee -a "$LOG_FILE"
log "로그 파일: $LOG_FILE" | tee -a "$LOG_FILE"

