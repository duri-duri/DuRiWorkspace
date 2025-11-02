#!/usr/bin/env bash
set -Eeuo pipefail

TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"
mkdir -p "$TEXTFILE_DIR"

out="$TEXTFILE_DIR/reload_probe.prom"
PROM_URL="${PROM_URL:-http://localhost:9090}"

ready() { curl -sf "$PROM_URL/-/ready" >/dev/null 2>&1; }
healthy() { curl -sf "$PROM_URL/-/healthy" >/dev/null 2>&1; }

emit() {
  local ok="$1"
  local tmp; tmp="$(mktemp)"
  echo "duri_prom_reload_timestamp $(date +%s)" > "$tmp"
  echo "duri_prom_reload_success ${ok}" >> "$tmp"
  mkdir -p "$TEXTFILE_DIR"
  mv "$tmp" "$out"
  
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

# 리로드 후 안정화 대기: 지수 백오프(최대 60s)
delay=2
for i in {1..6}; do
  if ready && healthy; then
    emit 1
    exit 0
  fi
  sleep "$delay"
  delay=$((delay * 2))
done

emit 0
exit 1

