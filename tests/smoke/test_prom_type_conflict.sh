#!/bin/bash
set -euo pipefail

echo "🧪 TYPE 상충 테스트"
echo "=== TYPE conflict 검증 ==="

# 직접 prom 파일 검증 (export_prom.sh 우회)
TEMP_PROM="/tmp/type_conflict_test.prom"
cp tests/samples/type_conflict.prom "$TEMP_PROM"

# validate_prom.sh의 검증 로직만 실행
if bash -c '
set -euo pipefail
OUT="'"$TEMP_PROM"'"

# TYPE 상충 검증 - 동일 메트릭명에 서로 다른 TYPE 선언 시 FAIL
echo "3.5. TYPE 상충 검증..."
awk "
  # 모든 레코드 공통 전처리: BOM/CR 제거
  { sub(/^\xEF\xBB\xBF/,\"\",\$0); sub(/\r$/,\"\",\$0) }

  /^# TYPE /{
    metric=\$3
    type_value=\$4
    if (metric in type_declared) {
      if (type_declared[metric] != type_value) {
        printf(\"❌ TYPE conflict for %s: %s vs %s\n\", metric, type_declared[metric], type_value) > \"/dev/stderr\"
        bad=1
      }
    } else {
      type_declared[metric]=type_value
    }
  }

  END{ exit bad }
" "$OUT"
'; then
  echo "❌ TYPE conflict should fail"
  exit 1
else
  echo "✅ TYPE conflict FAIL (expected)"
fi

echo "✅ TYPE 상충 테스트 PASS"
