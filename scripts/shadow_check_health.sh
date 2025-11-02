#!/usr/bin/env bash
# Shadow 훈련장 상태 확인 스크립트
# 사용법: bash scripts/shadow_check_health.sh [--verbose]

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 로그 함수
log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }
log_section() { echo -e "\n${CYAN}=== $* ===${NC}"; }

# 옵션 파싱
VERBOSE=0
if [[ "${1:-}" == "--verbose" || "${1:-}" == "-v" ]]; then
    VERBOSE=1
fi

# 작업 디렉토리 확인
cd /home/duri/DuRiWorkspace || {
    log_error "DuRiWorkspace 디렉토리를 찾을 수 없습니다."
    exit 1
}

# 통계 변수
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 체크 함수
check_pass() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    log_success "$1"
    [ "$VERBOSE" = "1" ] && [ -n "${2:-}" ] && echo "  └─ $2"
}

check_fail() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
    log_error "$1"
    [ "$VERBOSE" = "1" ] && [ -n "${2:-}" ] && echo "  └─ $2"
}

check_warn() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    log_warning "$1"
    [ "$VERBOSE" = "1" ] && [ -n "${2:-}" ] && echo "  └─ $2"
}

# ==========================================
# 1. 파일 구조 확인
# ==========================================
log_section "1. 파일 구조 확인"

if [ -f "scripts/shadow_duri_integration_final.sh" ]; then
    check_pass "Shadow 메인 스크립트 존재" "scripts/shadow_duri_integration_final.sh"
else
    check_fail "Shadow 메인 스크립트 없음" "scripts/shadow_duri_integration_final.sh"
fi

if [ -f "scripts/lib/transport.sh" ]; then
    check_pass "전송 어댑터 존재" "scripts/lib/transport.sh"
else
    check_fail "전송 어댑터 없음" "scripts/lib/transport.sh"
fi

if [ -f "shadow/metrics_exporter_enhanced.py" ]; then
    check_pass "메트릭 Exporter 존재" "shadow/metrics_exporter_enhanced.py"
else
    check_fail "메트릭 Exporter 없음" "shadow/metrics_exporter_enhanced.py"
fi

if [ -f ".shadow/ALLOW_RUN" ]; then
    check_pass "승인 플래그 존재" ".shadow/ALLOW_RUN"
else
    check_warn "승인 플래그 없음" "Shadow 실행 시 필요: mkdir -p .shadow && touch .shadow/ALLOW_RUN"
fi

# ==========================================
# 2. DuRi AI 서비스 확인
# ==========================================
log_section "2. DuRi AI 서비스 확인"

# Docker 컨테이너 확인
DOCKER_SERVICES=("duri-core" "duri-brain" "duri-evolution" "duri-control")
DOCKER_UP=0
for service in "${DOCKER_SERVICES[@]}"; do
    if docker ps --format "{{.Names}}" | grep -q "^${service}$"; then
        DOCKER_UP=$((DOCKER_UP + 1))
    fi
done

if [ "$DOCKER_UP" -eq 4 ]; then
    check_pass "모든 Docker 서비스 실행 중" "$DOCKER_UP/4 컨테이너"
else
    check_fail "일부 Docker 서비스 미실행" "$DOCKER_UP/4 컨테이너 실행 중"
fi

# HTTP 헬스 체크
HTTP_SERVICES=(
    "8080:core"
    "8081:brain"
    "8082:evolution"
    "8083:control"
)

HTTP_UP=0
for svc in "${HTTP_SERVICES[@]}"; do
    port="${svc%%:*}"
    name="${svc##*:}"
    if curl -sf --max-time 2 "http://localhost:${port}/health" >/dev/null 2>&1; then
        HTTP_UP=$((HTTP_UP + 1))
        [ "$VERBOSE" = "1" ] && check_pass "${name} HTTP 헬스 체크" "포트 ${port}"
    else
        [ "$VERBOSE" = "1" ] && check_fail "${name} HTTP 헬스 체크" "포트 ${port}"
    fi
done

if [ "$HTTP_UP" -eq 4 ]; then
    check_pass "모든 HTTP 서비스 응답" "$HTTP_UP/4 서비스"
else
    check_warn "일부 HTTP 서비스 미응답" "$HTTP_UP/4 서비스 응답"
