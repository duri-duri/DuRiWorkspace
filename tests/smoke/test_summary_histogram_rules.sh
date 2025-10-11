#!/bin/bash
set -euo pipefail

echo "🧪 Summary/Histogram 규칙 테스트"
echo "=== quantile/le 라벨 규칙 검증 ==="

# 직접 prom 파일 검증
TEMP_PROM="/tmp/summary_histogram_rules_test.prom"
cp tests/samples/summary_histogram_rules.prom "$TEMP_PROM"

# validate_prom.sh의 검증 로직 실행
if bash scripts/metrics/validate_prom.sh "$TEMP_PROM" >/dev/null; then
  echo "✅ Summary/Histogram 규칙 테스트 PASS"
else
  echo "❌ Summary/Histogram 규칙 테스트 FAIL"
  exit 1
fi

echo "✅ Summary/Histogram 규칙 테스트 완료"
