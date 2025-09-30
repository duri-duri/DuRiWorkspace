#!/usr/bin/env bash
set -Eeuo pipefail

# ===== 설정 =====
SRC="/mnt/h/ARCHIVE"                # 정리 대상 루트
ROOT="/mnt/h/ARCHIVE/docker"        # 표준 루트 (결과 적재)
SRC_COMPOSE="$SRC/docker-compose.yml"
SUDO=""; [[ $EUID -ne 0 ]] && SUDO="sudo"

# ===== 공용 유틸 =====
msg(){ printf "%b\n" "$*"; }
ensure_dirs(){ $SUDO mkdir -p "$ROOT/snapshots"; }
uniq_path(){ local p="$1"; $SUDO test ! -e "$p" && { echo "$p"; return; }
  local i=1; while $SUDO test -e "${p}-$i"; do ((i++)); done; echo "${p}-$i"; }

# ===== 1) docker_health_check_complete_* → 이동(mv) =====
move_health_complete(){
  shopt -s nullglob
  local moved=0
  for d in "$SRC"/docker_health_check_complete_*; do
    [[ -d "$d" ]] || continue
    local base ts date time dst
    base="$(basename "$d")"
    ts="$(grep -oE '[0-9]{8}_[0-9]{6}' <<<"$base" || true)" || true
    [[ -n "$ts" ]] || { msg "skip(move): $base (timestamp not found)"; continue; }
    date="${ts%%_*}"; time="${ts##*_}"
    date="${date:0:4}-${date:4:2}-${date:6:2}"
    dst="$(uniq_path "$ROOT/snapshots/$date/$time")"
    $SUDO mkdir -p "$(dirname "$dst")"
    msg "→ move '$base'  ->  ${dst#"$ROOT/"}"
    $SUDO mv "$d" "$dst"
    moved=1
  done
  [[ $moved -eq 0 ]] && msg "noop(move): nothing to move"
}

# ===== 2) DOCKER_* / Docker_* → 복사(rsync) + 체크섬/메타, 비었으면 삭제 =====
ingest_upper(){
  shopt -s nullglob
  local ing=0
  for d in "$SRC"/DOCKER_* "$SRC"/Docker_*; do
    [[ -d "$d" ]] || continue
    local base ts date time dst bkup
    base="$(basename "$d")"
    ts="$(grep -oE '[0-9]{8}_[0-9]{6}' <<<"$base" || true)"
    [[ -z "$ts" ]] && ts="$(date -d "@$($SUDO stat -c %Y "$d")" +%Y%m%d_%H%M%S)"
    date="${ts:0:4}-${ts:4:2}-${ts:6:2}"
    time="${ts:9:6}"
    dst="$(uniq_path "$ROOT/snapshots/$date/$time")"
    bkup="$dst/00_backup_original"
    $SUDO mkdir -p "$bkup"

    msg "→ ingest '$base'  ->  ${bkup#"$ROOT/"}"
    $SUDO rsync -a --human-readable "$d"/ "$bkup"/

    $SUDO bash -c "(cd '$bkup' && find . -type f -print0 | xargs -0 sha256sum) > '$dst/.sha256'"
    $SUDO bash -c "printf '{\"source\":\"%s\",\"ts\":\"%s\"}\n' '$d' '$ts' > '$dst/ingest_meta.json'"

    # 원본이 '이미' 비어 있으면 정리 (복사 방식이라 보통은 남겨둠)
    if [ "$($SUDO find "$d" -mindepth 1 -type f -o -type d | wc -l | tr -d ' ')" -eq 0 ]; then
      $SUDO rmdir "$d" && msg "🗑️  removed empty source: $base"
    else
      msg "⚠️  source not empty: $base (kept)"
    fi
    ing=1
  done
  [[ $ing -eq 0 ]] && msg "noop(ingest): nothing to ingest"
}

# ===== 3) ARCHIVE 루트의 docker-compose.yml → 최신 스냅샷으로 이동 =====
move_root_compose(){
  [[ -f "$SRC_COMPOSE" ]] || { msg "noop(compose): not found $SRC_COMPOSE"; return; }
  local TS DATE TIME DST_BASE DST_DIR DST_FILE
  TS="$($SUDO date -r "$SRC_COMPOSE" +%Y%m%d_%H%M%S 2>/dev/null || date +%Y%m%d_%H%M%S)"
  DATE="${TS:0:4}-${TS:4:2}-${TS:6:2}"
  TIME="${TS:9:6}"
  DST_BASE="$(uniq_path "$ROOT/snapshots/$DATE/$TIME")"
  DST_DIR="$DST_BASE/00_root_compose"
  $SUDO mkdir -p "$DST_DIR"
  DST_FILE="$DST_DIR/docker-compose.yml"
  if $SUDO test -e "$DST_FILE"; then
    local n=1; while $SUDO test -e "${DST_FILE%.*}-$n.yml"; do ((n++)); done
    DST_FILE="${DST_FILE%.*}-$n.yml"
  fi
  msg "→ move 'docker-compose.yml' -> ${DST_FILE#"$ROOT/"}"
  $SUDO mv "$SRC_COMPOSE" "$DST_FILE"
  $SUDO bash -c "sha256sum '$DST_FILE' > '$DST_BASE/.sha256'"
}

# ===== 4) 인덱스 & 최신 포인터 갱신 =====
update_index_latest(){
  local INDEX="$ROOT/index.md"
  $SUDO mkdir -p "$ROOT"
  {
    echo "# Docker Snapshots"
    echo
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

  local latest
  latest="$($SUDO find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d 2>/dev/null | sort | tail -n1 || true)"
  [[ -n "$latest" ]] && echo "${latest#"$ROOT/"}" | $SUDO tee "$ROOT/LATEST.txt" >/dev/null

  msg "index : $INDEX"
  msg "latest: $($SUDO cat "$ROOT/LATEST.txt" 2>/dev/null || echo '-')"
}

# ===== 실행 플로우 =====
ensure_dirs
move_health_complete
ingest_upper
move_root_compose
update_index_latest
msg "✅ all-in-one relayout complete. ROOT = $ROOT"


