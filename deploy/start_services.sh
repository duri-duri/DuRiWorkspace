#!/bin/bash

# DuRi Control System - 서비스 시작 스크립트
# 사용법: ./deploy/start_services.sh [--wait] [--health-check]

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
WAIT_FOR_SERVICES=false
HEALTH_CHECK=false

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --wait)
            WAIT_FOR_SERVICES=true
            shift
            ;;
        --health-check)
            HEALTH_CHECK=true
            shift
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            echo "사용법: $0 [--wait] [--health-check]"
            exit 1
            ;;
    esac
done

# 스크립트 시작
log_info "🚀 DuRi Control System 서비스 시작..."

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

# 기존 서비스 중지
log_info "🛑 기존 서비스 중지 중..."
docker-compose down --remove-orphans
log_success "기존 서비스 중지 완료"

# 서비스 시작
log_info "▶️ 서비스 시작 중..."
docker-compose up -d
log_success "서비스 시작 완료"

# 서비스 상태 확인
log_info "📊 서비스 상태 확인 중..."
sleep 5
docker-compose ps

# 서비스 대기 (--wait 옵션)
if [[ "$WAIT_FOR_SERVICES" == "true" ]]; then
    log_info "⏳ 서비스 완전 시작 대기 중..."
    
    # PostgreSQL 대기
    log_info "🔄 PostgreSQL 연결 대기 중..."
    until docker-compose exec -T duri-postgres pg_isready -U duri; do
        sleep 2
    done
    log_success "PostgreSQL 준비 완료"
    
    # Redis 대기
    log_info "🔄 Redis 연결 대기 중..."
    until docker-compose exec -T duri-redis redis-cli ping; do
        sleep 2
    done
    log_success "Redis 준비 완료"
    
    # DuRi Control API 대기
    log_info "🔄 DuRi Control API 대기 중..."
    until curl -s http://localhost:8083/health/ > /dev/null; do
        sleep 3
    done
    log_success "DuRi Control API 준비 완료"
fi

# 헬스 체크 (--health-check 옵션)
if [[ "$HEALTH_CHECK" == "true" ]]; then
    log_info "🏥 헬스 체크 수행 중..."
    
    # 기본 헬스 체크
    if curl -s http://localhost:8083/health/ | grep -q "healthy"; then
        log_success "기본 헬스 체크 통과"
    else
        log_error "기본 헬스 체크 실패"
        exit 1
    fi
    
    # 서비스 초기화 상태 확인
    if curl -s http://localhost:8083/health/services | grep -q "all_services_ready.*true"; then
        log_success "서비스 초기화 상태 확인 완료"
    else
        log_warning "일부 서비스가 아직 초기화 중입니다"
    fi
    
    # 모니터링 엔드포인트 확인
    if curl -s http://localhost:8083/monitor/services > /dev/null; then
        log_success "모니터링 엔드포인트 정상"
    else
        log_error "모니터링 엔드포인트 오류"
    fi
fi

# 서비스 정보 출력
echo ""
log_info "📋 서비스 정보:"
echo "  - DuRi Control API: http://localhost:8083"
echo "  - API 문서: http://localhost:8083/docs"
echo "  - 헬스 체크: http://localhost:8083/health/"
echo "  - 서비스 상태: http://localhost:8083/monitor/services"
echo ""

log_info "🔧 관리 명령어:"
echo "  - 서비스 중지: docker-compose down"
echo "  - 로그 확인: docker-compose logs -f [서비스명]"
echo "  - 서비스 재시작: docker-compose restart [서비스명]"
echo ""

log_success "🎉 DuRi Control System이 성공적으로 시작되었습니다!" 