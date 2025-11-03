#!/usr/bin/env bash
# PromQL Unit Test Runner
# Purpose: Run PromQL unit tests with absolute paths and proper glob handling
# Usage: bash scripts/ops/promql_unit.sh

set -euo pipefail

ROOT="$(git -C "$(dirname "$0")/../.." rev-parse --show-toplevel 2>/dev/null || realpath "$(dirname "$0")/../..")"
cd "$ROOT"

TEST_DIR="${TEST_DIR:-$ROOT/tests/promql}"
PROM_IMG="${PROM_IMG:-prom/prometheus:v2.54.1}"
PROM_DIR="${PROM_DIR:-$ROOT/prometheus}"

log() {
  echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $*" >&2
}

log "=== PromQL Unit Test Runner ==="
log "Test directory: $TEST_DIR"

# Enable nullglob to handle empty globs gracefully
shopt -s nullglob

# Collect test files (both .yml and .yaml) - deduplicate using sort -u
TEST_FILES=()
shopt -s nullglob
for pattern in "${TEST_DIR}"/*_test.yml "${TEST_DIR}"/*_test.yaml "${TEST_DIR}"/*.yml "${TEST_DIR}"/*.yaml; do
  if [ -f "$pattern" ]; then
    TEST_FILES+=("$pattern")
  fi
done
shopt -u nullglob

# Deduplicate: sort -u to remove duplicates
if [ ${#TEST_FILES[@]} -gt 0 ]; then
  # Use sort -u to remove duplicates (handles same file multiple times)
  TEST_FILES=($(printf '%s\n' "${TEST_FILES[@]}" | sort -u))
fi

if [ ${#TEST_FILES[@]} -eq 0 ]; then
  log "[SKIP] No PromQL test files found in $TEST_DIR"
  log "[INFO] Expected files: *_test.yml, *_test.yaml, or any .yml/.yaml files"
  exit 0
fi

log "Found ${#TEST_FILES[@]} test file(s):"
for f in "${TEST_FILES[@]}"; do
  log "  - $(basename "$f")"
done

# Run tests
FAILED=0
for test_file in "${TEST_FILES[@]}"; do
  test_name=$(basename "$test_file")
  log ""
  log "[RUN] promtool test rules: $test_name"
  
  # Use absolute path for test file
  test_file_abs=$(realpath "$test_file")
  
  # Run promtool test in container (mount both prometheus config and test file)
  if docker run --rm --entrypoint /bin/sh \
    -v "$PROM_DIR:/etc/prometheus:ro" \
    -v "$TEST_DIR:/tests:ro" \
    -w /tests \
    "$PROM_IMG" -lc "promtool test rules $(basename "$test_file")" 2>&1; then
    log "[OK] $test_name passed"
  else
    log "[FAIL] $test_name failed"
    FAILED=1
  fi
done

shopt -u nullglob

if [ "$FAILED" -eq 0 ]; then
  log ""
  log "[OK] All PromQL unit tests passed"
  exit 0
else
  log ""
  log "[FAIL] Some PromQL unit tests failed"
  exit 1
fi
