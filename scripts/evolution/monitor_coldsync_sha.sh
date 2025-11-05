#!/usr/bin/env bash
# coldsync SHA256 일치 여부 모니터링 메트릭 생성
# 목적: Prometheus에서 coldsync_sha_equal 메트릭 제공
# Usage: bash scripts/evolution/monitor_coldsync_sha.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

SRC="/home/duri/DuRiWorkspace/scripts/bin/coldsync_hosp_from_usb.sh"
DST="/usr/local/bin/coldsync_hosp_from_usb.sh"
METRICS_FILE="${ROOT}/var/evolution/coldsync_sha.prom"

# SHA256 계산
SHA_SRC=$(sha256sum "$SRC" 2>/dev/null | awk '{print $1}' || echo "")
SHA_DST=$(sha256sum "$DST" 2>/dev/null | awk '{print $1}' || echo "")

# 일치 여부 (1 = 일치, 0 = 불일치)
if [ -n "$SHA_SRC" ] && [ -n "$SHA_DST" ] && [ "$SHA_SRC" = "$SHA_DST" ]; then
    EQUAL=1
else
    EQUAL=0
fi

# Prometheus 메트릭 생성
mkdir -p "$(dirname "$METRICS_FILE")"
cat > "$METRICS_FILE" <<EOF
# TYPE coldsync_sha_equal gauge
# HELP coldsync_sha_equal SHA256 일치 여부 (1=일치, 0=불일치)
coldsync_sha_equal{job="coldsync",metric_realm="prod"} ${EQUAL}
# TYPE coldsync_sha_src_hash info
# HELP coldsync_sha_src_hash 소스 파일 SHA256 해시
coldsync_sha_src_hash{job="coldsync",metric_realm="prod",hash="${SHA_SRC}"} 1
# TYPE coldsync_sha_dst_hash info
# HELP coldsync_sha_dst_hash 설치본 파일 SHA256 해시
coldsync_sha_dst_hash{job="coldsync",metric_realm="prod",hash="${SHA_DST}"} 1
EOF

echo "✅ 메트릭 생성 완료: $METRICS_FILE"
echo "  일치 여부: $EQUAL (1=일치, 0=불일치)"

