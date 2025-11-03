#!/usr/bin/env bash
# 하이브리드 전송 어댑터 - HTTP/SSH 선택적 사용
# 기존 코드 패턴 준수: set -euo pipefail, jq 사용, 변수 초기화

set -Eeuo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin"

# 색상 정의 (기존 lib 패턴 준수)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수 (기존 lib 패턴)
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# 전송 방식 설정 (기본값 HTTP, 환경변수로 오버라이드)
# DURI_SHADOW_TRANSPORT 또는 TRANSPORT 사용 (기존 코드 호환성)
: "${DURI_SHADOW_TRANSPORT:=${TRANSPORT:-http}}"
: "${TRANSPORT:=$DURI_SHADOW_TRANSPORT}"  # http | ssh | mixed

# HTTP 설정 (기본값)
: "${CORE_HOST:=localhost}"
: "${CORE_PORT:=8080}"
: "${BRAIN_HOST:=localhost}"
: "${BRAIN_PORT:=8081}"
: "${EVOLUTION_HOST:=localhost}"
: "${EVOLUTION_PORT:=8082}"
: "${CONTROL_HOST:=localhost}"
: "${CONTROL_PORT:=8083}"

# SSH 설정 (기본값 - Docker 컨테이너 SSH 포트)
: "${CORE_SSH:=root@localhost:2220}"
: "${BRAIN_SSH:=root@localhost:2221}"
: "${EVOLUTION_SSH:=root@localhost:2222}"
: "${CONTROL_SSH:=root@localhost:2223}"

# 카나리 설정 (mixed 모드용)
# 환경 변수 파일에서 동적 값 읽기 (카나리 제어기 지원)
if [ -f "var/run/canary.env" ]; then
    source "var/run/canary.env" 2>/dev/null || true
fi
: "${SSH_CANARY:=0.15}"  # 15% 확률로 SSH 사용 (초기값, 카나리 제어기로 자동 조절)
: "${SSH_TIMEOUT:=8}"    # SSH 타임아웃 (초)
: "${SSH_RETRY:=2}"      # SSH 재시도 횟수
: "${CHAOS_ENABLED:=1}"  # 카오스 주입 활성화 (1=활성, 0=비활성)
: "${CHAOS_DELAY_PROB:=0.005}"  # 지연 카오스 확률 (0.5%)
: "${CHAOS_DROP_PROB:=0.01}"   # 패킷 드롭 카오스 확률 (1%)

# 메트릭 디렉토리
: "${METRICS_DIR:=var/metrics}"
mkdir -p "$METRICS_DIR" 2>/dev/null || true

# JSON 처리 함수 (jq 사용, 기존 패턴)
json_escape() {
    if command -v jq >/dev/null 2>&1; then
        jq -c .
    else
        # jq 없을 때 fallback (최소한의 이스케이프)
        sed 's/\\/\\\\/g; s/"/\\"/g'
    fi
}

# 메트릭 기록 함수 (기존 ab_eval.prom 패턴 활용)
# Prometheus textfile 형식으로 기록하여 exporter가 주기적으로 읽도록 함
record_transport_metric() {
    local mode="$1"  # http | ssh
    local service="$2"  # core | brain | evolution | control
    local status="$3"  # success | failure
    
    local metric_file="${METRICS_DIR}/transport_metrics.prom"
    local timestamp=$(date +%s)
    
    # Prometheus textfile 형식으로 기록 (기존 ab_eval.prom 패턴)
    # 형식: metric_name{labels} value timestamp
    printf 'duri_shadow_transport_total{mode="%s",service="%s",status="%s"} 1 %d\n' \
        "$mode" "$service" "$status" "$timestamp" >> "$metric_file" 2>/dev/null || true
    
    # 파일 크기 제한 (최근 1000줄만 유지, 기존 패턴)
    if [ -f "$metric_file" ]; then
        local line_count
        line_count=$(wc -l < "$metric_file" 2>/dev/null || echo "0")
        if [ "$line_count" -gt 1000 ]; then
            tail -n 1000 "$metric_file" > "${metric_file}.tmp" 2>/dev/null || true
            mv "${metric_file}.tmp" "$metric_file" 2>/dev/null || true
        fi
    fi
}

