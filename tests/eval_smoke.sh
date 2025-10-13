#!/usr/bin/env bash
set -euo pipefail

# --- Locale guard: ko_KR 없어도 경고 안 나게 고정 ---
if locale -a 2>/dev/null | grep -qi '^c\.utf-8$'; then
  export LC_ALL=C.UTF-8 LANG=C.UTF-8
else
  export LC_ALL=C LANG=C
fi

# --- Defaults (unbound 방지) ---
: "${GT:=.reports/day62/ground_truth_clean.tsv}"
: "${K:=3}"
: "${THRESH_P:=0.30}"
: "${QUIET:=1}"

# --- Run gate ---
out="$(K="$K" THRESH_P="$THRESH_P" QUIET="$QUIET" bash scripts/rag_gate.sh "$GT" 2>&1 || true)"
status=$?

# --- 중복 방지 회귀 테스트 ---
export SEARCH="${SEARCH:-scripts/rag_search.sh}"
if [[ "$SEARCH" == *"enhanced"* ]]; then
  # X-ray 중복 검사
  diff <(bash "$SEARCH" "X-ray" 2>/dev/null | sort) \
       <(bash "$SEARCH" "X-ray" 2>/dev/null | sort | uniq) \
  >/dev/null || { echo "[smoke] duplicate ids detected" >&2; exit 1; }
fi

# --- Minimal, CI-friendly output ---
echo "$out" | sed -n '1,20p'
if [[ $status -eq 0 ]]; then
  echo "OK: gate passed with K=$K"
  exit 0
else
  echo "FAIL: gate failed (exit=$status)"

  # 실패 시 아티팩트 남기기 (디버깅 용이)
  echo "[smoke] Running eval for debugging..." >&2
  bash scripts/rag_eval.sh "$GT" > .reports/last_smoke_eval.tsv 2>&1 || true
  echo "[smoke] Last eval results:" >&2
  sed -n '1,120p' .reports/last_smoke_eval.tsv >&2

  exit $status
fi
