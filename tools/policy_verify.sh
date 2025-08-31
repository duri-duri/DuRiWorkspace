#!/usr/bin/env bash
set -euo pipefail
usage(){ echo "usage: $0 --policy PATH [--plan PLAN.json] [--scan]"; }
POLICY="" PLAN="" SCAN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --policy) POLICY="$2"; shift 2;;
    --plan)   PLAN="$2"; shift 2;;
    --scan)   SCAN=1; shift;;
    *) usage; exit 2;;
  esac
done
[[ -s "$POLICY" ]] || { echo "[ERR] policy not found: $POLICY"; exit 2; }

# read YAML (awk/grep 기반 단순 파서)
mapfile -t WL < <(awk '/^whitelist:/{f=1;next}/^[^ -]/{f=0} f && /^\s*-/{sub(/^\s*-\s*/,"");print}' "$POLICY")
mapfile -t BL < <(awk '/^blacklist:/{f=1;next}/^[^ -]/{f=0} f && /^\s*-/{sub(/^\s*-\s*/,"");print}' "$POLICY")

# 파일 후보 집합
collect_candidates(){
  local arr=()
  for p in "${WL[@]}"; do
    while IFS= read -r -d '' f; do arr+=("$f"); done < <(find . -path "./.git" -prune -o -type f -name "$(basename "$p")" -print0 2>/dev/null)
  done
  printf "%s\n" "${arr[@]}" | sort -u
}

in_blacklist(){
  local f="$1"
  for b in "${BL[@]}"; do
    [[ "$f" == */${b##**/} ]] && return 0
    [[ "$f" == $b ]] && return 0
  done
  return 1
}

# PLAN 검사 모드: plan.json 내 파일들이 화이트리스트에 포함·블랙리스트 미포함인지 확인
if (( SCAN==0 )); then
  [[ -s "$PLAN" ]] || { echo "[ERR] --plan required (not scanning)"; exit 2; }
  files=$(jq -r '.plan[].file' "$PLAN")
  bad=0
  for f in $files; do
    ok=1
    # 화이트리스트 일치 여부(패턴 매칭 간단판: 실제 파일 존재 + WL 패턴 basename 매칭)
    match=0
    for w in "${WL[@]}"; do [[ "$f" == $w || "$(basename "$f")" == "$(basename "$w")" ]] && match=1; done
    (( match==1 )) || { echo "[DENY] not whitelisted: $f"; ok=0; }
    in_blacklist "$f" && { echo "[DENY] blacklisted: $f"; ok=0; }
    (( ok==1 )) && echo "[ALLOW] $f"
    (( ok==1 )) || bad=$((bad+1))
  done
  (( bad==0 )) && { echo "[PASS] policy verify OK"; exit 0; } || { echo "[FAIL] policy verify ($bad)"; exit 3; }
fi

# SCAN 모드: 작업트리에서 BL 위반·민감파일 탐지
viol=0
while IFS= read -r f; do
  in_blacklist "$f" && { echo "[DENY] blacklisted present: $f"; viol=$((viol+1)); }
done < <(git ls-files)

# 간단 민감패턴 탐지
grep -RIl --exclude-dir=.git -E 'AKIA[0-9A-Z]{16}|-----BEGIN (RSA|EC) PRIVATE KEY-----|secret_key|password=' . 2>/dev/null | while read -r s; do
  echo "[WARN] secret-like content: $s"
done

(( viol==0 )) && { echo "[PASS] security scan OK"; exit 0; } || { echo "[FAIL] security scan ($viol)"; exit 4; }











