#!/usr/bin/env bash
set -euo pipefail
echo "x x refs/heads/main x"    | scripts/hooks/pre-push origin url && { echo "main not blocked"; exit 1; }
echo "x x refs/heads/feature x" | scripts/hooks/pre-push origin url || { echo "feature blocked"; exit 1; }
: | scripts/hooks/pre-push origin url || { echo "EOF failed"; exit 1; }
echo "OK"
