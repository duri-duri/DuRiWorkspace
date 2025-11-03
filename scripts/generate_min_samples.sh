#!/usr/bin/env bash
# (S1) 최소 샘플 생성기 - n≥1 EV 2개 이상 확보
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 최소 샘플 생성기 ==="
echo ""

# 1) 서로 다른 입력 2건(variant 유도): prompt A/B
REQ_A='{"task":"ab_eval_probe","payload":{"prompt":"rehab: hip hinge cue v1","tag":"probeA","variant":"A"}}'
REQ_B='{"task":"ab_eval_probe","payload":{"prompt":"rehab: hip hinge cue v2","tag":"probeB","variant":"B"}}'

# 2) duri-control 경유 내부 HTTP 엔드포인트
# 엔드포인트 확인: /api/probe 또는 /api/emotion 또는 프로젝트 표준에 맞게 선택
CONTROL_URL="${DURI_CONTROL_URL:-http://localhost:8083}"
PROBE_ENDPOINT="${PROBE_ENDPOINT:-/api/probe}"

echo "[1] Probe A 전송..."
curl -sS -X POST "${CONTROL_URL}${PROBE_ENDPOINT}" \
    -H 'Content-Type: application/json' \
    -d "$REQ_A" 2>&1 | head -3 || echo "[WARN] Probe A 전송 실패 (엔드포인트 확인 필요)"

sleep 2

echo "[2] Probe B 전송..."
curl -sS -X POST "${CONTROL_URL}${PROBE_ENDPOINT}" \
    -H 'Content-Type: application/json' \
    -d "$REQ_B" 2>&1 | head -3 || echo "[WARN] Probe B 전송 실패 (엔드포인트 확인 필요)"

# 3) Shadow가 EV를 생성/집계할 시간(대기)
echo ""
echo "[3] Shadow EV 생성 대기 (10초)..."
sleep 10

# 4) 최신 2h EV 재집계 & 스모크
echo ""
echo "[4] 재집계..."
bash scripts/ab_pvalue_stats.sh "2 hours" 2>&1 | tail -10 || true

echo ""
echo "[5] 최종 판정..."
bash scripts/final_smoke_3metrics.sh 2>&1 | tail -15 || true

echo ""
echo "[OK] 최소 샘플 생성 완료"

