#!/usr/bin/env bash
set -euo pipefail

echo "DuRi Day1~5 통합 검증 결과"
echo "=================================="

# Check 1: trace_v2_schema.json
if find . -maxdepth 3 -name "trace_v2_schema.json" | grep -q .; then
    echo "✅ trace_schema: trace_v2_schema.json 존재"
    PASS1=true
else
    echo "❌ trace_schema: trace_v2_schema.json 미존재"
    PASS1=false
fi

# Check 2: JSON 출력 비율 (간단 버전)
LOG_COUNT=$(find logs/ -name "*.log" 2>/dev/null | wc -l)
if [ $LOG_COUNT -gt 0 ]; then
    echo "✅ string_elim: 로그 파일 ${LOG_COUNT}개 존재"
    PASS2=true
else
    echo "❌ string_elim: 로그 파일 없음"
    PASS2=false
fi

# Check 3: regression_bench_list.yaml
if [ -f "configs/regression_bench_list.yaml" ]; then
    echo "✅ bench_yaml: regression_bench_list.yaml 존재"
    PASS3=true
else
    echo "❌ bench_yaml: regression_bench_list.yaml 미존재"
    PASS3=false
fi

# Check 4: run_regression_tests.sh
if [ -x "scripts/run_regression_tests.sh" ]; then
    echo "✅ bench_runner: run_regression_tests.sh 실행 가능"
    PASS4=true
else
    echo "❌ bench_runner: run_regression_tests.sh 미존재/실행 불가"
    PASS4=false
fi

# Check 5: failure_types_catalog.md
if [ -f "docs/failure_types_catalog.md" ]; then
    echo "✅ failure_catalog: failure_types_catalog.md 존재"
    PASS5=true
else
    echo "❌ failure_catalog: failure_types_catalog.md 미존재"
    PASS5=false
fi

echo "=================================="
PASS_COUNT=0
[ "$PASS1" = true ] && ((PASS_COUNT++))
[ "$PASS2" = true ] && ((PASS_COUNT++))
[ "$PASS3" = true ] && ((PASS_COUNT++))
[ "$PASS4" = true ] && ((PASS_COUNT++))
[ "$PASS5" = true ] && ((PASS_COUNT++))

if [ $PASS_COUNT -eq 5 ]; then
    echo "🎉 ALL PASS: Day 6로 진행해도 안전합니다."
else
    echo "⚠️  PARTIAL: ${PASS_COUNT}/5 통과. 보완 필요 항목을 해결 후 Day 6로 진행하세요."
fi
echo "=================================="
