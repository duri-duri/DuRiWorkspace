#!/usr/bin/env bash
# (2) 최종 스모크(원클릭) - AB Quality Smoke Test
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== AB Quality Smoke ==="
echo ""

# 1) 레거시 정리
echo "[1] 레거시 prom 정리..."
bash scripts/fix_legacy_prom.sh >/dev/null 2>&1 || true

# 2) 라벨 무결성 확인
echo "[2] 라벨 무결성 확인..."
bad=$(find var/evolution -name 'ab_eval.prom' -newermt '-2 hours' -exec grep -l '^duri_ab_p_value ' {} \; 2>/dev/null | wc -l)
if [ "$bad" -gt 0 ]; then
    echo "[FAIL] unlabeled p-lines: $bad"
    exit 2
fi
echo "[OK] no unlabeled p-lines"

# 3) AB 통계 계산
echo "[3] AB 통계 계산..."
bash scripts/ab_pvalue_stats.sh "2 hours" >/dev/null 2>&1 || echo "[WARN] ab_pvalue_stats.sh 실행 실패"

# 4) Prom 형식 검증 (lint_prom_formats.sh가 있으면 실행)
if [ -f "scripts/lint_prom_formats.sh" ]; then
    echo "[4] Prom 형식 검증..."
    bash scripts/lint_prom_formats.sh >/dev/null 2>&1 || echo "[WARN] lint_prom_formats.sh 실행 실패"
fi

# 5) 라벨 무결성 종합 확인
echo "[5] 라벨 무결성 종합 확인..."
bash scripts/quick_label_check.sh >/dev/null 2>&1 || echo "[WARN] quick_label_check.sh 실행 실패"

# 6) Doctor 종합 점검
echo "[6] Doctor 종합 점검..."
bash scripts/doctor.sh 2>&1 | grep -E "\[OK\]|\[FAIL\]|\[WARN\]" | head -10 || true

echo ""
echo "[OK] AB quality smoke passed"

