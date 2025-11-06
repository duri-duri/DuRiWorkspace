#!/usr/bin/env bash
# L4 NDJSON Canonicalize (Sort & Dedup)
# Purpose: NDJSON 정렬 및 중복 제거로 정렬 미스매치 해결
# Usage: bash scripts/ops/inc/l4_canonicalize_ndjson.sh

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

f="${ROOT}/var/audit/decisions.ndjson"
lock="${ROOT}/var/audit/decisions.lock"
tmp="$(mktemp)"

mkdir -p "$(dirname "$f")"

exec 9>"${lock}"
flock -w 5 9 || { echo "[ERROR] Failed to acquire lock for canonicalize" >&2; exit 1; }

# 파일이 없으면 생성
if [[ ! -f "$f" ]]; then
    touch "$f"
fi

# 유효 JSON만 추출 → (ts,seq) 기준 정렬 → (ts,decision) 기준 중복 제거
jq -c 'select(type=="object" and .ts != null)' "$f" 2>/dev/null | \
jq -cs 'sort_by([.ts, (.seq // 0)]) | unique_by(.ts + "|" + (.decision // "")) | .[]' > "$tmp" || {
    echo "[WARN] Canonicalize failed, keeping original" >&2
    rm -f "$tmp"
    exit 0
}

mv "$tmp" "$f"
chmod 0644 "$f"

# 동기화 보장
sync
if command -v fdatasync >/dev/null 2>&1; then
    fdatasync <"$f" >/dev/null 2>&1 || true
fi

# 디렉터리 fsync
python3 "${ROOT}/scripts/ops/inc/_fsync_dir.py" "$(dirname "$f")" 2>/dev/null || true

echo "[INFO] Canonicalized: $(wc -l < "$f" 2>/dev/null || echo 0) lines"

