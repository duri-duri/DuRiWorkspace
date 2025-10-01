#!/usr/bin/env bash
# triple_protect.sh — DuRi CORE 삼중 보호 원샷
# 안전 기본값: DRY RUN. 실제 적용하려면 APPLY=1 로 실행.
# 예) APPLY=1 CLOUD=aws GPG_RECIPIENT="you@example.com" S3_URI="s3://bucket/duri/core_protected.enc.gpg" sudo -E bash triple_protect.sh

set -Eeuo pipefail

##### [설정] 환경 변수로 덮어쓰기 가능 #####
USB_MNT="${USB_MNT:-/mnt/usb}"
HDD_MNT="${HDD_MNT:-/mnt/hdd}"                 # 오프라인 미러 대상(마운트되어 있어야 함)
CORE_PAT_GLOB="${CORE_PAT_GLOB:-CORE__*__host-duri-head-.tar.zst}"  # CORE tar 파일 직접 찾기
CORE_OUT="${CORE_OUT:-$USB_MNT/CORE_PROTECTED}" # USB 내 금고(복제본; 원본은 제자리 유지)
META_PATTERNS="${META_PATTERNS:-backup-log.txt manifest.* filelist.* HASHLIST.* SHA256SUMS.*}"

# 실행/안전 모드
APPLY="${APPLY:-0}"             # 0=dry-run(추천), 1=실행
VERIFY_HASH="${VERIFY_HASH:-0}" # 1이면 sum 검증 수행(시간 오래 걸림)
ENABLE_CHATTR="${ENABLE_CHATTR:-1}"  # ext4일 때 chattr +i 시도
REMOUNT_RW="${REMOUNT_RW:-1}"        # 필요 시에만 USB rw remount

# 클라우드 업로드(옵션)
CLOUD="${CLOUD:-none}"          # none|aws|gcs
# AWS:  aws s3 cp --storage-class GLACIER/DEEP_ARCHIVE
S3_URI="${S3_URI:-s3://YOUR_BUCKET/path/core_protected.enc.gpg}"
S3_STORAGE_CLASS="${S3_STORAGE_CLASS:-GLACIER}"
# GCS:  gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" cp -n
GCS_URI="${GCS_URI:-gs://YOUR_BUCKET/path/core_protected.enc.gpg}"
GCS_STORAGE_CLASS="${GCS_STORAGE_CLASS:-COLDLINE}"

# 암호화(둘 중 하나 선택)
ENC_MODE="${ENC_MODE:-asym}"    # asym(수신자 공개키) | sym(대칭)
GPG_RECIPIENT="${GPG_RECIPIENT:-}"     # asym 모드일 때 필수
GPG_PASSPHRASE_FILE="${GPG_PASSPHRASE_FILE:-}"  # sym 모드일 때 권장(파일에 비밀구문 저장)
GPG_OPTS="${GPG_OPTS:---compress-algo zlib --cipher-algo AES256}"

# 로그/산출물
TS="$(date +%Y%m%d__%H%M%S)"
RUN_ID="triple_protect_${TS}"
WORKDIR="${WORKDIR:-/tmp/$RUN_ID}"
PLAN_JSONL="$WORKDIR/PLAN.jsonl"
LOG="$WORKDIR/run.log"
ARCHIVE_TAR="$WORKDIR/CORE_PROTECTED.$TS.tar"
ARCHIVE_GPG="$WORKDIR/CORE_PROTECTED.$TS.tar.gpg"
README="$WORKDIR/README_CORE_PROTECTED_$TS.md"

mkdir -p "$WORKDIR"
exec > >(tee -a "$LOG") 2>&1

##### 유틸 #####
die(){ echo "[FATAL] $*" >&2; exit 1; }
need(){ command -v "$1" >/dev/null 2>&1 || die "command not found: $1"; }

