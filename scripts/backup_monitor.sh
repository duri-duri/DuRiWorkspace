#!/usr/bin/env bash
set -euo pipefail
WS_ROOT="${WS_ROOT:-$PWD}"
STATE="${WS_ROOT}/var/state/backup_refs.json"
Y=$(date +%Y) ; M=$(date +%m) ; D=$(date +%d)
BASE="/mnt/c/Users/admin/Desktop/두리백업/${Y}/${M}/${D}"

echo "=== DuRi Backup Monitor ($(date +'%F %T %Z')) ==="
for lvl in CORE EXTENDED FULL; do
  f="$(ls -t ${BASE}/${lvl}__*.tar.* 2>/dev/null | head -n1 || true)"
  if [[ -n "${f}" ]]; then
    echo "- ${lvl}: $(basename "${f}")  ($(du -h "${f}" | awk '{print $1}'))"
    s="$(ls -t ${BASE}/SHA256SUMS.${lvl}.*.txt 2>/dev/null | head -n1 || true)"
    [[ -n "${s}" ]] && echo "  sha256sum: ${s##*/}"
    
    # --- manifest.full.json 상태 표시 (FULL 레벨만) ---
    if [[ "$lvl" == "FULL" ]]; then
      MF_FULL="${BASE}/manifest.full.json"
      if [[ -s "$MF_FULL" ]]; then
        echo "  manifest.full.json: present ($(stat -c%s "$MF_FULL" 2>/dev/null || stat -f%z "$MF_FULL" 2>/dev/null) bytes)"
      else
        echo "  manifest.full.json: (없음)"
      fi
    fi
  else
    echo "- ${lvl}: (없음)"
  fi
done

if command -v jq >/dev/null 2>&1 && [[ -f "${STATE}" ]]; then
  echo "--- state history (last 10) ---"
  jq -r '.history | sort_by(.time_kst) | reverse | .[0:10][] | "\(.time_kst)  \(.level)  \(.note)"' "${STATE}" || true
fi
