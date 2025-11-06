#!/usr/bin/env bash
# L4 Backfill Pipeline - 원자적 파이프라인 오케스트레이터
# Purpose: Prefilter → Autofix → Canonicalize → Window Metrics를 원자적으로 실행
# Usage: l4_backfill.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"

WORK="${WORK:-$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)}"
cd "$WORK"

# 경로 고정 (절대 경로 사용)
WROOT="var/audit"
RAW="${WROOT}/decisions.ndjson"
PREF="${WROOT}/decisions.pref.ndjson"
FIXD="${WROOT}/decisions.fixed.ndjson"
CANO="${WROOT}/decisions.canon.ndjson"
META="${CANO}.meta.json"

# 입력 해시 (변경 감지용)
if [[ -f "$RAW" ]]; then
  INPUT_HASH=$(sha256sum "$RAW" | awk '{print $1}')
else
  INPUT_HASH=""
fi

echo "=== L4 Backfill Pipeline Start $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Input: $RAW"
echo "Input hash: ${INPUT_HASH:0:16}..."

# 1) Prefilter
if [[ -z "$DRY_RUN" ]]; then
  echo "[1] Running prefilter..."
  bash scripts/ops/inc/ndjson_prefilter.sh "$RAW" "$PREF" || {
    echo "[ERROR] Prefilter failed" >&2
    exit 1
  }
else
  echo "[1] Prefilter (dry-run)"
fi

# 2) Autofix
if [[ -z "$DRY_RUN" ]]; then
  echo "[2] Running autofix..."
  bash scripts/ops/inc/ndjson_autofix.sh "$PREF" "$FIXD" || {
    echo "[ERROR] Autofix failed" >&2
    exit 1
  }
else
  echo "[2] Autofix (dry-run)"
fi

# 3) Canonicalize (입력 강제)
if [[ -z "$DRY_RUN" ]]; then
  echo "[3] Running canonicalize..."
  bash scripts/ops/inc/ndjson_canonicalize.sh "$FIXD" "$CANO" || {
    echo "[ERROR] Canonicalize failed" >&2
    exit 1
  }
else
  echo "[3] Canonicalize (dry-run)"
fi

# 4) 불변식 검증
if [[ -z "$DRY_RUN" ]]; then
  echo "[4] Verifying invariants..."
  N_SRC=$(wc -l < "$RAW" 2>/dev/null || echo 0)
  N_PREF=$(wc -l < "$PREF" 2>/dev/null || echo 0)
  N_FIXD=$(wc -l < "$FIXD" 2>/dev/null || echo 0)
  N_CANO=$(wc -l < "$CANO" 2>/dev/null || echo 0)
  
  if ! [[ $N_CANO -le $N_FIXD && $N_FIXD -le $N_PREF && $N_PREF -le $N_SRC ]]; then
    echo "[ERROR] Invariant broken: src=$N_SRC pref=$N_PREF fix=$N_FIXD canon=$N_CANO" >&2
    echo "[ERROR] Expected: src >= pref >= fix >= canon" >&2
    exit 1
  else
    echo "[OK] Invariant OK: src=$N_SRC >= pref=$N_PREF >= fix=$N_FIXD >= canon=$N_CANO"
  fi
  
  # 메타데이터 기록
  cat > "$META" <<EOF
{
  "input_hash": "$INPUT_HASH",
  "pref_lines": $N_PREF,
  "fix_lines": $N_FIXD,
  "canon_lines": $N_CANO,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
fi

# 5) Window Metrics Rollup (방금 생성된 canon 파일 사용)
if [[ -z "$DRY_RUN" ]]; then
  echo "[5] Computing window metrics..."
  bash scripts/ops/inc/metrics_window_rollup.sh --src "$CANO" --window last_2000 || {
    echo "[WARN] Window metrics rollup failed" >&2
  }
else
  echo "[5] Window metrics (dry-run)"
fi

# 6) Backfill 성공 타임스탬프 기록
if [[ -z "$DRY_RUN" ]]; then
  TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
  mkdir -p "$TEXTFILE_DIR"
  
  BACKFILL_TMP="$(mktemp)"
  {
    echo '# HELP l4_backfill_last_ok_ts_seconds Unix timestamp of last successful backfill (UTC)'
    echo '# TYPE l4_backfill_last_ok_ts_seconds gauge'
    echo "l4_backfill_last_ok_ts_seconds{} $(date -u +%s)"
  } > "$BACKFILL_TMP"
  mv -f "$BACKFILL_TMP" "${TEXTFILE_DIR}/l4_backfill_last_ok.prom"
  chmod 0644 "${TEXTFILE_DIR}/l4_backfill_last_ok.prom"
fi

echo "[OK] L4 Backfill Pipeline Complete"
echo "=== L4 Backfill Pipeline End ==="

