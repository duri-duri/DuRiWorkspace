#!/bin/bash

# DuRi Control System - 전체 빌드 스크립트
# 사용법: ./deploy/build_all.sh [--clean] [--prod]

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
CLEAN_BUILD=false
PROD_MODE=false

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --prod)
            PROD_MODE=true
            shift
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            echo "사용법: $0 [--clean] [--prod]"
            exit 1
            ;;
    esac
done

# 스크립트 시작
log_info "🚀 DuRi Control System 빌드 시작..."

# 현재 디렉토리 확인
if [[ ! -f "docker-compose.yml" ]]; then
    log_error "docker-compose.yml을 찾을 수 없습니다. 올바른 디렉토리에서 실행하세요."
    exit 1
fi

# 환경 변수 로드
if [[ -f ".env" ]]; then
    log_info "환경 변수 파일 로드 중..."
    source .env
else
    log_warning ".env 파일이 없습니다. 기본값을 사용합니다."
fi

# 기존 컨테이너 정리 (--clean 옵션)
if [[ "$CLEAN_BUILD" == "true" ]]; then
    log_info "🧹 기존 컨테이너 및 이미지 정리 중..."
    docker-compose down --remove-orphans
    docker system prune -f
    log_success "정리 완료"
fi

# Base 이미지 빌드
log_info "📦 Base 이미지 빌드 중..."
docker build -t duri-base:latest -f docker/Dockerfile.base .
log_success "Base 이미지 빌드 완료"

# 전체 서비스 빌드
log_info "🔨 전체 서비스 빌드 중..."
if [[ "$PROD_MODE" == "true" ]]; then
    log_info "프로덕션 모드로 빌드 중..."
    docker-compose build --no-cache
else
    docker-compose build
fi
log_success "전체 서비스 빌드 완료"

# 빌드 결과 확인
log_info "🔍 빌드 결과 확인 중..."
docker images | grep duri
log_success "빌드 완료!"

# 다음 단계 안내
echo ""
log_info "다음 명령어로 서비스를 시작할 수 있습니다:"
echo "  ./deploy/start_services.sh"
echo ""
log_info "또는 직접 실행:"
echo "  docker-compose up -d"
echo ""

log_success "🎉 DuRi Control System 빌드가 성공적으로 완료되었습니다!"
