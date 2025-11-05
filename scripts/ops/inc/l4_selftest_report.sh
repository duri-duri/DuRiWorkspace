#!/usr/bin/env bash
# L4 Selftest Report - 성공/실패 집계 메트릭 생성
# Purpose: l4_recover_and_verify.sh 실행 후 성공/실패 메트릭 생성
# Usage: Called by l4_recover_and_verify.sh at the end

set -euo pipefail

OUT_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-/tmp/test_textfile}"
ts=$(date -u +%Y%m%dT%H%M%SZ)

# Check if validation passed (by checking last log or exit code)
if [[ -f /tmp/l4_recover.last.log ]] && grep -q "Validation passed" /tmp/l4_recover.last.log 2>/dev/null; then
  echo "l4_selftest_pass 1 $(date +%s)" > "${OUT_DIR}/l4_selftest.pass.prom"
elif [[ -f /tmp/l4_validation.boot.log ]] && grep -q "✅ Validation passed" /tmp/l4_validation.boot.log 2>/dev/null; then
  echo "l4_selftest_pass 1 $(date +%s)" > "${OUT_DIR}/l4_selftest.pass.prom"
else
  echo "l4_selftest_pass 0 $(date +%s)" > "${OUT_DIR}/l4_selftest.pass.prom"
fi

# Ensure file permissions
chmod 0644 "${OUT_DIR}/l4_selftest.pass.prom" 2>/dev/null || true

exit 0

