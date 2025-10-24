#!/usr/bin/env bash
# SSH 분산 아키텍처 - 서브모듈 독립 실행 스크립트

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# 서비스별 포트 설정
declare -A SERVICE_PORTS=(
    ["duri_core"]="8080"
    ["duri_brain"]="8081"
    ["duri_evolution"]="8082"
    ["duri_control"]="8083"
)

# 서비스별 실행 명령
declare -A SERVICE_COMMANDS=(
    ["duri_core"]="cd duri_core && python -m flask --app app run --host=0.0.0.0 --port=8080"
    ["duri_brain"]="cd duri_brain && python -c 'from app import create_app; app=create_app(); app.run(host=\"0.0.0.0\", port=8081)'"
    ["duri_evolution"]="cd duri_evolution && python -c 'from app import create_app; app=create_app(); app.run(host=\"0.0.0.0\", port=8082)'"
    ["duri_control"]="cd duri_control && python run.py"
)

# 서비스 시작
start_service() {
    local service=$1
    local port=${SERVICE_PORTS[$service]}

    log_info "🚀 $service 서비스 시작 (포트: $port)..."

    # 포트 사용 확인
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "⚠️ 포트 $port가 이미 사용 중입니다. 기존 프로세스를 종료합니다."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi

    # 서비스 실행 (백그라운드)
    eval "${SERVICE_COMMANDS[$service]}" &
    local pid=$!

    # 프로세스 ID 저장
    echo $pid > "/tmp/duri_${service}.pid"

    # 서비스 시작 확인
    sleep 3
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
        log_success "✅ $service 서비스 시작 완료 (PID: $pid, 포트: $port)"
    else
        log_error "❌ $service 서비스 시작 실패"
        return 1
    fi
}

# 서비스 중지
stop_service() {
    local service=$1

    log_info "🛑 $service 서비스 중지..."

    local pid_file="/tmp/duri_${service}.pid"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log_success "✅ $service 서비스 중지 완료 (PID: $pid)"
        else
            log_warning "⚠️ $service 프로세스가 이미 종료되었습니다."
        fi
        rm -f "$pid_file"
    else
        log_warning "⚠️ $service PID 파일을 찾을 수 없습니다."
    fi
}

# 모든 서비스 시작
start_all() {
    log_info "🚀 모든 DuRi 서비스 시작..."

    for service in "${!SERVICE_PORTS[@]}"; do
        start_service "$service"
    done

    log_success "🎉 모든 서비스 시작 완료!"
    log_info "📊 서비스 상태 확인:"
    for service in "${!SERVICE_PORTS[@]}"; do
        local port=${SERVICE_PORTS[$service]}
        echo "  - $service: http://localhost:$port"
    done
}

# 모든 서비스 중지
stop_all() {
    log_info "🛑 모든 DuRi 서비스 중지..."

    for service in "${!SERVICE_PORTS[@]}"; do
        stop_service "$service"
    done

    log_success "✅ 모든 서비스 중지 완료!"
}

# 서비스 상태 확인
status() {
    log_info "📊 서비스 상태 확인..."

    for service in "${!SERVICE_PORTS[@]}"; do
        local port=${SERVICE_PORTS[$service]}
        local pid_file="/tmp/duri_${service}.pid"

        if [[ -f "$pid_file" ]]; then
            local pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
                    log_success "✅ $service: 실행 중 (PID: $pid, 포트: $port)"
                else
                    log_warning "⚠️ $service: 프로세스는 실행 중이지만 응답하지 않음 (PID: $pid)"
                fi
            else
                log_error "❌ $service: 프로세스가 종료됨 (PID: $pid)"
            fi
        else
            log_error "❌ $service: 실행되지 않음"
        fi
    done
}

# 메인 함수
main() {
    case "${1:-start}" in
        "start")
            start_all
            ;;
        "stop")
            stop_all
            ;;
        "restart")
            stop_all
            sleep 2
            start_all
            ;;
        "status")
            status
            ;;
        "start-service")
            if [[ -z "${2:-}" ]]; then
                log_error "❌ 서비스명을 지정해주세요."
                echo "사용법: $0 start-service <service_name>"
                echo "사용 가능한 서비스: ${!SERVICE_PORTS[*]}"
                exit 1
            fi
            start_service "$2"
            ;;
        "stop-service")
            if [[ -z "${2:-}" ]]; then
                log_error "❌ 서비스명을 지정해주세요."
                echo "사용법: $0 stop-service <service_name>"
                echo "사용 가능한 서비스: ${!SERVICE_PORTS[*]}"
                exit 1
            fi
            stop_service "$2"
            ;;
        *)
            echo "사용법: $0 {start|stop|restart|status|start-service|stop-service}"
            echo ""
            echo "명령어:"
            echo "  start          - 모든 서비스 시작"
            echo "  stop           - 모든 서비스 중지"
            echo "  restart        - 모든 서비스 재시작"
            echo "  status         - 서비스 상태 확인"
            echo "  start-service  - 특정 서비스 시작"
            echo "  stop-service   - 특정 서비스 중지"
            echo ""
            echo "사용 가능한 서비스: ${!SERVICE_PORTS[*]}"
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"
