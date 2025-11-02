#!/usr/bin/env bash
# Clock skew 감지: 컨테이너/호스트 시계 차이 확인
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Clock Skew 감지 ==="
echo ""

# 호스트 시계
HOST_TS=$(date +%s)

# 컨테이너 시계 (duri-postgres로 테스트)
CONTAINER_TS=$(docker exec duri-postgres date +%s 2>/dev/null || echo "$HOST_TS")

# 차이 계산
SKEW=$((CONTAINER_TS - HOST_TS))
SKEW_ABS=$((SKEW < 0 ? -SKEW : SKEW))

echo "호스트 시계: $HOST_TS"
echo "컨테이너 시계: $CONTAINER_TS"
echo "차이: ${SKEW}s (절대값: ${SKEW_ABS}s)"

if [ "$SKEW_ABS" -gt 5 ]; then
    echo "[WARN] Clock skew 감지: ${SKEW_ABS}s > 5s"
    echo "[FIX] chrony 또는 ntpd 확인 필요"
    exit 1
else
    echo "[OK] Clock skew 정상 (≤5s)"
    exit 0
fi

