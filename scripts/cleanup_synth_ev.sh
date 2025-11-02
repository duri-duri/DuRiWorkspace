#!/usr/bin/env bash
# 합성 EV 청소기 - 24시간 후 합성 EV 제거
# B. 청소 크론 드리프트 방지: 중복 실행 방지 (flock)
set -euo pipefail

cd "$(dirname "$0")/.."

LOCKFILE="/tmp/cleanup.lock"
exec 9>"$LOCKFILE"
if ! flock -n 9; then
    echo "[INFO] 청소 작업이 이미 실행 중입니다. 종료합니다."
    exit 0
fi

echo "=== 합성 EV 청소 (24시간 이상 경과) ==="
echo ""

# B. node_exporter textfile 단일 경로화
TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
mkdir -p "$TEXTFILE_DIR"

REMOVED=0
while IFS= read -r -d '' dir; do
    if [ -n "$dir" ] && [ -d "$dir" ]; then
        echo "[REMOVE] $dir"
        rm -rf "$dir"
        REMOVED=$((REMOVED + 1))
    fi
done < <(find var/evolution -type d -name "EV-*-SYN*" -mmin +1440 -print0 2>/dev/null || true)

if [ "$REMOVED" -eq 0 ]; then
    echo "[OK] 제거할 합성 EV 없음 (24시간 미경과)"
else
    echo "[OK] 합성 EV $REMOVED 개 제거 완료"
fi

# 하드닝: SYN 청소 크론 헬스 메트릭 노출
EXPORT="$TEXTFILE_DIR/cleanup.prom"

# Prometheus 텍스트파일 형식으로 메트릭 기록
{
    echo "# HELP duri_syn_cleanup_last_unixtime Last cleanup execution timestamp (Unix seconds)"
    echo "# TYPE duri_syn_cleanup_last_unixtime gauge"
    printf "duri_syn_cleanup_last_unixtime %d\n" "$(date +%s)"
    echo "# HELP duri_syn_cleanup_removed_total Total synthetic EVs removed in this run"
    echo "# TYPE duri_syn_cleanup_removed_total counter"
    printf "duri_syn_cleanup_removed_total %d\n" "$REMOVED"
} > "$EXPORT.$$"

# 원자적 교체
mv "$EXPORT.$$" "$EXPORT"

echo "[OK] 청소 메트릭 기록: $EXPORT"

echo ""

