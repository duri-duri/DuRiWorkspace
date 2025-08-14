#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

REG_DIR="registry"
CUR="$REG_DIR/current.json"
TARGET="${1:-}"

usage() {
  echo "Usage: $0 <registry json or sha-tag>.json"
  echo "       $0 --dry-run   (prints current and last 5 candidates)"
}

if [[ "${TARGET:-}" == "--dry-run" || -z "${TARGET:-}" ]]; then
  echo "[DRY-RUN] Current registry:"
  ls -l "$CUR" || true
  echo "[DRY-RUN] Recent registry snapshots:"
  ls -lt "$REG_DIR"/*.json 2>/dev/null | head -5 || true
  exit 0
fi

SRC="$TARGET"
if [[ ! -f "$SRC" ]]; then
  SRC="$REG_DIR/$TARGET"
fi
if [[ ! -f "$SRC" ]]; then
  echo " rollback source not found: $TARGET"
  usage; exit 1
fi

cp -v "$CUR" "$CUR.bak.$(date +%Y%m%d%H%M%S)"
cp -v "$SRC" "$CUR"
echo "[OK] Rolled back to: $SRC"

