#!/usr/bin/env bash
# CI Guard Script - Prevents environment mismatch issues

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

note "CI Guard: Environment Mismatch Prevention"

# 0) Check for attr namespace pollution (prevents flake8-bugbear conflicts)
note "Checking for attr namespace pollution"
python - <<'PY' || { echo "[CI GUARD] Found 'attr' shadowing 'attrs'"; exit 1; }
try:
    import attr  # 존재하면 실패시킴
    raise SystemExit(1)
except Exception:
    pass
PY

# 1) Check if we're in the right environment
if [[ "${CI:-}" == "true" ]]; then
    note "Running in CI environment"
    export DURICORE_SKIP_DB=1
else
    note "Running in local environment"
fi

# 2) Verify test dependencies
note "Checking test dependencies"
if command -v pytest >/dev/null 2>&1; then
    pass "pytest available"
else
    fail "pytest not found - install with: pip install -r requirements-dev.txt"
fi

if command -v jq >/dev/null 2>&1; then
    pass "jq available"
else
    fail "jq not found - install with: apt-get install jq"
fi

# Install dev dependencies if not available
note "Installing dev dependencies"
if [ -f requirements-dev.txt ]; then
    python -m pip install -U pip || true
    pip install -r requirements-dev.txt || {
        note "Fallback: installing individual packages"
        pip install -U pre-commit pytest pytest-asyncio pytest-benchmark black isort flake8 flake8-bugbear yamllint || true
    }
else
    note "No requirements-dev.txt found, installing individual packages"
    python -m pip install -U pip || true
    pip install -U pre-commit pytest pytest-asyncio pytest-benchmark black isort flake8 flake8-bugbear yamllint || true
fi

# Show versions for visibility
note "Installed tool versions:"
pre-commit --version || true
pytest --version || true
black --version || true
isort --version || true
flake8 --version || true
yamllint --version || true

# 3) Fail-fast module loading check (build-time guard)
note "Running fail-fast module loading check"
python3 - <<'PY'
import importlib
import sys

# Critical modules that must load at build time
critical_modules = [
    "duri_core.app.logic",
    "duri_core.core.decision",
    "duri_core.core.decision_processor",
    "duri_core.core.logging",
    "duri_core.core.stats",
    "duri_core.core.database",
    "duri_core.core.loop_orchestrator",
    "duri_common.config.emotion_labels",
]

failed_modules = []
for module_name in critical_modules:
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} loaded successfully")
    except Exception as e:
        failed_modules.append(f"{module_name}: {e}")
        print(f"❌ {module_name} failed to load: {e}")

if failed_modules:
    print("CRITICAL MODULES FAILED TO LOAD:")
    for failure in failed_modules:
        print(f"  - {failure}")
    sys.exit(1)

print("✅ All critical modules loaded successfully (build-time guard passed)")
PY

# 4) Run tests with proper environment
note "Running import tests with DB skip"
export DURICORE_SKIP_DB=1
export DURI_DB_SKIP=1
export DURI_TEST_SKIP_DB=1
DURI_DB_SKIP=1 DURI_TEST_SKIP_DB=1 PYTHONPATH="tests:$PYTHONPATH" python3 -m pytest tests/test_imports.py -v

# 5) Check for absolute imports (no relative imports in core modules)
note "Checking for absolute imports"
# 운영 중인 핵심 모듈만 체크 (서브모듈 제외, visualize/brain/evolution 등은 서브모듈 내부 구조)
RELATIVE_COUNT=$(grep -r "from \." duri_core/app/ duri_common/ 2>/dev/null | grep -v "__pycache__" | grep -v "__init__.py" | wc -l)
if [[ "$RELATIVE_COUNT" -gt 0 ]]; then
    echo "Found relative imports in core app modules:"
    grep -r "from \." duri_core/app/ duri_common/ 2>/dev/null | grep -v "__pycache__" | grep -v "__init__.py"
    fail "Found $RELATIVE_COUNT relative imports - use absolute imports only"
else
    pass "No relative imports found in core app modules"
fi

# 6) Run ruff lint check (should fail CI if violations found)
note "Running ruff lint check"
ruff check . || fail "Ruff lint violations found - fix before proceeding"

# 7) Verify container vs host consistency
note "Checking container consistency"
if docker ps --format '{{.Names}}' | grep -q duri-core; then
    CONTAINER_IMAGE=$(docker inspect duri-core --format '{{.Image}}')
    note "Container image: $CONTAINER_IMAGE"

    # Check if container is using latest built image
    LATEST_BUILD=$(docker images duri-core --format '{{.ID}}' | head -1)
    if [[ "$CONTAINER_IMAGE" == *"$LATEST_BUILD"* ]]; then
        pass "Container using latest image"
    else
        note "Container may be using older image - consider rebuild"
    fi
else
    note "No duri-core container running"
fi

pass "CI Guard checks completed successfully"
