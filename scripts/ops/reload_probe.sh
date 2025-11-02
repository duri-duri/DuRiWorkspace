#!/usr/bin/env bash
set -Eeuo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-./reports/textfile}"   # 디폴트 경로 통일
mkdir -p "$TEXTFILE_DIR"

PROM_URL="${PROM_URL:-http://localhost:9090}"

MAX_RETRY="${MAX_RETRY:-6}"        # 6회
BASE_SLEEP="${BASE_SLEEP:-2}"      # 2s → 총 ~2+4+8+16+32+64 ≈ 2분
READY_URL="${READY_URL:-http://localhost:9090/-/ready}"

ready() { curl -sf "$PROM_URL/-/ready" >/dev/null 2>&1; }
healthy() { curl -sf "$PROM_URL/-/healthy" >/dev/null 2>&1; }

# 1) Prometheus reload 시도(200이면 성공)
CODE="$(curl -sS -o /dev/null -w '%{http_code}' -X POST "$PROM_URL/-/reload" 2>/dev/null || echo 000)"
OK=0; [ "$CODE" = "200" ] && OK=1

# 2) 원자적 기록: tmp→mv, 숫자는 정수로
TS="$(date +%s)"
TMP="$(mktemp "${TEXTFILE_DIR}/.duri_prometheus_reload.prom.XXXXXX")"
{
  printf 'duri_prom_reload_success %d\n' "$OK"
  printf 'duri_prom_reload_timestamp %d\n' "$TS"
} > "$TMP"
chmod 644 "$TMP"  # node_exporter가 읽을 수 있도록 권한 설정
mv -f "$TMP" "${TEXTFILE_DIR}/duri_prometheus_reload.prom"

# 즉시 노출 확인(있으면 1줄 출력, 없으면 빈출력)
curl -s http://localhost:9100/metrics 2>/dev/null | grep '^duri_prom_reload_' || true

exit $((1 - OK))

