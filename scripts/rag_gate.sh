#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C.UTF-8

# --- Locale guard: ko_KR 없어도 경고 안 나게 고정 ---
if locale -a 2>/dev/null | grep -qi '^c\.utf-8$'; then
  export LC_ALL=C.UTF-8 LANG=C.UTF-8
else
  export LC_ALL=C LANG=C
fi

QUIET="${QUIET:-0}"

GT="${1:?usage: rag_gate.sh <ground_truth.tsv>}"

# --- load gate file with LOWER precedence than env ---
if [[ -f "$GT.gate" ]]; then
  while IFS='=' read -r key val; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    # trim whitespace from value
    val="$(echo "$val" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    # set only if not already set in environment and value is not empty
    if [[ -z "${!key+x}" && -n "$val" ]]; then
      export "$key"="$val"
    fi
  done < "$GT.gate"
fi

# final fallbacks
: "${K:=3}"
: "${THRESH_P:=0.30}"
: "${SEARCH:=scripts/rag_search_enhanced.sh}"

# 숫자 검증(오타 방지)
[[ "$THRESH_P" =~ ^[0-9]+(\.[0-9]+)?$ ]] || { echo "[gate] bad THRESH_P: $THRESH_P" >&2; exit 2; }
[[ "$K" =~ ^[0-9]+$ ]] || { echo "[gate] bad K: $K" >&2; exit 2; }

# 진단 편의용 디버그 출력
echo "[gate] K=$K THRESH_P=$THRESH_P SEARCH=${SEARCH:-scripts/rag_search_enhanced.sh}"

tmp_out="$(mktemp)"; tmp_err="$(mktemp)"; trap 'rm -f "$tmp_out" "$tmp_err"' EXIT
if ! bash scripts/rag_eval.sh "$GT" >"$tmp_out" 2>"$tmp_err"; then
  echo "[gate] ERROR: rag_eval failed (exit code != 0)" >&2
  sed -n '1,120p' "$tmp_err" >&2
  exit 2
fi

# 게이트 출력 모드 토글(조용한 CI 로그용)
if (( ! QUIET )); then
  printf '%s\n' "$tmp_out" | sed -n '1,40p' >&2
fi

line="$(grep -E "^micro_p@${K}[[:space:]]" "$tmp_out" | head -n1 || true)"
if [[ -z "${line//[[:space:]]/}" ]]; then
  echo "[gate] ERROR: micro_p@${K} not found" >&2
  echo "--- stdout(head) ---" >&2; sed -n '1,80p' "$tmp_out" >&2
  echo "--- stderr(head) ---" >&2; sed -n '1,80p' "$tmp_err" >&2
  exit 3
fi

mp="$(printf '%s' "$line" | cut -f2 | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')"
echo "[gate] micro_p@${K}=${mp} (threshold=${THRESH_P})" >&2

# JUnit XML 출력 (CI 대시보드 녹색 체크용)
if [[ -n "${JUNIT_OUT:-}" ]]; then
  {
    echo '<testsuite name="rag-gate" tests="1" failures="'$([[ "$mp" < "$THRESH_P" ]] && echo 1 || echo 0)'" time="0">'
    echo '  <testcase name="micro_p@'"$K"' >= '"$THRESH_P"'">'
    [[ "$mp" < "$THRESH_P" ]] && echo '    <failure message="micro_p@'"$K"'='"$mp"' below threshold '"$THRESH_P"'"/>'
    echo '  </testcase>'
    echo '</testsuite>'
  } > "$JUNIT_OUT"
fi

awk -v m="$mp" -v t="$THRESH_P" 'BEGIN{ exit((m+0 >= t+0)?0:1) }'
