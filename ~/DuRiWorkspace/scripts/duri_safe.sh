#!/usr/bin/env bash
set -Eeuo pipefail
LC_ALL=C

# ========= ENV =========
: "${DURI_HDD:=/mnt/h/ARCHIVE}"           # 소스 (운영용 주 저장소)
: "${DURI_VAULT:=/mnt/e/DuRiSafe_HOSP}"   # 타겟 (14TB 콜드 금고)
EXC="${HOME}/DuRiWorkspace/etc/vault_exclude.txt"
[[ -f "$EXC" ]] || EXC=/dev/null          # exclude 파일 없으면 /dev/null 대체

HOST="$(hostname | sed 's/ /_/g')"
TS="$(date +%Y-%m-%d__%H%M)"

# 튜닝(환경변수로 덮어쓰기 가능)
: "${DURI_ZSTD_LEVEL:=15}"     # 10~19 권장 (속도↔압축률)
: "${DURI_ZSTD_THREADS:=0}"    # 0=자동
: "${MIN_FREE_GIB:=5}"         # 타겟에 최소 여유 GiB

log(){ printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
err(){ printf '[%s] [ERR] %s\n' "$(date '+%F %T')" "$*" >&2; }

cleanup_part(){ [[ -f "$1" ]] && rm -f -- "$1" || true; }

need(){ command -v "$1" >/dev/null || { err "missing command: $1"; exit 127; }; }

preflight(){
  need tar; need zstd; need pv; need sha256sum

  [[ -d "$DURI_HDD" ]]   || { err "DURI_HDD not found: $DURI_HDD"; exit 2; }
  mkdir -p "$DURI_VAULT/FULL" "$DURI_VAULT/REPORTS"

  # 타겟 여유 공간 체크 (KB 단위 → GiB)
  local kb; kb=$(df -Pk "$DURI_VAULT" | awk 'NR==2{print $4}')
  local need_kb=$(( MIN_FREE_GIB * 1024 * 1024 ))
  (( kb > need_kb )) || { err "low space on $DURI_VAULT (need >= ${MIN_FREE_GIB}GiB)"; exit 28; }
}

full(){
  preflight

  local OUT="$DURI_VAULT/FULL/FULL__${TS}__host-${HOST}.tar.zst"
  local PART="${OUT}.part"
  local META="$DURI_VAULT/REPORTS/FULL__${TS}__host-${HOST}.meta"

  # 시그널/종료 시 .part 정리
  trap 'log "ABORT: cleanup .part"; cleanup_part "$PART"; exit 130' INT TERM
  trap 'cleanup_part "$PART"' EXIT

  log "FULL start → $OUT"
  du -sh "$DURI_HDD" > "$META" 2>/dev/null || true
  {
    echo "HOST=$HOST"
    echo "SRC=$DURI_HDD"
    echo "DST=$DURI_VAULT"
    echo "EXCLUDE_FILE=$EXC"
    echo "ZSTD_LEVEL=$DURI_ZSTD_LEVEL"
    echo "ZSTD_THREADS=$DURI_ZSTD_THREADS"
    echo "TAR_VER=$(tar --version | head -1)"
    echo "ZSTD_VER=$(zstd --version)"
  } >> "$META"

  # tar → pv → zstd (.part로 기록 후 원자적 rename)
  tar -C "$DURI_HDD" -cf - . \
    --numeric-owner --one-file-system \
    --exclude-from="$EXC" \
  | pv \
  | zstd -T"$DURI_ZSTD_THREADS" -"${DURI_ZSTD_LEVEL}" --long=31 -o "$PART"

  mv -f -- "$PART" "$OUT"

  # 아카이브 체크섬
  (cd "$(dirname "$OUT")" && sha256sum "$(basename "$OUT")") | tee "${OUT}.sha256" >/dev/null

  # 입력 트리 지문(아카이브 재해독 없이 소스 트리에서 계산)
  (cd "$DURI_HDD" && \
    find . -type f -print0 \
      | sort -z \
      | xargs -0r sha256sum -b -- 2>/dev/null \
      | sha256sum | awk '{print $1}') > "${OUT}.inputtree.sha256"

  sync || true

  log "FULL done."
  {
    echo "ARCHIVE=$OUT"
    echo "SHA256=$(awk '{print $1}' "${OUT}.sha256")"
    echo "INPUTTREE_SHA256=$(cat "${OUT}.inputtree.sha256")"
  } >> "$META"
}

verify_latest(){
  local LATEST
  LATEST="$(ls -1t "$DURI_VAULT"/FULL/FULL__*.tar.zst 2>/dev/null | head -1 || true)"
  [[ -n "$LATEST" ]] || { err "no FULL archive found"; exit 1; }
  log "verify: $LATEST"
  sha256sum -c "${LATEST}.sha256"
}

prune_keep(){
  local KEEP="${1:-3}"
  mapfile -t ALL < <(ls -1t "$DURI_VAULT"/FULL/FULL__*.tar.zst 2>/dev/null || true)
  (( ${#ALL[@]} <= KEEP )) && { log "nothing to prune (<= KEEP=$KEEP)"; return 0; }
  for ((i=KEEP;i<${#ALL[@]};i++)); do
    local f="${ALL[$i]}"
    log "prune $f"
    rm -f -- "$f" "${f}.sha256" "${f}.inputtree.sha256"
  done
}

usage(){
  cat <<USAGE
usage: $(basename "$0") {full|verify|prune [N]}
  full      - FULL 백업 수행 (.part → 원자적 rename, 체크섬/입력지문 생성)
  verify    - 최신 FULL 아카이브 sha256 검증
  prune [N] - 최신 N개만 남기고 나머지 정리 (기본 N=3)

env:
  DURI_HDD           (default: /mnt/h/ARCHIVE)
  DURI_VAULT         (default: /mnt/e/DuRiSafe_HOSP)
  DURI_ZSTD_LEVEL    (default: 15, 더 빠르게 10~12 / 더 작게 18~19)
  DURI_ZSTD_THREADS  (default: 0=auto)
  MIN_FREE_GIB       (default: 5 GiB)
USAGE
}

case "${1:-}" in
  full)   full ;;
  verify) verify_latest ;;
  prune)  prune_keep "${2:-3}" ;;
  *)      usage; exit 1 ;;
esac