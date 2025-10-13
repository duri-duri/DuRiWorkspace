#!/bin/bash
set -euo pipefail

echo "🧪 Summary/Histogram 제약 테스트"
echo "=== *_sum/*_count 라벨 제약 검증 ==="

# 직접 prom 파일 검증
TEMP_PROM="/tmp/summary_histogram_test.prom"
cp tests/samples/summary_histogram_constraints.prom "$TEMP_PROM"

# validate_prom.sh의 검증 로직 실행
if bash scripts/metrics/validate_prom.sh "$TEMP_PROM" >/dev/null; then
  echo "✅ Summary/Histogram 제약 테스트 PASS"
else
  echo "❌ Summary/Histogram 제약 테스트 FAIL"
  exit 1
fi

echo "✅ Summary/Histogram 제약 테스트 완료"
