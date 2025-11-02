#!/usr/bin/env bash
set -euo pipefail

# 1) 루트 고정: repo 루트 기준 (절대경로 금지)
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

# 2) 샌드박스 텍스트파일 디렉토리
TEXTFILE_DIR="$(mktemp -d)"
trap 'rm -rf "$TEXTFILE_DIR"' EXIT

# 3) 합성 데이터 생성: 2h/24h 모두
mkdir -p "$TEXTFILE_DIR"
cat >"$TEXTFILE_DIR/p_values_2h.prom" <<'EOF'
# HELP p_value p-value from AB test
# TYPE p_value gauge
p_value 0.4999999765
p_value 0.5000000120
p_value 0.4999999940
p_value 0.5000000035
p_value 0.4999999980
EOF
cp "$TEXTFILE_DIR/p_values_2h.prom" "$TEXTFILE_DIR/p_values_24h.prom"

# 4) 실행
TEXTFILE_DIR="$TEXTFILE_DIR" python3 scripts/ops/p_sigma_export.py

# 5) 산출물 검증
OUT="$TEXTFILE_DIR/p_sigma.prom"
test -s "$OUT"
grep -q '^duri_p_sigma{window="2h"} [0-9.e+-]\+' "$OUT"
grep -q '^duri_p_sigma{window="24h"} [0-9.e+-]\+' "$OUT"
grep -q '^duri_p_samples{window="2h"} [1-9][0-9]*' "$OUT"
grep -q '^duri_p_samples{window="24h"} [1-9][0-9]*' "$OUT"

# 6) 원자적 쓰기(단일 파일) 및 라벨 수 보존 확인
test "$(grep -c '^duri_p_sigma{' "$OUT")" -eq 2
test "$(grep -c '^duri_p_samples{' "$OUT")" -eq 2

echo "[OK] All tests passed"
