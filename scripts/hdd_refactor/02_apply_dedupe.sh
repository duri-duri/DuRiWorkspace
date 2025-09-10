#!/usr/bin/env bash
set -Eeuo pipefail
DRY=${DRYRUN:-1}  # 1=dry-run, 0=apply
ROOT="/mnt/h/ARCHIVE"
PLAN="$ROOT/META/DEDUPE_PLAN.jsonl"
LOG="$ROOT/_logs/02_apply_dedupe_$(date +%F_%H%M).log"

jq -c '. ' "$PLAN" | while read -r J; do
  FROM=$(echo "$J" | jq -r '.from'); TO=$(echo "$J" | jq -r '.to')
  [[ -f "$FROM" && -f "$TO" ]] || { echo "SKIP (missing): $FROM / $TO" | tee -a "$LOG"; continue; }
  # 같은 볼륨인지 확인
  [[ "$(df -P "$FROM" | tail -1 | awk "{print \$1}")" == "$(df -P "$TO" | tail -1 | awk "{print \$1}")" ]] || {
    echo "SKIP (cross-device): $FROM" | tee -a "$LOG"; continue; }
  if [[ $DRY -eq 1 ]]; then
    echo "DRYRUN ln -f \"$TO\" \"$FROM\"" | tee -a "$LOG"
  else
    TMP="${FROM}.linkswap"
    # 안전 링크 스왑: 새 하드링크 만들어 교체 → 원자성 강화
    ln "$TO" "$TMP" && touch -r "$FROM" "$TMP" && mv -f "$TMP" "$FROM"
    echo "LINKED: $FROM -> $TO" | tee -a "$LOG"
  fi
done
