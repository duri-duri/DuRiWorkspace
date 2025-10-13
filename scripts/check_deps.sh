#!/usr/bin/env bash
# 필수 바이너리 사전 점검
set -euo pipefail

need=(bash awk sed grep sort head mktemp flock)
for b in "${need[@]}"; do
    command -v "$b" >/dev/null || { echo "[err] $b not found" >&2; exit 2; }
done

# 선택적 바이너리 (있으면 좋음)
optional=(jq git bc python3)
for b in "${optional[@]}"; do
    if command -v "$b" >/dev/null; then
        echo "[info] $b found" >&2
    else
        echo "[warn] $b not found (optional)" >&2
    fi
done