for b in awk sed grep rsync tar du date; do need "$b"; done
[ "$CLOUD" = "aws" ] && need aws
[ "$CLOUD" = "gcs" ] && need gsutil
need gpg || echo "[WARN] gpg 미설치(서명/암호화 건너뜀)"

echo "=== DuRi CORE Triple-Protect (DRY_RUN=${APPLY/1/0}) RUN_ID=$RUN_ID ==="
echo "[1/9] 프리플라이트"

mount | grep -qE "$USB_MNT .* (ro,|,ro,|,ro$)" || {
  echo "[INFO] USB가 RO로 마운트되어 있지 않음(검사만 수행)."; }
[ -d "$USB_MNT" ] || die "USB_MNT not found: $USB_MNT"
[ -d "$HDD_MNT" ] || echo "[WARN] HDD_MNT not found: $HDD_MNT (HDD 동기화 건너뜀 가능)"

FS_USB="$(stat -f -c %T "$USB_MNT" 2>/dev/null || echo '?')"
echo "[INFO] USB FS: $FS_USB (ext4일 때만 chattr 가능)"

echo "[2/9] CORE tar 파일들 스캔 → PLAN 생성"
> "$PLAN_JSONL"
mapfile -t CORE_FILES < <(find "$USB_MNT" -type f -name "$CORE_PAT_GLOB" | sort || true)
[ "${#CORE_FILES[@]}" -gt 0 ] || die "CORE tar 파일들을 찾지 못함: $CORE_PAT_GLOB"

PAIR_CNT=0
for core_file in "${CORE_FILES[@]}"; do
  d="$(dirname "$core_file")"
  filename="$(basename "$core_file")"

  # 관련 메타데이터 파일들 찾기
  base_name="${filename%.tar.zst}"
  sha_file="$d/SHA256SUMS.CORE.${base_name#CORE__}.txt"
  hashlist_file="$d/HASHLIST.CORE.${base_name#CORE__}.txt"
  filelist_file="$d/filelist.CORE.${base_name#CORE__}.txt"

  echo "{\"core_file\":\"$core_file\",\"sha_file\":\"$sha_file\",\"hashlist_file\":\"$hashlist_file\",\"filelist_file\":\"$filelist_file\"}" >> "$PLAN_JSONL"
  PAIR_CNT=$((PAIR_CNT+1))
done

[ "$PAIR_CNT" -gt 0 ] || die "CORE 파일들을 하나도 찾지 못함"
echo "[OK] PLAN: $PAIR_CNT CORE files → $PLAN_JSONL"

