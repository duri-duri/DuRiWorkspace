#!/usr/bin/env bash
set -Eeuo pipefail
f="$1"
sha=$(sha256sum "$f" | awk '{print $1}')
size=$(stat -c%s "$f")
mt=$(stat -c%y "$f")
cat > "$f.prov" <<P
axis=tbd
gen_script=tbd
gen_time=$mt
inputs=tbd
sha256=$sha
size=$size
path=$(realpath "$f")
run_id=$(date '+%Y%m%d')_host-$(hostname)_$(date '+%H%M')
P
