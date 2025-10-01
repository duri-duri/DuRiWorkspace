#!/usr/bin/env bash
set -Eeuo pipefail
TS() { date '+%F %T'; }
log(){ echo "[$(TS)] $*"; }
die(){ log "[FATAL] $*"; exit 1; }

# === DuRi 집용 콜드 백업 스크립트 ===
# 목적: 집용 콜드 백업 드라이브에 백업 데이터 동기화
# 사용법: ./scripts/duri_cold_backup_home.sh

# 환경 변수 설정
COLD_HOME="/mnt/f/DuRiSafe_HOME"
COLD_HOSP="/mnt/e/DuRiSafe_HOSP"
LOG_FILE="/var/log/duri2-backup/cold_backup_home_$(date +%Y%m%d_%H%M%S).log"

# 로그 디렉토리 준비
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true

log "=== DuRi 집용 콜드 백업 시작 ===" | tee -a "$LOG_FILE"
log "집용 콜드 백업: $COLD_HOME" | tee -a "$LOG_FILE"
log "병원용 콜드 백업: $COLD_HOSP" | tee -a "$LOG_FILE"

# 1) 마운트 확인 (드라이브가 연결되었을 때만 실행)
if ! mountpoint -q "/mnt/f"; then
    log "⚠️ 집용 콜드 백업 드라이브가 연결되지 않음: /mnt/f" | tee -a "$LOG_FILE"
    log "드라이브를 연결한 후 다시 실행하세요." | tee -a "$LOG_FILE"
    exit 0  # 에러가 아닌 정상 종료 (드라이브가 연결되지 않은 상태)
fi

if ! mountpoint -q "/mnt/e"; then
    log "⚠️ 병원용 콜드 백업 드라이브가 연결되지 않음: /mnt/e" | tee -a "$LOG_FILE"
    log "드라이브를 연결한 후 다시 실행하세요." | tee -a "$LOG_FILE"
    exit 0  # 에러가 아닌 정상 종료 (드라이브가 연결되지 않은 상태)
fi

log "✅ 콜드 백업 드라이브들 마운트 확인됨" | tee -a "$LOG_FILE"

# 2) 디렉토리 구조 확인
if [[ ! -d "$COLD_HOME/FULL" ]]; then
    log "❌ 집용 FULL 디렉토리가 없음: $COLD_HOME/FULL" | tee -a "$LOG_FILE"
    exit 1
fi

if [[ ! -d "$COLD_HOSP/FULL" ]]; then
    log "❌ 병원용 FULL 디렉토리가 없음: $COLD_HOSP/FULL" | tee -a "$LOG_FILE"
    exit 1
fi

log "✅ 디렉토리 구조 확인됨" | tee -a "$LOG_FILE"

