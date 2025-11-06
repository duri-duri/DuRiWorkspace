#!/usr/bin/env bash
# L4 Recovery Try - 재시도 로직 포함 복구 스크립트
# Purpose: 재시도 로직으로 더 강력한 복구
# Usage: Called by systemd user unit

set -euo pipefail

WORK="/home/duri/DuRiWorkspace"
VALID="${WORK}/scripts/ops/l4_validation.sh"
MAX_RETRIES=3
RETRY_DELAY=30

retry_count=0
success=0

while [[ $retry_count -lt $MAX_RETRIES ]]; do
  echo "[Retry $((retry_count + 1))/$MAX_RETRIES] L4 recovery attempt..."
  
  # 기본 복구 실행
  if bash "${WORK}/scripts/ops/l4_recover_and_verify.sh" 2>/dev/null; then
    # 검증 실행
    if bash "$VALID" >/tmp/l4_validation_retry_${retry_count}.log 2>&1; then
      success=1
      echo "✅ Recovery successful"
      break
    fi
  fi
  
  retry_count=$((retry_count + 1))
  
  if [[ $retry_count -lt $MAX_RETRIES ]]; then
    echo "  Waiting ${RETRY_DELAY}s before retry..."
    sleep $RETRY_DELAY
  fi
done

if [[ $success -eq 0 ]]; then
  echo "❌ Recovery failed after ${MAX_RETRIES} attempts"
  touch /var/run/l4_recovery_failed 2>/dev/null || true
  logger -t l4-recover "L4 recovery failed after ${MAX_RETRIES} attempts" 2>/dev/null || true
  exit 1
fi

exit 0

