#!/usr/bin/env bash
set -euo pipefail

# Phase 3 최종 검증 스크립트
# 기존 run_verification_sweep.sh 패턴 완전 활용
# Usage: ./scripts/final_verify.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$WORKSPACE_DIR/verify_out"

# 출력 디렉토리 생성 (기존 패턴 활용)
mkdir -p "$OUTPUT_DIR"

# 로그 함수 (기존 패턴과 동일)
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

log "Phase 3 최종 검증 시작"

# 1. 환경 준비
log "환경 준비"
source "$WORKSPACE_DIR/env/dev_env.sh"

# 2. 계약 테스트 (API 동등성) - 기존 Makefile 패턴 활용
log "계약 테스트 실행"
cd "$WORKSPACE_DIR"
pytest -q tests/contracts -k "reasoning" || { log "계약 테스트 실패"; exit 1; }

# 3. 스모크 테스트 (안전망) - 기존 패턴 활용
log "스모크 테스트 실행"
if [ -d "$WORKSPACE_DIR/tests/smoke" ]; then
    pytest -q tests/smoke -k "reasoning" || { log "스모크 테스트 실패"; exit 1; }
else
    pytest -q tests/contracts -k "reasoning_smoke" || { log "스모크 테스트 실패"; exit 1; }
fi

# 4. 정적 분석 (스타일 + 타입) - 기존 check-env 패턴 활용
log "정적 분석 실행"
if command -v ruff >/dev/null 2>&1; then
    ruff DuRiCore/reasoning_engine/ || { log "Ruff 실패"; exit 1; }
else
    log "Ruff 없음, 스타일 검사 건너뜀"
fi

if command -v mypy >/dev/null 2>&1; then
    mypy DuRiCore/reasoning_engine/ --ignore-missing-imports || { log "MyPy 실패"; exit 1; }
else
    log "MyPy 없음, 타입 검사 건너뜀"
fi

# 5. 안전 커밋 - 기존 패턴 활용
log "안전 커밋 실행"
"$WORKSPACE_DIR/safe_additive_commit.sh"

log "최종 검증 완료"
