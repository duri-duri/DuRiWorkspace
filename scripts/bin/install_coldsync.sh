#!/usr/bin/env bash
# Helper script: Install coldsync_hosp_from_usb.sh to /usr/local/bin
# Usage: bash scripts/bin/install_coldsync.sh

set -euo pipefail

SCRIPT="scripts/bin/coldsync_hosp_from_usb.sh"
TARGET="/usr/local/bin/coldsync_hosp_from_usb.sh"

if [ ! -f "$SCRIPT" ]; then
    echo "[ERROR] Source file not found: $SCRIPT"
    exit 1
fi

echo "=== Installing coldsync_hosp_from_usb.sh ==="
echo "Source: $SCRIPT"
echo "Target: $TARGET"
echo ""

# Ensure LF line endings
if command -v dos2unix >/dev/null 2>&1; then
    dos2unix "$SCRIPT" 2>/dev/null || true
fi

# Set executable permission
chmod 755 "$SCRIPT"

# Install to /usr/local/bin with root ownership
sudo install -o root -g root -m 0755 "$SCRIPT" "$TARGET"

echo ""
echo "✅ Installation complete"
echo ""
echo "Verification:"
ls -lh "$TARGET"
which coldsync_hosp_from_usb.sh || echo "Note: Run 'hash -r' to refresh PATH cache"

