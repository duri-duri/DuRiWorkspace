#!/usr/bin/env bash
set -euo pipefail

# --- 기본 설정 ---------------------------------------------------------------
PROFILE="${PROFILE:-duri}"
CONFIG="${CONFIG:-configs/retention.yml}"
BASE_ROOT="${BASE_ROOT:-/mnt/c/Users/admin/Desktop/두리백업}"
LEVEL="${LEVEL:-}"                 # override: --level CORE|EXTENDED|FULL
KEEP="${KEEP:-}"                   # override: --keep N (CORE/EXTENDED)
POLICY="${POLICY:-}"               # override: --policy "8w+monthly" (FULL)
DRY_RUN=0                          # --dry-run
LOG="${LOG:-$PWD/var/log/rotate.log}"

mkdir -p "$(dirname "$LOG")"

usage() {
  cat <<USAGE
Usage: $0 [--profile duri] [--config configs/retention.yml] [--base-root PATH]
          [--level CORE|EXTENDED|FULL] [--keep N] [--policy "8w+monthly"] [--dry-run]
Examples:
  $0 --level CORE --keep 14 --dry-run
  $0 --level EXTENDED --keep 8
  $0 --level FULL --policy "8w+monthly" --dry-run
  $0 --profile duri --config configs/retention.yml
USAGE
  exit 2
}

log(){ echo "[$(date +'%F %T')] $*" | tee -a "$LOG"; }
have(){ command -v "$1" >/dev/null 2>&1; }

# --- 인자 파싱 ----------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2;;
    --config) CONFIG="$2"; shift 2;;
    --base-root) BASE_ROOT="$2"; shift 2;;
    --level) LEVEL="$2"; shift 2;;
    --keep) KEEP="$2"; shift 2;;
    --policy) POLICY="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) usage;;
    *) echo "unknown arg: $1"; usage;;
  esac
done

# --- YAML 로드(간단 파서: jq 있으면 yq 대체) ----------------------------------
# 기대 형식: retention.yml 예시 참고
load_from_yaml() {
  if [[ -f "$CONFIG" ]] && have python3; then
python3 - <<PY 2>/dev/null
import sys, yaml, json
with open("$CONFIG", "r", encoding="utf-8") as f:
    y = yaml.safe_load(f)
print(json.dumps(y.get("profiles", {}).get("$PROFILE", {})))
PY
  else
    echo "{}"
  fi
}

PROFILE_JSON="$(load_from_yaml)"
if have jq; then
  LEVEL="${LEVEL:-$(jq -r '.level // empty' <<<"$PROFILE_JSON")}"
  KEEP="${KEEP:-$(jq -r '.keep // empty' <<<"$PROFILE_JSON")}"
  POLICY="${POLICY:-$(jq -r '.policy // empty' <<<"$PROFILE_JSON")}"
fi

[[ -z "${LEVEL:-}" ]] && { echo "LEVEL이 필요합니다 (CORE|EXTENDED|FULL)."; usage; }

# --- 후보 수집 ---------------------------------------------------------------
# 형식: .../YYYY/MM/DD/LEVEL__YYYY-MM-DD__HHMM__host-*.tar.*
mapfile -t ALL < <(find "$BASE_ROOT" -type f -regextype posix-extended \
  -regex ".*/${LEVEL}__[^/]+\.tar\.(zst|gz)$" -print0 | xargs -0 ls -1t 2>/dev/null || true)

TOTAL="${#ALL[@]}"
[[ "$TOTAL" -eq 0 ]] && { log "no archives found for LEVEL=$LEVEL under $BASE_ROOT"; exit 0; }

# --- 보존 규칙: CORE/EXTENDED = 최신 N개 -------------------------------------
keep_latest_n() {
  local n="$1"
  local -a keep=("${ALL[@]:0:$n}")
  local -a purge=("${ALL[@]:$n}")

  log "LEVEL=$LEVEL keep latest $n of $TOTAL (base=$BASE_ROOT)"
  for f in "${keep[@]}"; do log "KEEP  $f"; done
  for f in "${purge[@]}"; do
    if [[ "$DRY_RUN" -eq 1 ]]; then
      log "DRY   rm $f"
    else
      rm -f -- "$f" && log "DEL   $f"
    fi
  done
}

# --- 보존 규칙: FULL = "8w+monthly" ------------------------------------------
# - 최근 8주: 각 ISO 주별 최신 1개 보존
# - 월별: 각 월의 최신 1개 추가 보존(중복은 자연히 제거)
# - 나머지는 삭제
keep_full_weekly_monthly() {
  local weeks=8
  local -A keepmap=()

  # 주별(최근 8주)
  local now=$(date +%s)
  for f in "${ALL[@]}"; do
    # 파일 mtime을 기준으로 주키 생성(ISO 주)
    local ts=$(date -r "$f" +%s 2>/dev/null || stat -c %Y "$f")
    local age_days=$(( (now - ts) / 86400 ))
    local week_key
    week_key="$(date -d @"$ts" +%G-W%V)"  # e.g., 2025-W33
    # 최근 8주 이내만 후보
    if (( age_days <= 7*weeks )); then
      # 주별 최신 1개만 (ls -t 정렬이므로 처음 만나는 게 최신)
      [[ -n "${keepmap[$week_key]:-}" ]] || keepmap["$week_key"]="$f"
    fi
  done

  # 월별(12개월 보존 예시)
  for f in "${ALL[@]}"; do
    local ts=$(date -r "$f" +%s 2>/dev/null || stat -c %Y "$f")
    local month_key
    month_key="$(date -d @"$ts" +%Y-%m)"  # e.g., 2025-08
    [[ -n "${keepmap[$month_key]:-}" ]] || keepmap["$month_key"]="$f"
  done

  # keep 집합 생성
  local -a keep_list=()
  for k in "${!keepmap[@]}"; do keep_list+=("${keepmap[$k]}"); done

  # 고유화
  IFS=$'\n' read -r -d '' -a keep_unique < <(printf '%s\n' "${keep_list[@]}" | awk '!seen[$0]++' && printf '\0')

  # purge = ALL - keep_unique
  declare -A mark=()
  for f in "${keep_unique[@]}"; do mark["$f"]=1; done

  log "LEVEL=FULL policy=8w+monthly (TOTAL=$TOTAL, KEEP=${#keep_unique[@]})"
  for f in "${keep_unique[@]}"; do log "KEEP  $f"; done
  for f in "${ALL[@]}"; do
    [[ "${mark[$f]:-0}" -eq 1 ]] && continue
    if [[ "$DRY_RUN" -eq 1 ]]; then
      log "DRY   rm $f"
    else
      rm -f -- "$f" && log "DEL   $f"
    fi
  done
}

# --- 실행 ---------------------------------------------------------------------
case "$LEVEL" in
  CORE|EXTENDED)
    n="${KEEP:-}"
    [[ -z "$n" ]] && { echo "KEEP가 필요합니다 (예: --keep 14)."; exit 2; }
    keep_latest_n "$n"
    ;;
  FULL)
    pol="${POLICY:-}"
    [[ -z "$pol" ]] && { echo "POLICY가 필요합니다 (예: --policy \"8w+monthly\")."; exit 2; }
    keep_full_weekly_monthly
    ;;
  *)
    echo "알 수 없는 LEVEL: $LEVEL"; exit 2;;
esac

log "rotation done (dry_run=$DRY_RUN)"
