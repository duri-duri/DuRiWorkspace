#!/usr/bin/env bash
# L4 fdatasync Test - 파일 동기화 보장 확인
# Purpose: fdatasync를 사용한 실제 동기화 보장 테스트
# Usage: bash scripts/ops/l4_fdatasync_test.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

AUDIT_DIR="${ROOT}/var/audit"
TEST_FILE="${AUDIT_DIR}/decisions.ndjson.sync_test"

echo "=== L4 fdatasync Test: 파일 동기화 보장 ==="
echo ""

# Python을 사용한 fdatasync 테스트
python3 << 'PYTHON'
import os
import sys

test_file = "var/audit/decisions.ndjson.sync_test"
test_content = '{"ts":"2025-11-05T12:00:00Z","score":0.5,"decision":"TEST"}\n'

try:
    # 쓰기 + fdatasync
    with open(test_file, 'w') as f:
        f.write(test_content)
        f.flush()
        os.fdatasync(f.fileno())
    
    # 파일 존재 확인
    if os.path.exists(test_file):
        # 내용 확인
        with open(test_file, 'r') as f:
            content = f.read()
            if content == test_content:
                print("✅ fdatasync test PASSED")
                print("  - File written and synced successfully")
                print("  - Content matches expected value")
                sys.exit(0)
            else:
                print("❌ fdatasync test FAILED: Content mismatch")
                sys.exit(1)
    else:
        print("❌ fdatasync test FAILED: File not found")
        sys.exit(1)
except Exception as e:
    print(f"❌ fdatasync test FAILED: {e}")
    sys.exit(1)
PYTHON

result=$?

# 정리
rm -f "${TEST_FILE}" 2>/dev/null || true

if [[ $result -eq 0 ]]; then
  echo ""
  echo "=== fdatasync Test Complete: PASS ==="
else
  echo ""
  echo "=== fdatasync Test Complete: FAIL ==="
fi

exit $result

