#!/usr/bin/env bash
set -euo pipefail

check() {
  name=$1; port=$2
  echo "== ${name} =="
  curl -sI localhost:${port}/health | head -1 | grep "200 OK"
  curl -s  localhost:${port}/health | jq -c 'has("status") and .status=="ok"' | grep true
  curl -sI localhost:${port}/metrics | head -1 | grep "200 OK"
  echo
}

check "duri_control" 8083
check "duri_brain"   8081
echo "✔ all good"
