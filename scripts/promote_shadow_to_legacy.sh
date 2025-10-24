#!/usr/bin/env bash
# 훈련장(SSH) → 레거시(HTTPS) 프로모션 스크립트
# 사용법: ./scripts/promote_shadow_to_legacy.sh

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

# 프로모션 대상 브랜치 설정 (훈련장 쪽)
PROMOTE_BRANCHES=(
  "duri_core:chore/metrics-alias-safe-logging"
  "duri_brain:auto/shadow-sync-20251022-155632"
  "duri_evolution:auto/shadow-sync-20251022-155634"
  "duri_control:main"
)

# 타임스탬프 생성
STAMP="$(date +%Y%m%d-%H%M%S)"
PR_PREFIX="pr/shadow-${STAMP}"
TAG_PREFIX="shadow-${STAMP}"

ROOT="/home/duri/DuRiWorkspace"

log_info "🚀 훈련장 → 레거시 프로모션 시작 (${STAMP})"

# 1) 사전 스모크 테스트 (도커 헬스 체크)
log_info "📋 1단계: 사전 스모크 테스트"
log_info "➜ Docker 컨테이너 헬스 체크..."

# 핵심 서비스 헬스 체크
curl -fsS http://localhost:8080/health >/dev/null && log_success "✅ duri-core 헬스 OK" || { log_error "❌ duri-core 헬스 실패"; exit 1; }
curl -fsS http://localhost:8081/health >/dev/null && log_success "✅ duri-brain 헬스 OK" || { log_error "❌ duri-brain 헬스 실패"; exit 1; }
curl -fsS http://localhost:8082/health >/dev/null && log_success "✅ duri-evolution 헬스 OK" || { log_error "❌ duri-evolution 헬스 실패"; exit 1; }
curl -fsS http://localhost:8083/health >/dev/null && log_success "✅ duri-control 헬스 OK" || { log_error "❌ duri-control 헬스 실패"; exit 1; }

# Prometheus 헬스 체크 (선택적)
curl -fsS http://localhost:9090/-/healthy >/dev/null && log_success "✅ Prometheus 헬스 OK" || log_warning "⚠️ Prometheus 헬스 체크 건너뜀"

log_success "✅ 사전 스모크 테스트 통과"

# 2) 모듈별 프로모션
log_info "📋 2단계: 모듈별 프로모션 시작"

for spec in "${PROMOTE_BRANCHES[@]}"; do
  mod="${spec%%:*}"
  br="${spec#*:}"

  log_info "=== 프로모션: $mod@$br → legacy ==="
  cd "$ROOT/$mod"

  # 현재 브랜치 확인
  current_branch=$(git branch --show-current)
  log_info "현재 브랜치: $current_branch"

  # 훈련장에서 최신 코드 가져오기
  log_info "🔄 훈련장에서 최신 코드 가져오기..."
  git fetch origin --tags
  git checkout "$br"
  git pull --rebase origin "$br" || log_warning "⚠️ pull 실패, 현재 상태 유지"

  # 테스트 훅 (모듈별 선택적 실행)
  if [ -f "Makefile" ]; then
    log_info "🧪 Makefile 테스트 실행..."
    make test || log_warning "⚠️ 테스트 실패, 계속 진행"
  elif [ -f "requirements.txt" ] && [ -d "tests" ]; then
    log_info "🧪 pytest 테스트 실행..."
    python -m pytest tests/ -v || log_warning "⚠️ pytest 실패, 계속 진행"
  else
    log_info "ℹ️ 테스트 스킵 (Makefile/pytest 없음)"
  fi

  # 훈련장 스냅샷 태그 생성
  log_info "🏷️ 훈련장 스냅샷 태그 생성..."
  git tag -f "${TAG_PREFIX}-${mod}"
  git push origin "refs/tags/${TAG_PREFIX}-${mod}" --force || log_warning "⚠️ 태그 푸시 실패"

  # 레거시에 PR용 브랜치로 푸시
  PR_BRANCH="${PR_PREFIX}-${mod}"
  log_info "📤 레거시에 PR 브랜치로 푸시: $PR_BRANCH"

  # HTTPS 인증 문제가 있을 수 있으므로 우선 시도
  if git push legacy "HEAD:refs/heads/${PR_BRANCH}" --force; then
    log_success "✅ $mod → legacy/$PR_BRANCH 푸시 성공"
  else
    log_error "❌ $mod → legacy 푸시 실패 (인증 문제일 수 있음)"
    log_info "수동 푸시 명령어:"
    log_info "  cd $ROOT/$mod"
    log_info "  git push legacy HEAD:refs/heads/${PR_BRANCH} --force"
  fi

  echo
done

# 3) 결과 요약
log_success "🎉 프로모션 완료!"
echo
log_info "📋 다음 단계:"
log_info "1) 레거시 GitHub에서 각 ${PR_PREFIX}-* 브랜치로 PR 생성"
log_info "2) CI 통과 후 main/release에 머지"
log_info "3) 서브모듈 포인터 업데이트"
echo
log_info "📊 생성된 태그들:"
for spec in "${PROMOTE_BRANCHES[@]}"; do
  mod="${spec%%:*}"
  echo "  - ${TAG_PREFIX}-${mod}"
done
echo
log_info "🔗 PR 브랜치들:"
for spec in "${PROMOTE_BRANCHES[@]}"; do
  mod="${spec%%:*}"
  echo "  - ${PR_PREFIX}-${mod}"
done

log_success "✅ 훈련장 → 레거시 프로모션 파이프라인 완료!"
