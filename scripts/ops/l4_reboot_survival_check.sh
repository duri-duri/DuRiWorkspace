#!/usr/bin/env bash
# L4 Reboot Survival Check
# Purpose: 재부팅 후에도 타이머가 영속되는지 확인 및 설정
# Usage: bash scripts/ops/l4_reboot_survival_check.sh

set -euo pipefail

echo "=== L4 Reboot Survival Check ==="
echo ""

# 1. Linger 활성화 확인
echo "1. Checking linger status..."
if loginctl show-user "$USER" | grep -q "Linger=yes"; then
  echo "  ✅ Linger is enabled"
else
  echo "  ⚠️  Linger is disabled, enabling..."
  loginctl enable-linger "$USER"
  echo "  ✅ Linger enabled"
fi

# 2. 모든 타이머 활성화 확인
echo ""
echo "2. Checking timer persistence..."
timers=("l4-daily.timer" "l4-daily-quick.timer" "l4-shadow-replay.timer" "l4-weekly.timer" "l4-canonicalize.timer")

for timer in "${timers[@]}"; do
  if systemctl --user is-enabled "$timer" >/dev/null 2>&1; then
    echo "  ✅ $timer is enabled"
  else
    echo "  ⚠️  $timer is not enabled, enabling..."
    systemctl --user enable "$timer" || echo "  ❌ Failed to enable $timer"
  fi
done

# 3. 타이머 상태 확인
echo ""
echo "3. Timer status:"
systemctl --user list-timers --all | grep -E 'l4-(daily|weekly|shadow|canonicalize)' || echo "  No L4 timers found"

# 4. 환경 변수 확인
echo ""
echo "4. Checking environment variables..."
if systemctl --user show l4-weekly.service | grep -q "NODE_EXPORTER_TEXTFILE_DIR"; then
  echo "  ✅ NODE_EXPORTER_TEXTFILE_DIR is set"
else
  echo "  ⚠️  NODE_EXPORTER_TEXTFILE_DIR not found in service environment"
fi

# 5. 시계 동기화 확인
echo ""
echo "5. Checking clock synchronization..."
if command -v timedatectl >/dev/null 2>&1; then
  if timedatectl show | grep -q "NTPSynchronized=yes"; then
    echo "  ✅ NTP synchronized"
  else
    echo "  ⚠️  NTP not synchronized"
  fi
else
  echo "  ⚠️  timedatectl not available"
fi

echo ""
echo "=== Reboot Survival Check Complete ==="

