#!/usr/bin/env bash
set -Eeuo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-./reports/textfile}"   # 디폴트 경로 통일
mkdir -p "$TEXTFILE_DIR"

out="$TEXTFILE_DIR/duri_prometheus_reload.prom"
PROM_URL="${PROM_URL:-http://localhost:9090}"

MAX_RETRY="${MAX_RETRY:-6}"        # 6회
BASE_SLEEP="${BASE_SLEEP:-2}"      # 2s → 총 ~2+4+8+16+32+64 ≈ 2분
READY_URL="${READY_URL:-http://localhost:9090/-/ready}"

ready() { curl -sf "$PROM_URL/-/ready" >/dev/null 2>&1; }
healthy() { curl -sf "$PROM_URL/-/healthy" >/dev/null 2>&1; }

emit() {
  local ok="$1"
  local tmp; tmp="$(mktemp)"
  printf 'duri_prom_reload_success %d\n' "$ok" > "$tmp"
  printf 'duri_prom_reload_timestamp %.0f\n' "$(date +%s)" >> "$tmp"
  mkdir -p "$TEXTFILE_DIR"
  mv -f "$tmp" "$out"
  
  # 즉시 노출 확인(있으면 1줄 출력, 없으면 빈출력)
  curl -s http://localhost:9100/metrics 2>/dev/null | grep '^duri_prom_reload_' || true
}

# 사전 준비 대기 (최대 30초)
for i in {1..6}; do
  if ready; then break; fi
  sleep 5
done

# 리로드 수행
if ! curl -sf --max-time 3 -X POST "$PROM_URL/-/reload" >/dev/null 2>&1; then
  emit 0
  exit 1
fi

# 리로드 후 안정화 대기: 지수 백오프(최대 60s) + 규칙 그룹 확인
delay=$BASE_SLEEP
ready_ok=0
for i in $(seq 1 $MAX_RETRY); do
  if ready; then
    # ready 200 확인 후, /api/v1/rules에서 duri-derived 그룹 존재 확인
    if curl -sf --get "$PROM_URL/api/v1/rules" 2>/dev/null | \
       jq -e '..|.name? // empty | select(.=="duri-derived")' >/dev/null 2>&1; then
      ready_ok=1
      break
    fi
  fi
  sleep "$delay"
  delay=$((delay * 2))
done

if [ "$ready_ok" -eq 1 ] && healthy; then
  emit 1
  exit 0
fi

emit 0
exit 1