echo "[3/9] (옵션) 해시 검증"
if [ "$VERIFY_HASH" = "1" ]; then
  while IFS= read -r line; do
    sha_file=$(echo "$line" | awk -F\" '/"sha_file":/ {print $4}')
    if [ -f "$sha_file" ]; then
      echo "[CHK] sha256sum -c $sha_file"
      sha256sum -c "$sha_file" || echo "[WARN] 무결성 실패: $sha_file (계속 진행)"
    else
      echo "[WARN] SHA 파일 없음: $sha_file"
    fi
  done < "$PLAN_JSONL"
fi

echo "[4/9] README/목록 생성(증거물)"
TOTAL_BYTES=0
echo "# CORE_PROTECTED 인벤토리 ($TS)" > "$README"
echo "- 생성: $(date '+%F %T %Z')" >> "$README"
echo "- USB: $USB_MNT" >> "$README"
echo "- 쌍(pair) 개수: $PAIR_CNT" >> "$README"
echo "" >> "$README"
echo "## 파일 목록" >> "$README"
while IFS= read -r core_file; do
  filename="$(basename "$core_file")"
  base_name="${filename%.tar.zst}"
  sha_file="$d/SHA256SUMS.CORE.${base_name#CORE__}.txt"
  hashlist_file="$d/HASHLIST.CORE.${base_name#CORE__}.txt"
  filelist_file="$d/filelist.CORE.${base_name#CORE__}.txt"

  sz=$(stat -c %s "$core_file" 2>/dev/null || echo 0)
  TOTAL_BYTES=$((TOTAL_BYTES+sz))
  echo "- $(realpath --relative-to="$USB_MNT" "$core_file")  (${sz}B)" >> "$README"
done < <(awk -F\" '/"core_file":/ {print $4}' "$PLAN_JSONL")
echo "" >> "$README"
echo "총 용량(바이트): $TOTAL_BYTES" >> "$README"

echo "[5/9] USB 금고(CORE_PROTECTED) 복제 및 봉인 준비"
echo "금고 위치: $CORE_OUT"
echo "[안전] 기본 DRY-RUN. APPLY=1일 때만 실제 복제/봉인"

# 금고에 복사할 목록 생성
FILES_TO_COPY=("$README")
# core_file + 메타
while IFS= read -r core_file; do FILES_TO_COPY+=("$core_file"); done < <(awk -F\" '/"core_file":/ {print $4}' "$PLAN_JSONL")
# 메타(디렉토리별 추가)
while IFS= read -r dir; do
  for p in $META_PATTERNS; do
    for m in "$dir"/$p; do [ -f "$m" ] && FILES_TO_COPY+=("$m"); done
  done
done < <(awk -F\" '/"core_file":/ {print $4}' "$PLAN_JSONL" | xargs -I{} dirname "{}" | sort -u)

if [ "$APPLY" = "1" ]; then
  if [ "$REMOUNT_RW" = "1" ]; then
    # 일시 RW 필요 시에만: mount 옵션에 따라 실패할 수 있음
    mount | grep -qE "$USB_MNT " && sudo mount -o remount,rw "$USB_MNT" || true
  fi
  mkdir -p "$CORE_OUT"/{CORE,META}
  # core_file → CORE, meta/readme → META
  for f in "${FILES_TO_COPY[@]}"; do
    base="$(basename "$f")"
    case "$base" in
      SHA256SUMS.CORE.*|*.tar|*.tar.zst) dest="$CORE_OUT/CORE/$base" ;;
      *) dest="$CORE_OUT/META/$base" ;;
    esac
    printf '[COPY] %s -> %s\n' "$f" "$dest" >&2
    rsync -a --mkpath "$f" "$dest"
  done

  # 봉인: 쓰기권한 제거 + (가능 시) immutable
  chmod -R a-w "$CORE_OUT/CORE" || true
  if [ "$ENABLE_CHATTR" = "1" ] && [ "$FS_USB" = "ext2/ext3" -o "$FS_USB" = "ext2/ext3/ext4" -o "$FS_USB" = "ext4" ]; then
    sudo chattr +i "$CORE_OUT/CORE"/* || true
  else
    echo "[INFO] chattr 미지원 FS($FS_USB) → 권한만 조정"
  fi

  # 작업 후 USB를 다시 RO로
  mount | grep -qE "$USB_MNT " && sudo mount -o remount,ro "$USB_MNT" || true
else
  echo "[DRY] 복제/봉인 생략. APPLY=1로 실행하면 적용됩니다."
fi

echo "[6/9] HDD 미러 동기화(+무결성 검증)"
if [ -d "$HDD_MNT" ]; then
  if [ "$APPLY" = "1" ]; then
    # USB가 RO로 돌아온 상태에서 HDD로 복사
    mkdir -p "$HDD_MNT/CORE_PROTECTED"/{CORE,META}
    rsync -a --delete --mkpath "$CORE_OUT/CORE/" "$HDD_MNT/CORE_PROTECTED/CORE/"
    rsync -a --mkpath "$CORE_OUT/META/" "$HDD_MNT/CORE_PROTECTED/META/" 2>/dev/null || true

    # HDD에서 sum 검증(빠른 표본검증: 1개 이상 OK 확인)
    if [ "$VERIFY_HASH" = "1" ]; then
      mapfile -t HDD_SUMS < <(find "$HDD_MNT/CORE_PROTECTED/CORE" -type f -name "$CORE_PAT_GLOB" | sort || true)
      for s in "${HDD_SUMS[@]}"; do
        (cd "$(dirname "$s")" && sha256sum -c "$(basename "$s")")
      done
    else
      echo "[SKIP] HDD 해시 검증(VERIFY_HASH=0)"
    fi
  else
    echo "[DRY] HDD rsync 생략"
  fi
else
  echo "[WARN] HDD 미탐색: $HDD_MNT"
fi

echo "[7/9] GPG 서명(불변성 보강)"
if command -v gpg >/dev/null 2>&1; then
  sign_dir(){
    local D="$1"
    [ -d "$D" ] || return 0
    mapfile -t sums < <(find "$D/CORE" -type f -name "$CORE_PAT_GLOB" | sort || true)
    for f in "${sums[@]}"; do
      if [ "$APPLY" = "1" ]; then
        echo "[SIGN] $f"
        gpg --batch --yes --detach-sign $GPG_OPTS "$f" || echo "[WARN] GPG 서명 실패: $f"
      else
        echo "[DRY] gpg --detach-sign $f"
      fi
    done
  }
  sign_dir "$CORE_OUT"
  [ -d "$HDD_MNT/CORE_PROTECTED" ] && sign_dir "$HDD_MNT/CORE_PROTECTED"
else
  echo "[WARN] gpg 없음 → 서명 생략"
fi

echo "[8/9] 클라우드 암호화 업로드($CLOUD)"
if [ "$CLOUD" != "none" ]; then
  echo "[PACK] $ARCHIVE_TAR ← $CORE_OUT"
  tar -cf "$ARCHIVE_TAR" -C "$(dirname "$CORE_OUT")" "$(basename "$CORE_OUT")"
  if command -v gpg >/dev/null 2>&1; then
    if [ "$ENC_MODE" = "asym" ]; then
      [ -n "$GPG_RECIPIENT" ] || die "ENC_MODE=asym 이면 GPG_RECIPIENT 필요"
      echo "[GPG] recipient=$GPG_RECIPIENT"
      gpg --batch --yes --encrypt --recipient "$GPG_RECIPIENT" $GPG_OPTS -o "$ARCHIVE_GPG" "$ARCHIVE_TAR"
    else
      echo "[GPG] symmetric"
      [ -n "$GPG_PASSPHRASE_FILE" ] && PASS_OPT="--passphrase-file $GPG_PASSPHRASE_FILE" || PASS_OPT="--pinentry-mode loopback"
      gpg --batch --yes --symmetric $PASS_OPT $GPG_OPTS -o "$ARCHIVE_GPG" "$ARCHIVE_TAR"
    fi
  else
    die "gpg 필요(클라우드 암호화 단계)"
  fi

  if [ "$APPLY" = "1" ]; then
    case "$CLOUD" in
      aws)
        need aws
        echo "[S3] 업로드 → $S3_URI ($S3_STORAGE_CLASS)"
        aws s3 cp "$ARCHIVE_GPG" "$S3_URI" --storage-class "$S3_STORAGE_CLASS"
        ;;
      gcs)
        need gsutil
        echo "[GCS] 업로드 → $GCS_URI ($GCS_STORAGE_CLASS)"
        gsutil -h "x-goog-storage-class:$GCS_STORAGE_CLASS" cp -n "$ARCHIVE_GPG" "$GCS_URI"
        ;;
      *) die "알 수 없는 CLOUD=$CLOUD" ;;
    esac
  else
    echo "[DRY] 클라우드 업로드 생략"
  fi
else
  echo "[SKIP] CLOUD=none"
fi

echo "[9/9] 결과 요약"
echo "PLAN:   $PLAN_JSONL"
echo "LOG:    $LOG"
echo "README: $README"
[ -f "$ARCHIVE_GPG" ] && echo "CLOUD OBJ: $ARCHIVE_GPG"

echo "=== 완료(DRY_RUN=$APPLY) : 에러 없었는지 로그 확인 ==="
