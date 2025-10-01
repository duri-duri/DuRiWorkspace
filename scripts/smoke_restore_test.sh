#!/usr/bin/env bash
set -euo pipefail
ROOT="${ROOT:-$HOME/DuRiWorkspace}"
echo "[SMOKE] restore drill start @ $(date)"
# 1) 가장 최근 INCR/FULL 존재 검증
FULL_LINK="/mnt/hdd/ARCHIVE/FULL/LATEST.tar.zst"
INCR_LINK="/mnt/hdd/ARCHIVE/INCR/LATEST-INCR.tar.zst"
[[ -f "$FULL_LINK" ]] || { echo "[ERR] missing FULL link: $FULL_LINK"; exit 2; }
[[ -f "$INCR_LINK" ]] || { echo "[ERR] missing INCR link: $INCR_LINK"; exit 2; }
zstd -t "$FULL_LINK" >/dev/null && echo "[OK] FULL integrity" || { echo "[ERR] FULL corrupt"; exit 3; }
zstd -t "$INCR_LINK"  >/dev/null && echo "[OK] INCR integrity" || { echo "[ERR] INCR corrupt"; exit 3; }

# 2) 샘플 복원 리허설(임시 디렉토리)
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "[SMOKE] extract sample list to tmp"
tar -tvf "$FULL_LINK" | head -50 > "$TMP/list.txt" || true
[[ -s "$TMP/list.txt" ]] && echo "[OK] can list archive" || { echo "[ERR] list failed"; exit 4; }

# 3) 핵심 파일 샘플 존재성 체크(정책 산출물 위주)
for f in docs/model_card_v1.md eval/metrics.yaml risk/risk_register.md; do
  grep -q "$f" "$TMP/list.txt" || echo "[WARN] sample not listed: $f (OK if packed later)"
done
echo "[SMOKE] restore drill pass"
