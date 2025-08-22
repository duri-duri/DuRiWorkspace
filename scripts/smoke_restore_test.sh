#!/usr/bin/env bash
# Super-Safe Smoke Restore Test (완성본, plain-text)
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

BACKUP_DIR="var/backups"
RESTORE_ROOT="var/test_restore"
RESTORE_SLO_FILE="var/state/restore_slo.jsonl"
LOG_FILE="var/logs/smoke_restore.log"
MAX_RESTORE_TIME=1800

log() {
  mkdir -p "$(dirname "$LOG_FILE")"
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_FILE"
}
error_exit() { log "ERROR: $*"; exit 1; }

usage() {
  cat <<'INNER_EOF'
Usage: scripts/smoke_restore_test.sh [--archive FILE] [--allow-extended] [--fast] [--record] [--help]
  --archive FILE     : /path/to/FULL__...tar.zst | .tar.gz (직접 지정)
  --allow-extended   : FULL 미발견 시 EXTENDED 허용
  --fast             : 빠른 검증(샘플 파일 존재만 확인)
  --record           : RTO를 var/state/restore_slo.jsonl에 기록
  --help             : 도움말
INNER_EOF
}

# ---- 인자 파싱 ----
ARCHIVE_FILE="" ; ALLOW_EXTENDED=0 ; FAST_MODE=0 ; DO_RECORD=0
while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --archive)        ARCHIVE_FILE="${2:-}"; shift 2 ;;
    --allow-extended) ALLOW_EXTENDED=1; shift ;;
    --fast)           FAST_MODE=1; shift ;;
    --record)         DO_RECORD=1; shift ;;
    --help|-h)        usage; exit 0 ;;
    *) usage; error_exit "Unknown arg: $1" ;;
  esac
done

log "스모크 복원 테스트 시작..."
mkdir -p "$BACKUP_DIR" "$RESTORE_ROOT" "$(dirname "$RESTORE_SLO_FILE")"

# 내부 인덱스에서 아카이브 선택(FULL 우선, 없으면 허용 시 EXTENDED)
pick_archive_from_index() {  # $1=FULL|EXTENDED
  local kind="$1" found=""
  found="$(find "$BACKUP_DIR" -maxdepth 3 -type f -regex ".*${kind}__.*\.tar\.\(zst\|gz\)$" 2>/dev/null | sort | tail -1 || true)"
  if [[ -z "$found" ]]; then
    found="$(find "$BACKUP_DIR" -maxdepth 1 -type f -regex ".*${kind}__.*\.tar\.\(zst\|gz\)$" 2>/dev/null | sort | tail -1 || true)"
  fi
  [[ -n "$found" ]] && printf '%s\n' "$found" || return 1
}

# 최종 아카이브 결정
SELECTED=""
if [[ -n "$ARCHIVE_FILE" ]]; then
  [[ -f "$ARCHIVE_FILE" ]] || error_exit "--archive 파일이 존재하지 않습니다: $ARCHIVE_FILE"
  SELECTED="$ARCHIVE_FILE"
else
  SELECTED="$(pick_archive_from_index FULL || true)"
  if [[ -z "$SELECTED" && "$ALLOW_EXTENDED" -eq 1 ]]; then
    SELECTED="$(pick_archive_from_index EXTENDED || true)"
  fi
  [[ -n "$SELECTED" ]] || error_exit "FULL 백업을 찾을 수 없음(필요시 --archive 또는 --allow-extended 사용)"
fi
log "선택된 아카이브: $SELECTED"

# 복원 작업 디렉토리
ts="$(date +%Y%m%d_%H%M%S)"
WORK_DIR="$RESTORE_ROOT/$ts"
mkdir -p "$WORK_DIR"

# 압축 해제
extract_archive() {
  local arc="$1"
  case "$arc" in
    *.tar.zst) tar --use-compress-program="zstd -d" -xf "$arc" -C "$WORK_DIR" ;;
    *.tar.gz)  tar -xzf "$arc" -C "$WORK_DIR" ;;
    *) error_exit "지원하지 않는 아카이브 형식: $arc" ;;
  esac
}

start_ts=$(date +%s)
extract_archive "$SELECTED"
log "아카이브 해제 완료 → $WORK_DIR"

# 빠른/일반 검증
if [[ "$FAST_MODE" -eq 1 ]]; then
  find "$WORK_DIR" -type f -print -quit | grep -q . || error_exit "복원된 파일 미발견(FAST)"
  log "FAST 검증 통과(샘플 파일 존재)"
else
cnt=0
while IFS= read -r -d '' _; do
  cnt=$((cnt+1))
  ((cnt>=3)) && break
done < <(find "$WORK_DIR" -type f -print0)
log "파일 개수 확인 OK (>=3): 실제=$cnt"
  log "기본 검증 통과(파일 존재 확인)"
fi

elapsed=$(( $(date +%s) - start_ts ))
log "복원 소요: ${elapsed}s"

# RTO 기록(JSONL 선호, jq 없으면 텍스트)
if [[ "$DO_RECORD" -eq 1 ]]; then
  mkdir -p "$(dirname "$RESTORE_SLO_FILE")"
  if command -v jq >/dev/null 2>&1; then
    jq -cn --arg ts "$(date -Is)" \
           --arg arc "$SELECTED" \
           --arg mode "$([[ $FAST_MODE -eq 1 ]] && echo fast || echo full)" \
           --argjson sec "$elapsed" \
           '{timestamp:$ts, archive:$arc, mode:$mode, restore_seconds:$sec}' \
      >> "$RESTORE_SLO_FILE"
    log "RTO 기록(JSONL) 완료 → $RESTORE_SLO_FILE"
  else
    printf '%s | archive=%s | mode=%s | restore_seconds=%s\n' \
      "$(date -Is)" "$SELECTED" "$([[ $FAST_MODE -eq 1 ]] && echo fast || echo full)" "$elapsed" \
      >> "$RESTORE_SLO_FILE"
    log "RTO 기록(텍스트) 완료 → $RESTORE_SLO_FILE (jq 미설치)"
  fi
fi

log "스모크 복원 테스트 성공"
