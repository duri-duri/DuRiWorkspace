#!/usr/bin/env bash
# Export timestamp metric for artifact
# Usage: export_timestamp <name>

export_timestamp() {
  local name="$1"
  local ts=$(date +%s)
  local textfile_dir="${NODE_EXPORTER_TEXTFILE_DIR:-${HOME}/.cache/node_exporter/textfile}"
  
  mkdir -p "$textfile_dir"
  echo "l4_${name}_ts $ts" > "$textfile_dir/l4_${name}_ts.prom"
  chmod 0644 "$textfile_dir/l4_${name}_ts.prom" 2>/dev/null || true
}
