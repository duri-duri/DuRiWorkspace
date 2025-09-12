#!/usr/bin/env bash
# tools/cleanup_space.sh
# A단계 자동화: 내부 아카이브 원본(=S2 OK)만 안전 격리 + 스냅샷 로깅 + 유예기간(purge)
# 사용법:
#   MODE=dry    bash tools/cleanup_space.sh [/mnt/h/ARCHIVE]
#   MODE=commit DAYS_KEEP=7 bash tools/cleanup_space.sh [/mnt/h/ARCHIVE]
#   MODE=purge  DAYS_KEEP=7 bash tools/cleanup_space.sh [/mnt/h/ARCHIVE]
#   MODE=status bash tools/cleanup_space.sh [/mnt/h/ARCHIVE]
set -Eeuo pipefail

ROOT="${1:-/mnt/h/ARCHIVE}"
MODE="${MODE:-dry}"         # dry | commit | purge | status
DAYS_KEEP="${DAYS_KEEP:-7}" # trash 보관일
LOCK="${ROOT}/.UNWRAP/D/_locks/cleanup.lock"
LOGDIR="${ROOT}/.UNWRAP/D/_logs"
MANI="${ROOT}/.UNWRAP/D/STAGE2_INNER/_state/manifest.tsv"
TS="$(date '+%Y%m%d_%H%M%S')"
TRASH="${ROOT}/.UNWRAP/D/_trash_inner_${TS}"

mkdir -p "${ROOT}/.UNWRAP/D/_trash_summaries" "${LOGDIR}" "$(dirname "$LOCK")"

log(){ echo "[$(date '+%F %T')] $*" | tee -a "${LOGDIR}/cleanup.log"; }
snap(){
  local tag="$1"
  {
    echo "=== SNAPSHOT ${tag} $(date '+%F %T') ==="
    du -sh "${ROOT}" 2>/dev/null || true
    du -sh "${ROOT}/.UNWRAP/D/STAGE1_OUT" 2>/dev/null || true
    du -sh "${ROOT}/.UNWRAP/D/STAGE2_INNER" 2>/dev/null || true
    find "${ROOT}/.UNWRAP/D" -maxdepth 1 -type d -name "_trash_inner_*" -printf "%TY-%Tm-%Td %TH:%TM %p\n" 2>/dev/null | sort
    echo
  } | tee -a "${LOGDIR}/cleanup_snapshots.log" >/dev/null
}
with_lock(){
  if ( set -o noclobber; echo "$$" > "$LOCK") 2>/dev/null; then
    trap 'rm -f "$LOCK"' EXIT INT TERM
  else
    log "[ERR] 이미 다른 실행이 동작 중입니다: $LOCK"; exit 2
  fi
}

# 공통 점검
[[ -d "$ROOT" ]] || { echo "[ERR] ROOT not found: $ROOT" >&2; exit 1; }

case "$MODE" in
  dry|commit)
    [[ -f "$MANI" ]] || { echo "[ERR] manifest not found: $MANI" >&2; exit 1; }
    with_lock
    ;;
  purge|status)
    # manifest 없어도 됨
    ;;
  *)
    echo "[ERR] MODE must be dry|commit|purge|status"; exit 1;;
esac

if [[ "$MODE" == "status" ]]; then
  snap "STATUS"
  exit 0
fi

if [[ "$MODE" == "dry" ]]; then
  log "[INFO] DRY-RUN 시작 ROOT=$ROOT"
  snap "BEFORE-DRY"
  mkdir -p "$TRASH"
  awk -F'\t' '$8=="OK"{print $1}' "$MANI" \
  | while IFS= read -r f; do
      [[ -f "$f" ]] || continue
      rel="${f#$ROOT/}"
      echo "mv -- \"$f\" \"$TRASH/$rel\""
    done | tee "${TRASH}/DRYRUN.txt"
  log "[INFO] 후보 개수: $(wc -l < "${TRASH}/DRYRUN.txt")"
  snap "AFTER-DRY"
  exit 0
fi

if [[ "$MODE" == "commit" ]]; then
  log "[INFO] COMMIT 시작 ROOT=$ROOT DAYS_KEEP=${DAYS_KEEP}"
  snap "BEFORE-COMMIT"
  mkdir -p "$TRASH"
  LIST="$(mktemp)"
  awk -F'\t' '$8=="OK"{print $1}' "$MANI" > "$LIST"

  # 실행 로그 + 요약 파일
  SUM="${ROOT}/.UNWRAP/D/_trash_summaries/summary_${TS}.tsv"
  echo -e "src\ttrash_dest\tsize_bytes" > "$SUM"

  # 실제 이동
  while IFS= read -r f; do
    [[ -f "$f" ]] || continue
    rel="${f#$ROOT/}"
    dest="${TRASH}/${rel}"
    mkdir -p "$(dirname "$dest")"
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    mv -v -- "$f" "$dest" | tee -a "${LOGDIR}/cleanup.log"
    echo -e "${f}\t${dest}\t${size}" >> "$SUM"
  done < "$LIST"

  # 효율 보고
  moved_cnt=$(( $(wc -l < "$SUM") - 1 ))
  saved_bytes=$(awk -F'\t' 'NR>1{sum+=$3} END{print sum+0}' "$SUM")
  log "[INFO] 이동 파일수: ${moved_cnt}, 대략 회수 용량: ${saved_bytes} bytes"
  du -sh "${ROOT}/.UNWRAP/D/STAGE1_OUT" "$TRASH" 2>/dev/null || true
  snap "AFTER-COMMIT"
  log "[INFO] trash 경로: $TRASH (보관 ${DAYS_KEEP}일 후 purge 권장)"
  exit 0
fi

if [[ "$MODE" == "purge" ]]; then
  with_lock
  log "[INFO] PURGE 시작 ROOT=$ROOT DAYS_KEEP=${DAYS_KEEP}"
  snap "BEFORE-PURGE"
  # 보관기한 초과 trash 디렉터리만 삭제
  find "${ROOT}/.UNWRAP/D" -maxdepth 1 -type d -name "_trash_inner_*" -mtime +"$DAYS_KEEP" -print0 \
  | while IFS= read -r -d '' d; do
      log "[PURGE] 삭제: $d"
      rm -rf -- "$d"
    done
  snap "AFTER-PURGE"
  log "[INFO] PURGE 완료"
  exit 0
fi





