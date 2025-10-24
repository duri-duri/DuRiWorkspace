#!/usr/bin/env bash
# 서브모듈 동기화 공통 라이브러리
# SSH로 연결된 duri_core, duri_brain, duri_evolution, duri_control 동기화

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

# 서브모듈 목록
SUBMODULES=("duri_core" "duri_brain" "duri_evolution" "duri_control")

# 서브모듈 상태 확인
check_submodule_status() {
    log_info "서브모듈 상태 확인 중..."

    for submodule in "${SUBMODULES[@]}"; do
        if [ -d "$submodule" ]; then
            log_info "✅ $submodule 디렉토리 존재"

            # Git 상태 확인 (서브모듈은 .git 파일로 연결됨)
            if [ -f "$submodule/.git" ] || [ -d "$submodule/.git" ]; then
                log_info "✅ $submodule Git 리포지토리 존재"

                # 현재 브랜치 확인
                cd "$submodule"
                current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
                log_info "   현재 브랜치: $current_branch"
                cd ..
            else
                log_warning "⚠️ $submodule Git 리포지토리 없음"
            fi
        else
            log_error "❌ $submodule 디렉토리 없음"
        fi
    done
}

# 서브모듈 동기화 (읽기 전용 - 로컬 변경사항 보존)
sync_submodules() {
    log_info "서브모듈 동기화 시작 (읽기 전용 모드)..."

    for submodule in "${SUBMODULES[@]}"; do
        if [ -d "$submodule" ]; then
            log_info "🔄 $submodule 동기화 중..."

            cd "$submodule"

            # 로컬 변경사항 확인
            local_changes=$(git status --porcelain 2>/dev/null || echo "")
            if [[ -n "$local_changes" ]]; then
                log_warning "⚠️ $submodule에 로컬 변경사항 감지됨 - 동기화 중단"
                log_warning "   변경사항: $local_changes"
                log_warning "   로컬 변경사항을 커밋하거나 stash 후 다시 시도하세요"
                cd ..
                continue
            fi

            # 현재 커밋 확인
            current_commit=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
            log_info "   현재 커밋: ${current_commit:0:8}"

            # 원격 정보 확인
            if git remote -v | grep -q origin; then
                log_info "   원격 저장소: $(git remote get-url origin)"

                # 원격 변경사항 가져오기
                if git fetch origin 2>/dev/null; then
                    log_success "✅ $submodule fetch 완료"

                    # Fast-forward merge 시도 (로컬 변경사항 없을 때만)
                    if git merge --ff-only origin/main 2>/dev/null || git merge --ff-only origin/master 2>/dev/null; then
                        log_success "✅ $submodule 최신 커밋으로 업데이트 완료"
                    else
                        log_warning "⚠️ $submodule Fast-forward 불가능 (충돌 또는 로컬 변경사항)"
                    fi
                else
                    log_warning "⚠️ $submodule fetch 실패 (네트워크 또는 권한 문제)"
                fi
            else
                log_warning "⚠️ $submodule 원격 저장소 없음"
            fi

            cd ..
        else
            log_error "❌ $submodule 디렉토리 없음 - 동기화 건너뜀"
        fi
    done
}

# 서브모듈 변경사항 커밋 및 푸시
commit_and_push_submodules() {
    log_info "서브모듈 변경사항 커밋 및 푸시 시작..."

    for submodule in "${SUBMODULES[@]}"; do
        if [ -d "$submodule" ]; then
            cd "$submodule"

            # 변경사항 확인 (pyc 파일 제외)
            changes=$(git status --porcelain | grep -v '\.pyc$' | grep -v '__pycache__/' || true)
            if [[ -n "$changes" ]]; then
                log_info "🔄 $submodule 변경사항 발견 - 커밋 중..."

                # pyc 파일 제외하고 변경사항 추가
                git add . 2>/dev/null || true
                git reset HEAD '*.pyc' '__pycache__/' 2>/dev/null || true

                # 커밋 메시지 생성
                commit_msg="Auto-sync: $(date '+%Y-%m-%d %H:%M:%S') - Shadow training integration"

                # 커밋
                if git commit -m "$commit_msg" 2>/dev/null; then
                    log_success "✅ $submodule 커밋 완료"

                    # 푸시
                    current_branch=$(git branch --show-current 2>/dev/null || echo "main")
                    if git push origin "$current_branch" 2>/dev/null; then
                        log_success "✅ $submodule 푸시 완료"
                    else
                        log_warning "⚠️ $submodule 푸시 실패 (네트워크 또는 권한 문제)"
                    fi
                else
                    log_warning "⚠️ $submodule 커밋 실패 (변경사항 없음 또는 충돌)"
                fi
            else
                log_info "ℹ️ $submodule 변경사항 없음 (pyc 파일 제외)"
            fi

            cd ..
        fi
    done
}

