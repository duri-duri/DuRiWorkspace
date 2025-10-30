#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/DuRiWorkspace"
mkdir -p var/ANCHOR
# Git이 추적하는 파일들의 SHA256을 앵커로 사용
(git ls-files -z | xargs -0 sha256sum > var/ANCHOR/SHA256SUMS) || true
echo "[OK] anchor written: var/ANCHOR/SHA256SUMS"
