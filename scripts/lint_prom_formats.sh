#!/usr/bin/env bash
# lint_prom_formats.sh: Prometheus 형식 검증
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Prometheus 형식 검증 ==="
echo ""

FAILED=0

# 최근 2시간 창 ab_eval.prom 파일 검증
while IFS= read -r f; do
    if [ ! -f "$f" ]; then
        continue
    fi
    
    # 라벨 없는 p라인 검사
    if grep -q '^duri_ab_p_value ' "$f" 2>/dev/null; then
        echo "[FAIL] $f: 라벨 없는 p라인 발견"
        FAILED=$((FAILED + 1))
    fi
    
    # n=0 샘플 검사 (p라인은 없어야 함)
    if grep -q '^duri_ab_p_value{' "$f" 2>/dev/null && grep -q 'n="0"' "$f" 2>/dev/null; then
        echo "[FAIL] $f: n=0인데 p라인 존재"
        FAILED=$((FAILED + 1))
    fi
    
    # build_unixtime 라벨 일관성 검사 (I3)
    if grep -q '^duri_ab_p_value{' "$f" 2>/dev/null && grep -q '^duri_ab_samples{' "$f" 2>/dev/null; then
        P_BUILD=$(grep '^duri_ab_p_value{' "$f" | sed -n 's/.*build_unixtime="\([^"]*\)".*/\1/p' | head -1)
        S_BUILD=$(grep '^duri_ab_samples{' "$f" | sed -n 's/.*build_unixtime="\([^"]*\)".*/\1/p' | head -1)
        if [ -n "$P_BUILD" ] && [ -n "$S_BUILD" ] && [ "$P_BUILD" != "$S_BUILD" ]; then
            echo "[FAIL] $f: build_unixtime 불일치 (p=$P_BUILD, samples=$S_BUILD)"
            FAILED=$((FAILED + 1))
        fi
    fi
    
done < <(find var/evolution -name "ab_eval.prom" -newermt "-2 hours" 2>/dev/null || true)

if [ "$FAILED" -eq 0 ]; then
    echo "[OK] Prometheus 형식 검증 통과"
    exit 0
else
    echo "[FAIL] $FAILED 건의 형식 오류 발견"
    exit 1
fi

