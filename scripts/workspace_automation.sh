#!/bin/bash

# DuRi Workspace 자동화 스크립트
# 서브모듈 푸시, Docker 정리, Redis 영속성 확인을 자동화합니다.

set -e

echo "🚀 DuRi Workspace 자동화 스크립트"
echo "================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. 서브모듈 상태 확인 및 푸시
submodule_push() {
    log_info "서브모듈 상태 확인 및 푸시"

    # duri_core
    if [ -d "duri_core" ]; then
        log_info "duri_core 서브모듈 처리"
        cd duri_core
        if git status --porcelain | grep -q .; then
            log_warning "duri_core에 커밋되지 않은 변경사항이 있습니다"
            git add .
            git commit -m "chore: update submodule changes"
        fi
        git push origin HEAD || log_warning "duri_core 푸시 실패 (인증 문제일 수 있음)"
        cd ..
    fi

    # duri_common
    if [ -d "duri_common" ]; then
        log_info "duri_common 서브모듈 처리"
        cd duri_common
        if git status --porcelain | grep -q .; then
            log_warning "duri_common에 커밋되지 않은 변경사항이 있습니다"
            git add .
            git commit -m "chore: update submodule changes"
        fi
        git push origin HEAD || log_warning "duri_common 푸시 실패 (인증 문제일 수 있음)"
        cd ..
    fi

    log_success "서브모듈 처리 완료"
}

# 2. Docker 시스템 정리
docker_cleanup() {
    log_info "Docker 시스템 정리"

    # 현재 상태 확인
    log_info "현재 Docker 시스템 상태:"
    docker system df

    # Dangling 이미지 정리
    log_info "Dangling 이미지 정리 중..."
    docker image prune -f

    # 빌드 캐시 정리 (7일 이상)
    log_info "오래된 빌드 캐시 정리 중..."
    docker buildx prune --filter until=168h -f

    # 미사용 볼륨 정리
    log_info "미사용 볼륨 정리 중..."
    docker volume prune -f

    log_success "Docker 정리 완료"

    # 정리 후 상태
    log_info "정리 후 Docker 시스템 상태:"
    docker system df
}

# 3. Redis 영속성 확인
redis_persistence_check() {
    log_info "Redis 영속성 확인"

    # Redis 컨테이너 상태 확인
    if ! docker compose -p duriworkspace ps duri-redis | grep -q "Up"; then
        log_error "Redis 컨테이너가 실행 중이지 않습니다"
        return 1
    fi

    # 테스트 키 설정
    log_info "테스트 키 설정 중..."
    docker compose -p duriworkspace exec duri-redis redis-cli SET duri:auto_test "자동화 테스트 $(date)"

    # Redis 재시작
    log_info "Redis 컨테이너 재시작 중..."
    docker compose -p duriworkspace restart duri-redis
    sleep 5

    # 키 존속 확인
    log_info "키 존속 확인 중..."
    result=$(docker compose -p duriworkspace exec duri-redis redis-cli GET duri:auto_test)

    if [ -n "$result" ]; then
        log_success "Redis 영속성 확인 완료: $result"
    else
        log_error "Redis 영속성 테스트 실패"
        return 1
    fi
}

# 4. 서비스 헬스체크
health_check() {
    log_info "서비스 헬스체크"

    services=("duri_core:8080" "duri_brain:8081" "duri_evolution:8082" "duri_control:8083")

    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)

        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$name 서비스 정상"
        else
            log_warning "$name 서비스 응답 없음"
        fi
    done
}

# 5. 로깅 테스트
logging_test() {
    log_info "로깅 모듈 테스트"

    if python -m pytest tests/test_logging_shadowing.py -v > /dev/null 2>&1; then
        log_success "로깅 모듈 테스트 통과"
    else
        log_error "로깅 모듈 테스트 실패"
        return 1
    fi
}

# 메인 실행
main() {
    echo
    log_info "DuRi Workspace 자동화 시작"
    echo

    # 옵션 처리
    case "${1:-all}" in
        "submodule")
            submodule_push
            ;;
        "docker")
            docker_cleanup
            ;;
        "redis")
            redis_persistence_check
            ;;
        "health")
            health_check
            ;;
        "logging")
            logging_test
            ;;
        "all")
            submodule_push
            docker_cleanup
            redis_persistence_check
            health_check
            logging_test
            ;;
        *)
            echo "사용법: $0 [submodule|docker|redis|health|logging|all]"
            echo "기본값: all"
            exit 1
            ;;
    esac

    echo
    log_success "DuRi Workspace 자동화 완료!"
    echo
    log_info "다음 명령어로 수동 실행 가능:"
    echo "  $0 submodule  # 서브모듈 푸시"
    echo "  $0 docker     # Docker 정리"
    echo "  $0 redis      # Redis 영속성 확인"
    echo "  $0 health     # 서비스 헬스체크"
    echo "  $0 logging    # 로깅 테스트"
    echo "  $0 all        # 전체 실행"
}

# 스크립트 실행
main "$@"
