#!/usr/bin/env bash
set -Eeuo pipefail

SRC="/mnt/h/ARCHIVE"                 # 레거시 폴더가 있는 상위
ROOT="/mnt/h/ARCHIVE/docker"         # 표준 루트
mkdir -p "$ROOT/snapshots"

ingested=0
shopt -s nullglob
for d in "$SRC"/DOCKER_* "$SRC"/Docker_*; do
  [[ -d "$d" ]] || continue
  base="$(basename "$d")"

  # 1) 타임스탬프 추출(없으면 mtime 사용)
  if TS="$(grep -oE '[0-9]{8}_[0-9]{6}' <<<"$base" || true)"; [[ -z "$TS" ]]; then
    TS="$(date -d "@$(stat -c %Y "$d")" +%Y%m%d_%H%M%S)"
  fi
  DATE="${TS:0:4}-${TS:4:2}-${TS:6:2}"
  TIME="${TS:9:6}"

  # 2) 목적지 결정
  DST="$ROOT/snapshots/$DATE/$TIME"
  if [[ -e "$DST" ]]; then
    i=1; while [[ -e "${DST}-$i" ]]; do ((i++)); done; DST="${DST}-$i"
  fi
  BKDST="$DST/00_backup_original"
  sudo mkdir -p "$BKDST"

  echo "→ ingest '$base' -> $BKDST"
  # 3) 복사(무삭제, 무손실)
  sudo rsync -a --human-readable "$d"/ "$BKDST"/

  # 4) 체크섬 기록(검증용)
  sudo bash -c "(cd '$BKDST' && find . -type f -print0 | xargs -0 sha256sum) > '$DST/.sha256'"

  # 5) 메타데이터 기록
  sudo bash -c "printf '{\"source\":\"%s\",\"ts\":\"%s\"}\n' '$d' '$TS' > '$DST/ingest_meta.json'"

  ingested=1
done

# 6) 인덱스/최신 포인터 갱신
if (( ingested )); then
  INDEX="$ROOT/index.md"
  {
    echo "# Docker Snapshots"
    echo
    echo "| Date | Time | Path | Files |"
    echo "|---|---|---|---|"
    while IFS= read -r -d '' dir; do
      rel="${dir#$ROOT/}"
      date="$(echo "$rel" | cut -d/ -f3)"
      time="$(echo "$rel" | cut -d/ -f4)"
      files="$(sudo find "$dir" -type f | wc -l | tr -d ' ')"
      echo "| $date | $time | $rel | $files |"
    done < <(find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d -print0 | sort -z)
  } | sudo tee "$INDEX" >/dev/null

  latest_dir="$(find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d | sort | tail -n1 || true)"
  [[ -n "$latest_dir" ]] && echo "${latest_dir#$ROOT/}" | sudo tee "$ROOT/LATEST.txt" >/dev/null
fi

echo "✅ ingest complete. (no deletion)"