# HTTP 호출 함수 (기존 curl 패턴 활용)
call_http() {
    local service="$1"   # core | brain | evolution | control
    local path="$2"      # /api/emotion, /health 등
    local method="${3:-GET}"  # GET | POST
    local data="${4:-}"  # JSON 데이터 (선택)
    
    local host port url
    
    case "$service" in
        core)
            host="${CORE_HOST}"
            port="${CORE_PORT}"
            ;;
        brain)
            host="${BRAIN_HOST}"
            port="${BRAIN_PORT}"
            ;;
        evolution)
            host="${EVOLUTION_HOST}"
            port="${EVOLUTION_PORT}"
            ;;
        control)
            host="${CONTROL_HOST}"
            port="${CONTROL_PORT}"
            ;;
        *)
            log_error "Unknown service: $service"
            return 1
            ;;
    esac
    
    url="http://${host}:${port}${path}"
    
    # curl 호출 (기존 패턴: --fail-with-body, --max-time, --retry)
    if [ -n "$data" ]; then
        # POST 요청
        if ! curl -sSf -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data" \
            --max-time 10 \
            --retry 2 \
            --retry-delay 1; then
            record_transport_metric "http" "$service" "failure"
            return 1
        fi
    else
        # GET 요청
        if ! curl -sSf "$url" \
            --max-time 10 \
            --retry 2 \
            --retry-delay 1; then
            record_transport_metric "http" "$service" "failure"
            return 1
        fi
    fi
    
    record_transport_metric "http" "$service" "success"
    return 0
}

