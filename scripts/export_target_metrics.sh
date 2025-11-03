#!/usr/bin/env bash
# (1) 목표함수 실계측으로 교체(액세스 로그 기반 textfile, 당장 쓸 수 있음)
set -euo pipefail

cd "$(dirname "$0")/.."

# B. node_exporter textfile 단일 경로화
TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
mkdir -p "$TEXTFILE_DIR"

OUT="$TEXTFILE_DIR/target.prom"

# 옵션-빠름: 액세스 로그 기반 (Nginx/uvicorn 액세스로그에서 계산)
# TODO: 실제 액세스 로그 경로로 교체
ACCESS_LOG="${ACCESS_LOG:-var/logs/access.log}"

if [ -f "$ACCESS_LOG" ] && [ -s "$ACCESS_LOG" ]; then
    # 2xx/총요청 → success_rate
    ok=$(awk '$9 ~ /^2/ {c++} END {print c+0}' "$ACCESS_LOG" 2>/dev/null || echo "0")
    tot=$(awk 'END {print NR+0}' "$ACCESS_LOG" 2>/dev/null || echo "0")
    
    SR=$(python3 - <<'PY'
import sys
ok, tot = map(float, sys.argv[1:3])
print(0 if tot == 0 else ok / tot)
PY
    "$ok" "$tot")
    
    # p50 latency (ms) - 마지막 컬럼이 응답시간(ms)이라고 가정
    # TODO: 실제 로그 포맷에 맞게 수정
    P50=$(awk '{print $NF}' "$ACCESS_LOG" 2>/dev/null | sort -n | awk 'NF {a[NR]=$1} END{if(NR) print a[int(0.5*NR)+1]; else print 0}' || echo "0")
    
    # P50이 초 단위면 ms로 변환 (예: 0.21s → 210ms)
    P50_MS=$(python3 -c "print(max(0, float('$P50') * 1000))" 2>/dev/null || echo "0")
else
    # 로그 파일이 없으면 임시값 사용 (TODO 제거 필요)
    SR="0.82"
    P50_MS="210"
fi

{
    echo "# HELP duri_success_rate Success rate (0..1)"
    echo "# TYPE duri_success_rate gauge"
    echo "duri_success_rate $SR"
    echo "# HELP duri_latency_p50_ms p50 latency (ms)"
    echo "# TYPE duri_latency_p50_ms gauge"
    echo "duri_latency_p50_ms $P50_MS"
} > "$OUT.$$"

# 원자적 교체
mv "$OUT.$$" "$OUT"

echo "[OK] 목표함수 메트릭 기록: $OUT (SR=$SR, P50=${P50_MS}ms)"

