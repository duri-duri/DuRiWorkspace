#!/usr/bin/env bash
# Shadow Tier 관리 스크립트
# Tier-0: 온디맨드, Tier-1: 파일럿, Tier-2: 상시 풀가동

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[✓]${NC} $*"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $*"; }
log_error() { echo -e "${RED}[✗]${NC} $*"; }

cd /home/duri/DuRiWorkspace || exit 1

# Tier 설정 파일
TIER_FILE="var/run/shadow_tier.env"
TIER_STATE_FILE="var/run/shadow_tier.state"

# 현재 Tier 로드
CURRENT_TIER="0"
if [ -f "$TIER_FILE" ]; then
    source "$TIER_FILE" 2>/dev/null || true
    CURRENT_TIER="${SHADOW_TIER:-0}"
fi

# Tier 정의
# Tier-0: 온디맨드 (기본, 안전)
# Tier-1: 파일럿 (하이브리드, 실험)
# Tier-2: 상시 풀가동 (보류)

show_status() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Shadow Tier 상태"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "현재 Tier: $CURRENT_TIER"
    echo ""
    case "$CURRENT_TIER" in
        0)
            echo "  Tier-0: 온디맨드 모드"
            echo "    - HTTP 기본"
            echo "    - 수동 실행만"
            echo "    - 주기적 건강검진"
            ;;
        1)
            echo "  Tier-1: 파일럿 모드"
            echo "    - HTTP 기본 + SSH 플러그인 (온디맨드)"
            echo "    - 하이브리드 전송 지원"
            echo "    - 실험 모드 (30% SSH)"
            ;;
        2)
            echo "  Tier-2: 상시 풀가동 모드"
            echo "    - 자동 카나리 제어기"
            echo "    - 상시 가동"
            echo "    - 카오스 주입 활성화"
            ;;
    esac
    echo ""
    
    # Tier 상태 파일 확인
    if [ -f "$TIER_STATE_FILE" ]; then
        echo "Tier 상태 파일: $TIER_STATE_FILE"
        cat "$TIER_STATE_FILE" | head -10
    fi
}

set_tier() {
    local tier="$1"
    
    case "$tier" in
        0)
            log_info "Tier-0로 전환: 온디맨드 모드"
            cat > "$TIER_FILE" <<EOF
# Shadow Tier 설정
SHADOW_TIER=0
TRANSPORT=http
SSH_CANARY=0.0
CHAOS_ENABLED=0
MODE=ondemand
EOF
            # 카나리 제어기 중지
            if [ -f "var/run/canary_controller.pid" ]; then
                PID=$(cat "var/run/canary_controller.pid" 2>/dev/null)
                if ps -p "${PID:-0}" >/dev/null 2>&1; then
                    kill "$PID" 2>/dev/null || true
                fi
                rm -f "var/run/canary_controller.pid"
            fi
            log_success "Tier-0 설정 완료 (온디맨드)"
            ;;
        1)
            log_info "Tier-1로 전환: 파일럿 모드"
            cat > "$TIER_FILE" <<EOF
# Shadow Tier 설정
SHADOW_TIER=1
TRANSPORT=mixed
SSH_CANARY=0.30
CHAOS_ENABLED=0
MODE=pilot
EOF
            log_success "Tier-1 설정 완료 (파일럿, SSH 30%)"
            ;;
        2)
            log_warning "Tier-2로 전환: 상시 풀가동 모드 (주의)"
            log_warning "48시간 파일럿 검증 후 사용 권장"
            read -p "계속하시겠습니까? (y/N) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "취소됨"
                return 1
            fi
            cat > "$TIER_FILE" <<EOF
# Shadow Tier 설정
SHADOW_TIER=2
TRANSPORT=mixed
SSH_CANARY=0.15
CHAOS_ENABLED=1
MODE=full
EOF
            # 카나리 제어기 시작
            log_info "카나리 제어기 시작..."
            python3 shadow/canary_controller.py &
            echo $! > var/run/canary_controller.pid
            log_success "Tier-2 설정 완료 (상시 풀가동)"
            ;;
        *)
            log_error "알 수 없는 Tier: $tier (0, 1, 2만 가능)"
            return 1
            ;;
    esac
    
    # 상태 저장
    cat > "$TIER_STATE_FILE" <<EOF
# Shadow Tier 상태
tier=$tier
updated_at=$(date -Iseconds)
EOF
    
    CURRENT_TIER="$tier"
    log_success "Tier-$tier 설정 완료"
}

