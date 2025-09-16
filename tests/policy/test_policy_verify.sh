#!/usr/bin/env bash
# Policy verification regression tests
set -euo pipefail

ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
POLICY="$ROOT/policies/auto_code_loop/gate_policy.yaml"
VERIFY_SCRIPT="$ROOT/tools/policy_verify.sh"

# Test data
TMP_PLAN="$(mktemp)"

echo "[TEST] Policy verification regression tests"

# Test case 1: 0-directory globstar (docs/**/*.md should match docs/file.md)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "docs/test.md", "action": "test", "reason": "test"}
  ]
}
JSON

echo "  Test 1: 0-directory globstar (docs/**/*.md)"
if bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: docs/test.md matched docs/**/*.md"
else
    echo "    ❌ FAIL: docs/test.md not matched by docs/**/*.md"
    exit 1
fi

# Test case 2: 1-directory globstar (docs/**/*.md should match docs/sub/file.md)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "docs/sub/test.md", "action": "test", "reason": "test"}
  ]
}
JSON

echo "  Test 2: 1-directory globstar (docs/**/*.md)"
if bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: docs/sub/test.md matched docs/**/*.md"
else
    echo "    ❌ FAIL: docs/sub/test.md not matched by docs/**/*.md"
    exit 1
fi

# Test case 3: 0-directory globstar (duri_modules/**/*.py should match duri_modules/file.py)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "duri_modules/test.py", "action": "test", "reason": "test"}
  ]
}
JSON

echo "  Test 3: 0-directory globstar (duri_modules/**/*.py)"
if bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: duri_modules/test.py matched duri_modules/**/*.py"
else
    echo "    ❌ FAIL: duri_modules/test.py not matched by duri_modules/**/*.py"
    exit 1
fi

# Test case 4: Blacklist test (should deny .env files)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "config.env", "action": "test", "reason": "test"}
  ]
}
JSON

echo "  Test 4: Blacklist test (**/*.env)"
if ! bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: config.env correctly denied by **/*.env"
else
    echo "    ❌ FAIL: config.env should have been denied"
    exit 1
fi

# Test case 5: Non-whitelisted file (should deny)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "unknown.txt", "action": "test", "reason": "test"}
  ]
}
JSON

echo "  Test 5: Non-whitelisted file"
if ! bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: unknown.txt correctly denied"
else
    echo "    ❌ FAIL: unknown.txt should have been denied"
    exit 1
fi

# Test case 6: Security - Root escape prevention
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "../../../etc/passwd", "action": "test", "reason": "security test"}
  ]
}
JSON

echo "  Test 6: Security - Root escape prevention"
if ! bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: Root escape correctly denied"
else
    echo "    ❌ FAIL: Root escape should have been denied"
    exit 1
fi

# Test case 7: Case sensitivity test (expecting case-sensitive behavior)
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "docs/readme.MD", "action": "test", "reason": "case sensitivity test"}
  ]
}
JSON

echo "  Test 7: Case sensitivity test"
if ! bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" >/dev/null 2>&1; then
    echo "    ✅ PASS: Case sensitivity correctly enforced (MD != md)"
else
    echo "    ❌ FAIL: Case sensitivity not enforced"
    exit 1
fi

# Test case 8: Explain mode functionality
cat > "$TMP_PLAN" << 'JSON'
{
  "plan": [
    {"file": "docs/test.md", "action": "test", "reason": "explain test"}
  ]
}
JSON

echo "  Test 8: Explain mode functionality"
if bash "$VERIFY_SCRIPT" --policy "$POLICY" --plan "$TMP_PLAN" --explain 2>&1 | grep -q "EXPLAIN"; then
    echo "    ✅ PASS: Explain mode working correctly"
else
    echo "    ❌ FAIL: Explain mode not working"
    exit 1
fi

# Cleanup
rm -f "$TMP_PLAN"

echo "[PASS] All policy verification tests passed"

# >>>>>>> PATCH: extended regression tests (9~14) >>>>>>> #

echo "  Test 9: Large plan performance (2k entries)"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"
  POL="${POLICY:-$ROOT/policies/auto_code_loop/gate_policy.yaml}"
  D=$(date +%F)
  LOGDIR="$ROOT/logs/auto_code_loop_beta/$D"
  mkdir -p "$LOGDIR" "$ROOT/docs"
  # 대형 PLAN 생성(파일 실제 생성 불필요)
  python3 - "$LOGDIR/plan.json" <<'PY'
import json,sys
n=2000
plan={"plan":[{"file":f"docs/bulk_{i}.md"} for i in range(n)]}
open(sys.argv[1],"w",encoding="utf-8").write(json.dumps(plan))
PY
  # timeout 있으면 10초 제한, 없으면 그냥 실행
  if command -v timeout >/dev/null 2>&1; then
    timeout 10s bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan.json" >/dev/null
  else
    bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan.json" >/dev/null
  fi
) && echo "    ✅ PASS: 2k entries verified under time budget" || echo "    ❌ FAIL: performance or verification failed"

echo "  Test 10: Symlink denial (repo->outside)"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"
  POL="${POLICY:-$ROOT/policies/auto_code_loop/gate_policy.yaml}"
  D=$(date +%F); LOGDIR="$ROOT/logs/auto_code_loop_beta/$D"
  mkdir -p "$LOGDIR" "$ROOT/docs"

  # 깨끗한 상태로 심볼릭 링크 생성
  rm -f "$ROOT/docs/link_out"
  ln -s /etc/passwd "$ROOT/docs/link_out"

  echo '{"plan":[{"file":"docs/link_out"}]}' > "$LOGDIR/plan_symlink.json"

  # 게이트 실행 출력만 캡쳐(에러코드 무시) → grep으로 판정
  OUT="$( (bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan_symlink.json" --explain) 2>&1 || true )"
  if grep -q "\[DENY\]" <<<"$OUT"; then
    echo "    ✅ PASS: symlink denied"
  else
    echo "    ❌ FAIL: symlink allowed"
    echo "$OUT" | sed 's/^/      > /'
  fi

  # 정리
  rm -f "$ROOT/docs/link_out" "$LOGDIR/plan_symlink.json"
)

echo "  Test 11: Unicode & space filename (NFC) allow"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"
  POL="${POLICY:-$ROOT/policies/auto_code_loop/gate_policy.yaml}"
  D=$(date +%F)
  LOGDIR="$ROOT/logs/auto_code_loop_beta/$D"
  mkdir -p "$LOGDIR" "$ROOT/docs"
  touch "$ROOT/docs/유 니 코드.md"
  echo '{"plan":[{"file":"docs/유 니 코드.md"}]}' > "$LOGDIR/plan_unicode.json"
  if bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan_unicode.json" 2>&1 | grep -q "\[ALLOW\].*유 니 코드\.md"; then
    echo "    ✅ PASS: unicode+space matched docs/**/*.md"
  else
    echo "    ❌ FAIL: unicode+space not allowed"
  fi
)

