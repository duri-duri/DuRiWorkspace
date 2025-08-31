#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="${1:-}"
if [[ -z "$TARGET_DIR" ]]; then
  echo "Usage: $0 /path/to/backup/YYYY/MM/DD" >&2
  exit 2
fi
cd "$TARGET_DIR"

# 최신 FULL 아카이브 선택
LATEST="$(ls -1t FULL__*.tar* 2>/dev/null | head -n1 || true)"
if [[ -z "$LATEST" ]]; then
  echo "[ERR] No FULL archive found in: $TARGET_DIR" >&2
  exit 1
fi

ARCHIVE="$TARGET_DIR/$LATEST"
# 시간 스탬프 추출 (FULL__YYYY-MM-DD__HHMM__host-*.tar*)
STAMP="$(echo "$LATEST" | sed -n 's/^FULL__\([0-9-]\{10\}__[0-9]\{4\}\)__host.*$/\1/p')"
STAMP="${STAMP:-$(date +%Y-%m-%d__%H%M)}"

BACKUP_ROOT="$TARGET_DIR"
HOSTNAME_SAFE="$(echo "$LATEST" | sed -n 's/^.*__host-\(.*\)\..*$/\1/p')"

# size
if command -v stat >/dev/null 2>&1; then
  ARCH_SIZE="$(stat -c%s "$ARCHIVE" 2>/dev/null || stat -f%z "$ARCHIVE" 2>/dev/null || echo 0)"
else
  ARCH_SIZE=0
fi

# SHA256SUMS (있으면 사용, 없으면 생성)
SUMS_BASENAME="SHA256SUMS.FULL.${STAMP}.txt"
SUMS_PATH="$BACKUP_ROOT/$SUMS_BASENAME"
if [[ ! -s "$SUMS_PATH" ]]; then
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$BACKUP_ROOT" && sha256sum "$LATEST" > "$SUMS_BASENAME")
  else
    echo "[WARN] sha256sum not found; creating empty sums file." >&2
    : > "$SUMS_PATH"
  fi
fi

# filelist (항상 tar에서 추출)
FILELIST_PATH="${BACKUP_ROOT}/filelist.FULL.${STAMP}.txt"
if [[ "$LATEST" == *.zst && "$(command -v zstd)" ]]; then
  zstd -dc "$ARCHIVE" | tar -tf - > "$FILELIST_PATH"
else
  tar -tf "$ARCHIVE" > "$FILELIST_PATH"
fi

# entry_count
ENTRY_COUNT="$(wc -l < "$FILELIST_PATH" | tr -d ' ')"

# lightweight HASHLIST
HASHLIST_PATH="${BACKUP_ROOT}/HASHLIST.FULL.${STAMP}.txt"
{
  echo "# HASHLIST.FULL (lightweight/backfilled)"
  [[ -s "$SUMS_PATH" ]] && awk '{print $1, $2}' "$SUMS_PATH"
  echo "# SAMPLE_PATHS (up to 100):"
  head -n 100 "$FILELIST_PATH" 2>/dev/null || true
} > "$HASHLIST_PATH"

# manifest.full.json
MF_PATH="${BACKUP_ROOT}/manifest.full.json"
KST_ISO="$(TZ=Asia/Seoul date -Iseconds -r "$ARCHIVE" 2>/dev/null || TZ=Asia/Seoul date -Iseconds)"
cat > "$MF_PATH" <<JSON
{
  "profile": "DuRi-FULL",
  "level": "FULL",
  "created_at_kst": "$KST_ISO",
  "host": "${HOSTNAME_SAFE:-unknown}",
  "workspace_root": "unknown",
  "archive": "$LATEST",
  "archive_path": "${BACKUP_ROOT%/}/$LATEST",
  "size_bytes": $ARCH_SIZE,
  "sha256_file": "$SUMS_BASENAME",
  "filelist_file": "$(basename "$FILELIST_PATH")",
  "hashlist_file": "$(basename "$HASHLIST_PATH")",
  "entry_count": $ENTRY_COUNT,
  "verify_entry_mode": 1,
  "backfilled": true
}
JSON

chmod a-w "$MF_PATH" 2>/dev/null || true
echo "[OK] backfilled manifest: $MF_PATH"
