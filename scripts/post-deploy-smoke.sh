#!/usr/bin/env bash
set -euo pipefail

ensure_promtool() {
  if command -v promtool >/dev/null 2>&1; then
    promtool --version
    return 0
  fi
  echo "[SMOKE] promtool not found; downloading..."
  set -euo pipefail
  TMP="${TMPDIR:-/tmp}/promtool.$$"
  mkdir -p "$TMP" && cd "$TMP"
  VER="${PROM_VERSION:-2.55.0}"
  base="https://github.com/prometheus/prometheus/releases/download/v${VER}"
  tarball="prometheus-${VER}.linux-amd64.tar.gz"
  curl -fsSLO "${base}/${tarball}"
  tar -xzf "${tarball}"
  chmod +x "prometheus-${VER}.linux-amd64/promtool"
  # 로컬 전용: PATH에 둔 임시 바이너리 사용
  export PATH="$PWD/prometheus-${VER}.linux-amd64:$PATH"
  promtool --version
}

retry() { local n=0; local max=${2:-3}; until "$1"; do n=$((n+1)); [ $n -ge $max ] && return 1; sleep 2; done; }

ensure_promtool
echo "[SMOKE] basic reachability checks (placeholder)"
exit 0
