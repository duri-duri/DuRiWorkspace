#!/usr/bin/env bash
# Metrics Window Rollup - 시간 윈도우 기반 메트릭 계산
# Purpose: 누적 카운터 대신 시간 윈도우 기반 비율 계산
# Usage: metrics_window_rollup.sh [--window <1h|6h|24h|last_N>]

set -euo pipefail

WINDOW="${1:-last_2000}"
TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
CANON_FILE="var/audit/decisions.canon.ndjson"

mkdir -p "$TEXTFILE_DIR"

# 윈도우 크기 결정
case "$WINDOW" in
  last_*)
    N=$(echo "$WINDOW" | sed 's/last_//')
    if [[ -f "$CANON_FILE" ]]; then
      TOTAL=$(tail -n "$N" "$CANON_FILE" | wc -l)
      # 원본에서 해당 라인 수만큼의 불량 라인 추정
      SRC_FILE="var/audit/decisions.ndjson"
      if [[ -f "$SRC_FILE" ]]; then
        SRC_TOTAL=$(wc -l < "$SRC_FILE")
        CANON_TOTAL=$(wc -l < "$CANON_FILE")
        BAD=$((SRC_TOTAL - CANON_TOTAL))
        # 윈도우 비율 추정
        WINDOW_BAD=$((BAD * TOTAL / SRC_TOTAL))
      else
        WINDOW_BAD=0
      fi
    else
      TOTAL=0
      WINDOW_BAD=0
    fi
    ;;
  *)
    TOTAL=0
    WINDOW_BAD=0
    ;;
esac

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

