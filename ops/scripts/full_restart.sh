#!/bin/bash
set -euo pipefail

echo "=== Docker System Full Restart ==="
echo "Timestamp: $(date -Iseconds)"

# 1. Stop all containers
echo "• Stopping Docker system..."
docker compose -f docker-compose.yml -f compose.health.overlay.yml down

# 2. Wait a moment
sleep 2

# 3. Start all services
echo "• Starting Docker system..."
~/DuRiWorkspace/ops/scripts/one_shot_start.sh

# 4. Health check
echo "• Running health check..."
~/DuRiWorkspace/ops/scripts/check_health.sh

echo "=== Full Restart Complete ==="
