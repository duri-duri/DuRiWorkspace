#!/usr/bin/env bash
set -euo pipefail
echo "🧪 CWD 독립성 스모크"
REPO="$(pwd)"

cd /tmp
out=/tmp/cwd.out; err=/tmp/cwd.err
: > "$out"; : > "$err"

"$REPO/scripts/rag_search_fusion_v1.sh" "요통" ---rank --k 3 --format ids \
  >"$out" 2>"$err"
RC=$?

if [[ $RC -ne 0 ]]; then
  echo "❌ /tmp 실행 실패 (rc=$RC)"
  echo "—— stderr ——"; sed -n '1,120p' "$err"
  exit 1
fi

lines=$(wc -l < "$out" | tr -d ' ')
# ID 형식 검증까지 동시 체크
re='^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)+\.v[0-9]+(\.[0-9]+)?$'
ok=$(awk -v RS='\n' '
  /^[a-z][a-z0-9_-]*(\.[a-z0-9_-]+)+\.v[0-9]+(\.[0-9]+)?$/ {c++}
  END{print c+0}
' "$out")

if [[ "$lines" -eq 3 && "$ok" -eq 3 ]]; then
  echo "✅ /tmp에서도 3줄 ID-only"
else
  echo "❌ /tmp 실패: $lines 줄 / 유효 ${ok}/3 (예상: 3줄)"
  echo "—— stdout ——"; sed -n '1,120p' "$out"
  echo "—— stderr ——"; sed -n '1,120p' "$err"
  exit 1
fi
