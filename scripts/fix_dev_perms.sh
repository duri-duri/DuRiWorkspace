#!/usr/bin/env bash
set -euo pipefail

echo "[fix_dev_perms] Fixing ownership for local runtime data directories..."

# Check if sudo is available
command -v sudo >/dev/null || { echo "Error: sudo is required but not found"; exit 1; }

# Fix ownership for common docker/container runtime directories (only if they exist)
[[ -d data ]] && sudo chown -R "$USER":"$USER" data || echo "[fix_dev_perms] data/ directory not found, skipping"
[[ -d grafana ]] && sudo chown -R "$USER":"$USER" grafana || echo "[fix_dev_perms] grafana/ directory not found, skipping"
[[ -d prom-data ]] && sudo chown -R "$USER":"$USER" prom-data || echo "[fix_dev_perms] prom-data/ directory not found, skipping"

echo "[fix_dev_perms] Ownership fixed for existing directories."
echo "[fix_dev_perms] You can now safely run git operations."
