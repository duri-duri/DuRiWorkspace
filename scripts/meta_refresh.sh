#!/usr/bin/env bash
set -euo pipefail

DST_DIR="/mnt/e/DuRiSafe_HOSP/FULL"
GOLD="${1:-}"    # 인자로 GOLD 타겟 파일명 넘기면 GOLD.txt 갱신

cd "$DST_DIR"

# LATEST.txt가 가리키는 파일이 실제 존재하는지 보정
if [ -s LATEST.txt ]; then
  L=$(cat LATEST.txt)
  if [ ! -f "$L" ]; then
    echo "[META] LATEST.txt가 유효하지 않음 → 최신 파일로 치환"
    NEW=$(ls -1t FULL__*.tar.zst 2>/dev/null | head -n1 || true)
    [ -n "$NEW" ] && echo "$NEW" > LATEST.txt && echo "[META] LATEST.txt -> $NEW"
  fi
else
  NEW=$(ls -1t FULL__*.tar.zst 2>/dev/null | head -n1 || true)
  [ -n "$NEW" ] && echo "$NEW" > LATEST.txt && echo "[META] LATEST.txt -> $NEW"
fi

# GOLD 지정 시 반영(명시적으로만 변경)
if [ -n "$GOLD" ]; then
  if [ -f "$GOLD" ]; then
    echo "$GOLD" > GOLD.txt
    echo "[META] GOLD.txt -> $GOLD"
  else
    echo "[META] GOLD 지정 파일 없음: $GOLD" >&2
    exit 2
  fi
fi

echo "[META] 완료"
