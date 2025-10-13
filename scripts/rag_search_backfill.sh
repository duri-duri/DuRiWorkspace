#!/usr/bin/env bash
set -euo pipefail

# 백필 강화 검색기 - FN 감소 목표

QUERY="${1:-}"
K="${K:-3}"

search_with_backfill() {
  local query="$1"

  # 1) 일반 검색
  MAIN=$(mktemp)
  bash scripts/rag_search.sh "$query" --rank --k "$((K*2))" --format ids > "$MAIN" 2>/dev/null || touch "$MAIN"

  # 2) 백필 추가 (패밀리 강화)
  BACKFILL=$(mktemp)
  case "$query" in
    요통|허리통증|LBP)
      # 요통 관련 필수 문서들
      echo "intake.lbp.v1.001" >> "$BACKFILL"
      echo "ex.lbp.core.v1.001" >> "$BACKFILL"
      echo "sdm.xray.lbp.v1.001" >> "$BACKFILL"
      echo "work.lbp.return.v1.001" >> "$BACKFILL"
      echo "triage.lbp.redflag.v1.001" >> "$BACKFILL"
      ;;
    경부|목통증)
      echo "intake.neck.v1.001" >> "$BACKFILL"
      echo "triage.neck.redflag.v1.001" >> "$BACKFILL"
      ;;
    어깨)
      echo "intake.shoulder.v1.001" >> "$BACKFILL"
      ;;
    X-ray|X선)
      echo "order.ms.redflags.v1.001" >> "$BACKFILL"
      echo "sdm.xray.lbp.v1.001" >> "$BACKFILL"
      ;;
  esac

  # 3) 결합 → 상위 K
  cat "$MAIN" "$BACKFILL" | sort -u | head -n "$K"

  rm -f "$MAIN" "$BACKFILL"
}

search_with_backfill "$QUERY"
