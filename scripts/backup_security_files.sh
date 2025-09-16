#!/usr/bin/env bash
set -Eeuo pipefail
LC_ALL=C

# === 보안 파일 백업 스크립트 ===
# 목적: 중요 보안 파일들을 HDD에 안전하게 백업
# 사용법: ./scripts/backup_security_files.sh

# 환경 변수 설정
HDD="${HDD:-/mnt/hdd}"
BACKUP_ROOT="${BACKUP_ROOT:-$HDD/ARCHIVE}"
SECURITY_DIR="${SECURITY_DIR:-SECURITY}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="$BACKUP_ROOT/$SECURITY_DIR/$TIMESTAMP"
LOG_FILE="${LOG_FILE:-var/logs/security_backup.log}"

# 로깅 함수
TS() { date "+%F %T"; }
log() { echo "[$(TS)] $*" | tee -a "$LOG_FILE"; }

# 초기화
mkdir -p "$(dirname "$LOG_FILE")"
log "=== 보안 파일 백업 시작 ==="
log "HDD: $HDD"
log "백업 경로: $BACKUP_PATH"

# 1) HDD 마운트 확인
if ! mountpoint -q "$HDD"; then
    log "❌ HDD가 마운트되지 않음: $HDD"
    log "마운트 명령어: sudo mount /dev/sdX $HDD"
    exit 1
fi
log "✅ HDD 마운트 확인됨"

# 2) 백업 디렉토리 생성
if ! mkdir -p "$BACKUP_PATH"; then
    log "❌ 백업 디렉토리 생성 실패: $BACKUP_PATH"
    exit 1
fi
log "✅ 백업 디렉토리 생성: $BACKUP_PATH"

# 3) 보안 파일 목록 정의
SECURITY_FILES=(
    "policies/auto_code_loop/gate_policy.yaml"
    "tools/policy_verify.sh"
    "tools/extract_lists.py"
    "tests/policy/test_policy_verify.sh"
    ".env"
    "config.env"
    "docker-compose.yml"
    "scripts/backup_security_files.sh"
    "README.md"
    "CHANGELOG.md"
    "BACKUP_INFO.md"
)

# 4) 각 보안 파일 백업
FAILS=0
for file in "${SECURITY_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        log "백업 중: $file"
        
        # 파일 복사
        if cp -p "$file" "$BACKUP_PATH/"; then
            log "✅ $file 백업 완료"
        else
            log "❌ $file 백업 실패"
            FAILS=$((FAILS+1))
        fi
    else
        log "⚠️ 파일 없음: $file"
    fi
done

# 5) 시스템 정보 백업
log "시스템 정보 백업 중..."
{
    echo "=== 시스템 정보 ==="
    echo "백업 시간: $(date)"
    echo "호스트명: $(hostname)"
    echo "사용자: $(whoami)"
    echo "디스크 사용량:"
    df -h "$HDD"
    echo "백업 파일 목록:"
    ls -la "$BACKUP_PATH"
} > "$BACKUP_PATH/system_info.txt"

# 6) 권한 설정
log "권한 설정 중..."
chmod 600 "$BACKUP_PATH"/*.yaml 2>/dev/null || true
chmod 600 "$BACKUP_PATH"/*.env 2>/dev/null || true
chmod 700 "$BACKUP_PATH"/*.sh 2>/dev/null || true
chmod 644 "$BACKUP_PATH"/*.md 2>/dev/null || true
chmod 644 "$BACKUP_PATH"/*.yml 2>/dev/null || true

# 7) 백업 검증
log "백업 검증 중..."
BACKUP_COUNT=$(find "$BACKUP_PATH" -type f | wc -l)
log "백업된 파일 수: $BACKUP_COUNT"

# 8) 결과 보고
if [[ $FAILS -eq 0 ]]; then
    log "🎉 보안 파일 백업 완료!"
    log "백업 위치: $BACKUP_PATH"
    log "백업 파일 수: $BACKUP_COUNT"
    echo "[SUCCESS] 보안 파일 백업 완료: $BACKUP_PATH"
else
    log "⚠️ 백업 중 $FAILS개 파일 실패"
    echo "[WARNING] 백업 완료 (일부 실패): $BACKUP_PATH"
fi

# 9) 정리 (오래된 백업 삭제)
log "오래된 백업 정리 중..."
find "$BACKUP_ROOT/$SECURITY_DIR" -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true

log "=== 보안 파일 백업 종료 ==="
exit $FAILS
