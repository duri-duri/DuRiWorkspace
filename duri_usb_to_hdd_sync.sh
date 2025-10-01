#!/usr/bin/env bash
set -Eeuo pipefail

# 안전 가드: 중단 시 정리 함수
cleanup() {
  echo "$(date +%F_%T) [WARN] interrupted; you can re-run safely (rsync resume)."
}
trap cleanup INT TERM

# CR 제거 함수
strip_cr() { printf '%s' "$1" | tr -d '\r'; }

SRC="$(strip_cr "${1:-/mnt/usb}")"              # USB 루트
DST="$(strip_cr "${2:-/mnt/hdd/ARCHIVE}")"      # HDD 아카이브 루트
MODE="${3:-dry-run}"              # dry-run | apply
TS="$(date -u +%F_%H%M%S)"

# 고정 경로
LOGDIR="$DST/Logs"
MANIDIR="$DST/Manifest"
CURR="$DST/Current_Backups"
HIST="$DST/DuRi_History"
DUPS="$DST/duplicates"

mkdir -p "$LOGDIR" "$MANIDIR" "$CURR/FULL" "$CURR/DEV" "$CURR/INCR" "$DST/Disk_Images" "$HIST" "$DUPS"

# 보호 대상(USB 원본 순도/롤백 히스토리) — 건드리지 않음
PROTECT_REGEX='/(CORE_PROTECTED|FINAL|INCR)(/|$)'

log(){ printf '%s %s\n' "$(date -u +%F_%T)" "$*" | tee -a "$LOGDIR/usb_sync_$TS.log" ; }

copy_file(){
  local src="$1" dst="$2"
  if [[ "$MODE" == "apply" ]]; then
    # 목적지 디렉토리 생성 보장
    mkdir -p "$(dirname "$dst")"
    rsync -a --inplace --no-whole-file --no-compress --partial --append-verify --info=progress2 "$src" "$dst"
  else
    # dry-run에서도 디렉토리 생성 (실제 복사는 안 함)
    mkdir -p "$(dirname "$dst")" 2>/dev/null || true
    rsync -an --progress "$src" "$dst"
  fi
}

sha256_of(){
  sha256sum "$1" | awk '{print $1}'
}

# 1) 소스 인벤토리(보호폴더 제외) - SHA256SUMS 전역 제외 강화
mapfile -t FILES < <(
  find "$SRC" \
    \( -path "$SRC/CORE_PROTECTED" -o -path "$SRC/CORE_PROTECTED/*" \
       -o -path "$SRC/FINAL" -o -path "$SRC/FINAL/*" \
       -o -path "$SRC/INCR"  -o -path "$SRC/INCR/*" \
       -o -path "$SRC/System Volume Information" -o -path "$SRC/System Volume Information/*" \) -prune -o \
    -type f ! -name 'SHA256SUMS*' ! -name '*SHA256SUMS*' -print | sort
)

log "[INFO] inventory count=${#FILES[@]} (protected excluded)"

# 인벤토리 검증: 보호 파일 누출 확인
if printf '%s\n' "${FILES[@]}" | grep -E '/(CORE_PROTECTED|FINAL|INCR)/|/System Volume Information/|/SHA256SUMS' -q; then
  log "[FATAL] protected file leak detected in inventory"
  exit 2
fi

# 2) 우선순위 분류
small=() mid=() large=()
for f in "${FILES[@]}"; do
  sz=$(stat -c %s "$f" 2>/dev/null || echo 0)
  if   (( sz < 10*1024*1024 )); then small+=("$f")
  elif (( sz < 2*1024*1024*1024 )); then mid+=("$f")
  else large+=("$f"); fi
done
log "[INFO] buckets: small=${#small[@]} mid=${#mid[@]} large=${#large[@]}"

# 3) 대상별 목적지 결정 함수 (quarantine 매핑 수정 + 상대경로 보존)
dest_path(){
  local p="$1" base; base="$(basename "$p")"

  # quarantine 파일은 HDD의 quarantine로 매핑 (상대경로 보존)
  if [[ "$p" == *"/.quarantine/"* ]]; then
    rel="${p#*'/.quarantine/'}"
    echo "$DST/.quarantine/$rel"
    return
  fi

  # 일반 파일은 상대경로 보존 (이름 충돌 방지)
  rel="${p#"$SRC"/}"
  shopt -s nocasematch
  case "$base" in
    *.txt|*.log) echo "$LOGDIR/$base" ;;
    SHA256SUMS*|*.sha256*) echo "$MANIDIR/$base" ;;
    duri*.img|*.img|*.iso) echo "$DST/Disk_Images/$base" ;;
    FULL_*.tar.zst|FULL_*.tar.gz) echo "$CURR/FULL/$base" ;;
    DEV_*.tar.zst|DEV_*.tar.gz) echo "$CURR/DEV/$base" ;;
    *.tar.zst|*.tar.gz)
      # 7월 변천사/기타는 History로
      echo "$HIST/$base" ;;
    *) echo "$HIST/$rel" ;;  # 상대경로 보존
  esac
}