# SSH 호출 함수 (원격 실행 - 컨테이너 내부에서 직접 curl)
# 기존 패턴 활용: docker exec에서 컨테이너 내부 curl 사용하는 방식과 동일
call_ssh() {
    local service="$1"   # core | brain | evolution | control
    local path="$2"      # /api/emotion, /health 등
    local method="${3:-GET}"  # GET | POST
    local data="${4:-}"  # JSON 데이터 (선택)
    
    local ssh_target local_port
    
    # 서비스별 SSH 타겟 및 로컬 포트 확인
    case "$service" in
        core)
            ssh_target="${CORE_SSH}"
            local_port="${CORE_PORT:-8080}"
            ;;
        brain)
            ssh_target="${BRAIN_SSH}"
            local_port="${BRAIN_PORT:-8081}"
            ;;
        evolution)
            ssh_target="${EVOLUTION_SSH}"
            local_port="${EVOLUTION_PORT:-8082}"
            ;;
        control)
            ssh_target="${CONTROL_SSH}"
            local_port="${CONTROL_PORT:-8083}"
            ;;
        *)
            log_error "Unknown service: $service"
            return 1
            ;;
    esac
    
    # SSH 연결 정보 파싱 (user@host:port 또는 host:port)
    local ssh_host ssh_port ssh_user
    if [[ "$ssh_target" =~ ^([^@]+)@([^:]+):([0-9]+)$ ]]; then
        ssh_user="${BASH_REMATCH[1]}"
        ssh_host="${BASH_REMATCH[2]}"
        ssh_port="${BASH_REMATCH[3]}"
    elif [[ "$ssh_target" =~ ^([^:]+):([0-9]+)$ ]]; then
        ssh_user="root"
        ssh_host="${BASH_REMATCH[1]}"
        ssh_port="${BASH_REMATCH[2]}"
    else
        log_error "Invalid SSH target format: $ssh_target (expected: user@host:port or host:port)"
        return 1
    fi
    
    # 카오스 주입 (경량: 0.5~1% 확률의 지연/패킷 드롭 시뮬레이션)
    if [ "${CHAOS_ENABLED:-1}" = "1" ]; then
        local chaos_rand=$(awk 'BEGIN{srand(); printf "%.4f", rand()}')
        
        # 지연 카오스 (0.5% 확률로 50~200ms 지연)
        if (( $(echo "$chaos_rand < $CHAOS_DELAY_PROB" | bc -l 2>/dev/null || awk -v r="$chaos_rand" -v p="$CHAOS_DELAY_PROB" 'BEGIN{if (r < p) print 1; else print 0}') )); then
            local delay_ms=$(awk -v seed=$RANDOM 'BEGIN{srand(seed); printf "%.0f", 50 + rand() * 150}')
            log_info "[CHAOS] SSH 지연 시뮬레이션: ${delay_ms}ms"
            sleep "0.${delay_ms:0:3}" 2>/dev/null || sleep 0.05  # 최소 50ms
        fi
        
        # 패킷 드롭 카오스 (1% 확률로 실패 시뮬레이션)
        local drop_rand=$(awk 'BEGIN{srand(); printf "%.4f", rand()}')
        if (( $(echo "$drop_rand < $CHAOS_DROP_PROB" | bc -l 2>/dev/null || awk -v r="$drop_rand" -v p="$CHAOS_DROP_PROB" 'BEGIN{if (r < p) print 1; else print 0}') )); then
            log_warning "[CHAOS] SSH 패킷 드롭 시뮬레이션"
            record_transport_metric "ssh" "$service" "failure"
            return 1
        fi
    fi
    
    # SSH 옵션 (기존 패턴: StrictHostKeyChecking=no, 비밀번호 없이 키 사용)
    local ssh_opts=(
        -p "$ssh_port"
        -o ConnectTimeout="${SSH_TIMEOUT}"
        -o StrictHostKeyChecking=no
        -o UserKnownHostsFile=/dev/null
        -o LogLevel=ERROR
        -o BatchMode=yes  # 비대화형 (키 인증 필수)
    )
    
    # 지연 시간 측정 시작
    local start_time=$(date +%s%N 2>/dev/null || date +%s)
    
    # 컨테이너 내부에서 직접 curl 호출 (기존 robust_shell_patterns.sh 패턴 활용)
    local url="http://localhost:${local_port}${path}"
    local curl_cmd
    
    if [ -n "$data" ]; then
        # POST 요청 (기존 curl 패턴: --fail-with-body, --max-time, --retry)
        curl_cmd="curl -sSf -X ${method} '${url}' \
            -H 'Content-Type: application/json' \
            -d '${data}' \
            --max-time 10 \
            --retry ${SSH_RETRY} \
            --retry-delay 1"
    else
        # GET 요청
        curl_cmd="curl -sSf '${url}' \
            --max-time 10 \
            --retry ${SSH_RETRY} \
            --retry-delay 1"
    fi
    
    # SSH로 원격 실행 (컨테이너 내부에서 curl 실행)
    local retry_count=0
    local max_retries="${SSH_RETRY}"
    
    while [ $retry_count -le $max_retries ]; do
        if ssh "${ssh_opts[@]}" "${ssh_user}@${ssh_host}" "$curl_cmd" 2>/dev/null; then
            # 지연 시간 측정 종료
            local end_time=$(date +%s%N 2>/dev/null || date +%s)
            local latency_ms=0
            if command -v bc >/dev/null 2>&1; then
                latency_ms=$(echo "scale=0; ($end_time - $start_time) / 1000000" | bc 2>/dev/null || echo "0")
            fi
            
            # 메트릭 기록 (성공)
            record_transport_metric "ssh" "$service" "success"
            
            # 지연 시간 기록 (간단 버전: 파일에 기록, exporter가 읽음)
            if [ "$latency_ms" -gt 0 ]; then
                echo "duri_shadow_ssh_latency_ms{service=\"${service}\"} ${latency_ms}" >> "${METRICS_DIR}/transport_metrics.prom" 2>/dev/null || true
            fi
            
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -le $max_retries ]; then
            sleep 1
        fi
    done
    
    record_transport_metric "ssh" "$service" "failure"
    return 1
}

