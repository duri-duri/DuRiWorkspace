#!/usr/bin/env bash
set -euo pipefail
echo "[INFO] Sunday transition to 100% started at $(date)"
export DURI_UNIFIED_REASONING_MODE=force
export DURI_UNIFIED_REASONING_ROLLOUT=100
export DURI_UNIFIED_CONVERSATION_MODE=force
export DURI_UNIFIED_CONVERSATION_ROLLOUT=100
export DURI_UNIFIED_LEARNING_MODE=force
export DURI_UNIFIED_LEARNING_ROLLOUT=100
echo "[INFO] Environment variables set to 100% force mode"
./scripts/final_verify.sh || { echo "[ERROR] Final verify failed"; exit 1; }
echo "[INFO] ✅ Sunday transition to 100% completed successfully"
