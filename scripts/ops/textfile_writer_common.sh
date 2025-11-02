#!/usr/bin/env bash
# Common header for all textfile metric writers
# Observability Contract v1: atomic write + permission standardization

set -euo pipefail

# Standard umask for textfile metrics (readable by node-exporter)
umask 022

# Default textfile directory
TEXTFILE_DIR="${TEXTFILE_DIR:-.reports/synth}"

# Ensure directory exists
mkdir -p "$TEXTFILE_DIR"

# Atomic write helper
atomic_write_textfile() {
    local output_file="$1"
    local content="$2"
    
    # Create temporary file in same directory (ensures same filesystem)
    local tmp_file
    tmp_file="$(mktemp "$TEXTFILE_DIR/.tmp.XXXXXX")"
    
    # Write content to temp file
    printf '%s\n' "$content" > "$tmp_file"
    
    # Atomic move (mv is atomic on same filesystem)
    mv "$tmp_file" "$output_file"
    
    # Ensure readable
    chmod 644 "$output_file"
}