get_kpi() {
    log_info "KPI 수집 중..."
    
    # Evidence Velocity (EV/일)
    EV_COUNT=$(find var/evolution -maxdepth 1 -type d -name "EV-*" -mtime -1 2>/dev/null | wc -l)
    
    # 유의 EV 비율 (p<0.05) - 간단 버전
    # 실제로는 evidence_score.sh 결과 파싱 필요
    SIGNIFICANT_COUNT=0
    TOTAL_COUNT=0
    
    # 알림 경보 수
    ALERT_COUNT=0
    if curl -sf http://localhost:9090/api/v1/alerts >/dev/null 2>&1; then
        ALERT_COUNT=$(curl -sf http://localhost:9090/api/v1/alerts 2>/dev/null | grep -c "ABTestPValueEdgeCase" || echo "0")
    fi
    
    # Exporter/Health 실패율
    EXPORTER_FAIL_RATE=0.0
    if curl -sf http://localhost:9109/metrics >/dev/null 2>&1; then
        EXPORTER_UP=$(curl -sf http://localhost:9109/metrics 2>/dev/null | grep "^duri_shadow_exporter_up" | awk '{print $2}' | head -1)
        if [ "$EXPORTER_UP" != "1" ]; then
            EXPORTER_FAIL_RATE=1.0
        fi
    fi
    
    # CPU/RAM 스파이크 (간단 버전)
    CPU_USAGE=0
    if command -v top >/dev/null 2>&1; then
        CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' | awk '{print int($1)}' || echo "0")
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Shadow KPI (48시간 파일럿 기준)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Evidence Velocity: ${EV_COUNT} EV/일 (목표: ≥24)"
    echo "2. 유의 EV 비율: 측정 중... (목표: HTTP vs SSH 차이 +10~20%p)"
    echo "3. 알림 경보 수: ${ALERT_COUNT}건 (목표: 0건)"
    echo "4. Exporter 실패율: ${EXPORTER_FAIL_RATE} (목표: <0.5%)"
    echo "5. CPU 사용률: ${CPU_USAGE}% (목표: <70%)"
    echo ""
    
    # 판정
    PASSED=0
    if [ "$EV_COUNT" -ge 24 ]; then
        log_success "Evidence Velocity 통과"
        PASSED=$((PASSED + 1))
    else
        log_warning "Evidence Velocity 미달 (${EV_COUNT}/24)"
    fi
    
    if [ "$ALERT_COUNT" -eq 0 ]; then
        log_success "알림 품질 통과"
        PASSED=$((PASSED + 1))
    else
        log_warning "알림 경보 발생 (${ALERT_COUNT}건)"
    fi
    
    if (( $(echo "$EXPORTER_FAIL_RATE < 0.005" | bc -l 2>/dev/null || awk -v r="$EXPORTER_FAIL_RATE" 'BEGIN{if (r < 0.005) print 1; else print 0}') )); then
        log_success "안정성 통과"
        PASSED=$((PASSED + 1))
    else
        log_warning "안정성 미달 (실패율: ${EXPORTER_FAIL_RATE})"
    fi
    
    if [ "$CPU_USAGE" -lt 70 ]; then
        log_success "자원 사용 통과"
        PASSED=$((PASSED + 1))
    else
        log_warning "자원 사용 초과 (CPU: ${CPU_USAGE}%)"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  판정: ${PASSED}/4 지표 통과"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ "$PASSED" -ge 3 ]; then
        log_success "Tier-1 유지 권장 (부분 활성화 지속)"
        return 0
    else
        log_warning "온디맨드 전환 권장 (Tier-0)"
        return 1
    fi
}

# 메인
case "${1:-status}" in
    status)
        show_status
        ;;
    set)
        if [ -z "${2:-}" ]; then
            log_error "사용법: $0 set <tier> (0|1|2)"
            exit 1
        fi
        set_tier "$2"
        ;;
    kpi)
        get_kpi
        ;;
    *)
        echo "사용법: $0 {status|set <tier>|kpi}"
        echo ""
        echo "명령어:"
        echo "  status  - 현재 Tier 상태 확인"
        echo "  set 0   - Tier-0로 전환 (온디맨드)"
        echo "  set 1   - Tier-1로 전환 (파일럿)"
        echo "  set 2   - Tier-2로 전환 (상시 풀가동)"
        echo "  kpi     - KPI 수집 및 판정"
        exit 1
        ;;
esac

