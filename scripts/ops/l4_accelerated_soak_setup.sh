#!/usr/bin/env bash
# L4 Accelerated Soak Test Setup
# Purpose: 이벤트 밀도 가속을 위한 타이머 오버레이 (스테이징/검증용)
# Usage: bash scripts/ops/l4_accelerated_soak_setup.sh [enable|disable]

set -euo pipefail

MODE="${1:-enable}"

if [[ "$MODE" == "enable" ]]; then
  echo "=== Enabling L4 Accelerated Soak Test Mode ==="
  echo "Warning: This will change timer intervals for testing purposes"
  echo ""
  
  # 타이머 오버레이 드롭인 생성
  mkdir -p ~/.config/systemd/user/l4-daily.service.d
  mkdir -p ~/.config/systemd/user/l4-daily-quick.service.d
  mkdir -p ~/.config/systemd/user/l4-shadow-replay.service.d
  
  cat > ~/.config/systemd/user/l4-daily.service.d/accelerated.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/bin/bash -lc 'cd /home/duri/DuRiWorkspace && timeout 900 bash scripts/ops/l4_daily_runner.sh'
EOF
  
  cat > ~/.config/systemd/user/l4-daily-quick.service.d/accelerated.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/bin/bash -lc 'cd /home/duri/DuRiWorkspace && timeout 600 bash scripts/ops/l4_daily_quick_check.sh'
EOF
  
  # 타이머 간격 변경 (테스트용)
  systemctl --user edit l4-daily.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*:0/15
EOF
  
  systemctl --user edit l4-daily-quick.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*:0/10
EOF
  
  systemctl --user edit l4-shadow-replay.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*:0/5
EOF
  
  systemctl --user daemon-reload
  systemctl --user restart l4-daily.timer l4-daily-quick.timer l4-shadow-replay.timer
  
  echo "✅ Accelerated soak test mode enabled"
  echo "  - l4-daily: every 15 minutes"
  echo "  - l4-daily-quick: every 10 minutes"
  echo "  - l4-shadow-replay: every 5 minutes"
  
elif [[ "$MODE" == "disable" ]]; then
  echo "=== Disabling L4 Accelerated Soak Test Mode ==="
  
  rm -f ~/.config/systemd/user/l4-daily.service.d/accelerated.conf
  rm -f ~/.config/systemd/user/l4-daily-quick.service.d/accelerated.conf
  rm -f ~/.config/systemd/user/l4-shadow-replay.service.d/accelerated.conf
  
  # 원래 타이머 설정 복원
  systemctl --user edit l4-daily.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*-*-* 09:11
EOF
  
  systemctl --user edit l4-daily-quick.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*-*-* 09:10
EOF
  
  systemctl --user edit l4-shadow-replay.timer <<'EOF' || true
[Timer]
OnCalendar=
OnCalendar=*-*-* 09:30,21:30
EOF
  
  systemctl --user daemon-reload
  systemctl --user restart l4-daily.timer l4-daily-quick.timer l4-shadow-replay.timer
  
  echo "✅ Accelerated soak test mode disabled"
  echo "  - Timers restored to normal schedule"
else
  echo "Usage: $0 [enable|disable]"
  exit 1
fi