# 4) 복사 함수(순차 실행) - 2차 안전가드 추가 (SHA256SUMS 제외)
process_list(){
  local -n arr=$1
  for src in "${arr[@]}"; do
    # 2차 안전가드: 보호 폴더 및 SHA256SUMS 재확인
    case "$src" in
      *"/CORE_PROTECTED/"*|*"/FINAL/"*|*"/INCR/"*|*"/System Volume Information/"*|*"/SHA256SUMS"*)
        log "[SKIP-PROTECTED] $src"; continue;;
    esac

    dst="$(dest_path "$src")"
    log "[COPY] $src -> $dst"
    copy_file "$src" "$dst"
  done
}

# 5) 실행
log "[STEP] phase=small"
process_list small
log "[STEP] phase=mid"
process_list mid
log "[STEP] phase=large"
process_list large

# 6) 해시 + 무결성 + 매니페스트 (apply 모드에서만)
MANI=""; SUMS=""
if [[ "$MODE" == "apply" ]]; then
  mkdir -p "$DST/Manifest" "$DST/Logs"
  ts="$(date +%F_%H%M%S)"
  MANI="$DST/Manifest/BACKUP_MANIFEST_${ts}.tsv"
  SUMS="$DST/Manifest/BACKUP_SHA256SUMS_${ts}.tsv"
  printf "path\tsize_bytes\tmtime_utc\tsha256\text\tkind\tsource\n" > "$MANI"
  : > "$SUMS"

  enumerate_dst(){
    find "$DST" -type f \( -path "$CURR/*" -o -path "$HIST/*" -o -path "$DST/Disk_Images/*" -o -path "$LOGDIR/*" -o -path "$MANIDIR/*" \) -printf '%p\n'
  }

  while IFS= read -r f; do
    # CR 제거
    f="${f%$'\r'}"
    ext="${f##*.}"
    sz=$(stat -c %s "$f")
    mt=$(date -u -d "@$(stat -c %Y "$f")" +%F"T"%T"Z")
    sha=$(sha256_of "$f")
    base=$(basename "$f")
    kind="misc"
    shopt -s nocasematch
    [[ "$base" =~ ^FULL_ ]] && kind="full"
    [[ "$base" =~ ^DEV_  ]] && kind="dev"
    [[ "$base" =~ phase|snapshot|repack|final ]] && kind="${kind},tagged"
    printf "%s\t%s\t%s\t%s\t%s\t%s\tHDD\n" "$f" "$sz" "$mt" "$sha" "$ext" "$kind" >> "$MANI"
    printf "%s  %s\n" "$sha" "$f" >> "$SUMS"
  done < <(enumerate_dst)

  log "[OK] manifest=$MANI"
  log "[OK] checksums=$SUMS"
fi

# 매니페스트 FAIL 스캔 함수 (apply에서만 실행)
scan_manifest_failures() {
  if [[ "${MODE:-}" == "apply" ]]; then
    files=()

    # set -u 안전 + 존재/비어있지 않음만 추가
    [[ -n ${MANI:-} && -s "$MANI" ]] && files+=("$MANI")
    [[ -n ${SUMS:-} && -s "$SUMS" ]] && files+=("$SUMS")

    if (( ${#files[@]} )); then
      # FAIL/ERROR/MISSING 같은 키워드 스캔 (필요시 패턴 수정)
      # grep가 매치 못해서 종료코드 1이면 set -e에서 끊기니까 우측에 '|| :'로 흡수
      grep -HnE '^(FAIL|ERROR|MISSING)\b' -- "${files[@]}" || :
      log "[OK] report scan done: ${#files[@]} file(s)"
    else
      log "[SKIP] no report files to scan (dry-run or not generated)"
    fi
  fi
}

# 7) 포맷별 스모크(가능한 경우만, 실패해도 중단 X)
smoke_check(){
  local f="$1"; shopt -s nocasematch
  case "$f" in
    *.tar.gz)  tar -tzf "$f" >/dev/null 2>&1 && echo "OK" || echo "FAIL" ;;
    *.tar.zst) tar --zstd -tf "$f" >/dev/null 2>&1 && echo "OK" || echo "FAIL" ;;
    *.img|*.iso) echo "SKIP" ;; # 별도 툴 필요
    *) echo "SKIP" ;;
  esac
}

# 스모크 체크 (apply에서만, MANI가 존재할 때만)
if [[ "${MODE:-}" == "apply" && -n ${MANI:-} && -s "$MANI" ]]; then
  while IFS= read -r f; do
    # CR 제거
    f="${f%$'\r'}"
    r=$(smoke_check "$f"); echo -e "$r\t$f" >> "$LOGDIR/integrity_$TS.log"
  done < <(grep -E '\.tar\.(gz|zst)$' "$MANI" | cut -f1)
fi

log "[DONE] mode=$MODE  (apply로 실복사 수행)"

# 매니페스트 FAIL 스캔 실행
scan_manifest_failures
