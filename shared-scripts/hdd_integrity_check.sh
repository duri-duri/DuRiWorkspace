#!/usr/bin/env bash
# hdd_integrity_check.sh — HDD 무결성 점검(비차단), 결과를 플래그/로그로 남김
# 사용: ./hdd_integrity_check.sh [--once|--daemon] [--no-bg] [--logdir DIR]
set -Eeo pipefail

# ========== 설정 ==========
LOGDIR="${LOGDIR:-/var/log/duri/hdd_check}"
STATEDIR="${STATEDIR:-/var/lib/duri/state}"      # 루트권한 어려우면 ~/.local/state/duri 로 바꿔도 OK
LOCKFILE="${LOCKFILE:-/var/lock/hdd_integrity_check.lock}"
PASS_FLAG="${STATEDIR}/.hdd_check_passed"        # 성공 플래그
FAIL_FLAG="${STATEDIR}/.hdd_check_failed"        # 실패 플래그
JSON_OUT="${STATEDIR}/hdd_check_summary.json"

# 체크 타임아웃(초)
CHECK_TIMEOUT="${CHECK_TIMEOUT:-180}"            # 한 단계 최대 3분
# ========== /설정 ==========

mkdir -p "$LOGDIR" "$STATEDIR" || true
LOGFILE="${LOGDIR}/hdd_check_$(date +%Y%m%d_%H%M%S).log"

log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*" | tee -a "$LOGFILE" >&2; }

run_with_timeout(){ # timeout SEC cmd...
  local sec="$1"; shift
  timeout --preserve-status "${sec}" "$@" || return $?
}

# ---------- 개별 점검(스텁) ----------
check_hdd_backup(){
  # 예: 최신 덤프 파일 유무/사이즈/해시 등
  log "HDD 백업 축 점검 시작"
  run_with_timeout "$CHECK_TIMEOUT" bash -lc '
    # TODO: 실제 검증 로직 작성 (find/sha256sum 등)
    sleep 1
  '
}
check_git_backup(){
  log "Git 백업 축 점검 시작"
  run_with_timeout "$CHECK_TIMEOUT" bash -lc '
    # TODO: git rev-parse, tag, remote 상태 확인
    sleep 1
  '
}
check_drive_mount(){
  log "드라이브 마운트 상태 점검 시작"
  run_with_timeout "$CHECK_TIMEOUT" bash -lc '
    # TODO: mount -v, df -h, test -w /mnt/{c,d,e,h} 등
    sleep 1
  '
}
check_hdd_main(){
  log "HDD 메인 전환 기준 점검 시작"
  run_with_timeout "$CHECK_TIMEOUT" bash -lc '
    # TODO: last_full_backup.txt / topology.json 존재·갱신 등
    sleep 1
  '
}
check_work_env(){
  log "작업 환경/정책 점검 시작"
  run_with_timeout "$CHECK_TIMEOUT" bash -lc '
    # TODO: 필요 디렉토리/권한/정책파일 일치성
    sleep 1
  '
}
# ---------- /개별 점검 ----------

write_summary_json(){
  cat >"$JSON_OUT" <<JSON
{
  "timestamp":"$(date -Is)",
  "log":"$LOGFILE",
  "result":"$1"
}
JSON
  log "요약 JSON 저장: $JSON_OUT"
}

do_checks(){
  trap 'log "오류 발생"; touch "$FAIL_FLAG"; rm -f "$PASS_FLAG"; write_summary_json fail; exit 1' ERR
  : > "$LOGFILE"
  log "=== HDD 무결성 점검 시작(비차단) ==="
  check_hdd_backup
  check_git_backup
  check_drive_mount
  check_hdd_main
  check_work_env
  log "=== HDD 무결성 점검 성공 ==="
  touch "$PASS_FLAG"; rm -f "$FAIL_FLAG"
  write_summary_json ok
}

maybe_bg=true; mode="once"
for a in "$@"; do
  case "$a" in
    --daemon) mode="daemon" ;;
    --once) mode="once" ;;
    --no-bg) maybe_bg=false ;;
    --logdir) shift; LOGDIR="$1" ;;
  esac
done

if $maybe_bg; then
  # 이미 실행 중이면 중복 방지
  exec 9>"$LOCKFILE" || true
  if ! flock -n 9; then
    log "이미 실행 중 → 종료"; exit 0
  fi
fi

if [[ "$mode" == "daemon" ]]; then
  while :; do
    do_checks || true
    sleep 900 # 15분 간격
  done
else
  do_checks
fi
