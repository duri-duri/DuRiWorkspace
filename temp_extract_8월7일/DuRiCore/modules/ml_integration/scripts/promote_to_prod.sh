#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-artifacts_phase1/frozen/current_freeze.json}"
REG="registry"
mkdir -p "$REG"

SHA=$(jq -r '.meta.sha256' "$SRC")
VER=$(date +%Y%m%d_%H%M%S)

cp -f "$SRC" "$REG/model_${VER}.json"
ln -sfn "model_${VER}.json" "$REG/current.json"

cat > "$REG/version.txt" <<EOF
version: ${VER}
sha256: ${SHA}
source: ${SRC}
promoted_at: $(date -Is)
EOF

echo "✅ Promoted to prod"
echo " - $REG/current.json"
cat "$REG/version.txt"

