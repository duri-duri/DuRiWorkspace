#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="/mnt/h/ARCHIVE/docker"
SRC="/mnt/h/ARCHIVE"
mkdir -p "$ROOT/snapshots"

# 1) 기존 산재 폴더(예: docker_health_check_complete_20250922_150617)를 표준 위치로 이동
shopt -s nullglob
moved=0
for d in "$SRC"/docker_health_check_complete_*; do
  [[ -d "$d" ]] || continue
  base="$(basename "$d")"
  ts="$(echo "$base" | grep -oE '[0-9]{8}_[0-9]{6}' || true)"
  [[ -n "$ts" ]] || { echo "skip: $base (timestamp not found)"; continue; }
  date="${ts%%_*}"; time="${ts##*_}"
  date="${date:0:4}-${date:4:2}-${date:6:2}"
  dst="$ROOT/snapshots/$date/$time"
  mkdir -p "$dst"
  # 이동(덮어쓰기 방지)
  if [[ -d "$dst" ]]; then
    # 동일 타임스탬프가 이미 있으면 suffix 부여
    i=1; while [[ -e "$dst-$i" ]]; do ((i++)); done; dst="$dst-$i"
    mkdir -p "$dst"
  fi
  echo "→ move '$d' -> '$dst'"
  mv "$d" "$dst"
  moved=1
done

# 2) 빈 폴더 정리(표준 위치 제외, .keep 보존)
#   - 안전 장치: SRC 바로 아래 docker_*로 시작하는 빈 폴더만 제거
find "$SRC" -maxdepth 1 -type d -name 'docker_*' -empty -not -name '*.keep' -print -delete || true

# 3) 스냅샷 인덱스 생성
INDEX="$ROOT/index.md"
{
  echo "# Docker Snapshots"
  echo ""
  echo "| Date | Time | Path | Files |"
  echo "|---|---|---|---|"
  while IFS= read -r -d '' dir; do
    rel="${dir#$ROOT/}"
    date="$(echo "$rel" | cut -d/ -f3)"
    time="$(echo "$rel" | cut -d/ -f4)"
    files="$(find "$dir" -type f | wc -l | tr -d ' ')"
    echo "| $date | ${time} | $rel | $files |"
  done < <(find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d -print0 | sort -z)
} > "$INDEX"

# 4) 최신 포인터 갱신 (텍스트)
latest_dir="$(find "$ROOT/snapshots" -mindepth 2 -maxdepth 2 -type d | sort | tail -n1 || true)"
if [[ -n "$latest_dir" ]]; then
  echo "${latest_dir#$ROOT/}" > "$ROOT/LATEST.txt"
fi

echo "✅ relayout done. ROOT = $ROOT"
echo "   - index: $INDEX"
echo "   - latest: $(cat "$ROOT/LATEST.txt" 2>/dev/null || echo '-')"
