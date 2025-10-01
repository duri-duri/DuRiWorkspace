#!/usr/bin/env bash
set -euo pipefail

# ---------- 기본 설정 ----------
LEVEL="FULL"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-$PWD}"
HOSTNAME_SAFE="$(hostname 2>/dev/null || echo host)"
NOW_KST="$(TZ=Asia/Seoul date +'%Y-%m-%d__%H%M')"
Y="$(TZ=Asia/Seoul date +'%Y')"
M="$(TZ=Asia/Seoul date +'%m')"
D="$(TZ=Asia/Seoul date +'%d')"

# 기본 백업 루트(WSL/Windows 데스크톱 폴더), 필요 시 환경변수로 덮어쓰기 가능
DEFAULT_BACKUP_ROOT="/mnt/c/Users/admin/Desktop/두리백업/${Y}/${M}/${D}"
BACKUP_ROOT="${BACKUP_ROOT:-$DEFAULT_BACKUP_ROOT}"

# --- [패치1] 동시 실행 차단 + 프리플라이트 ---
LOCK="/tmp/duri-backup.${LEVEL}.lock"
exec 9>"$LOCK"
flock -n 9 || { echo "⏳ $LEVEL already running"; exit 0; }

# 최소 여유 공간(GB) – FULL은 15GB 권장
REQUIRED_GB="${REQUIRED_GB:-15}"
FREE_GB=$(df -P "$BACKUP_ROOT" 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
[[ ${FREE_GB:-0} -lt $REQUIRED_GB ]] && { echo "❌ not enough space: need ${REQUIRED_GB}GB, have ${FREE_GB}GB"; exit 3; }

mkdir -p "$BACKUP_ROOT"

# ---------- 압축기 선택(zstd → gzip 폴백) ----------
EXT=".tar.zst"
COMPRESS_CMD="zstd -T0 -19 -q -c"
if ! command -v zstd >/dev/null 2>&1; then
  EXT=".tar.gz"
  COMPRESS_CMD="gzip -9 -c"
fi

# 이중 확장자 방지 - EXT에 .tar.zst 포함
ARCHIVE="${BACKUP_ROOT}/${LEVEL}__${NOW_KST}__host-${HOSTNAME_SAFE}${EXT}"

# ---------- include / exclude ----------
# 사전에 준비된 include 리스트가 있으면 우선 사용(예: backup_include_full.txt)
INCLUDE_HINT="${INCLUDE_HINT:-backup_include_full.txt}"
EXCLUDE_FILE="${EXCLUDE_FILE:-backup_exclude.txt}"

# 존재하는 경로만 tar에 태우기 위해 동적으로 files.list 작성
TMP_LIST="$(mktemp)"
cleanup() { rm -f "$TMP_LIST"; }
trap cleanup EXIT

# (1) 힌트 파일이 있으면 거기서 읽고, 없으면 기본 셋 구성
if [[ -f "$INCLUDE_HINT" ]]; then
  mapfile -t CANDIDATES < <(grep -v '^\s*$' "$INCLUDE_HINT" | sed 's/\r$//')
else
  # 기본 후보: 프로젝트 핵심/문서/스크립트/도커/테스트
  CANDIDATES=(
    "DuRiCore" "duri_core" "duri_brain" "duri_control"
    "scripts" "tools" "docs" "configs" "resources"
    "docker" "docker-compose.yml" "docker-compose.allinone.yml"
    "*.md" "*.json" "pytest.ini" ".env" "requirements*.txt"
    "tests" "test_*.py"
  )
fi

# (2) 글롭 허용해서 실존 파일만 리스트업
shopt -s nullglob dotglob
for pat in "${CANDIDATES[@]}"; do
  # 워크스페이스 기준 상대경로로 정규화
  while IFS= read -r -d '' p; do
    # git 저장소/캐시/가상환경 등 무거운 것 일부 자동 제외(추가로 exclude 파일에서도 제외)
    case "$p" in
      */.git|*/.git/*|*/.pytest_cache|*/.pytest_cache/*|*/__pycache__|*/__pycache__/*|*/.venv|*/.venv/*)
        continue;;
    esac
    printf '%s\0' "$p" >> "$TMP_LIST"
  done < <(cd "$WORKSPACE_ROOT" && find $pat -type f -print0 2>/dev/null || true)
done
shopt -u nullglob dotglob

# ---------- tar 옵션(결정적 빌드) ----------
# --sort=name  : 파일명 순 정렬
# --mtime='@0' : mtime 고정(재현 가능성 ↑)  ※ BusyBox tar 호환 X → GNU tar 기준
# --numeric-owner/--owner/--group : 소유자 정보를 고정
# --pax-option : 메타 축소
TAR_COMMON_OPTS=(
  --sort=name
  --mtime='@0'
  --numeric-owner --owner=0 --group=0
  --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime
  --ignore-failed-read
)

# exclude 파일이 있으면 반영
if [[ -f "$EXCLUDE_FILE" ]]; then
  TAR_COMMON_OPTS+=( --exclude-from="$EXCLUDE_FILE" )
fi

# ---------- 생성 시작 ----------
umask 077
echo "[$LEVEL] 백업 시작 → $ARCHIVE"
echo " - workspace: $WORKSPACE_ROOT"
echo " - output   : $ARCHIVE"

# --- [패치6] 진행상황 모니터링 ---
BACKUP_START_TIME=$(date +%s)
# NUL 리스트에서 정확한 파일 수 계산 (여러 방법 시도)
TOTAL_FILES=0
if [[ -s "$TMP_LIST" ]]; then
  # 방법 1: awk NUL 처리
  TOTAL_FILES=$(awk -v RS='\0' 'END{print NR}' "$TMP_LIST" 2>/dev/null || echo 0)

  # 방법 2: tr로 개행 변환 후 wc
  if [[ "$TOTAL_FILES" -eq 0 ]]; then
    TOTAL_FILES=$(tr '\0' '\n' < "$TMP_LIST" | wc -l | tr -d ' ' 2>/dev/null || echo 0)
  fi

  # 방법 3: 직접 카운트
  if [[ "$TOTAL_FILES" -eq 0 ]]; then
    TOTAL_FILES=$(grep -c . "$TMP_LIST" 2>/dev/null || echo 0)
  fi
fi
echo " - 총 파일 수: ${TOTAL_FILES}"
echo " - 백업 시작 시간: $(date +'%H:%M:%S')"
echo "--- 백업 진행상황 ---"

# 진행상황 표시 함수
show_progress() {
    local current_size="$1"
    local processed_files="$2"
    local elapsed_time="$3"

    local progress_percent=$((processed_files * 100 / TOTAL_FILES))
    echo "[$(date +'%H:%M:%S')] 진행률: ${progress_percent}% (${processed_files}/${TOTAL_FILES} 파일) - 크기: ${current_size} - 경과시간: ${elapsed_time}"
}

# 파일 리스트가 비어있으면 안전 중단
if [[ ! -s "$TMP_LIST" ]]; then
  echo "⚠️  포함할 파일이 없습니다. include 힌트 혹은 기본 후보가 실존하지 않아요."
  exit 2
fi

# --- [패치5] 파일리스트 보존(결정성 증거물) ---
cp -f "$TMP_LIST" "${BACKUP_ROOT}/filelist.${LEVEL}.${NOW_KST}.txt" 2>/dev/null || true

# tar + 압축 파이프
# GNU tar에서 --files-from=- --null 로 NUL 분리 입력 처리
set -o pipefail

# --- [패치2] 해시리스트 생성 (FULL은 필수) ---
if command -v sha256sum >/dev/null 2>&1; then
  HASHLIST="${BACKUP_ROOT}/HASHLIST.${LEVEL}.${NOW_KST}.txt"
  # 주요 폴더만 선택
  find DuRiCore scripts tools configs docs -type f -print0 2>/dev/null \
    | xargs -0 sha256sum > "${HASHLIST}" || true
fi

# 원자적 산출물 작성
TMP="${ARCHIVE}.partial"
echo "압축 시작... 현재 터미널에서 실시간 진행상황을 표시합니다."

# 백업 로그 파일 생성
BACKUP_LOG="/tmp/full_backup.log"
echo "[$(date +'%H:%M:%S')] FULL 백업 시작 - 총 $TOTAL_FILES 파일" > "$BACKUP_LOG"

# 백업 로그 파일 생성
BACKUP_LOG="/tmp/full_backup.log"
echo "[$(date +'%H:%M:%S')] FULL 백업 시작 - 총 $TOTAL_FILES 파일" > "$BACKUP_LOG"

# 실제 백업 실행 (pv를 사용한 실시간 진행률)
echo "--- 백업 진행상황 ---"

# 총 바이트 수 계산 (pv 진행률용)
echo "총 크기 계산 중..."
TOTAL_BYTES=$(du -sb --files0-from="$TMP_LIST" 2>/dev/null | awk '{s+=$1} END{print s+0}')

if [[ "$TOTAL_BYTES" -gt 0 ]]; then
    echo "총 크기: $(numfmt --to=iec $TOTAL_BYTES) (${TOTAL_BYTES} bytes)"
    echo "pv를 사용한 실시간 진행률 표시 시작..."

    # pv를 사용한 실시간 진행률 (인터넷 다운로드처럼!)
    tar -C "$WORKSPACE_ROOT" "${TAR_COMMON_OPTS[@]}" --null -T "$TMP_LIST" -cf - \
    | pv -s "$TOTAL_BYTES" -p -t -e -r \
    | eval "$COMPRESS_CMD" > "$TMP"
else
    echo "총 크기 계산 실패, 기본 진행률 표시..."
    tar -C "$WORKSPACE_ROOT" "${TAR_COMMON_OPTS[@]}" --null -T "$TMP_LIST" -cf - \
    | pv -p -t -e -r \
    | eval "$COMPRESS_CMD" > "$TMP"
fi



sync; mv "$TMP" "$ARCHIVE"
echo "압축 완료! 최종 크기: $(du -h "$ARCHIVE" | awk '{print $1}')" | tee -a "$BACKUP_LOG"

# --- [패치3] 불변 보관 ---
chmod a-w "$ARCHIVE" 2>/dev/null || true

# --- [패치4] 알림 ---
notify(){
  local msg="$1"; command -v curl >/dev/null 2>&1 || return 0
  [[ -n "${NTFY_TOPIC:-}" ]] || return 0
  curl -s -H "Title: DuRi Backup ${LEVEL}" -d "$msg" "https://ntfy.sh/${NTFY_TOPIC}" >/dev/null || true
}
notify "OK $(basename "$ARCHIVE") size=$(du -h "$ARCHIVE" | awk '{print $1}') host=${HOSTNAME_SAFE} at=${NOW_KST}"

# ---------- 해시/매니페스트 ----------
if command -v sha256sum >/dev/null 2>&1; then
  SUMS="${BACKUP_ROOT}/SHA256SUMS.${LEVEL}.${NOW_KST}.txt"
  (cd "$(dirname "$ARCHIVE")" && sha256sum "$(basename "$ARCHIVE")") > "$SUMS"
  echo "SHA256SUM 생성: $SUMS"
fi

# -------- FULL manifest builder (fast/verify modes) --------
VERIFY_ENTRY=0
[[ "${1:-}" == "--verify-entry-count" ]] && VERIFY_ENTRY=1
[[ "${FULL_VERIFY_ENTRY:-}" == "1" ]] && VERIFY_ENTRY=1

STAMP="${NOW_KST}"                               # e.g. 2025-08-14__2215
SUMS_BASENAME="SHA256SUMS.FULL.${STAMP}.txt"
SUMS_PATH="${BACKUP_ROOT}/${SUMS_BASENAME}"
ARCH_BASENAME="$(basename "$ARCHIVE")"

# size (bytes)
if command -v stat >/dev/null 2>&1; then
  ARCH_SIZE="$(stat -c%s "$ARCHIVE" 2>/dev/null || stat -f%z "$ARCHIVE" 2>/dev/null || echo 0)"
else
  ARCH_SIZE=0
fi

# filelist (prefer prebuilt list, otherwise tar-list from archive)
FILELIST_PATH="${BACKUP_ROOT}/filelist.FULL.${STAMP}.txt"
if [[ -n "${TMP_LIST:-}" && -s "${TMP_LIST:-/dev/null}" ]]; then
  cp -f "$TMP_LIST" "$FILELIST_PATH"
else
  if [[ "$ARCHIVE" == *.zst ]]; then
    if command -v zstd >/dev/null 2>&1; then
      zstd -dc -- "$ARCHIVE" | tar -tf - > "$FILELIST_PATH"
    else
      echo "[WARN] zstd not found; cannot list .zst archive. Skipping filelist." >&2
      : > "$FILELIST_PATH"
    fi
  else
    tar -tf -- "$ARCHIVE" > "$FILELIST_PATH"
  fi
fi

# entry_count
ENTRY_COUNT=0
if [[ "$VERIFY_ENTRY" -eq 1 ]]; then
  # 정확 모드: tar 내부 엔트리 직접 카운트
  if [[ "$ARCHIVE" == *.zst && "$(command -v zstd)" ]]; then
    ENTRY_COUNT="$(zstd -dc -- "$ARCHIVE" | tar -tf - | wc -l | tr -d ' ')"
  else
    ENTRY_COUNT="$(tar -tf -- "$ARCHIVE" | wc -l | tr -d ' ')"
  fi
else
  # 빠른 모드: 파일리스트 줄 수 사용(없으면 0)
  [[ -s "$FILELIST_PATH" ]] && ENTRY_COUNT="$(wc -l < "$FILELIST_PATH" | tr -d ' ')" || ENTRY_COUNT=0
fi

# lightweight HASHLIST (archive sha256 + 샘플 경로)
HASHLIST_PATH="${BACKUP_ROOT}/HASHLIST.FULL.${STAMP}.txt"
{
  echo "# HASHLIST.FULL (lightweight)"
  if [[ -s "$SUMS_PATH" ]]; then
    awk '{print $1, $2}' "$SUMS_PATH"
  fi
  echo "# SAMPLE_PATHS (up to 100):"
  head -n 100 "$FILELIST_PATH" 2>/dev/null || true
} > "$HASHLIST_PATH"

# manifest.full.json (원자적 쓰기 + NTFS RO 해제)
MF_PATH="${BACKUP_ROOT}/manifest.full.json"
MF_TMP="${BACKUP_ROOT}/.manifest.full.json.$$"
KST_NOW_ISO="$(TZ=Asia/Seoul date -Iseconds)"

# NTFS에서 기존 manifest가 RO면 해제(있을 때만)
if command -v powershell.exe >/dev/null 2>&1 && [ -f "$MF_PATH" ]; then
  WINPATH=$(wslpath -w "$MF_PATH")
  powershell.exe -NoProfile -Command "attrib -R \"$WINPATH\"" >/dev/null 2>&1 || true
fi

# 임시 파일에 JSON 생성
cat > "$MF_TMP" <<JSON
{
  "profile": "DuRi-FULL",
  "level": "FULL",
  "created_at_kst": "$KST_NOW_ISO",
  "host": "${HOSTNAME_SAFE}",
  "workspace_root": "${WORKSPACE_ROOT:-$PWD}",
  "archive": "$ARCH_BASENAME",
  "archive_path": "${BACKUP_ROOT%/}/$ARCH_BASENAME",
  "size_bytes": $ARCH_SIZE,
  "sha256_file": "$SUMS_BASENAME",
  "filelist_file": "$(basename "$FILELIST_PATH")",
  "hashlist_file": "$(basename "$HASHLIST_PATH")",
  "entry_count": $ENTRY_COUNT,
  "verify_entry_mode": ${VERIFY_ENTRY},
  "backfilled": false
}
JSON

# 원자적 교체
mv -f "$MF_TMP" "$MF_PATH"

# manifest는 불변 대상에서 제외 (수정/갱신 가능해야 함)
# chmod a-w "$MF_PATH" 2>/dev/null || true

# manifest.json (간단 버전)
MANIFEST="${BACKUP_ROOT}/manifest.json"
SIZE_BYTES="$(stat -c%s "$ARCHIVE" 2>/dev/null || wc -c <"$ARCHIVE")"
cat > "$MANIFEST" <<JSON
{
  "host": "${HOSTNAME_SAFE}",
  "created_kst": "$(TZ=Asia/Seoul date --iso-8601=seconds)",
  "level": "${LEVEL}",
  "archive": "$(basename "$ARCHIVE")",
  "archive_path": "${ARCHIVE}",
  "size_bytes": ${SIZE_BYTES}
}
JSON
echo "manifest 갱신: $MANIFEST"

# ---------- state.json 동기화(선택) ----------
# tools/generate_or_update_state.py 있으면 활용
if [[ -f "tools/generate_or_update_state.py" ]]; then
python3 tools/generate_or_update_state.py \
    --workspace-root "$WORKSPACE_ROOT" \
    --state "${STATE_JSON:-tools/state.json}" \
    --backup-root "$BACKUP_ROOT" \
    --backup-archive "$ARCHIVE" \
    --logical-prefix "$LEVEL" \
    --scan-glob "*.tar.*" || true
fi

echo "[$LEVEL] 백업 완료 ✅ → $ARCHIVE"
