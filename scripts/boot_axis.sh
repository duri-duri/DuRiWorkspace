#!/bin/bash
# DuRi 부팅 축 시스템 v1.0
# 목적: 새로운 작업 세션 시작 시 전체 시스템 상태 확인

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# 1. HDD 백업 축 확인
check_hdd_backup() {
    log "=== HDD 백업 축 확인 ==="
    
    # 오늘 날짜 백업 파일 확인
    TODAY=$(date +%Y%m%d)
    BACKUP_FILE="/mnt/d/backup/DAILY/Dump_${TODAY}*.dump"
    
    if ls $BACKUP_FILE 2>/dev/null; then
        success "HDD 백업: 오늘 백업 완료"
        ls -la $BACKUP_FILE | head -1
    else
        warning "HDD 백업: 오늘 백업 없음"
        
        # 최근 백업 파일 확인
        RECENT_BACKUP=$(ls -t /mnt/d/backup/DAILY/Dump_*.dump 2>/dev/null | head -1)
        if [ -n "$RECENT_BACKUP" ]; then
            echo "최근 백업: $(basename $RECENT_BACKUP)"
            ls -la "$RECENT_BACKUP"
        else
            error "HDD 백업: 백업 파일 없음"
        fi
    fi
    
    # C 드라이브 백업도 확인
    C_BACKUP_FILE="/mnt/c/backup/DAILY/Dump_${TODAY}*.dump"
    if ls $C_BACKUP_FILE 2>/dev/null; then
        success "C 드라이브 백업: 오늘 백업 완료"
    else
        warning "C 드라이브 백업: 오늘 백업 없음"
    fi
}

# 2. Git 백업 축 확인
check_git_backup() {
    log "=== Git 백업 축 확인 ==="
    
    # 현재 브랜치 확인
    CURRENT_BRANCH=$(git branch --show-current)
    success "현재 브랜치: $CURRENT_BRANCH"
    
    # 최신 커밋 확인
    LATEST_COMMIT=$(git log --oneline -1)
    success "최신 커밋: $LATEST_COMMIT"
    
    # 백업 태그 확인
    echo "최근 백업 태그:"
    git tag --sort=-creatordate | head -3 | while read tag; do
        echo "  - $tag"
    done
    
    # 원격 동기화 상태 확인
    UNCOMMITTED=$(git status --porcelain | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        success "Git 상태: 깨끗함"
    else
        warning "Git 상태: $UNCOMMITTED 개 변경사항"
    fi
    
    # 원격 저장소 상태 확인
    if git remote -v | grep -q origin; then
        success "원격 저장소: 연결됨"
    else
        warning "원격 저장소: 연결 안됨"
    fi
}

# 3. 드라이브 마운트 상태 확인
check_drive_mount() {
    log "=== 드라이브 마운트 상태 확인 ==="
    
    for drive in e f g h; do
        MOUNT_POINT="/mnt/$drive"
        if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
            success "/mnt/$drive: 마운트됨"
            df -h "$MOUNT_POINT" | tail -1 | awk '{print "  용량: " $3 "/" $2 " (" $5 " 사용)"}'
        else
            warning "/mnt/$drive: 마운트 안됨"
        fi
    done
}

# 4. 백업 축 관리 원칙 확인
check_backup_principles() {
    log "=== 백업 축 관리 원칙 확인 ==="
    
    # 1. HDD 백업이 기본
    TODAY=$(date +%Y%m%d)
    if ls /mnt/d/backup/DAILY/Dump_${TODAY}*.dump 2>/dev/null; then
        success "1. HDD 백업이 기본: 준수"
    else
        error "1. HDD 백업이 기본: 위반"
    fi
    
    # 2. Git은 추가 보안
    if git status --porcelain | wc -l | grep -q "^0$"; then
        success "2. Git은 추가 보안: 준수"
    else
        warning "2. Git은 추가 보안: 변경사항 있음"
    fi
    
    # 3. 시계열 추적
    LATEST_BACKUP=$(ls -t /mnt/d/backup/DAILY/Dump_*.dump 2>/dev/null | head -1)
    if [ -n "$LATEST_BACKUP" ]; then
        success "3. 시계열 추적: 준수 ($(basename $LATEST_BACKUP))"
    else
        error "3. 시계열 추적: 위반"
    fi
    
    # 4. 맥락 보존
    if [ -f "backup_log_$(date +%Y%m%d)_final.md" ]; then
        success "4. 맥락 보존: 준수"
    else
        warning "4. 맥락 보존: 오늘 로그 없음"
    fi
    
    # 5. 상호 참조
    if git tag --sort=-creatordate | head -1 | grep -q "backup"; then
        success "5. 상호 참조: 준수"
    else
        warning "5. 상호 참조: 백업 태그 없음"
    fi
}

# 5. 작업 환경 확인
check_work_environment() {
    log "=== 작업 환경 확인 ==="
    
    # 현재 디렉토리 확인
    success "현재 디렉토리: $(pwd)"
    
    # 활성 프로세스 확인
    ACTIVE_PROCESSES=$(ps aux | grep -E "(duri|backup|git)" | grep -v grep | wc -l)
    if [ "$ACTIVE_PROCESSES" -gt 0 ]; then
        success "활성 프로세스: $ACTIVE_PROCESSES 개"
    else
        warning "활성 프로세스: 없음"
    fi
    
    # 디스크 사용량 확인
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -lt 80 ]; then
        success "디스크 사용량: ${DISK_USAGE}%"
    else
        warning "디스크 사용량: ${DISK_USAGE}% (높음)"
    fi
}

# 메인 함수
main() {
    echo "🚀 DuRi 부팅 축 시작..."
    echo "=================================="
    
    check_hdd_backup
    echo ""
    
    check_git_backup
    echo ""
    
    check_drive_mount
    echo ""
    
    check_backup_principles
    echo ""
    
    check_work_environment
    echo ""
    
    echo "=================================="
    success "부팅 축 완료 - 작업 준비됨"
}

# 스크립트 실행
main "$@"
