#!/usr/bin/env bash
# Red 발생 시 즉각 트리아지 (10분 컷)
set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
PROM_CONTAINER="${PROM_CONTAINER:-prometheus}"

echo "[$(date +%Y-%m-%d\ %H:%M:%S)] Red 트리아지 시작 (10분 컷)"

# 1) Exporter 산출물 존재/라벨 확인
echo "[1] Exporter 산출물 확인"
mkdir -p "$TEXTFILE_DIR"

if [ -f "scripts/ops/p_sigma_export.py" ]; then
    echo "  → p_sigma_export.py 실행"
    TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_sigma_export.py
    if [ -f "$TEXTFILE_DIR/p_sigma.prom" ]; then
        echo "  ✓ p_sigma.prom 생성됨"
        local label_count=$(grep -c 'window="2h"\|window="24h"' "$TEXTFILE_DIR/p_sigma.prom" 2>/dev/null || echo "0")
        if [ "$label_count" -ge 2 ]; then
            echo "  ✓ 라벨 쌍 존재 (2h/24h)"
        else
            echo "  ✗ 라벨 쌍 부족: $label_count"
        fi
        head -20 "$TEXTFILE_DIR/p_sigma.prom"
    else
        echo "  ✗ p_sigma.prom 생성 실패"
    fi
else
    echo "  ✗ scripts/ops/p_sigma_export.py 없음"
fi

if [ -f "scripts/ops/p_uniform_ks.py" ]; then
    echo "  → p_uniform_ks.py 실행"
    TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_uniform_ks.py
    if [ -f "$TEXTFILE_DIR/p_uniform_ks.prom" ]; then
        echo "  ✓ p_uniform_ks.prom 생성됨"
        head -10 "$TEXTFILE_DIR/p_uniform_ks.prom"
    else
        echo "  ✗ p_uniform_ks.prom 생성 실패"
    fi
else
    echo "  ✗ scripts/ops/p_uniform_ks.py 없음"
fi

# 2) Prometheus 규칙 문법/적재 확인
echo ""
echo "[2] Prometheus 규칙 확인"
if docker run --rm -v "$(pwd)/prometheus/rules:/rules:ro" \
    --entrypoint /bin/sh prom/prometheus:latest \
    -c "promtool check rules /rules/duri-ab-quality.rules.yml" 2>&1 | grep -q "SUCCESS"; then
    echo "  ✓ 규칙 문법 OK"
else
    echo "  ✗ 규칙 문법 오류"
    docker run --rm -v "$(pwd)/prometheus/rules:/rules:ro" \
        --entrypoint /bin/sh prom/prometheus:latest \
        -c "promtool check rules /rules/duri-ab-quality.rules.yml" 2>&1 | tail -5
fi

# 3) 스크레이프 타깃 살아있나
echo ""
echo "[3] 스크레이프 타깃 확인"
if docker exec "$PROM_CONTAINER" sh -lc 'wget -qO- localhost:9090/api/v1/targets' 2>/dev/null | \
    jq -r '.data.activeTargets[]? | "\(.labels.job): \(.health)"' 2>/dev/null | head -5; then
    echo "  ✓ 타깃 응답 OK"
else
    echo "  ✗ 타깃 응답 실패"
fi

# 4) 워크스페이스 테스트
echo ""
echo "[4] 워크스페이스 테스트"
if make test-p-sigma 2>&1 | tail -1 | grep -q "OK\|PASS"; then
    echo "  ✓ 워크스페이스 테스트 PASS"
else
    echo "  ✗ 워크스페이스 테스트 FAIL"
    echo "  → 워크스페이스 문제 의심"
fi

# 5) 요약
echo ""
echo "[SUMMARY]"
echo "  → 경로/쓰기 이슈: make test-p-sigma FAIL면 워크스페이스 문제"
echo "  → PASS면 스크레이프/권한/퍼미션 외부 요인"
echo "[COMPLETE] $(date +%Y-%m-%d\ %H:%M:%S)"

