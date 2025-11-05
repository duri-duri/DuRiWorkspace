#!/usr/bin/env bash
# Setup L4 Bootstrap - 시스템 레벨 부팅 보장 설정
# Purpose: 재부팅 후 자동 복구를 위한 시스템 레벨 설정
# Usage: sudo bash scripts/ops/setup_l4_bootstrap.sh

set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root (use sudo)"
  exit 1
fi

USER="duri"
HOME="/home/${USER}"

echo "=== L4 Bootstrap System Setup ==="
echo ""

# 1. System service 설치
echo "[1] Installing system service..."
cat > /etc/systemd/system/l4-ensure.service <<'EOF'
[Unit]
Description=Ensure L4 user-systemd timers & env at boot

After=network.target
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/l4_ensure_bootstrap.sh
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

# 2. Bootstrap 스크립트 설치
echo "[2] Installing bootstrap script..."
cat > /usr/local/bin/l4_ensure_bootstrap.sh <<'BOOTSTRAP'
#!/usr/bin/env bash
set -euo pipefail

USER="duri"
HOME="/home/${USER}"
SU="/bin/su - ${USER} -c"

# 1) ensure linger so user systemd starts without login
if loginctl show-user "${USER}" &>/dev/null; then
  loginctl enable-linger "${USER}" || true
else
  echo "User ${USER} not found, skipping linger"
fi

# 2) ensure user drop-ins exist
mkdir -p "${HOME}/.config/systemd/user" || true

# 3) reload user's systemd and enable timers
${SU} "systemctl --user daemon-reload || true" || true

# 4) enable timers (non-blocking)
${SU} "systemctl --user enable l4-*.timer || true" || true

# 5) run one-shot verification (non-blocking, background)
${SU} "bash -lc 'cd ${HOME}/DuRiWorkspace && bash scripts/ops/inc/l4_canonicalize_ndjson.sh || true; bash scripts/ops/l4_validation.sh || true'" &

exit 0
BOOTSTRAP

chmod +x /usr/local/bin/l4_ensure_bootstrap.sh

# 3. System service 활성화
echo "[3] Enabling system service..."
systemctl daemon-reload
systemctl enable --now l4-ensure.service

echo ""
echo "✅ L4 Bootstrap System Setup Complete"
echo ""
echo "Verification:"
systemctl status l4-ensure.service --no-pager | head -10

