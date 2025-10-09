#!/usr/bin/env bash
set -euo pipefail

echo "🧪 추출기 네거티브 스모크 테스트"
if echo -e "📄 edu.xray.expectation.v1.001: X-ray 기대치\n카테고리: education\n{\"id\":\"ex.lbp.core.v1.001\"}" \
| awk -v RE='([a-z][a-z0-9_-]*([.][a-z0-9_-]+)+[.]v[0-9]+([.][0-9]+)?)' '
  { l=$0; gsub(/^[ \t]+|[ \t]+$/, "", l)
    if (match(l, /"id"[[:space:]]*:[[:space:]]*"([^"]+)"/, m) && m[1] ~ RE) { print m[1]; next }
    if (match(l, RE, m)) { print m[1]; next } }' \
| diff -u <(printf "ex.lbp.core.v1.001\nedu.xray.expectation.v1.001\n" | LC_ALL=C sort) - >/dev/null; then
  echo "✅ extract_ids: ID만 통과"
else
  echo "❌ extract_ids: 비-ID 누출"
  exit 1
fi