# 하이브리드 호출 함수 (mixed 모드: 카나리 확률에 따라 HTTP/SSH 선택)
# 기존 설계: 기본 80~90% HTTP, 10~20% 카나리를 SSH에 태워 "진화 자극" 부여
call_mixed() {
    local service="$1"
    local path="$2"
    local method="${3:-GET}"
    local data="${4:-}"
    
    # 카나리 확률 계산 (0~1 사이 랜덤값)
    # awk 사용 (bc 없어도 동작, 기존 패턴)
    local rand=$(awk 'BEGIN{srand(); printf "%.3f", rand()}')
    
    # SSH 사용 여부 결정 (기본값 0.2 = 20%)
    local use_ssh=0
    if command -v bc >/dev/null 2>&1; then
        use_ssh=$(echo "$rand < $SSH_CANARY" | bc -l 2>/dev/null || echo "0")
    else
        # bc 없을 때 awk로 비교 (부동소수점 비교)
        use_ssh=$(awk -v r="$rand" -v c="$SSH_CANARY" 'BEGIN{if (r < c) print 1; else print 0}')
    fi
    
    if [ "$use_ssh" = "1" ]; then
        # SSH 경로 (카나리 - 실전 변이 생성)
        log_info "[MIXED] SSH canary for $service (rand=$rand, threshold=$SSH_CANARY)"
        if call_ssh "$service" "$path" "$method" "$data"; then
            return 0
        else
            # SSH 실패 시 HTTP로 폴백 (안정성 우선)
            log_warning "[MIXED] SSH failed for $service, falling back to HTTP"
            call_http "$service" "$path" "$method" "$data"
        fi
    else
        # HTTP 경로 (기본 - 안정성 우선)
        call_http "$service" "$path" "$method" "$data"
    fi
}

# 통합 호출 함수 (TRANSPORT 변수에 따라 자동 선택)
# 기존 Shadow 스크립트와의 호환성 유지
call_service() {
    local service="$1"   # core | brain | evolution | control
    local path="$2"      # /api/emotion, /health 등
    local method="${3:-GET}"  # GET | POST
    local data="${4:-}"  # JSON 데이터 (선택)
    
    # TRANSPORT 변수 확인 (대소문자 무관)
    local transport_mode
    transport_mode=$(echo "${TRANSPORT:-http}" | tr '[:upper:]' '[:lower:]')
    
    case "$transport_mode" in
        http)
            call_http "$service" "$path" "$method" "$data"
            ;;
        ssh)
            call_ssh "$service" "$path" "$method" "$data"
            ;;
        mixed)
            call_mixed "$service" "$path" "$method" "$data"
            ;;
        *)
            log_error "Unknown TRANSPORT mode: $TRANSPORT (expected: http|ssh|mixed)"
            # Fallback: HTTP 사용
            log_warning "Falling back to HTTP"
            call_http "$service" "$path" "$method" "$data"
            ;;
    esac
}

# 편의 함수들 (기존 Shadow 스크립트와의 호환성)
call_core() {
    local path="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    call_service "core" "$path" "$method" "$data"
}

call_brain() {
    local path="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    call_service "brain" "$path" "$method" "$data"
}

call_evolution() {
    local path="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    call_service "evolution" "$path" "$method" "$data"
}

call_control() {
    local path="$1"
    local method="${2:-GET}"
    local data="${3:-}"
    call_service "control" "$path" "$method" "$data"
}

# 내보내기
export -f call_service call_core call_brain call_evolution call_control
export -f call_http call_ssh call_mixed
export -f record_transport_metric json_escape

