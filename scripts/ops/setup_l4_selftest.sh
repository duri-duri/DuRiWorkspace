#!/usr/bin/env bash
# Setup L4 Selftest - 일일 자동 자체검증 설치
# Purpose: L4 자동화 검증을 위한 데일리 타이머 및 Prometheus 알람 설정
# Usage: bash scripts/ops/setup_l4_selftest.sh

set -euo pipefail

WORK="/home/duri/DuRiWorkspace"
USER="duri"

echo "=== L4 Selftest Setup ==="
echo ""

# 1. Autotest script 설치
echo "[1] Installing autotest script..."
chmod +x "${WORK}/scripts/ops/l4_autotest.sh"
chmod +x "${WORK}/scripts/ops/inc/l4_selftest_report.sh"

# 2. Systemd user units 설치
echo "[2] Installing systemd user units..."
mkdir -p ~/.config/systemd/user

# Copy service and timer files
cp "${WORK}/scripts/ops/install_templates/l4-selftest.service" ~/.config/systemd/user/ 2>/dev/null || {
  cat > ~/.config/systemd/user/l4-selftest.service <<'EOF'
[Unit]
Description=L4 Daily Self-Test (canonicalize+validate+metrics)

[Service]
Type=oneshot
WorkingDirectory=/home/duri/DuRiWorkspace
ExecStart=/home/duri/DuRiWorkspace/scripts/ops/l4_autotest.sh
Environment=NODE_EXPORTER_TEXTFILE_DIR=/tmp/test_textfile

[Install]
WantedBy=default.target
EOF
}

cp "${WORK}/scripts/ops/install_templates/l4-selftest.timer" ~/.config/systemd/user/ 2>/dev/null || {
  cat > ~/.config/systemd/user/l4-selftest.timer <<'EOF'
[Unit]
Description=Daily L4 Self-Test Timer

[Timer]
OnCalendar=*-*-* 09:12:00
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF
}

systemctl --user daemon-reload
systemctl --user enable --now l4-selftest.timer

echo "✅ Selftest timer enabled"
echo ""

# 3. 즉시 실행 테스트
echo "[3] Running immediate test..."
bash "${WORK}/scripts/ops/l4_autotest.sh" || echo "⚠️  Initial test had issues (check logs)"

# 4. Prometheus 알람 규칙 확인
echo "[4] Prometheus alert rules updated"
echo "  Check: prometheus/rules/l4_alerts.yml"
echo "  New rules:"
echo "    - L4SelftestLowSuccessRate (7d ratio < 95%)"
echo "    - L4SelftestRecentFailure (last 30m)"
echo "    - Recording rules: l4_selftest_success_7d_ratio, l4_selftest_success_30d_ratio"

# 5. 검증 명령 제공
echo ""
echo "=== Verification Commands ==="
echo ""
echo "# Check timer status:"
echo "systemctl --user list-timers --all | grep l4-selftest"
echo ""
echo "# Check latest selftest result:"
echo "cat \${NODE_EXPORTER_TEXTFILE_DIR:-/tmp/test_textfile}/l4_selftest.pass.prom"
echo ""
echo "# View latest autotest log:"
echo "ls -1t /tmp/l4_autotest.*.log | head -1 | xargs tail -50"
echo ""
echo "# Run manual test:"
echo "bash ${WORK}/scripts/ops/l4_autotest.sh"
echo ""

echo "✅ L4 Selftest Setup Complete"
echo ""
echo "Next steps:"
echo "  1. Wait for tomorrow 09:12 KST for first automatic test"
echo "  2. Check Prometheus for l4_selftest_pass metrics"
echo "  3. Monitor 7-day success ratio via l4_selftest_success_7d_ratio"

