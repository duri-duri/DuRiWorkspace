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

# 서브모듈 동기화 함수
sync_submodules() {
  say "🔄 서브모듈 동기화 시작..."
  source scripts/lib/submodule_sync.sh
  sync_all_submodules
  say "✅ 서브모듈 동기화 완료"
}

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

# 롤백 관련 함수들
save_current_tags() {
  say "💾 현재 상태 저장 중..."
  mkdir -p "${STATE_DIR}"

  # Docker 이미지 정보 저장
  docker compose -p duriworkspace images --quiet > "${STATE_DIR}/current_digests.txt" 2>/dev/null || true

  # 각 서비스의 현재 이미지 태그 저장
  {
    echo "# Last good state saved at $(date)"
    echo "SAVED_AT=\"$(date -Iseconds)\""
    echo "DURI_CORE_IMAGE=\"$(docker inspect duri-core --format='{{.Image}}' 2>/dev/null || echo 'unknown')\""
    echo "DURI_BRAIN_IMAGE=\"$(docker inspect duri-brain --format='{{.Image}}' 2>/dev/null || echo 'unknown')\""
    echo "DURI_EVOLUTION_IMAGE=\"$(docker inspect duri-evolution --format='{{.Image}}' 2>/dev/null || echo 'unknown')\""
    echo "DURI_CONTROL_IMAGE=\"$(docker inspect duri-control --format='{{.Image}}' 2>/dev/null || echo 'unknown')\""
  } > "${STATE_DIR}/last_good.env"

  say "✅ 현재 상태 저장 완료: ${STATE_DIR}/last_good.env"
}

redeploy_last_good() {
  say "🔄 마지막 안전 상태로 롤백 중..."

  if [[ ! -f "${STATE_DIR}/last_good.env" ]]; then
    say "❌ last_good.env 파일이 없습니다. 롤백 불가능"
    exit 2
  fi

  # 저장된 상태 로드
  set -a
  source "${STATE_DIR}/last_good.env"
  set +a

  say "📅 롤백 대상: ${SAVED_AT:-unknown}"

  # Docker Compose 재배포 (현재 이미지로)
  if docker compose -p duriworkspace up -d --no-deps duri-core duri-brain duri-evolution duri-control; then
    say "✅ 롤백 완료"
    say "📊 상태 확인: docker ps"
  else
    say "❌ 롤백 실패"
    exit 1
  fi
}

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
    sync_submodules  # 서브모듈 동기화 추가
    save_current_tags  # 승격 전 현재 상태 저장
    backup_extended
    tag_safe "pre-promote__${NOW_HM}"
    update_state "EXTENDED" "pre-promote"
    say "✅ PRE-PROMOTE done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  post-promote)
    say "▶ POST-PROMOTE gate start"
    sync_submodules  # 서브모듈 동기화 추가
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
  rollback)
    say "▶ ROLLBACK gate start"
    sync_submodules  # 서브모듈 동기화 추가
    redeploy_last_good
    say "✅ ROLLBACK done"
    source scripts/common_notify.sh 2>/dev/null || true; notify "gate $cmd ok $(date +'%F %T')"
    ;;
  *)
    usage
    ;;
esac
