#!/usr/bin/env bash
set -Eeuo pipefail

HOOK=".git/hooks/pre-push"
bak="${HOOK}.bak.$(date +%s)"
[ -f "$HOOK" ] && cp -f "$HOOK" "$bak"

cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
remote="${1:-}"; url="${2:-}"

# 1) 표준 입력에서 업데이트 라인 수집
mapfile -t updates < <(cat)
((${#updates[@]}==0)) && exit 0

# 2) 태그만 푸시되면 조용히 통과
if printf '%s\n' "${updates[@]}" | awk '{print $3}' | grep -q '^refs/tags/'; then
  exit 0
fi

# 3) 업스트림 해석(없으면 현재 브랜치의 origin/<branch>로 가정)
resolve_upstream() {
  if upstream="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)"; then
    printf '%s\n' "$upstream"         # e.g. origin/feat/...
  else
    cur="$(git rev-parse --abbrev-ref HEAD)"
    printf 'origin/%s\n' "$cur"
  fi
}
target="$(resolve_upstream)"

# target이 실제 커밋이면만 비교; 아니면 통과
git rev-parse --verify "$target^{commit}" >/dev/null 2>&1 || exit 0

# (선택) Freeze 가드가 필요한 경우에만 실행
BASE="$(git merge-base HEAD "$target" || echo HEAD~1)"
CHANGES="$(git diff --name-status "$BASE"...HEAD || true)"

[[ "${FREEZE_BYPASS:-}" == "1" ]] && exit 0
export GIT_TERMINAL_PROMPT=0

if echo "$CHANGES" | grep -F 'scripts/freeze-preflight.sh' >/dev/null; then
  timeout "30s" bash scripts/freeze-preflight.sh || { echo "[freeze-guard] failed or timeout"; exit 1; }
fi

# 기본 OK
exit 0
EOF

chmod +x "$HOOK"
echo "✅ pre-push hook fixed (backup: $bak)"
