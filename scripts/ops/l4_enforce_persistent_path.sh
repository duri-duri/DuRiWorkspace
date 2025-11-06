#!/usr/bin/env bash
# L4 Environment Path Enforcer - 영속 경로 강제 적용
# Purpose: 모든 L4 서비스에 영속 경로를 일괄 적용하고 검증
# Usage: 한 번만 실행 (자동화된 경로 통일)

set -euo pipefail

PERSISTENT_PATH="${HOME}/.cache/node_exporter/textfile"

echo "=== L4 Environment Path Enforcer ==="
echo "Target path: ${PERSISTENT_PATH}"
echo ""

# 1. Create persistent directory
mkdir -p "${PERSISTENT_PATH}"
chmod 0755 "${PERSISTENT_PATH}"
chown "$(whoami):$(whoami)" "${PERSISTENT_PATH}" 2>/dev/null || true
echo "✅ Created persistent directory: ${PERSISTENT_PATH}"

# 2. Update user-level systemd default environment
mkdir -p ~/.config/systemd/user.conf.d
cat > ~/.config/systemd/user.conf.d/textfile-env.conf <<CONF
[Manager]
DefaultEnvironment="NODE_EXPORTER_TEXTFILE_DIR=${PERSISTENT_PATH}"
DefaultEnvironment="TZ=UTC"
CONF
echo "✅ Updated user systemd default environment"

# 3. Update all L4 service drop-ins
services=("l4-daily" "l4-daily-quick" "l4-shadow-replay" "l4-weekly" "l4-canonicalize" "l4-selftest" "l4-bootstrap" "l4-recovery")

for s in "${services[@]}"; do
  mkdir -p ~/.config/systemd/user/${s}.service.d
  cat > ~/.config/systemd/user/${s}.service.d/env.conf <<EOF
[Service]
Environment="NODE_EXPORTER_TEXTFILE_DIR=${PERSISTENT_PATH}"
Environment="TZ=UTC"
EOF
  echo "  ✅ ${s}.service environment configured"
done

# 4. Reload and restart
systemctl --user daemon-reload
echo "✅ Daemon reloaded"

# 5. Verify all services
echo ""
echo "=== Verification ==="
for s in "${services[@]}"; do
  env=$(systemctl --user show "${s}.service" 2>/dev/null | grep '^Environment=' | grep NODE_EXPORTER_TEXTFILE_DIR | head -1 || echo "not found")
  if echo "$env" | grep -q "${PERSISTENT_PATH}"; then
    echo "  ✅ ${s}: ${env}"
  else
    echo "  ⚠️  ${s}: ${env}"
  fi
done

echo ""
echo "✅ Environment path enforcement complete"
echo ""
echo "Next steps:"
echo "  1. Restart services: systemctl --user restart l4-*.service"
echo "  2. Verify: bash scripts/ops/l4_autotest.sh"

