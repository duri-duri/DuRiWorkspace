#!/usr/bin/env bash
set -euo pipefail
AM_CONTAINER="${ALERTMANAGER_CONTAINER:-alertmanager}"
WEBHOOK_FILE="${WEBHOOK_FILE:-ops/observability/slack_webhook_url}"

echo "ALERTMANAGER_CONTAINER=${AM_CONTAINER}"
echo "WEBHOOK_FILE=${WEBHOOK_FILE}"

echo "---- verify-container ----"
command -v docker >/dev/null || { echo "❌ docker not found"; exit 1; }
docker ps --format '{{.Names}}' | sed 's/^/running: /'
docker ps --format '{{.Names}}' | grep -qx "${AM_CONTAINER}" \
  && echo "✅ container '${AM_CONTAINER}' is running" \
  || { echo "❌ container '${AM_CONTAINER}' not running"; exit 1; }
docker exec "${AM_CONTAINER}" sh -lc 'amtool --version || true'

echo "---- verify-perms ----"
[[ -f "${WEBHOOK_FILE}" ]] || { echo "❌ ${WEBHOOK_FILE} missing"; exit 1; }
perm="$(stat -c '%a' "${WEBHOOK_FILE}" 2>/dev/null || stat -f '%Lp' "${WEBHOOK_FILE}" 2>/dev/null || echo 000)"
echo "path=${WEBHOOK_FILE} perm=${perm}"
docker exec "${AM_CONTAINER}" sh -lc "test -r /etc/alertmanager/secrets/slack_webhook_url && echo '✅ readable in container' || { echo '❌ not readable in container'; exit 1; }"

echo "---- verify-webhook ----"
if head -c 10 "${WEBHOOK_FILE}" >/dev/null 2>&1; then
  grep -q 'YOUR/SLACK/WEBHOOK' "${WEBHOOK_FILE}" \
    && { echo "🔴 placeholder webhook (replace required)"; exit 2; } \
    || echo "🟢 not a placeholder (light check)"
else
  echo "ℹ️ host can't read (secure mode) — skipping placeholder check"
fi

echo "✅ diag complete (no changes applied)"
