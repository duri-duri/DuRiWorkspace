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
