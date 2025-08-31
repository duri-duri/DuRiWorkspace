#!/usr/bin/env bash
# yq 없이 동작하는 Gate 검증기
set -euo pipefail

# allow sourcing without running main
if [[ "${BASH_SOURCE[0]}" != "$0" ]]; then
  return 0 2>/dev/null || exit 0
fi
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

# === PATCH: BEGIN ===
shopt -s extglob nullglob globstar

# repo root
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  REPO_ROOT="$(git rev-parse --show-toplevel)"
else
  REPO_ROOT="$(pwd)"
fi

# fast relative path
relpath() {
  local p="$1" rp=""
  if rp="$(realpath -m --relative-to="$REPO_ROOT" "$p" 2>/dev/null)"; then :; else rp="${p#"$REPO_ROOT"/}"; fi
  printf '%s\n' "${rp#./}"
}

# 경로 컴포넌트 중 하나라도 심볼릭이면 true
path_has_symlink() {
  local rel="$1" base="$REPO_ROOT"
  local IFS='/'; local comp
  for comp in $rel; do
    base="$base/$comp"
    if [[ -L "$base" || -h "$base" ]]; then
      return 0
    fi
  done
  return 1
}

# 실제 대상 경로가 반드시 repo 안에 있어야 함. 실패/외부면 DENY.
is_under_root_resolved() {
  local rel="$1"
  local abs="$REPO_ROOT/$rel"
  local tgt
  tgt="$(readlink -f "$abs")" || return 1
  [[ "$tgt" == "$REPO_ROOT"* ]]
}

# 0-depth 지원 매처(/**/ → /)
match_glob_0depth() {
  local path="$1" pat="$2"
  pat="${pat#./}"
  [[ "$path" == $pat ]] && return 0
  if [[ "$pat" == *"/**/"* ]]; then
    local p0="${pat//\/**\//\/}"
    [[ "$path" == $p0 ]] && return 0
  fi
  return 1
}

make_union() {
  # stdin: 패턴들(줄 단위)
  local pats=() p p0 p1
  while IFS= read -r p; do
    [[ -z "$p" ]] && continue
    p="${p#./}"
    pats+=("$p")
    # A) 중간 "/**/" -> "/" (0-depth)
    if [[ "$p" == *"/**/"* ]]; then
      p0="${p//\/**\//\/}"
      pats+=("$p0")
    fi
    # B) 선두 "**/" -> "" (예: **/*.env => *.env)
    if [[ "$p" == **/* ]]; then
      p1="${p#**/}"
      [[ "$p1" != "**" ]] && pats+=("$p1")
    fi
    # C) 자기자신 "**"는 생성/유지하지 않음(전부 매칭 방지)
    [[ "$p" == "**" ]] && unset 'pats[${#pats[@]}-1]'
  done
  # 간단 dedup
  local uniq=() seen
  for p in "${pats[@]}"; do
    [[ -z "${p}" ]] && continue
    seen="|$p|"
    [[ " ${uniq[*]} " == *" $seen "* ]] && continue
    uniq+=("$p")
  done
  local IFS='|'
  printf '@(%s)\n' "${uniq[*]}"
}
# === PATCH: END ===

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

# compile union patterns for O(1) match
WL_UNION="$(printf '%s\n' "${WL[@]}" | make_union)"
BL_UNION="$(printf '%s\n' "${BL[@]}" | make_union)"

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
  
  raw="$raw"
  f_rel="$(relpath "$raw")"

  # 0) path validation first
  if path_has_symlink "$f_rel" || ! is_under_root_resolved "$f_rel"; then
    echo "[DENY] outside repo: $raw"
    ((EXPLAIN)) && echo "[EXPLAIN] $raw -> symlink/escape detected"
    rc=$((rc+1)); continue
  fi

  # 1) BL ≻ WL
  if [[ -n "$BL_UNION" && "$f_rel" == $BL_UNION ]]; then
    echo "[DENY] blacklisted: $raw"
    ((EXPLAIN)) && echo "[EXPLAIN] $raw -> BL(union)"
    rc=$((rc+1)); continue
  else
    bl_hit=""
    for pat in "${BL[@]}"; do
      match_glob_0depth "$f_rel" "$pat" && { bl_hit="$pat"; break; }
    done
    if [[ -n "$bl_hit" ]]; then
      echo "[DENY] blacklisted: $raw"
      ((EXPLAIN)) && echo "[EXPLAIN] $raw -> BL by '$bl_hit'"
      rc=$((rc+1)); continue
    fi
  fi

  # 2) WL
  if [[ -n "$WL_UNION" && "$f_rel" == $WL_UNION ]]; then
    echo "[ALLOW] $raw  (union)"
    ((EXPLAIN)) && echo "[EXPLAIN] $raw -> WL(union)"
    continue
  else
    wl_hit=""
    for pat in "${WL[@]}"; do
      match_glob_0depth "$f_rel" "$pat" && { wl_hit="$pat"; break; }
    done
    if [[ -n "$wl_hit" ]]; then
      echo "[ALLOW] $raw  (pattern: $wl_hit)"
      ((EXPLAIN)) && echo "[EXPLAIN] $raw -> WL by '$wl_hit'"
      continue
    fi
  fi

  # 3) 최종 거부
  echo "[DENY] not whitelisted: $raw"
  rc=$((rc+1))
done

echo "[SUMMARY] allow=$allow_cnt deny=$deny_cnt files=${#FILES[@]}"
if (( rc )); then
  echo "[FAIL] policy verify ($rc)"
  exit 1
fi
echo "[PASS] policy verified"











