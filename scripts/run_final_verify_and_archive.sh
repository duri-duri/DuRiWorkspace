#!/usr/bin/env bash
set -Eeuo pipefail

# Phase 3 최종 검증 래퍼 스크립트
# 기존 아티팩트 패턴 완전 활용
# Usage: ./scripts/run_final_verify_and_archive.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS="$(date +%Y%m%d_%H%M)"
OUT="$ROOT/var/reports/final_verify_${TS}"

# 출력 디렉토리 생성 (기존 패턴 활용)
mkdir -p "$OUT"

# 로그 함수 (기존 패턴과 동일)
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

log "final_verify 실행 시작 → $OUT/run.log"

# 최종 검증 스크립트 실행 + 전체 로그 보관 (기존 패턴 활용)
bash "$ROOT/scripts/final_verify.sh" 2>&1 | tee "$OUT/run.log"

# 리포트 보강 (기존 패턴 활용)
if command -v pytest >/dev/null 2>&1; then
    log "contracts junit 리포트 생성"
    pytest tests/contracts -k "reasoning" \
        --junitxml="$OUT/contracts.junit.xml" || true

    if [ -d "$ROOT/tests/smoke" ]; then
        log "smoke junit 리포트 생성"
        pytest tests/smoke -k "reasoning" \
            --junitxml="$OUT/smoke.junit.xml" || true
    else
        pytest tests/contracts -k "reasoning_smoke" \
            --junitxml="$OUT/smoke.junit.xml" || true
    fi
fi

if command -v ruff >/dev/null 2>&1; then
    log "ruff 리포트 생성"
    ruff DuRiCore/reasoning_engine/ | tee "$OUT/ruff.txt" || true
fi

if command -v mypy >/dev/null 2>&1; then
    log "mypy 리포트 생성"
    mypy DuRiCore/reasoning_engine/ --ignore-missing-imports | tee "$OUT/mypy.txt" || true
fi

log "아티팩트 저장 완료: $OUT"
