#!/usr/bin/env bash
# yq 없이 동작하는 Gate 검증기
set -euo pipefail
shopt -s globstar nullglob extglob

POLICY=""
PLAN=""

usage(){ echo "usage: $0 --policy policies/...yaml --plan logs/.../plan.json" >&2; }

# ── args
EXPLAIN=0; DRYRUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --policy) POLICY="$2"; shift 2;;
    --plan)   PLAN="$2"; shift 2;;
    --explain) EXPLAIN=1; shift;;
    --dry-run) DRYRUN=1; shift;;
    *) echo "unknown arg: $1" >&2; exit 2;;
  esac
done
[[ -f "${POLICY:-}" && -f "${PLAN:-}" ]] || { usage; exit 2; }

# ── environment hardening
export LC_ALL=C
IFS=$'\n\t'

# ── dependency checks
command -v jq >/dev/null || { echo "[FAIL] missing jq"; exit 2; }

# ── repo root
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  REPO_ROOT="$(pwd)"
fi
export REPO_ROOT

# ── path helpers
is_under_root() {
  local p="$1"
  local abs
  abs="$(realpath -m "$p")" || return 1
  [[ "$abs" == "$REPO_ROOT"* ]]
}

relpath() {
  local p="$1" rp=""
  if rp="$(realpath -m --relative-to="$REPO_ROOT" "$p" 2>/dev/null)"; then
    :
  else
    rp="${p#"$REPO_ROOT"/}"
  fi
  rp="${rp#./}"
  printf '%s\n' "$rp"
}

norm_pattern() {
  local pat="${1#./}"
  printf '%s\n' "$pat"
}

match_glob() {  # [[ path == pattern ]] with globstar
  local path pat
  path="$(relpath "$1")"
  pat="$(norm_pattern "$2")"
  
  # 1) 직접 매치
  [[ "$path" == $pat ]] && return 0

  # 2) '**'가 들어간 패턴은 '0개 디렉터리' 해석도 시도
  #   예: docs/**/*.md  →  docs/*.md 도 추가로 확인
  if [[ "$pat" == *"/**/"* ]]; then
    local pat0="${pat//\/**\//\/}"
    [[ "$path" == $pat0 ]] && return 0
  fi

  # 3) '**'가 꼬리(끝)에 오는 경우도 0-디렉터리 판정 시도
  #   예: duri_modules/**/*.py → duri_modules/*.py
  if [[ "$pat" == *"/**."* || "$pat" == *"/**"* ]]; then
    local pat_tail="${pat/\/**\//\/}"
    [[ "$path" == $pat_tail ]] && return 0
  fi

  return 1
}

# ── load policy lists via Python parser
mapfile -t WL < <(python3 tools/extract_lists.py "$POLICY" | jq -r '.whitelist[]')
mapfile -t BL < <(python3 tools/extract_lists.py "$POLICY" | jq -r '.blacklist[]')

# ── plan schema validation
jq -e '.plan and (.plan|type=="array") and all(.plan[]; has("file"))' "$PLAN" \
  >/dev/null || { echo "[FAIL] invalid plan schema"; exit 2; }

# ── plan files
mapfile -t FILES < <(jq -r '.plan[].file' "$PLAN")

echo "[GATE] policy verification"
policy_sha=$(sha256sum "$POLICY" | cut -d' ' -f1)
[[ $EXPLAIN -eq 1 ]] && echo "[INFO] policy_sha=$policy_sha root=$REPO_ROOT"
rc=0
allow_cnt=0
deny_cnt=0
for raw in "${FILES[@]}"; do
  [[ -n "$raw" ]] || continue
  
  # ── security: root escape prevention
  abs="$(realpath -m "$raw" 2>/dev/null || true)"
  if [[ -z "$abs" ]] || ! is_under_root "$abs"; then
    echo "[DENY] outside repo: $raw"
    rc=$((rc+1)); continue
  fi
  
  f_rel="$(relpath "$raw")"

  # 1) blacklist 우선
  bl_hit=""
  for pat in "${BL[@]}"; do
    [[ -z "$pat" ]] && continue
    if match_glob "$f_rel" "$pat"; then
      bl_hit="$pat"; break
    fi
  done
  if [[ -n "$bl_hit" ]]; then
    echo "[DENY] blacklisted: $raw  (pattern: $bl_hit)"
    [[ $EXPLAIN -eq 1 ]] && echo "[EXPLAIN] $raw -> BL by '$bl_hit'"
    rc=$((rc+1))
    deny_cnt=$((deny_cnt+1))
    continue
  fi

  # 2) whitelist
  wl_hit=""
  for pat in "${WL[@]}"; do
    [[ -z "$pat" ]] && continue
    if match_glob "$f_rel" "$pat"; then
      wl_hit="$pat"; break
    fi
  done

  if [[ -n "$wl_hit" ]]; then
    echo "[ALLOW] $raw  (pattern: $wl_hit)"
    [[ $EXPLAIN -eq 1 ]] && echo "[EXPLAIN] $raw -> WL by '$wl_hit'"
    allow_cnt=$((allow_cnt+1))
  else
    echo "[DENY] not whitelisted: $raw"
    rc=$((rc+1))
    deny_cnt=$((deny_cnt+1))
  fi
done

echo "[SUMMARY] allow=$allow_cnt deny=$deny_cnt files=${#FILES[@]}"
if (( rc )); then
  echo "[FAIL] policy verify ($rc)"
  exit 1
fi
echo "[PASS] policy verified"











