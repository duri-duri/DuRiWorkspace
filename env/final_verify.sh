#!/usr/bin/env bash
# DuRi Phase 3 최종 검증 스크립트
# 기존 검증 스윕 패턴을 따라 구현
# Usage: ./env/final_verify.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

# 로그 함수 (기존 패턴 활용)
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

log "🔍 Phase 3 최종 검증 시작..."

# 1. 환경 준비
log "📋 1. 환경 준비"
source "$WORKSPACE_DIR/env/dev_env.sh"
log "✅ 환경 준비 완료"

# 2. 계약 테스트 (API 동등성)
log "📋 2. 계약 테스트 (API 동등성)"
cd "$WORKSPACE_DIR"
pytest -q tests/contracts -k "reasoning" || {
    log "❌ 계약 테스트 실패"
    exit 1
}
log "✅ 계약 테스트 통과"

# 3. 스모크 테스트 (안전망)
log "📋 3. 스모크 테스트 (안전망)"
pytest -q tests/contracts -k "reasoning_smoke" || {
    log "❌ 스모크 테스트 실패"
    exit 1
}
log "✅ 스모크 테스트 통과"

# 4. 정적 분석 (타입 + 스타일)
log "📋 4. 정적 분석 (타입 + 스타일)"
if command -v ruff >/dev/null 2>&1; then
    ruff DuRiCore/reasoning_engine/ || {
        log "❌ Ruff 스타일 검사 실패"
        exit 1
    }
    log "✅ Ruff 스타일 검사 통과"
else
    log "⚠️ Ruff 없음, 스타일 검사 건너뜀"
fi

if command -v mypy >/dev/null 2>&1; then
    mypy DuRiCore/reasoning_engine/ --ignore-missing-imports || {
        log "❌ MyPy 타입 검사 실패"
        exit 1
    }
    log "✅ MyPy 타입 검사 통과"
else
    log "⚠️ MyPy 없음, 타입 검사 건너뜀"
fi

# 5. 안전 커밋 (추가 전용)
log "📋 5. 안전 커밋 (추가 전용)"
./safe_additive_commit.sh || {
    log "❌ 안전 커밋 실패"
    exit 1
}

log "🎉 Phase 3 최종 검증 완료!"
log "✅ 모든 검증 통과 - 안전하게 커밋됨"