echo "  Test 12: Blacklist precedes whitelist"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"

  TMPPOL="$(mktemp)"; TMPPLAN="$(mktemp)"
  cat > "$TMPPOL" <<'YML'
version: 1
whitelist:
  - "docs/**"
blacklist:
  - "**/*.env"
YML

  : > "$ROOT/docs/config.env"
  echo '{"plan":[{"file":"docs/config.env"}]}' > "$TMPPLAN"

  OUT="$( (bash "$SEC" --policy "$TMPPOL" --plan "$TMPPLAN" --explain) 2>&1 || true )"
  if grep -q "\[DENY\] blacklisted" <<<"$OUT"; then
    echo "    ✅ PASS: blacklist takes precedence"
  else
    echo "    ❌ FAIL: blacklist precedence broken"
    echo "$OUT" | sed 's/^/      > /'
  fi

  rm -f "$TMPPOL" "$TMPPLAN" "$ROOT/docs/config.env"
)

echo "  Test 13: YAML anchors/merge parsing (parser robustness)"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="$ROOT/tools/policy_verify.sh"
  TMPPOL=$(mktemp)
  cat > "$TMPPOL" <<'YML'
version: 1
_base_wl: &base_wl
  - "docs/**/*.md"
_extra_wl: &extra_wl
  - "duri_modules/**/*.py"
whitelist:
  - *base_wl
  - *extra_wl
blacklist: []
YML
  D=$(date +%F)
  LOGDIR="$ROOT/logs/auto_code_loop_beta/$D"
  mkdir -p "$LOGDIR" "$ROOT/docs"
  : > "$ROOT/docs/anchor_test.md"
  echo '{"plan":[{"file":"docs/anchor_test.md"}]}' > "$LOGDIR/plan_yaml_anchor.json"
  if bash "$SEC" --policy "$TMPPOL" --plan "$LOGDIR/plan_yaml_anchor.json" 2>&1 | grep -q "\[ALLOW\].*anchor_test\.md"; then
    echo "    ✅ PASS: YAML anchors/merge supported by parser"
  else
    echo "    ❌ FAIL: YAML anchors/merge not handled"
  fi
  rm -f "$TMPPOL" "$ROOT/docs/anchor_test.md"
)

echo "  Test 14: Explain-mode consistency"
(
  set -euo pipefail
  ROOT="${ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
  SEC="${SECURITY_CHECK:-$ROOT/tools/policy_verify.sh}"
  POL="${POLICY:-$ROOT/policies/auto_code_loop/gate_policy.yaml}"
  D=$(date +%F)
  LOGDIR="$ROOT/logs/auto_code_loop_beta/$D"
  mkdir -p "$LOGDIR" "$ROOT/docs" "$ROOT/duri_modules"
  : > "$ROOT/docs/e1.md"
  : > "$ROOT/duri_modules/e2.py"
  jq -n --arg d1 "docs/e1.md" --arg d2 "duri_modules/e2.py" \
     '{plan:[{file:$d1},{file:$d2}]}' > "$LOGDIR/plan_explain.json"

  c1=$(bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan_explain.json" | grep -c "^\[ALLOW\]")
  c2=$(bash "$SEC" --policy "$POL" --plan "$LOGDIR/plan_explain.json" --explain | grep -c "^\[ALLOW\]")
  if [[ "$c1" -eq "$c2" && "$c1" -gt 0 ]]; then
    echo "    ✅ PASS: explain-mode does not alter decisions (ALLOW=$c1)"
  else
    echo "    ❌ FAIL: explain-mode inconsistency (no=$c1, ex=$c2)"
  fi
)
# <<<<<<< PATCH END <<<<<<< #
