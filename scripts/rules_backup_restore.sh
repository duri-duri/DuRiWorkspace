#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

CMD="${1:-}"
TS="$(date +%Y%m%d_%H%M%S)"
ARCH="rules_${TS}.tar.gz"
SHA="${ARCH}.sha256"

case "$CMD" in
  backup)
    tar -C prometheus -czf "$ARCH" rules
    sha256sum "$ARCH" > "$SHA"
    echo "[OK] backup: $ARCH"
    ;;
  restore)
    FILE="${2:?usage: $0 restore <archive.tar.gz>}"
    sha256sum -c "${FILE}.sha256"
    tar -C prometheus -xzf "$FILE"
    curl -X POST http://localhost:9090/-/reload || true
    echo "[OK] restored and reloaded"
    ;;
  *)
    echo "usage: $0 backup | restore <archive.tar.gz>"; exit 2;;
esac
