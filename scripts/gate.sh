#!/usr/bin/env bash
set -euo pipefail

# ==== 공통 메타 ====
WS_ROOT="${WS_ROOT:-$PWD}"
HOST_ID="$(hostname -s || echo host)"
TZ=Asia/Seoul
export TZ
NOW_HM="$(date +'%Y-%m-%d__%H%M')"
Y=$(date +%Y) ; M=$(date +%m) ; D=$(date +%d)
DEST_ROOT_DEFAULT="/mnt/c/Users/admin/Desktop/두리백업/${Y}/${M}/${D}"
DEST_ROOT="${DEST_ROOT:-$DEST_ROOT_DEFAULT}"

STATE_DIR="${WS_ROOT}/var/state"
LOG_DIR="${WS_ROOT}/var/log"
mkdir -p "${STATE_DIR}" "${LOG_DIR}" "${DEST_ROOT}"

LOG="${LOG_DIR}/gate.log"
touch "${LOG}"

say(){ echo "[$(date +'%F %T')] $*" | tee -a "${LOG}"; }

have(){ command -v "$1" >/dev/null 2>&1; }

tag_safe() {
  local tag="$1"
  if git rev-parse -q --verify "refs/tags/${tag}" >/dev/null 2>&1; then
    say "ℹ️  tag ${tag} already exists, skipping."
    return 0
  fi
  git tag -a "${tag}" -m "${tag}" || say "⚠️ tag ${tag} failed (non-fatal)"
}

backup_core()     { ./scripts/unified_backup_core.sh     >/dev/null && say "✅ CORE backup ok"; }
backup_extended() { ./scripts/unified_backup_extended.sh >/dev/null && say "✅ EXTENDED backup ok"; }
backup_full()     { ./scripts/unified_backup_full.sh     >/dev/null && say "✅ FULL backup ok"; }

update_state() {
  local level="$1"; local note="$2"
  local ref="${STATE_DIR}/backup_refs.json"
  mkdir -p "${STATE_DIR}"
  if [[ ! -f "${ref}" ]]; then echo '{"history":[]}' > "${ref}"; fi
  if have jq; then
    jq --arg lvl "$level" --arg t "$NOW_HM" --arg n "$note" \
       '.history += [{"level":$lvl,"time_kst":$t,"note":$n}]' "${ref}" \
       > "${ref}.tmp" && mv "${ref}.tmp" "${ref}"
  else
    printf '%s\n' "${NOW_HM} ${level} ${note}" >> "${STATE_DIR}/backup_refs.log"
  fi
}

usage(){
  cat <<USAGE
Usage: $0 {pre-rewrite|post-rewrite|pre-promote|post-promote}
USAGE
  exit 2
}

[[ $# -ge 1 ]] || usage
cmd="$1"

case "${cmd}" in
  pre-rewrite)
    say "▶ PRE-REWRITE gate start"
    backup_core
    tag_safe "pre-rewrite__${NOW_HM}"
    update_state "CORE" "pre-rewrite"
    say "✅ PRE-REWRITE done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  post-rewrite)
    say "▶ POST-REWRITE gate start"
    # 품질 검증(있으면)
    if [[ -x ./scripts/check_quality.sh ]]; then
      ./scripts/check_quality.sh && say "✅ quality check passed" || { say "❌ quality check failed"; exit 1; }
    fi
    backup_core
    tag_safe "post-rewrite__${NOW_HM}"
    update_state "CORE" "post-rewrite"
    say "✅ POST-REWRITE done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  pre-promote)
    say "▶ PRE-PROMOTE gate start"
    backup_extended
    tag_safe "pre-promote__${NOW_HM}"
    update_state "EXTENDED" "pre-promote"
    say "✅ PRE-PROMOTE done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  post-promote)
    say "▶ POST-PROMOTE gate start"
    # 최종 검증(있으면)
    if [[ -x ./scripts/check_release.sh ]]; then
      ./scripts/check_release.sh && say "✅ release check passed" || { say "❌ release check failed"; exit 1; }
    fi
    # 레벨 분리도 검증
    if [[ -x ./tools/check_levels.py ]]; then
      python3 ./tools/check_levels.py "/mnt/c/Users/admin/Desktop/두리백업/${Y}/${M}/${D}" && say "✅ level policy check passed" || { say "❌ level policy violation"; exit 1; }
    fi
    backup_full
    tag_safe "post-promote__${NOW_HM}"
    update_state "FULL" "post-promote"
    say "✅ POST-PROMOTE done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  *)
    usage
    ;;
esac
