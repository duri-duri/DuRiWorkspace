#!/usr/bin/env bash
# tools/apply_trace_config.sh
# selected.json -> runtime 반영 (+옵션으로 env export)
set -euo pipefail

# --- 위치 계산 (repo root) ---
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$( cd "$SCRIPT_DIR/.." && pwd -P )"

SELECTED="configs/trace_v2_selected.json"
RUNTIME_DIR="config"
RUNTIME_JSON="$RUNTIME_DIR/trace_v2_runtime.json"
SERVICE_JSON="config/core_app.json"   # 있으면 패치, 없으면 건너뜀

# --- 유틸 ---
fail(){ echo "[ERR]" "$*" >&2; exit 1; }
info(){ echo "[INFO]" "$*"; }

command -v jq >/dev/null || fail "jq가 필요합니다 (apt-get install jq 등)."

[[ -f "$SELECTED" ]] || fail "선택 파일이 없습니다: $SELECTED"

sampling="$(jq -r '.sampling_rate' "$SELECTED")"
ser="$(jq -r '.serialization' "$SELECTED")"
comp="$(jq -r '.compression' "$SELECTED")"

# 값 검증
[[ "$sampling" =~ ^[0-9]+(\.[0-9]+)?$ ]] || fail "sampling_rate 숫자 아님: $sampling"
awk "BEGIN{ exit !($sampling>=0 && $sampling<=1) }" || fail "sampling_rate는 [0,1]이어야 합니다: $sampling"

case "$ser" in json|msgpack|protobuf) ;; *) fail "serialization은 json|msgpack|protobuf 중 하나여야 합니다: $ser";; esac
case "$comp" in none|gzip|zstd) ;; *) fail "compression은 none|gzip|zstd 중 하나여야 합니다: $comp";; esac

# 반영 파일 생성
mkdir -p "$RUNTIME_DIR"
ts="$(date -Iseconds)"
cat > "$RUNTIME_JSON.tmp" <<JSON
{
  "schema": "trace_v2.runtime.v1",
  "updated_at": "$ts",
  "source": "$SELECTED",
  "trace": {
    "sampling_rate": $sampling,
    "serialization": "$ser",
    "compression": "$comp"
  }
}
JSON
mv "$RUNTIME_JSON.tmp" "$RUNTIME_JSON"
info "런타임 설정 생성/갱신: $RUNTIME_JSON"

# core_app.json이 있으면 패치
if [[ -f "$SERVICE_JSON" ]]; then
  info "서비스 설정 패치: $SERVICE_JSON (trace.* 갱신)"
  tmp="$(mktemp)"
  jq --arg s "$ser" --arg c "$comp" --argjson r "$sampling" '
    .trace = (.trace // {}) |
    .trace.sampling_rate = $r |
    .trace.serialization = $s |
    .trace.compression = $c
  ' "$SERVICE_JSON" > "$tmp"
  mv "$tmp" "$SERVICE_JSON"
else
  info "서비스 설정($SERVICE_JSON) 없음: 패치 건너뜀"
fi

# 옵션: --export-env 주면 export 문 출력
if [[ "${1:-}" == "--export-env" ]]; then
  echo "export TRACE_SAMPLING=$sampling"
  echo "export TRACE_SER=$ser"
  echo "export TRACE_COMP=$comp"
fi

info "적용 완료"

