#!/usr/bin/env bash
# CI Guard Script - Prevents environment mismatch issues

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YEL='\033[1;33m'; NC='\033[0m'
pass(){ echo -e "${GREEN}✔ $*${NC}"; }
fail(){ echo -e "${RED}✘ $*${NC}"; exit 1; }
note(){ echo -e "${YEL}➜ $*${NC}"; }

note "CI Guard: Environment Mismatch Prevention"

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
pip install -r requirements-dev.txt >/dev/null 2>&1 || fail "Failed to install dev dependencies"

# 3) Run tests with proper environment
note "Running import tests with DB skip"
export DURICORE_SKIP_DB=1
export DURI_DB_SKIP=1
export DURI_TEST_SKIP_DB=1
DURI_DB_SKIP=1 DURI_TEST_SKIP_DB=1 PYTHONPATH="tests:$PYTHONPATH" python3 -m pytest tests/test_imports.py -v

# 4) Check for absolute imports (no relative imports in core modules)
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

# 5) Run ruff lint check (should fail CI if violations found)
note "Running ruff lint check"
ruff check . || fail "Ruff lint violations found - fix before proceeding"

# 6) Verify container vs host consistency
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
