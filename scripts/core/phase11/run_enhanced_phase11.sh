#!/usr/bin/env bash
"""
Phase 11 Enhanced Orchestrator 실행 스크립트

기존 DuRi 시스템들을 통합하고 Insight Engine과 연동하는
향상된 오케스트레이터를 실행합니다.

Usage:
    ./run_enhanced_phase11.sh [options]

Options:
    --demo          데모 모드로 실행 (기본값)
    --interactive   대화형 모드로 실행
    --status        시스템 상태만 확인
    --help          도움말 표시
"""

set -euo pipefail

# 스크립트 디렉터리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# 로깅 설정
LOG_FILE="${PROJECT_ROOT}/logs/phase11_enhanced_orchestrator.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 색상 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${PURPLE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

show_help() {
    cat << EOF
Phase 11 Enhanced Orchestrator 실행 스크립트

Usage: $0 [options]

Options:
    --demo          데모 모드로 실행 (기본값)
    --interactive   대화형 모드로 실행  
    --status        시스템 상태만 확인
    --help          이 도움말 표시

Examples:
    $0                    # 데모 모드 실행
    $0 --demo            # 데모 모드 실행
    $0 --interactive     # 대화형 모드 실행
    $0 --status          # 시스템 상태 확인

Features:
    - 기존 DuRiCore 오케스트레이터 통합
    - Insight Engine 연동
    - 내부 사고 시스템 강화
    - 통합 학습 시스템 활용
    - 실시간 품질 계측

Logs:
    로그 파일: $LOG_FILE
EOF
}

check_dependencies() {
    log "의존성 확인 중..."
    
    # Python 3.11+ 확인
    if ! command -v python3 &> /dev/null; then
        error "Python3가 설치되지 않았습니다"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log "Python 버전: $python_version"
    
    # 필요한 모듈 확인
    if ! python3 -c "import asyncio, json, logging, time, datetime, pathlib" 2>/dev/null; then
        error "필요한 Python 모듈이 없습니다"
        exit 1
    fi
    
    # DuRiCore 디렉터리 확인
    if [ ! -d "$PROJECT_ROOT/DuRiCore" ]; then
        warn "DuRiCore 디렉터리를 찾을 수 없습니다. 일부 기능이 제한될 수 있습니다."
    fi
    
    # Insight Engine 확인
    if [ ! -d "$PROJECT_ROOT/insight" ]; then
        warn "Insight Engine 디렉터리를 찾을 수 없습니다. 기본 모드로 실행됩니다."
    fi
    
    success "의존성 확인 완료"
}

run_demo() {
    log "Phase 11 Enhanced 오케스트레이터 데모 모드 실행"
    
    cd "$PROJECT_ROOT"
    
    # 환경 변수 설정
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # 데모 실행
    python3 "$SCRIPT_DIR/enhanced_orchestrator.py"
    
    if [ $? -eq 0 ]; then
        success "데모 실행 완료"
    else
        error "데모 실행 실패"
        exit 1
    fi
}

run_interactive() {
    log "Phase 11 Enhanced 오케스트레이터 대화형 모드 실행"
    warn "대화형 모드는 아직 구현되지 않았습니다. 데모 모드로 실행합니다."
    run_demo
}

check_status() {
    log "Phase 11 Enhanced 시스템 상태 확인"
    
    cd "$PROJECT_ROOT"
    
    # 오케스트레이터 파일 존재 확인
    if [ ! -f "$SCRIPT_DIR/enhanced_orchestrator.py" ]; then
        error "향상된 오케스트레이터 파일이 없습니다: $SCRIPT_DIR/enhanced_orchestrator.py"
        exit 1
    fi
    
    # Python 문법 검사
    if python3 -m py_compile "$SCRIPT_DIR/enhanced_orchestrator.py"; then
        success "향상된 오케스트레이터 파일 문법 검사 통과"
    else
        error "향상된 오케스트레이터 파일 문법 오류"
        exit 1
    fi
    
    # 기존 시스템 파일 확인
    info "기존 시스템 파일 확인:"
    
    if [ -f "$PROJECT_ROOT/DuRiCore/duri_orchestrator.py" ]; then
        success "DuRiCore 오케스트레이터 발견"
    else
        warn "DuRiCore 오케스트레이터를 찾을 수 없습니다"
    fi
    
    if [ -f "$PROJECT_ROOT/DuRiCore/inner_thinking_system.py" ]; then
        success "내부 사고 시스템 발견"
    else
        warn "내부 사고 시스템을 찾을 수 없습니다"
    fi
    
    if [ -f "$PROJECT_ROOT/DuRiCore/unified_learning_system.py" ]; then
        success "통합 학습 시스템 발견"
    else
        warn "통합 학습 시스템을 찾을 수 없습니다"
    fi
    
    if [ -f "$PROJECT_ROOT/DuRiCore/integrated_system_manager.py" ]; then
        success "통합 시스템 매니저 발견"
    else
        warn "통합 시스템 매니저를 찾을 수 없습니다"
    fi
    
    if [ -d "$PROJECT_ROOT/insight" ]; then
        success "Insight Engine 발견"
    else
        warn "Insight Engine을 찾을 수 없습니다"
    fi
    
    # 로그 파일 확인
    if [ -f "$LOG_FILE" ]; then
        log "로그 파일 크기: $(du -h "$LOG_FILE" | cut -f1)"
        log "최근 로그 (마지막 5줄):"
        tail -5 "$LOG_FILE" | sed 's/^/  /'
    else
        warn "로그 파일이 없습니다: $LOG_FILE"
    fi
    
    success "시스템 상태 확인 완료"
}

run_integration_test() {
    log "Phase 11 통합 테스트 실행"
    
    cd "$PROJECT_ROOT"
    
    # 환경 변수 설정
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # 통합 테스트 실행
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from scripts.core.phase11.enhanced_orchestrator import EnhancedDuRiOrchestrator
    print('✅ EnhancedDuRiOrchestrator 임포트 성공')
    
    orchestrator = EnhancedDuRiOrchestrator()
    print('✅ EnhancedDuRiOrchestrator 초기화 성공')
    
    status = orchestrator.get_phase11_status_report()
    print(f'✅ 상태 리포트 생성 성공: {len(status)} 항목')
    
    print('✅ 통합 테스트 완료')
except Exception as e:
    print(f'❌ 통합 테스트 실패: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        success "통합 테스트 완료"
    else
        error "통합 테스트 실패"
        exit 1
    fi
}

# 메인 실행 로직
main() {
    log "Phase 11 Enhanced Orchestrator 시작"
    
    # 인수 처리
    case "${1:-}" in
        --demo|"")
            check_dependencies
            run_demo
            ;;
        --interactive)
            check_dependencies
            run_interactive
            ;;
        --status)
            check_status
            ;;
        --test)
            check_dependencies
            run_integration_test
            ;;
        --help|-h)
            show_help
            ;;
        *)
            error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"

