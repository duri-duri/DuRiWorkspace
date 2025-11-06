#!/usr/bin/env bash
# NDJSON Canonicalizer - 손상 라인/중복/개행 문제를 정규화 단계에서 제거
# Purpose: 입력 NDJSON을 정규화하여 다운스트림 파이프가 항상 정상 NDJSON만 받도록 보장
# Usage: ndjson_canonicalize.sh <input> <output>

set -euo pipefail

SRC="${1:-var/audit/decisions.ndjson}"
OUT="${2:-var/audit/decisions.canon.ndjson}"
PROM_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"

# 소스 파일 존재 확인
if [[ ! -f "$SRC" ]] || [[ ! -s "$SRC" ]]; then
  echo "[WARN] Source file not found or empty: $SRC" >&2
  exit 0
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

# 허용 결정값 집합
ALLOW='["GO","NO-GO","REVIEW","HOLD","HEARTBEAT","APPROVED","CONTINUE"]'

# 총 라인 수 카운트
TOTAL_LINES=$(wc -l < "$SRC" 2>/dev/null || echo 0)

# nl: 라인 번호 추가 (타이브레이커용)
# jq -Rn: 입력을 라인별로 읽고 fromjson?로 파싱 실패 시 자동 드랍
# 정렬: (ts, seq) 순으로 안정 정렬
# 중복 제거: 같은 ts에서 마지막 1건만 유지 + idempotency (ts, seq) 조합으로 중복 제거
jq -Rn '
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
' < "$SRC" > "$TMP" 2>/dev/null || {
  echo "[WARN] Canonicalization failed, using empty" >&2
  touch "$TMP"
}

# 원자적 쓰기
mkdir -p "$(dirname "$OUT")"
mv -f "$TMP" "$OUT"
chmod 0644 "$OUT"

VALID_LINES=$(wc -l < "$OUT" 2>/dev/null || echo 0)
BAD_LINES=$(( TOTAL_LINES > VALID_LINES ? TOTAL_LINES - VALID_LINES : 0 ))

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

echo "[OK] canonicalized -> $OUT ($VALID_LINES lines, $BAD_LINES bad dropped)" >&2

