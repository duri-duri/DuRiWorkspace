#!/usr/bin/env bash
# shellcheck 훅 - 스크립트 품질 검사
set -euo pipefail

echo "🔍 shellcheck 품질 검사 시작..."

# 주요 스크립트들 검사
scripts_to_check=(
    "scripts/rag_search_tuned.sh"
    "scripts/rag_search_enhanced.sh"
    "scripts/rag_search_fusion.sh"
    "scripts/rag_search_fusion_v1.sh"
    "scripts/rag_eval_day62.sh"
    "scripts/rag_gate_day62.sh"
    "scripts/pr_gate_day63.sh"
    "tests/smoke_ensemble.sh"
    "tests/smoke_cwd_safe.sh"
    "tests/smoke_locale_safe.sh"
    "tests/smoke_deterministic.sh"
    "tests/smoke_extract_ids_negative.sh"
)

errors=0
for script in "${scripts_to_check[@]}"; do
    if [[ -f "$script" ]]; then
        echo "  📄 $script"
        if command -v shellcheck >/dev/null 2>&1; then
            if shellcheck -x "$script"; then
                echo "    ✅ PASS"
            else
                echo "    ❌ FAIL"
                ((errors++))
            fi
        else
            echo "    ⚠️  shellcheck 미설치 - 건너뜀"
        fi
    else
        echo "  ⚠️  파일 없음: $script"
    fi
done

if [[ $errors -eq 0 ]]; then
    echo "🎉 모든 스크립트 shellcheck 통과!"
    exit 0
else
    echo "💢 $errors 개 스크립트에서 shellcheck 오류 발견"
    exit 1
fi
