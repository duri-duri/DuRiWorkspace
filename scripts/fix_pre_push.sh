#!/usr/bin/env bash
set -euo pipefail

# pre-push 훅에서 잘못된 target 합성 수정
HOOK=".git/hooks/pre-push"

if [ ! -f "$HOOK" ]; then
  echo "❌ pre-push hook not found at $HOOK"
  exit 1
fi

# 백업
cp "$HOOK" "$HOOK.bak"

# upstream 파싱 블록을 안전 버전으로 치환
python3 - <<'PY'
import re, pathlib
p = pathlib.Path(".git/hooks/pre-push"); s = p.read_text()
s = re.sub(r'(?s)upstream=.*?\n.*?target=.*?\n',
r'''upstream="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
if [[ -n "$upstream" && "$upstream" == */* ]]; then
  remote="${upstream%%/*}"
  branch="${upstream#*/}"
else
  remote="origin"
  branch="$(git rev-parse --abbrev-ref HEAD)"
fi
target="$remote/$branch"
''', s)
p.write_text(s)
PY

chmod +x "$HOOK"
echo "✅ pre-push hook fixed (backup: $HOOK.bak)"
