#!/usr/bin/env bash
# Metrics Window Rollup - 시간 윈도우 기반 메트릭 계산
# Purpose: 누적 카운터 대신 시간 윈도우 기반 비율 계산
# Usage: metrics_window_rollup.sh --src <canon_file> --window <last_N|1h|6h|24h>

set -euo pipefail

# 인자 파싱
CANON_FILE=""
WINDOW="last_2000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --src)
      CANON_FILE="$2"
      shift 2
      ;;
    --window)
      WINDOW="$2"
      shift 2
      ;;
    *)
      # 레거시 지원: 첫 번째 인자가 window인 경우
      WINDOW="$1"
      shift
      ;;
  esac
done

# --src가 없으면 기본값 사용 (하지만 경고)
if [[ -z "$CANON_FILE" ]]; then
  CANON_FILE="var/audit/decisions.canon.ndjson"
  echo "[WARN] --src not specified, using default: $CANON_FILE" >&2
fi

# 절대 경로로 변환
if [[ ! "$CANON_FILE" =~ ^/ ]]; then
  CANON_FILE="$(cd "$(dirname "$CANON_FILE")" 2>/dev/null && pwd || pwd)/$(basename "$CANON_FILE")"
fi

TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"

mkdir -p "$TEXTFILE_DIR"

# 입력 파일 존재 확인
if [[ ! -f "$CANON_FILE" ]] || [[ ! -s "$CANON_FILE" ]]; then
  echo "[WARN] Canon file not found or empty: $CANON_FILE" >&2
  TOTAL=0
  WINDOW_BAD=0
else
  # 윈도우 크기 결정
  case "$WINDOW" in
    last_*)
      N=$(echo "$WINDOW" | sed 's/last_//')
      # 최근 N 라인만 사용
      TOTAL=$(tail -n "$N" "$CANON_FILE" | wc -l)
      
      # 원본 파일에서 불량 라인 수 추정
      SRC_FILE="var/audit/decisions.ndjson"
      if [[ -f "$SRC_FILE" ]]; then
        SRC_TOTAL=$(wc -l < "$SRC_FILE")
        CANON_TOTAL=$(wc -l < "$CANON_FILE")
        BAD=$((SRC_TOTAL - CANON_TOTAL))
        # 윈도우 비율 추정 (최근 N 라인 기준)
        if [[ $CANON_TOTAL -gt 0 ]]; then
          WINDOW_BAD=$((BAD * TOTAL / CANON_TOTAL))
        else
          WINDOW_BAD=0
        fi
      else
        # 원본 파일이 없으면 0으로 설정
        WINDOW_BAD=0
      fi
      ;;
    *)
      # 시간 윈도우는 Prometheus recording rule에서 처리
      TOTAL=$(wc -l < "$CANON_FILE")
      WINDOW_BAD=0
      ;;
  esac
fi

# 비율 계산
RATIO=$(python3 -c "print($WINDOW_BAD/$TOTAL if $TOTAL > 0 else 0.0)")

# 윈도우 메트릭 생성
METRIC_TMP="$(mktemp)"
{
  echo '# HELP l4_canon_bad_ratio_window Bad ratio in rolling window'
  echo '# TYPE l4_canon_bad_ratio_window gauge'
  echo "l4_canon_bad_ratio_window{window=\"${WINDOW}\"} $RATIO"
  echo '# HELP l4_canon_total_window Total lines in rolling window'
  echo '# TYPE l4_canon_total_window gauge'
  echo "l4_canon_total_window{window=\"${WINDOW}\"} $TOTAL"
  echo '# HELP l4_canon_bad_window Bad lines in rolling window'
  echo '# TYPE l4_canon_bad_window gauge'
  echo "l4_canon_bad_window{window=\"${WINDOW}\"} $WINDOW_BAD"
} > "$METRIC_TMP"

mv -f "$METRIC_TMP" "${TEXTFILE_DIR}/l4_canon_window.prom"
chmod 0644 "${TEXTFILE_DIR}/l4_canon_window.prom"

echo "[OK] window metrics -> ${TEXTFILE_DIR}/l4_canon_window.prom (ratio=$RATIO, total=$TOTAL, bad=$WINDOW_BAD)"

