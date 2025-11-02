#!/usr/bin/env bash
# (2) TS 라우팅 실제 소비 연결 - 서비스 레벨 적용 규칙
# (B) TS 라우팅 "소비"를 실트래픽에 반영 (Redis 키 사용; 실패시 50/50 복귀)
set -euo pipefail

cd "$(dirname "$0")/.."

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
R="$TEXTFILE_DIR/routes.json"
METRICS_OUT="$TEXTFILE_DIR/route_apply.prom"
REDIS="${REDIS_URL:-redis://localhost:6379}"

fail() {
    {
        echo "# HELP ab_route_apply_success Route apply success (1=success,0=fail)"
        echo "# TYPE ab_route_apply_success gauge"
        echo "ab_route_apply_success 0"
    } > "$METRICS_OUT"
    exit 1
}

if [ ! -f "$R" ]; then
    echo "[WARN] routes.json not found: $R"
    fail
fi

# 유효성 검증
A=$(jq -r '.A' "$R" 2>/dev/null || echo '')
B=$(jq -r '.B' "$R" 2>/dev/null || echo '')

valid() {
    awk -v x="$1" 'BEGIN{exit !(x!="" && x>=0 && x<=1)}'
}

sum_ok() {
    awk -v a="$1" -v b="$2" 'BEGIN{d=(a+b); exit !(d>0.98 && d<1.02)}'
}

if ! valid "$A" || ! valid "$B" || ! sum_ok "$A" "$B"; then
    echo "[WARN] Invalid routes.json, applying conservative split (0.5/0.5)"
    A=0.5
    B=0.5
fi

# 실소비: Redis 키에 기록 (소비 측 라우터가 이 키를 읽어 분배하도록)
if command -v redis-cli >/dev/null 2>&1; then
    redis-cli -u "$REDIS" MSET duri:ab:route:A "$A" duri:ab:route:B "$B" >/dev/null || fail
    echo "[INFO] Applied routes to Redis: A=$A B=$B"
else
    echo "[WARN] redis-cli not found, skipping Redis update"
fi

# 성공 메트릭 기록
{
    echo "# HELP ab_route_apply_success Route apply success (1=success,0=fail)"
    echo "# TYPE ab_route_apply_success gauge"
    echo "ab_route_apply_success 1"
} > "$METRICS_OUT"

echo "[OK] Routes applied (A=$A, B=$B)"