fi

# SSH 연결 확인
SSH_SERVICES=(
    "2220:core"
    "2221:brain"
    "2222:evolution"
    "2223:control"
)

SSH_UP=0
for svc in "${SSH_SERVICES[@]}"; do
    port="${svc%%:*}"
    name="${svc##*:}"
    if timeout 2 ssh -p "$port" -o ConnectTimeout=1 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost "echo OK" >/dev/null 2>&1; then
        SSH_UP=$((SSH_UP + 1))
        [ "$VERBOSE" = "1" ] && check_pass "${name} SSH 연결" "포트 ${port}"
    else
        [ "$VERBOSE" = "1" ] && check_warn "${name} SSH 연결 실패" "포트 ${port} (HTTP 모드 사용 가능)"
    fi
done

if [ "$SSH_UP" -ge 2 ]; then
    check_pass "SSH 연결 가능" "$SSH_UP/4 서비스 (하이브리드 모드 사용 가능)"
elif [ "$SSH_UP" -ge 1 ]; then
    check_warn "일부 SSH 연결 실패" "$SSH_UP/4 서비스 (HTTP 모드 권장)"
else
    check_warn "SSH 연결 불가" "HTTP 모드로 실행 권장"
fi

# ==========================================
# 3. 전송 어댑터 확인
# ==========================================
log_section "3. 전송 어댑터 확인"

if source scripts/lib/transport.sh 2>/dev/null; then
    check_pass "전송 어댑터 로드 성공"
    
    # 함수 존재 확인
    if declare -f call_service >/dev/null 2>&1; then
        check_pass "call_service 함수 사용 가능"
    else
        check_fail "call_service 함수 없음"
    fi
    
    # HTTP 호출 테스트
    if call_service "core" "/health" "GET" "" >/dev/null 2>&1; then
        check_pass "HTTP 호출 테스트 성공" "core 서비스"
    else
        check_fail "HTTP 호출 테스트 실패" "core 서비스"
    fi
else
    check_fail "전송 어댑터 로드 실패"
fi

# ==========================================
# 4. 메트릭 Exporter 확인
# ==========================================
log_section "4. 메트릭 Exporter 확인"

# Exporter 프로세스 확인
if pgrep -f "metrics_exporter_enhanced.py" >/dev/null 2>&1; then
    EXPORTER_PID=$(pgrep -f "metrics_exporter_enhanced.py" | head -1)
    check_pass "메트릭 Exporter 실행 중" "PID: $EXPORTER_PID"
else
    check_warn "메트릭 Exporter 미실행" "수동 시작: python3 shadow/metrics_exporter_enhanced.py &"
fi

# 메트릭 HTTP 노출 확인
if curl -sf --max-time 2 "http://localhost:9109/metrics" >/dev/null 2>&1; then
    check_pass "메트릭 HTTP 노출 확인" "포트 9109"
    
    if [ "$VERBOSE" = "1" ]; then
        METRIC_COUNT=$(curl -sf "http://localhost:9109/metrics" 2>/dev/null | grep -c "duri_shadow" || echo "0")
        echo "  └─ Shadow 메트릭 수: $METRIC_COUNT"
    fi
else
    check_warn "메트릭 HTTP 노출 불가" "포트 9109 확인 필요"
fi

# 메트릭 파일 확인
if [ -f "var/metrics/transport_metrics.prom" ]; then
    METRIC_LINES=$(wc -l < "var/metrics/transport_metrics.prom" 2>/dev/null || echo "0")
    check_pass "메트릭 파일 존재" "$METRIC_LINES 줄"
else
    check_warn "메트릭 파일 없음" "Shadow 실행 후 생성됨"
fi

# ==========================================
# 5. Shadow 실행 상태 확인
# ==========================================
log_section "5. Shadow 실행 상태 확인"

# PID 파일 확인
if [ -f "var/run/shadow.pid" ]; then
    SHADOW_PID=$(cat "var/run/shadow.pid" 2>/dev/null)
    if ps -p "${SHADOW_PID:-0}" >/dev/null 2>&1; then
        check_pass "Shadow 실행 중" "PID: $SHADOW_PID"
    else
        check_warn "Shadow PID 파일 존재하나 프로세스 없음" "PID: $SHADOW_PID"
    fi
