#!/usr/bin/env bash
# 스모크 앙상블 러너 - 모든 스모크 테스트를 한 번에 실행
set -euo pipefail
trap '' PIPE

echo "🎭 스모크 앙상블 러너 시작"
echo "================================"

# 스모크 테스트 목록
smoke_tests=(
    "tests/smoke_extract_ids_negative.sh"
    "tests/smoke_locale_safe.sh"
    "tests/smoke_deterministic.sh"
    "tests/smoke_cwd_safe.sh"
)

# 각 스모크 테스트 실행
for test in "${smoke_tests[@]}"; do
    if [[ -f "$test" ]]; then
        echo "🧪 실행: $test"
        if bash "$test"; then
            echo "   ✅ PASS"
        else
            echo "   ❌ FAIL"
            exit 1
        fi
    else
        echo "⚠️  파일 없음: $test"
    fi
done

echo "🎉 모든 스모크 테스트 통과!"
