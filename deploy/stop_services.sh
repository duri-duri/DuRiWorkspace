#!/bin/bash

# DuRi Control System - 서비스 중지 스크립트
# 사용법: ./deploy/stop_services.sh [--clean]

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

# 변수 초기화
CLEAN_STOP=false

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_STOP=true
            shift
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            echo "사용법: $0 [--clean]"
            exit 1
            ;;
    esac
done

# 스크립트 시작
log_info "🛑 DuRi Control System 서비스 중지..."

# 현재 디렉토리 확인
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml을 찾을 수 없습니다. 올바른 디렉토리에서 실행하세요."
    exit 1
fi

# 서비스 상태 확인
log_info "📊 현재 서비스 상태 확인 중..."
docker-compose ps

# 서비스 중지
log_info "⏹️ 서비스 중지 중..."
docker-compose down --remove-orphans
log_success "서비스 중지 완료"

# 정리 작업 (--clean 옵션)
if [[ "$CLEAN_STOP" == "true" ]]; then
    log_info "🧹 컨테이너 및 이미지 정리 중..."
    docker system prune -f
    log_success "정리 완료"
fi

# 최종 상태 확인
log_info "🔍 최종 상태 확인 중..."
if docker-compose ps | grep -q "Up"; then
    log_warning "일부 서비스가 여전히 실행 중입니다."
    docker-compose ps
else
    log_success "모든 서비스가 정상적으로 중지되었습니다."
fi

echo ""
log_info "📋 다음 명령어로 서비스를 다시 시작할 수 있습니다:"
echo "  ./deploy/start_services.sh"
echo "  또는"
echo "  docker-compose up -d"
echo ""

log_success "🎉 DuRi Control System 서비스 중지가 완료되었습니다!"
