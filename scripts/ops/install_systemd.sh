#!/usr/bin/env bash
# Install L4 systemd services and timers
# Purpose: Copy templates to ~/.config/systemd/user/ and activate timers

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo /home/duri/DuRiWorkspace)"
cd "${ROOT}"

SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
TEMPLATE_DIR="${ROOT}/systemd"
NODE_EXPORTER_TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"

mkdir -p "${SYSTEMD_USER_DIR}"
mkdir -p "${TEMPLATE_DIR}"

# Install service files
for service in l4-weekly l4-daily l4-daily-quick l4-shadow-replay; do
  template="${TEMPLATE_DIR}/${service}.service.tmpl"
  target="${SYSTEMD_USER_DIR}/${service}.service"
  
  if [[ -f "${template}" ]]; then
    # Replace NODE_EXPORTER_TEXTFILE_DIR placeholder
    sed "s|@NODE_EXPORTER_TEXTFILE_DIR@|${NODE_EXPORTER_TEXTFILE_DIR}|g" "${template}" > "${target}"
    echo "✅ Installed: ${service}.service"
  else
    echo "⚠️  Template not found: ${template}"
  fi
done

# Install timer files
for timer in l4-weekly l4-daily l4-daily-quick l4-shadow-replay; do
  template="${TEMPLATE_DIR}/${timer}.timer.tmpl"
  target="${SYSTEMD_USER_DIR}/${timer}.timer"
  
  if [[ -f "${template}" ]]; then
    cp "${template}" "${target}"
    echo "✅ Installed: ${timer}.timer"
  else
    echo "⚠️  Template not found: ${template}"
  fi
done

# Reload systemd
systemctl --user daemon-reload
echo "✅ systemd daemon-reload completed"

# Enable and start timers
for timer in l4-weekly l4-daily l4-daily-quick l4-shadow-replay; do
  if systemctl --user enable --now "${timer}.timer" 2>/dev/null; then
    echo "✅ Enabled and started: ${timer}.timer"
  else
    echo "⚠️  Failed to enable: ${timer}.timer"
  fi
done

echo ""
echo "=== Installation Summary ==="
systemctl --user list-timers --all | grep -E 'l4-(weekly|daily|shadow-replay)' || echo "No L4 timers found"

