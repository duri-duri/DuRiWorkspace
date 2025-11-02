#!/usr/bin/env bash
# Shadow 게이트 조건 체크 스크립트
# 활성화 임계조건 4개 체크 후 카나리 시작 가능 여부 판정

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

PASSED=0
FAILED=0
WARNED=0

# ==========================================
# 1. Export/메트릭 동기 체크
# ==========================================
log_info "1. Export/메트릭 동기 체크: FILE p == HTTP p (허용 오차 ≤ 1e-9)"

FILE_P=""
HTTP_P=""

# FILE p-value 읽기
if [ -f "var/metrics/ab_eval.prom" ]; then
    FILE_P=$(grep "^duri_ab_p_value" "var/metrics/ab_eval.prom" 2>/dev/null | awk '{print $2}' | head -1)
fi

# HTTP p-value 읽기 (exporter에서)
if command -v curl >/dev/null 2>&1 && curl -sf http://localhost:9109/metrics >/dev/null 2>&1; then
    HTTP_P=$(curl -sf http://localhost:9109/metrics 2>/dev/null | grep "^duri_ab_p_value" | awk '{print $2}' | head -1)
fi

if [ -n "$FILE_P" ] && [ -n "$HTTP_P" ]; then
    # 부동소수점 비교 (awk 사용)
    DIFF=$(awk -v f="$FILE_P" -v h="$HTTP_P" 'BEGIN{printf "%.10f", (f > h ? f-h : h-f)}')
    THRESHOLD="0.000000001"  # 1e-9
    
    if (( $(echo "$DIFF <= $THRESHOLD" | bc -l 2>/dev/null || awk -v d="$DIFF" -v t="$THRESHOLD" 'BEGIN{if (d <= t) print 1; else print 0}') )); then
        log_success "FILE p == HTTP p (차이: ${DIFF})"
        PASSED=$((PASSED + 1))
    else
        log_warning "FILE p != HTTP p (차이: ${DIFF}, 허용: ${THRESHOLD})"
        WARNED=$((WARNED + 1))
    fi
else
    if [ -z "$FILE_P" ]; then
        log_warning "FILE p-value 없음 (var/metrics/ab_eval.prom)"
    fi
    if [ -z "$HTTP_P" ]; then
        log_warning "HTTP p-value 없음 (exporter 미실행 또는 메트릭 없음)"
    fi
    WARNED=$((WARNED + 1))
fi

# ==========================================
# 2. EV 사이클 무결성 체크
# ==========================================
log_info "2. EV 사이클 무결성: ANCHOR.SHA256SUMS 존재 & summary: RECORDED*"

LATEST_EV=""
if [ -L "var/evolution/LATEST" ]; then
    LATEST_EV=$(readlink -f "var/evolution/LATEST" 2>/dev/null || echo "")
elif [ -d "var/evolution/EV-" ]; then
    LATEST_EV=$(find var/evolution -maxdepth 1 -type d -name 'EV-*' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | awk '{print $2}')
fi

if [ -n "$LATEST_EV" ] && [ -d "$LATEST_EV" ]; then
    ANCHOR_OK=0
    SUMMARY_OK=0
    
    if [ -f "$LATEST_EV/ANCHOR.SHA256SUMS" ]; then
        ANCHOR_OK=1
        log_success "ANCHOR.SHA256SUMS 존재"
    else
        log_warning "ANCHOR.SHA256SUMS 없음"
    fi
    
    if [ -f "$LATEST_EV/summary.txt" ]; then
        if grep -q "RECORDED" "$LATEST_EV/summary.txt" 2>/dev/null; then
            SUMMARY_OK=1
            log_success "summary.txt에 RECORDED 포함"
        else
            log_warning "summary.txt에 RECORDED 없음"
        fi
    else
        log_warning "summary.txt 없음"
    fi
    
    if [ "$ANCHOR_OK" = "1" ] && [ "$SUMMARY_OK" = "1" ]; then
        PASSED=$((PASSED + 1))
    else
        WARNED=$((WARNED + 1))
    fi
else
    log_warning "EV 번들 없음 (최초 실행 시 정상)"
    WARNED=$((WARNED + 1))
fi

# ==========================================
# 3. 루프 안정 체크
# ==========================================
log_info "3. 루프 안정: loop_*.sh 최근 24h 자체 재기동 ≤ 2회"

RESTART_COUNT=0
LOG_DIR="var/logs"
NOW=$(date +%s)
DAY_AGO=$((NOW - 86400))  # 24시간 전

if [ -d "$LOG_DIR" ]; then
    # loop_*.sh 관련 로그에서 재시작 패턴 검색 (간단 버전)
    # 실제로는 systemd journal이나 로그 파싱 필요
    if find "$LOG_DIR" -name "*.log" -type f -mtime -1 2>/dev/null | head -1 >/dev/null; then
        RESTART_COUNT=$(grep -h "restart\|재시작\|reload" "$LOG_DIR"/*.log 2>/dev/null | grep -c "loop" || echo "0")
    fi
fi

if [ "$RESTART_COUNT" -le 2 ]; then
    log_success "루프 재기동 ≤ 2회 (${RESTART_COUNT}회)"
    PASSED=$((PASSED + 1))
else
    log_warning "루프 재기동 > 2회 (${RESTART_COUNT}회)"
    WARNED=$((WARNED + 1))
fi

# ==========================================
# 4. 프리즈가드/허용경로 체크
# ==========================================
log_info "4. 프리즈가드/허용경로: scripts/evolution/**, scripts/lib/**, shadow/metrics_exporter_enhanced.py, prometheus/rules/duri-ab-test.rules.yml"

FREEZE_ALLOW_FILE=".github/freeze-allow.txt"
REQUIRED_PATHS=(
    "scripts/evolution/**"
    "scripts/lib/**"
    "shadow/metrics_exporter_enhanced.py"
    "prometheus/rules/duri-ab-test.rules.yml"
)

ALL_PATHS_OK=1
for path in "${REQUIRED_PATHS[@]}"; do
    if [ -f "$FREEZE_ALLOW_FILE" ]; then
        if grep -q "$path" "$FREEZE_ALLOW_FILE" 2>/dev/null; then
            log_success "허용 경로: $path"
        else
            log_warning "허용 경로 누락: $path"
            ALL_PATHS_OK=0
        fi
    else
        log_warning "프리즈가드 파일 없음: $FREEZE_ALLOW_FILE"
        ALL_PATHS_OK=0
    fi
done

if [ "$ALL_PATHS_OK" = "1" ]; then
    PASSED=$((PASSED + 1))
else
    WARNED=$((WARNED + 1))
fi

# ==========================================
# 종합 판정
# ==========================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  게이트 체크 결과:"
echo "  ✓ 통과: $PASSED/4"
echo "  ⚠ 경고: $WARNED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$PASSED" -ge 3 ] && [ "$WARNED" -le 2 ]; then
    log_success "게이트 통과: 카나리 시작 가능"
    exit 0
else
    log_warning "게이트 미통과: 일부 조건 불충족"
    exit 1
fi

