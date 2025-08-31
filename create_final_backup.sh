#!/bin/bash

# DuRi Control System v1.0.0 최종 백업 생성 스크립트
# 사용법: ./create_final_backup.sh

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 스크립트 시작
log_info "🎯 DuRi Control System v1.0.0 최종 백업 생성 시작..."

# 현재 디렉토리 확인
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml을 찾을 수 없습니다. 올바른 디렉토리에서 실행하세요."
    exit 1
fi

# 백업 파일명 생성
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="DuRiWorkspace_v1.0.0_final_${BACKUP_DATE}.tar.gz"
EXCLUDE_FILE="backup_exclude.txt"

log_info "📦 백업 파일명: $BACKUP_NAME"

# 기존 백업 파일 정리
log_info "🧹 기존 백업 파일 정리 중..."
find . -name "*.tar.gz" -type f -delete 2>/dev/null || true
find . -name "*.zip" -type f -delete 2>/dev/null || true
log_success "기존 백업 파일 정리 완료"

# 시스템 상태 확인
log_info "🔍 시스템 상태 확인 중..."

# Docker 컨테이너 상태 확인
if docker-compose ps | grep -q "Up"; then
    log_success "Docker 컨테이너들이 정상 실행 중입니다."
else
    log_warning "일부 Docker 컨테이너가 실행되지 않고 있습니다."
fi

# API 서버 상태 확인
if curl -s http://localhost:8083/health/ > /dev/null 2>&1; then
    log_success "DuRi Control API 서버가 정상 동작 중입니다."
else
    log_warning "DuRi Control API 서버에 접근할 수 없습니다."
fi

# 백업 생성
log_info "📦 백업 파일 생성 중..."

# exclude 파일이 있는지 확인
if [[ -f "$EXCLUDE_FILE" ]]; then
    log_info "제외 파일 목록 사용: $EXCLUDE_FILE"
    tar --exclude-from="$EXCLUDE_FILE" -czf "$BACKUP_NAME" .
else
    log_warning "제외 파일 목록을 찾을 수 없습니다. 기본 설정으로 백업합니다."
    tar --exclude='*.tar.gz' --exclude='*.zip' --exclude='.git' --exclude='__pycache__' --exclude='*.log' --exclude='logs' --exclude='.env' -czf "$BACKUP_NAME" .
fi

# 백업 파일 크기 확인
BACKUP_SIZE=$(du -h "$BACKUP_NAME" | cut -f1)
log_success "백업 파일 생성 완료: $BACKUP_NAME ($BACKUP_SIZE)"

# 백업 파일 무결성 확인
log_info "🔍 백업 파일 무결성 확인 중..."
if tar -tzf "$BACKUP_NAME" > /dev/null 2>&1; then
    log_success "백업 파일이 정상적으로 생성되었습니다."
else
    log_error "백업 파일에 문제가 있습니다."
    exit 1
fi

# 백업 정보 출력
echo ""
log_info "📋 백업 정보:"
echo "  - 파일명: $BACKUP_NAME"
echo "  - 크기: $BACKUP_SIZE"
echo "  - 생성일: $(date)"
echo "  - 위치: $(pwd)/$BACKUP_NAME"
echo ""

# 백업 파일 목록
log_info "📁 현재 디렉토리의 백업 파일들:"
ls -lh *.tar.gz 2>/dev/null || echo "  백업 파일이 없습니다."

echo ""
log_success "🎉 DuRi Control System v1.0.0 최종 백업이 성공적으로 완료되었습니다!"
log_info "💡 백업 파일을 안전한 곳에 보관하세요." 