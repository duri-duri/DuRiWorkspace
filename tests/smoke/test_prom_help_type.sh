#!/usr/bin/env bash
# 미니 유닛테스트: HELP/TYPE 검증 로직
set -euo pipefail

echo "🧪 HELP/TYPE 검증 로직 테스트"

# 테스트용 임시 파일
tmp="$(mktemp)"

# 정상 샘플 → PASS
cat > "$tmp" <<'EOF'
# HELP test_metric Test metric
# TYPE test_metric gauge
test_metric{label="value"} 1.0
test_metric 2.0
EOF

if bash scripts/metrics/validate_prom.sh "$tmp" >/dev/null 2>&1; then
  echo "✅ 정상 샘플 PASS"
else
  echo "❌ 정상 샘플 FAIL"
  exit 1
fi

# 중복 HELP 주입 → FAIL (직접 awk로 검증)
cat > "$tmp" <<'EOF'
# HELP test_metric Test metric
# TYPE test_metric gauge
# HELP test_metric Duplicate HELP
test_metric{label="value"} 1.0
EOF

if awk '
  BEGIN{num="(?:[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)(?:[eE][+-]?[0-9]+)?|[+-]?(?:Inf|NaN))"}
  /^# HELP /{help[$3]++}
  /^# TYPE /{type[$3]++}
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*\\{[^}]*\\}[[:space:]]+" num "$" {split($0,a,"{"); seen[a[1]]=1; next}
  $0 ~ "^[A-Za-z_:][A-Za-z0-9_:]*[[:space:]]+" num "$" {split($0,a," "); seen[a[1]]=1; next}
  END{bad=0; for(m in help) if(help[m]>1){printf("❌ duplicate HELP for %s (%d)\n",m,help[m])>"/dev/stderr"; bad=1} for(m in type) if(type[m]>1){printf("❌ duplicate TYPE for %s (%d)\n",m,type[m])>"/dev/stderr"; bad=1} for(m in seen){if(!(m in help)){printf("❌ missing HELP for %s\n",m)>"/dev/stderr"; bad=1} if(!(m in type)){printf("❌ missing TYPE for %s\n",m)>"/dev/stderr"; bad=1}} exit bad}
' "$tmp" >/dev/null 2>&1; then
  echo "❌ 중복 HELP FAIL (예상: PASS)"
  exit 1
else
  echo "✅ 중복 HELP FAIL (예상대로)"
fi

# 라벨 없는 샘플 포함 → PASS
cat > "$tmp" <<'EOF'
# HELP test_metric Test metric
# TYPE test_metric gauge
test_metric{label="value"} 1.0
test_metric 2.0
test_metric_without_labels 3.0
EOF

if bash scripts/metrics/validate_prom.sh "$tmp" >/dev/null 2>&1; then
  echo "✅ 라벨 없는 샘플 PASS"
else
  echo "❌ 라벨 없는 샘플 FAIL"
  exit 1
fi

# 과학표기법 포함 → PASS
cat > "$tmp" <<'EOF'
# HELP test_metric Test metric
# TYPE test_metric gauge
test_metric{label="value"} 1.23e-4
test_metric 2.5E+6
EOF

if bash scripts/metrics/validate_prom.sh "$tmp" >/dev/null 2>&1; then
  echo "✅ 과학표기법 PASS"
else
  echo "❌ 과학표기법 FAIL"
  exit 1
fi

rm -f "$tmp"
echo "✅ 모든 HELP/TYPE 테스트 통과"
