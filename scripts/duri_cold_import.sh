#!/usr/bin/env bash
set -Eeuo pipefail
export LC_ALL=C

ok(){ echo "[OK ] $*"; }; ng(){ echo "[ERR] $*"; }; info(){ echo "[.. ] $*"; }

USB_ROOT="/mnt/g/DuRiSync"
E_ROOT="/mnt/e/DuRiSafe_HOSP/DAILY"

# 전제
mountpoint -q /mnt/e || { ng "/mnt/e not mounted"; exit 2; }
[ -d "$USB_ROOT" ] || { ng "USB_ROOT not found: $USB_ROOT"; exit 3; }
mkdir -p "$E_ROOT"

# 대상 선택
DUMP="${1:-}"
if [ -z "$DUMP" ]; then
  DUMP="$(timeout 3s bash -c "find '$USB_ROOT' -maxdepth 1 -type f -name 'Dump_*.dump' -printf '%T@ %p\n' 2>/dev/null" \
          | sort -nr | head -1 | awk '{ $1=""; sub(/^ /,""); print }')"
fi
[ -n "$DUMP" ] && [ -f "$DUMP" ] || { ng "dump not found on USB"; exit 4; }

F="$(basename "$DUMP")"
SHA_SRC="${DUMP}.sha256"

# 복사(존재 시 보존)
cp -n "$DUMP" "$E_ROOT/$F"       2>/dev/null || true
[ -f "$SHA_SRC" ] && cp -n "$SHA_SRC" "$E_ROOT/${F}.sha256" 2>/dev/null || true

# 해시 검증/생성
if [ -f "$E_ROOT/${F}.sha256" ]; then
  EXP="$(awk '{print $1}' "$E_ROOT/${F}.sha256" | head -1)"
  ACT="$(sha256sum "$E_ROOT/$F" | awk '{print $1}')"
  [ "$EXP" = "$ACT" ] || { ng "sha256 mismatch"; exit 10; }
  ok "sha256 verified"
else
  sha256sum "$E_ROOT/$F" > "$E_ROOT/${F}.sha256"
  ok "sha256 created"
fi

# 로그
DAY="$(date +%Y%m%d)"
LOG_MD="/mnt/e/DuRiSafe_HOSP/backup_log_${DAY}.md"
{ echo "# Cold Import Log $(date '+%F %T')"; echo "- src(USB): $DUMP"; echo "- dst(E): $E_ROOT/$F"; echo "- sha256: $(awk '{print $1}' "$E_ROOT/${F}.sha256")"; } >> "$LOG_MD"

ok "COLD_IMPORT_OK -> $E_ROOT/$F"
