#!/usr/bin/env bash
set -Eeuo pipefail
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SRC_DIR/../var/secrets/alerts.env" 2>/dev/null || true
MSG="${1:-[OPS] unspecified alert}"

# Slack
if [[ -n "${SLACK_WEBHOOK:-}" ]]; then
  curl -sS -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"${MSG//$'\n'/\\n}\"}" "$SLACK_WEBHOOK" >/dev/null || true
fi

# Telegram
if [[ -n "${TELEGRAM_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT_ID}" -d "text=${MSG}" >/dev/null || true
fi
