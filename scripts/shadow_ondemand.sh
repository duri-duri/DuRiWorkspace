#!/usr/bin/env bash
# Shadow 온디맨드 실행 스크립트
# Tier-0: 수동 실행 전용

set -euo pipefail

cd /home/duri/DuRiWorkspace || exit 1

# Tier 설정 확인
if [ -f "var/run/shadow_tier.env" ]; then
    source "var/run/shadow_tier.env" 2>/dev/null || true
fi

# Tier-0 강제 (온디맨드)
export SHADOW_TIER=0
export TRANSPORT="${TRANSPORT:-http}"  # 기본 HTTP
export SSH_CANARY=0.0
export CHAOS_ENABLED=0

echo "[INFO] Shadow 온디맨드 실행 (Tier-0: HTTP 기본)"
echo "[INFO] TRANSPORT=$TRANSPORT"

# Shadow 실행
bash scripts/shadow_duri_integration_final.sh

