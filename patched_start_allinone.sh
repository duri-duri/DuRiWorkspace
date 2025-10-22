#!/usr/bin/env bash
set -euo pipefail

# Defensive startup wrapper for DuRi allinone
# - synthesize /app/.env from environment if missing
# - load docker secret into POSTGRES_PASSWORD if present
# - then exec original start logic (if present)

# If a real start_allinone.sh exists in image, we'll preserve the name and exec it at the end.
ORIG="/app/start_allinone.orig.sh"

# If original file is not present, expect this script to perform starting itself.
# Load secrets first (if any)
if [ -f /run/secrets/db_password ] && [ -z "${POSTGRES_PASSWORD:-}" ]; then
  export POSTGRES_PASSWORD="$(cat /run/secrets/db_password)"
fi

# If /app/.env missing, synthesize a minimal .env from current environment
if [ ! -f /app/.env ]; then
  echo "Info: /app/.env not found -> creating /app/.env from environment (synthesized)."
  {
    # list variables we commonly need; adapt if you have extras
    [ -n "${PORT:-}" ] && echo "PORT=${PORT}"
    [ -n "${PYTHONPATH:-}" ] && echo "PYTHONPATH=${PYTHONPATH}"
    [ -n "${DB_NAME:-}" ] && echo "DB_NAME=${DB_NAME}"
    [ -n "${POSTGRES_USER:-}" ] && echo "POSTGRES_USER=${POSTGRES_USER}"
    # prefer explicit password env if present (dangerous in git - but this is runtime)
    if [ -n "${POSTGRES_PASSWORD:-}" ]; then
      echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}"
    fi
    [ -n "${DATABASE_URL:-}" ] && echo "DATABASE_URL=${DATABASE_URL}"
    [ -n "${REDIS_URL:-}" ] && echo "REDIS_URL=${REDIS_URL}"
    [ -n "${DB_HOST:-}" ] && echo "DB_HOST=${DB_HOST}"
    [ -n "${DB_PORT:-}" ] && echo "DB_PORT=${DB_PORT}"
    [ -n "${REDIS_HOST:-}" ] && echo "REDIS_HOST=${REDIS_HOST}"
    [ -n "${REDIS_PORT:-}" ] && echo "REDIS_PORT=${REDIS_PORT}"
    # Add any other envvars your app strictly needs here...
  } > /tmp/.env.synth || true
  # move into place if created
  if [ -s /tmp/.env.synth ]; then
    mv /tmp/.env.synth /app/.env || cp /tmp/.env.synth /app/.env || true
    chmod 0640 /app/.env || true
  fi
fi

# Source /app/.env into current environment if readable (so older start script which sources will find values)
if [ -r /app/.env ]; then
  set -o allexport
  # shellcheck disable=SC1091
  source /app/.env 2>/dev/null || true
  set +o allexport
fi

# If the original start file exists at /app/start_allinone.sh and it's not this wrapper,
# rename it to preserve and exec it (so behavior remains identical)
if [ -f /app/start_allinone.sh ] && [ "$(readlink -f /app/start_allinone.sh)" != "$(readlink -f /app/start_allinone.orig.sh 2>/dev/null || true)" ]; then
  # try to avoid clobbering our patched file if it's already mounted — only move if different
  if [ -f /app/start_allinone.sh ] && ! grep -q "Defensive startup wrapper" /app/start_allinone.sh 2>/dev/null; then
    mv /app/start_allinone.sh "$ORIG" 2>/dev/null || true
    # if original exists, exec it
    if [ -x "$ORIG" ]; then
      exec "$ORIG" "$@"
    fi
  fi
fi

# If no original to exec, try to run supervisor/start command if present (fallback)
if command -v supervisord >/dev/null 2>&1; then
OLD_PYTHONPATH="${PYTHONPATH:-}"
unset PYTHONPATH
  exec supervisord -n
fi

# Last fallback: print environment and sleep so docker healthcheck can catch failures rather than crash-looping.
echo "No original start found; environment:"
env | sort
sleep 86400
