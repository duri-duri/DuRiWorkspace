#!/usr/bin/env bash
set -euo pipefail

# ====== 원장님 표준 경로 ======
SRC_DIRS=(
  "/mnt/h/ARCHIVE/FULL"    # 운영 주 저장소(H:)
  "/mnt/hdd/ARCHIVE/FULL"  # HDD 직경로(심볼릭 타겟 등)
)
DST_DIR="/mnt/e/DuRiSafe_HOSP/FULL"   # 콜드 금고(E:)
REPORT_DIR="/mnt/e/DuRiSafe_HOSP/REPORTS"

mkdir -p "$DST_DIR" "$REPORT_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="$REPORT_DIR/auto_mirror_$STAMP.log"

echo "[INFO] === AUTO MIRROR START @ $(date -Iseconds) ===" | tee -a "$REPORT"

# 1) 최신 FULL 아카이브 탐색 (여러 소스에서 가장 최신 1개)
LATEST_PATH=""
LATEST_MTIME=0
for D in "${SRC_DIRS[@]}"; do
  [ -d "$D" ] || continue
  while IFS= read -r line; do
    ts="${line%% *}"
    path="${line#* }"
    if awk "BEGIN{exit !($ts>$LATEST_MTIME)}"; then
      LATEST_MTIME="$ts"
      LATEST_PATH="$path"
    fi
  done < <(find "$D" -maxdepth 2 -type f -name 'FULL__*.tar.zst' -printf '%T@ %p\n' 2>/dev/null | sort -nr)
done

if [ -z "${LATEST_PATH:-}" ]; then
  echo "[WARN] 새 풀백업(.tar.zst) 미발견 — 종료" | tee -a "$REPORT"
  exit 0
fi

NAME="$(basename "$LATEST_PATH")"
DST_FILE="$DST_DIR/$NAME"

echo "[INFO] NEW=$LATEST_PATH" | tee -a "$REPORT"
echo "[INFO] -> COPY TO: $DST_FILE" | tee -a "$REPORT"

# 2) 재개 가능한 rsync (권한/소유권 속성 제외: drvfs 호환)
rsync -avh --progress --partial --append-verify \
  --no-perms --no-owner --no-group \
  "$LATEST_PATH" "$DST_DIR/" | tee -a "$REPORT"

# 3) SHA256 생성/검증
(
  cd "$DST_DIR"
  sha256sum "$NAME" | tee "$NAME.sha256"
  sha256sum -c "$NAME.sha256"
) | tee -a "$REPORT"

# 4) 포인터 갱신 (심링크 금지 → 텍스트 포인터)
echo "$NAME" > "$DST_DIR/LATEST.txt"
echo "[OK] LATEST.txt -> $NAME" | tee -a "$REPORT"

echo "[DONE] === AUTO MIRROR END @ $(date -Iseconds) ===" | tee -a "$REPORT"
