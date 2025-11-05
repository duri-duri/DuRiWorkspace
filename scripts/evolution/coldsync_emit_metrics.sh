#!/usr/bin/env bash
# L4.0 coldsync 운영 가시성 (Prometheus textfile metrics)
# Usage: bash scripts/evolution/coldsync_emit_metrics.sh
# 목적: 최근 설치 시각/해시를 Prometheus textfile 형식으로 노출

set -euo pipefail

DST="$HOME/.local/bin/coldsync_hosp_from_usb.sh"

# textfile 디렉토리 (Prometheus node_exporter가 읽는 경로)
TEXTFILE_DIR="${HOME}/DuRiWorkspace/.reports/textfile"
mkdir -p "$TEXTFILE_DIR"

OUT="${TEXTFILE_DIR}/coldsync.prom"

# 해시 계산
if [ -f "$DST" ]; then
    SUM=$(sha256sum "$DST" | awk '{print $1}')
    TS=$(date +%s)
    FILE_SIZE=$(stat -c%s "$DST" 2>/dev/null || echo 0)
    
    # Prometheus textfile 형식으로 출력
    {
        echo "# HELP coldsync_last_install_ts Last installation timestamp"
        echo "# TYPE coldsync_last_install_ts gauge"
        echo "coldsync_last_install_ts ${TS}"
        
        echo "# HELP coldsync_file_size File size in bytes"
        echo "# TYPE coldsync_file_size gauge"
        echo "coldsync_file_size{file=\"${DST}\"} ${FILE_SIZE}"
        
        echo "# HELP coldsync_file_exists File existence (1=exists, 0=missing)"
        echo "# TYPE coldsync_file_exists gauge"
        echo "coldsync_file_exists{file=\"${DST}\"} 1"
        
        echo "# SHA256: ${SUM}"
    } > "${OUT}.tmp"
    
    # atomic write
    mv -f "${OUT}.tmp" "${OUT}"
    
    echo "[OK] Metrics emitted: ${OUT}"
else
    {
        echo "coldsync_file_exists{file=\"${DST}\"} 0"
    } > "${OUT}.tmp"
    mv -f "${OUT}.tmp" "${OUT}"
    
    echo "[WARN] File not found: ${DST}"
fi

