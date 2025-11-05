#!/usr/bin/env bash
# L4 Bootstrap - 부팅 시 자동 실행 스크립트
# Purpose: 부팅 시 환경/디렉터리 보장 및 기본 복구
# Usage: Called by systemd user unit

set -euo pipefail

WORK="/home/duri/DuRiWorkspace"
TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"

# 텍스트파일 디렉터리 생성 및 권한 보장
mkdir -p "${TEXTFILE_DIR}"
chmod 0755 "${TEXTFILE_DIR}" 2>/dev/null || true
chown "$(whoami):$(whoami)" "${TEXTFILE_DIR}" 2>/dev/null || true

# 재부팅 생존성 체크 실행
if [[ -f "${WORK}/scripts/ops/l4_reboot_survival_check.sh" ]]; then
  bash "${WORK}/scripts/ops/l4_reboot_survival_check.sh" || true
fi

# 복구 스크립트 실행 (비동기, 실패해도 계속)
if [[ -f "${WORK}/scripts/ops/l4_recover_and_verify.sh" ]]; then
  bash "${WORK}/scripts/ops/l4_recover_and_verify.sh" &
fi

exit 0