# 메인 서브모듈 동기화 함수
sync_all_submodules() {
    log_info "=== 서브모듈 전체 동기화 시작 ==="

    # 1. 상태 확인
    check_submodule_status

    # 2. 동기화 (pull)
    sync_submodules

    # 3. 변경사항 커밋 및 푸시
    commit_and_push_submodules

    log_success "=== 서브모듈 전체 동기화 완료 ==="
}

# Docker 컨테이너 재빌드 (서브모듈 변경사항 반영)
rebuild_containers() {
    log_info "Docker 컨테이너 재빌드 시작..."

    # 서브모듈 변경사항이 있으면 컨테이너 재빌드
    local need_rebuild=false

    for submodule in "${SUBMODULES[@]}"; do
        if [ -d "$submodule" ]; then
            cd "$submodule"
            if git status --porcelain | grep -q .; then
                need_rebuild=true
                log_info "🔄 $submodule 변경사항 감지 - 재빌드 필요"
            fi
            cd ..
        fi
    done

    if [ "$need_rebuild" = true ]; then
        log_info "🔄 Docker 컨테이너 재빌드 중..."

        # 각 서비스별 재빌드
        for submodule in "${SUBMODULES[@]}"; do
            case "$submodule" in
                "duri_core")
                    log_info "🔄 duri-core 컨테이너 재빌드..."
                    docker compose -p duriworkspace build duri-core
                    docker compose -p duriworkspace up -d duri-core
                    ;;
                "duri_brain")
                    log_info "🔄 duri-brain 컨테이너 재빌드..."
                    docker compose -p duriworkspace build duri-brain
                    docker compose -p duriworkspace up -d duri-brain
                    ;;
                "duri_evolution")
                    log_info "🔄 duri-evolution 컨테이너 재빌드..."
                    docker compose -p duriworkspace build duri-evolution
                    docker compose -p duriworkspace up -d duri-evolution
                    ;;
                "duri_control")
                    log_info "🔄 duri-control 컨테이너 재빌드..."
                    docker compose -p duriworkspace build duri-control
                    docker compose -p duriworkspace up -d duri-control
                    ;;
            esac
        done

        log_success "✅ Docker 컨테이너 재빌드 완료"
    else
        log_info "ℹ️ 변경사항 없음 - 재빌드 건너뜀"
    fi
}

# 전체 동기화 및 재빌드
full_sync_and_rebuild() {
    log_info "=== 전체 동기화 및 재빌드 시작 ==="

    # 1. 서브모듈 동기화
    sync_all_submodules

    # 2. Docker 컨테이너 재빌드
    rebuild_containers

    log_success "=== 전체 동기화 및 재빌드 완료 ==="
}

# 스크립트 직접 실행 시
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-full}" in
        "check")
            check_submodule_status
            ;;
        "sync")
            sync_all_submodules
            ;;
        "rebuild")
            rebuild_containers
            ;;
        "full")
            full_sync_and_rebuild
            ;;
        *)
            echo "사용법: $0 [check|sync|rebuild|full]"
            echo "  check  - 서브모듈 상태만 확인"
            echo "  sync   - 서브모듈 동기화만"
            echo "  rebuild - Docker 컨테이너 재빌드만"
            echo "  full   - 전체 동기화 및 재빌드 (기본값)"
            exit 1
            ;;
    esac
fi
