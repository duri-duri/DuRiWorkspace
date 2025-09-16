#!/usr/bin/env bash
set -euo pipefail
TS="$(date +'%Y-%m-%d__%H%M')"
HOST="$(hostname | tr '[:space:]' '-')"
LEVEL="FULL"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
DAY_DIR="${DEST_ROOT}/$(date +'%Y')/$(date +'%m')/$(date +'%d')"
WORK="/tmp/du_backup_${LEVEL}_${TS}"

mkdir -p "$DAY_DIR" "$WORK"

# 전체 워크스페이스를 백업하되, 불필요한 파일들은 제외
EXC=(
    "--exclude=.git"
    "--exclude=__pycache__"
    "--exclude=*.pyc"
    "--exclude=.pytest_cache"
    "--exclude=.cache"
    "--exclude=node_modules"
    "--exclude=logs"
    "--exclude=temp_*"
    "--exclude=.DS_Store"
    "--exclude=var/tmp"
    "--exclude=var/run"
    "--exclude=var/cache"
    "--exclude=var/ephemeral_logs"
    "--exclude=*.log"
    "--exclude=*.tmp"
    "--exclude=*.swp"
    "--exclude=*.bak"
)

# 전체 워크스페이스를 백업 (include.lst 대신 직접 백업)
PAY="${WORK}/payload.tar"
echo "백업 시작: $(pwd) -> $PAY"
tar --sort=name --mtime='@0' --numeric-owner --owner=0 --group=0 \
    "${EXC[@]}" -cf "$PAY" .

OUT="${DAY_DIR}/${LEVEL}__${TS}__host-${HOST}.tar.zst"
echo "압축 시작: $PAY -> $OUT"
zstd -19 --long=27 --threads=0 -q -o "$OUT" "$PAY"

pushd "$DAY_DIR" >/dev/null
sha256sum "$(basename "$OUT")" > "SHA256SUMS.${LEVEL}.${TS}.txt"
popd >/dev/null

# state.json 동기화 (대형 아티팩트 참조)
if [ -f "tools/generate_or_update_state.py" ]; then
    echo "상태 파일 동기화 중..."
    python3 tools/generate_or_update_state.py \
      --workspace-root "/home/duri/DuRiWorkspace" \
      --state "/home/duri/DuRiWorkspace/learning_journal/state.json" \
      --backup-root "/mnt/c/Users/admin/Desktop/두리백업" \
      --backup-archive "$OUT" \
      --logical-prefix "full_"
fi

# 백업 통계 출력
BACKUP_SIZE=$(du -h "$OUT" | cut -f1)
ORIGINAL_SIZE=$(du -sh . | cut -f1)
FILE_COUNT=$(find . -type f | wc -l)
BACKUP_FILE_COUNT=$(tar -tf "$PAY" | wc -l)

echo "[OK] ${LEVEL} 백업: $OUT"
echo "백업 크기: $BACKUP_SIZE (압축됨)"
echo "원본 크기: $ORIGINAL_SIZE"
echo "원본 파일 수: $FILE_COUNT"
echo "백업 파일 수: $BACKUP_FILE_COUNT"
echo "백업률: $(echo "scale=1; $BACKUP_FILE_COUNT * 100 / $FILE_COUNT" | bc)%"

# 임시 파일 정리
rm -rf "$WORK"