# 3) 최신 백업 파일 확인
LATEST_HOSP=$(find "$COLD_HOSP/FULL" -name "FULL__*.tar.zst" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
if [[ -z "$LATEST_HOSP" ]]; then
    log "❌ 병원용 최신 백업 파일을 찾을 수 없음" | tee -a "$LOG_FILE"
    exit 1
fi

log "병원용 최신 백업: $LATEST_HOSP" | tee -a "$LOG_FILE"

# 4) 집용에 동일한 파일이 있는지 확인
BASENAME_HOSP=$(basename "$LATEST_HOSP")
LATEST_HOME="$COLD_HOME/FULL/$BASENAME_HOSP"

if [[ -f "$LATEST_HOME" ]]; then
    log "✅ 집용에 이미 동일한 백업 파일 존재: $BASENAME_HOSP" | tee -a "$LOG_FILE"

    # 파일 크기 비교
    SIZE_HOSP=$(stat -c %s "$LATEST_HOSP")
    SIZE_HOME=$(stat -c %s "$LATEST_HOME")

    if [[ "$SIZE_HOSP" -eq "$SIZE_HOME" ]]; then
        log "✅ 파일 크기 일치: ${SIZE_HOSP} bytes" | tee -a "$LOG_FILE"

        # SHA256 해시 비교
        if command -v sha256sum >/dev/null 2>&1; then
            HASH_HOSP=$(sha256sum "$LATEST_HOSP" | cut -d' ' -f1)
            HASH_HOME=$(sha256sum "$LATEST_HOME" | cut -d' ' -f1)

            if [[ "$HASH_HOSP" == "$HASH_HOME" ]]; then
                log "✅ SHA256 해시 일치: $HASH_HOSP" | tee -a "$LOG_FILE"
                log "집용 콜드 백업이 이미 최신 상태입니다." | tee -a "$LOG_FILE"
                exit 0
            else
                log "⚠️ SHA256 해시 불일치, 재복사 필요" | tee -a "$LOG_FILE"
            fi
        fi
    else
        log "⚠️ 파일 크기 불일치 (병원: ${SIZE_HOSP}, 집: ${SIZE_HOME}), 재복사 필요" | tee -a "$LOG_FILE"
    fi
fi

# 5) 백업 파일 복사
log "📁 백업 파일 복사 시작: $BASENAME_HOSP" | tee -a "$LOG_FILE"

if cp "$LATEST_HOSP" "$LATEST_HOME"; then
    log "✅ 백업 파일 복사 완료" | tee -a "$LOG_FILE"
else
    log "❌ 백업 파일 복사 실패" | tee -a "$LOG_FILE"
    exit 1
fi

# 6) SHA256 파일 복사
SHA256_HOSP="$LATEST_HOSP.sha256"
SHA256_HOME="$LATEST_HOME.sha256"

if [[ -f "$SHA256_HOSP" ]]; then
    if cp "$SHA256_HOSP" "$SHA256_HOME"; then
        log "✅ SHA256 파일 복사 완료" | tee -a "$LOG_FILE"
    else
        log "⚠️ SHA256 파일 복사 실패" | tee -a "$LOG_FILE"
    fi
fi

# 7) 메타데이터 파일들 복사
META_FILES=$(find "$COLD_HOSP/FULL" -name "*.txt" -o -name "*.sh" -o -name "*.meta" | head -10)
for meta_file in $META_FILES; do
    if [[ -f "$meta_file" ]]; then
        basename_meta=$(basename "$meta_file")
        if cp "$meta_file" "$COLD_HOME/FULL/$basename_meta"; then
            log "✅ 메타데이터 복사: $basename_meta" | tee -a "$LOG_FILE"
        else
            log "⚠️ 메타데이터 복사 실패: $basename_meta" | tee -a "$LOG_FILE"
        fi
    fi
done

# 8) REPORTS 디렉토리 동기화
if [[ -d "$COLD_HOSP/REPORTS" ]]; then
    log "📁 REPORTS 디렉토리 동기화 시작" | tee -a "$LOG_FILE"

    if rsync -av --delete "$COLD_HOSP/REPORTS/" "$COLD_HOME/REPORTS/" 2>>"$LOG_FILE"; then
        log "✅ REPORTS 디렉토리 동기화 완료" | tee -a "$LOG_FILE"
    else
        log "⚠️ REPORTS 디렉토리 동기화 실패" | tee -a "$LOG_FILE"
    fi
fi

# 9) 최종 검증
if [[ -f "$LATEST_HOME" ]]; then
    SIZE_FINAL=$(stat -c %s "$LATEST_HOME")
    log "✅ 최종 검증 완료: $BASENAME_HOSP (${SIZE_FINAL} bytes)" | tee -a "$LOG_FILE"

    # 스탬프 파일 생성
    echo "$(date '+%F %T') $(hostname) $(whoami) $BASENAME_HOSP" > "$COLD_HOME/FULL/.last_cold_backup.txt"
    log "✅ 스탬프 파일 생성 완료" | tee -a "$LOG_FILE"
else
    log "❌ 최종 검증 실패: 백업 파일이 존재하지 않음" | tee -a "$LOG_FILE"
    exit 1
fi

log "=== DuRi 집용 콜드 백업 완료 ===" | tee -a "$LOG_FILE"
log "로그 파일: $LOG_FILE" | tee -a "$LOG_FILE"
