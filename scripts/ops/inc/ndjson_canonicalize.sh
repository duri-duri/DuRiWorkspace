#!/usr/bin/env bash
# NDJSON Canonicalizer - 손상 라인/중복/개행 문제를 정규화 단계에서 제거
# Purpose: 입력 NDJSON을 정규화하여 다운스트림 파이프가 항상 정상 NDJSON만 받도록 보장
# Usage: ndjson_canonicalize.sh <input> <output>
# 
# 불변식: output_lines <= input_lines (항상 성립해야 함)

set -euo pipefail

# 입력 인자 강제 검증
IN="${1:?usage: ndjson_canonicalize.sh <in.ndjson> <out.ndjson>}"
OUT="${2:?usage: ndjson_canonicalize.sh <in.ndjson> <out.ndjson>}"

# 절대 경로로 변환 (상대 경로 처리)
if [[ ! "$IN" =~ ^/ ]]; then
  IN="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
fi
if [[ ! "$OUT" =~ ^/ ]]; then
  OUT="$(cd "$(dirname "$OUT")" 2>/dev/null && pwd || pwd)/$(basename "$OUT")"
fi

# 입력 파일 존재 확인
if [[ ! -f "$IN" ]] || [[ ! -s "$IN" ]]; then
  echo "[WARN] Source file not found or empty: $IN" >&2
  exit 0
fi

# 기존 출력 파일 삭제 (덮어쓰기 보장)
rm -f "$OUT"

# 임시 파일 생성 (원자적 교체 보장)
TMP="$(mktemp "${OUT}.XXXXXX")"
trap 'rm -f "$TMP"' EXIT

PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"

# 허용 결정값 집합
ALLOW='["GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"]'

# 입력 라인 수 카운트 (불변식 검증용)
TOTAL_LINES=$(wc -l < "$IN" 2>/dev/null || echo 0)

# 핵심: 입력 파일($IN)만 읽고, 임시 파일에 쓰기
# cat으로 명시적으로 파일 읽기 후 jq에 파이프
# jq -Rn: 입력을 라인별로 읽고 fromjson?로 파싱 실패 시 자동 드랍
# 정렬: (ts, seq) 순으로 안정 정렬
# 중복 제거: 같은 ts에서 마지막 1건만 유지 + idempotency (ts, seq) 조합으로 중복 제거
cat "$IN" | jq -Rn '
  def ok_decision: '"$ALLOW"' | index(.);
  [ inputs
    | fromjson? // empty
    | select(. and type=="object" and .ts and .decision)
    | select( (.decision|tostring) as $d | ('"$ALLOW"') | index($d) != null )
    | { ts: ((.ts|fromdateiso8601) // 0), seq: ((.seq|tonumber) // 0), decision: .decision, orig: . }
  ]
  | sort_by(.ts, .seq)
  | (group_by(.ts) | map(last))  # 같은 ts 그룹에서 마지막 1건만
  | unique_by(.ts, .seq)          # idempotency: (ts, seq) 조합으로 중복 제거
  | .[]
  | .orig
' > "$TMP" 2>/dev/null || {
  echo "[WARN] Canonicalization failed, using empty" >&2
  touch "$TMP"
}

# 원자적 쓰기 (덮어쓰기, append 금지)
mkdir -p "$(dirname "$OUT")"
mv -f "$TMP" "$OUT"
chmod 0644 "$OUT"

VALID_LINES=$(wc -l < "$OUT" 2>/dev/null || echo 0)
BAD_LINES=$(( TOTAL_LINES > VALID_LINES ? TOTAL_LINES - VALID_LINES : 0 ))

# 불변식 검증: 출력 라인 수는 입력 이하여야 함
if [[ $VALID_LINES -gt $TOTAL_LINES ]]; then
  echo "[ERROR] Invariant violation: output_lines($VALID_LINES) > input_lines($TOTAL_LINES)" >&2
  echo "[ERROR] Input file: $IN" >&2
  echo "[ERROR] Output file: $OUT" >&2
  echo "[ERROR] This indicates canonicalize read from wrong source or appended data" >&2
  exit 1
fi

# 메트릭 노출 (canon_total, canon_bad)
mkdir -p "$PROM_DIR"
METRIC_TMP="$(mktemp)"
{
  echo '# HELP l4_canon_total Total lines processed by canonicalizer'
  echo '# TYPE l4_canon_total counter'
  echo "l4_canon_total{} $TOTAL_LINES"
  echo '# HELP l4_canon_bad Bad lines dropped by canonicalizer'
  echo '# TYPE l4_canon_bad counter'
  echo "l4_canon_bad{} $BAD_LINES"
} > "$METRIC_TMP"
mv -f "$METRIC_TMP" "$PROM_DIR/l4_canon_metrics.prom"
chmod 0644 "$PROM_DIR/l4_canon_metrics.prom"

echo "[OK] canonicalized -> $OUT ($VALID_LINES lines, $BAD_LINES bad dropped, input=$TOTAL_LINES)" >&2
