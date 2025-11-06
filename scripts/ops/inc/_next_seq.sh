#!/usr/bin/env bash
# L4 Next Sequence ID Generator
# Purpose: 모노토닉 시퀀스 ID 부여로 정렬 안정성 보장
# Usage: seq=$(bash scripts/ops/inc/_next_seq.sh)

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

seqf="${ROOT}/var/audit/decisions.seq"
mkdir -p "$(dirname "$seqf")"

exec 9>"${seqf}.lock"
flock -w 5 9 || { echo "[ERROR] Failed to acquire lock for sequence file" >&2; exit 1; }

touch "$seqf"
v=$(cat "$seqf" 2>/dev/null || echo 0)
v=$((v+1))
echo "$v" > "$seqf"
echo "$v"

