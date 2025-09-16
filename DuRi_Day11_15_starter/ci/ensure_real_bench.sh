#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

fail() { echo "::error:: $*"; exit 1; }

# 1) bin/trace_bench 커밋 금지
if git ls-files --error-unmatch "bin/trace_bench" >/dev/null 2>&1; then
  fail "bin/trace_bench is checked in. Commit forbidden. Use TRACE_BENCH_CMD to point to real bench."
fi

# 2) 스크립트 내 더미/폴백 금지
if grep -RIl --exclude-dir=.git -E 'dummy|simulator|AWK.*rand\(|/bin/true|auto-generate.*trace_bench' "$ROOT/tools" 2>/dev/null | grep -q .; then
  fail "Found dummy/simulator fallback in tools/. Remove dummy logic from bench runners."
fi

# 3) run_trace_bench.sh: 실벤치 검증 필수 플로우 확인
runner="tools/run_trace_bench.sh"
[[ -x "$runner" ]] || fail "tools/run_trace_bench.sh not executable."

# self-check 또는 version 체크를 코드에 포함했는지 정적 점검(간단한 검증)
grep -Eq -- '--self-check|--version' "$runner" || fail "run_trace_bench.sh must verify real bench (--self-check/--version)."

# 4) 환경 변수 강제: TRACE_BENCH_CMD 없으면 실패하도록 구성되었는지 (선호)
grep -Eq 'TRACE_BENCH_CMD' "$runner" || echo "::warning:: TRACE_BENCH_CMD lookup not found; ensure PATH-only discovery is sufficient."

echo "[OK] CI guard: no dummy & real bench verification enforced."
