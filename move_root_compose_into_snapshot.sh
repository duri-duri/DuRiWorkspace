#!/usr/bin/env bash
set -Eeuo pipefail

SRC_COMPOSE="/mnt/h/ARCHIVE/docker-compose.yml"
ROOT="/mnt/h/ARCHIVE/docker"
SUDO="" ; [[ $EUID -ne 0 ]] && SUDO="sudo"

[[ -f "$SRC_COMPOSE" ]] || { echo "❌ not found: $SRC_COMPOSE"; exit 1; }

# 타임스탬프는 파일 mtime 기준(재실행해도 동일 경로로 들어감)
TS="$($SUDO date -r "$SRC_COMPOSE" +%Y%m%d_%H%M%S 2>/dev/null || date +%Y%m%d_%H%M%S)"
DATE="${TS:0:4}-${TS:4:2}-${TS:6:2}"
TIME="${TS:9:6}"

# 충돌 시 -1, -2 접미사
uniq_path(){ local p="$1"; $SUDO test ! -e "$p" && { echo "$p"; return; }
  local i=1; while $SUDO test -e "${p}-$i"; do ((i++)); done; echo "${p}-$i"; }

DST_BASE="$ROOT/snapshots/$DATE/$TIME"
DST_BASE="$(uniq_path "$DST_BASE")"
DST_DIR="$DST_BASE/00_root_compose"
$SUDO mkdir -p "$DST_DIR"

# 이동(파일명 충돌 시 접미사)
DST_FILE="$DST_DIR/docker-compose.yml"
if $SUDO test -e "$DST_FILE"; then
  n=1; while $SUDO test -e "${DST_FILE%.*}-$n.yml"; do ((n++)); done
  DST_FILE="${DST_FILE%.*}-$n.yml"
fi
$SUDO mv "$SRC_COMPOSE" "$DST_FILE"
$SUDO bash -c "sha256sum '$DST_FILE' > '$DST_BASE/.sha256'"

# 인덱스/LATEST 갱신
INDEX="$ROOT/index.md"
{
  echo "# Docker Snapshots"; echo
  echo "| Date | Time | Path | Files |"
  echo "|---|---|---|---|"
  while IFS= read -r -d '' dir; do
    rel="${dir#"$ROOT/"}"
    d="$(basename "$(dirname "$dir")")"
    t="$(basename "$dir")"
    files="$($SUDO find "$dir" -type f | wc -l | tr -d ' ')"
    echo "| $d | $t | $rel | $files |"
  done < <($SUDO find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d -print0 2>/dev/null | sort -z)
} | $SUDO tee "$INDEX" >/dev/null

echo "${DST_BASE#"$ROOT/"}" | $SUDO tee "$ROOT/LATEST.txt" >/dev/null

echo "✅ moved -> $DST_FILE"
echo "📄 index : $INDEX"
echo "➡️ latest: $(cat "$ROOT/LATEST.txt")"
