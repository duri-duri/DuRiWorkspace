#!/bin/bash
set -euo pipefail

echo "🧪 숫자 더티케이스 테스트"
echo "=== 다양한 숫자 표기 검증 ==="

nums=(
  "0" "+0" "-0" "1." ".5" "1.0" "1e9" "1E-9" "+Inf" "-Inf" "NaN"
)

{
  echo "# HELP n num"
  echo "# TYPE n gauge"
  for v in "${nums[@]}"; do
    echo "n $v"
  done
} > /tmp/numbers.prom

if bash scripts/metrics/validate_prom.sh /tmp/numbers.prom >/dev/null; then
  echo "✅ number dirty-cases PASS"
else
  echo "❌ number dirty-cases FAIL"
  exit 1
fi

echo "✅ 숫자 더티케이스 테스트 PASS"


