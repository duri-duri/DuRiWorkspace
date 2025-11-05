#!/usr/bin/env bash
# L4 Final Environment Fix - 완전 자동화를 위한 환경 변수 고정
# Purpose: 모든 서비스에 NODE_EXPORTER_TEXTFILE_DIR 자동 설정
# Usage: 한 번만 실행하면 됨 (자동화된 설정)

set -euo pipefail

NODE_EXPORTER_TEXTFILE_DIR="${NODE_EXPORTER_TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"

echo "=== L4 Final Environment Fix (One-time Setup) ==="
echo ""

# user-level systemd 기본 환경 설정
mkdir -p ~/.config/systemd/user.conf.d
cat > ~/.config/systemd/user.conf.d/textfile-env.conf <<'CONF'
[Manager]
DefaultEnvironment="NODE_EXPORTER_TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector"
DefaultEnvironment="TZ=UTC"
CONF

# 개별 서비스 drop-in (이미 있는 경우 덮어쓰기)
services=("l4-daily" "l4-daily-quick" "l4-shadow-replay" "l4-weekly" "l4-canonicalize")

for s in "${services[@]}"; do
  mkdir -p ~/.config/systemd/user/${s}.service.d
  cat > ~/.config/systemd/user/${s}.service.d/env.conf <<EOF
[Service]
Environment="NODE_EXPORTER_TEXTFILE_DIR=${NODE_EXPORTER_TEXTFILE_DIR}"
Environment="TZ=UTC"
EOF
  echo "  ✅ ${s}.service environment configured"
done

systemctl --user daemon-reload
echo ""
echo "✅ Environment configuration complete"
echo ""
echo "Verification:"
for s in "${services[@]}"; do
  env=$(systemctl --user show "${s}.service" | grep -E '^Environment=' | head -1 || echo "not found")
  echo "  ${s}: ${env}"
done

