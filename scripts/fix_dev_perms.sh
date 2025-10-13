#!/usr/bin/env bash
set -euo pipefail

echo "[fix_dev_perms] Fixing ownership for local runtime data directories..."

# Fix ownership for common docker/container runtime directories
sudo chown -R "$USER":"$USER" data grafana prom-data || true

echo "[fix_dev_perms] Ownership fixed for data/, grafana/, and prom-data/."
echo "[fix_dev_perms] You can now safely run git operations."