else
    check_warn "Shadow 미실행" "PID 파일 없음"
fi

# 로그 파일 확인
if [ -f "var/logs/shadow.log" ]; then
    LOG_SIZE=$(stat -c%s "var/logs/shadow.log" 2>/dev/null || echo "0")
    LOG_LINES=$(wc -l < "var/logs/shadow.log" 2>/dev/null || echo "0")
    LOG_SIZE_MB=$((LOG_SIZE / 1024 / 1024))
    check_pass "로그 파일 존재" "${LOG_SIZE_MB}MB, ${LOG_LINES}줄"
    
    if [ "$VERBOSE" = "1" ]; then
        echo "  └─ 최근 로그 (마지막 3줄):"
        tail -n 3 "var/logs/shadow.log" 2>/dev/null | sed 's/^/      /'
    fi
else
    check_warn "로그 파일 없음" "Shadow 실행 후 생성됨"
fi

# EV 번들 확인
EV_COUNT=$(find var/evolution -maxdepth 1 -type d -name "EV-*" 2>/dev/null | wc -l)
if [ "$EV_COUNT" -gt 0 ]; then
    LATEST_EV=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
    if [ -n "$LATEST_EV" ]; then
        EV_AGE=$(stat -c %Y "$LATEST_EV" 2>/dev/null || echo "0")
        NOW=$(date +%s)
        EV_AGE_SEC=$((NOW - EV_AGE))
        EV_AGE_MIN=$((EV_AGE_SEC / 60))
        check_pass "EV 번들 존재" "$EV_COUNT개 (최신: ${EV_AGE_MIN}분 전)"
        
        if [ "$VERBOSE" = "1" ] && [ -f "$LATEST_EV/summary.txt" ]; then
            echo "  └─ 최신 EV 번들: $(basename "$LATEST_EV")"
            if grep -q "transport=" "$LATEST_EV/summary.txt" 2>/dev/null; then
                TRANSPORT_MODE=$(grep "transport=" "$LATEST_EV/summary.txt" | cut -d= -f2)
                echo "  └─ Transport 모드: $TRANSPORT_MODE"
            fi
        fi
    fi
else
    check_warn "EV 번들 없음" "Shadow 실행 후 생성됨"
fi

# ==========================================
# 6. 종합 상태 리포트
# ==========================================
log_section "종합 상태 리포트"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  총 체크: $TOTAL_CHECKS"
echo "  ✓ 통과: $PASSED_CHECKS"
echo "  ✗ 실패: $FAILED_CHECKS"
echo "  ⚠ 경고: $((TOTAL_CHECKS - PASSED_CHECKS - FAILED_CHECKS))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 상태 판정
if [ "$FAILED_CHECKS" -eq 0 ] && [ "$PASSED_CHECKS" -ge $((TOTAL_CHECKS * 7 / 10)) ]; then
    log_success "Shadow 훈련장 상태: 정상"
    echo ""
    echo "💡 다음 단계:"
    echo "   1. Shadow 훈련 시작: TRANSPORT=http bash scripts/shadow_duri_integration_final.sh"
    echo "   2. 로그 모니터링: tail -f var/logs/shadow.log"
    echo "   3. 메트릭 확인: curl -s http://localhost:9109/metrics | grep duri_shadow"
    exit 0
elif [ "$FAILED_CHECKS" -le 2 ]; then
    log_warning "Shadow 훈련장 상태: 경고 (일부 기능 제한)"
    echo ""
    echo "💡 권장 조치:"
    echo "   1. 실패한 항목 확인: bash scripts/shadow_check_health.sh --verbose"
    echo "   2. DuRi AI 서비스 시작: docker compose up -d"
    echo "   3. HTTP 모드로 실행: TRANSPORT=http bash scripts/shadow_duri_integration_final.sh"
    exit 1
else
    log_error "Shadow 훈련장 상태: 비정상"
    echo ""
    echo "💡 즉시 조치 필요:"
    echo "   1. 상세 확인: bash scripts/shadow_check_health.sh --verbose"
    echo "   2. 파일 구조 확인: ls -la scripts/lib/transport.sh shadow/metrics_exporter_enhanced.py"
    echo "   3. Docker 서비스 확인: docker ps | grep duri"
    exit 2
fi

