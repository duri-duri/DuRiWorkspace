#!/usr/bin/env bash
# Shadow 파일럿 실행 스크립트 (48시간 파일럿)
# Tier-1: 하이브리드 실험 모드

set -euo pipefail

cd /home/duri/DuRiWorkspace || exit 1

# Tier 설정 확인
if [ -f "var/run/shadow_tier.env" ]; then
    source "var/run/shadow_tier.env" 2>/dev/null || true
fi

# Tier-1 설정 (파일럿)
export SHADOW_TIER=1
export TRANSPORT="${TRANSPORT:-mixed}"  # 하이브리드
export SSH_CANARY="${SSH_CANARY:-0.30}"  # 30% SSH
export CHAOS_ENABLED=0  # 파일럿에서는 카오스 비활성화

echo "[INFO] Shadow 파일럿 실행 (Tier-1: 하이브리드, SSH ${SSH_CANARY})"
echo "[INFO] TRANSPORT=$TRANSPORT, SSH_CANARY=$SSH_CANARY"

# 게이트 체크
if ! bash scripts/shadow_gate_check.sh >/dev/null 2>&1; then
    echo "[WARNING] 게이트 체크 실패, HTTP 모드로 폴백"
    export TRANSPORT=http
    export SSH_CANARY=0.0
fi

# Shadow 실행
bash scripts/shadow_duri_integration_final.sh

