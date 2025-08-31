#!/usr/bin/env bash
set -euo pipefail
TS="$(date +'%Y-%m-%d__%H%M')"
HOST="$(hostname | tr '[:space:]' '-')"
LEVEL="FULL"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
DAY_DIR="${DEST_ROOT}/$(date +'%Y')/$(date +'%m')/$(date +'%d')"
WORK="/tmp/du_backup_${LEVEL}_${TS}"

mkdir -p "$DAY_DIR" "$WORK"

# include
INC="${WORK}/include.lst"
cat >"$INC" <<'EOF'
DuRiCore
duri_brain
duri_core
duri_common
core
tools
tests
configs
scripts
docs
docker-compose.yml
Dockerfile
requirements.txt
requirements-dev.txt
pyproject.toml
poetry.lock
README.md
CHANGELOG.md
.github/workflows
.pre-commit-config.yaml
*.md
*.yaml
*.yml
*.json
BACKUP_INFO.md
models
artifacts
var/checkpoints
var/prom_data
var/metadata
backup_repository
*.tar.gz
*.zst
EOF

EXC=(
    "--exclude=.git"
    "--exclude=__pycache__"
    "--exclude=*.pyc"
    "--exclude=.pytest_cache"
    "--exclude=.cache"
    "--exclude=node_modules"
    "--exclude=logs"
    "--exclude=temp_*"
    "--exclude=.DS_Store"
    "--exclude=var/tmp"
    "--exclude=var/run"
    "--exclude=var/cache"
    "--exclude=var/ephemeral_logs"
)

PAY="${WORK}/payload.tar"
tar --sort=name --mtime='@0' --numeric-owner --owner=0 --group=0 \
    "${EXC[@]}" -cf "$PAY" -T "$INC"

OUT="${DAY_DIR}/${LEVEL}__${TS}__host-${HOST}.tar.zst"
zstd -19 --long=27 --threads=0 -q -o "$OUT" "$PAY"

pushd "$DAY_DIR" >/dev/null
sha256sum "$(basename "$OUT")" > "SHA256SUMS.${LEVEL}.${TS}.txt"
popd >/dev/null

# state.json 동기화 (대형 아티팩트 참조)
python3 tools/generate_or_update_state.py \
  --workspace-root "/home/duri/DuRiWorkspace" \
  --state "/home/duri/DuRiWorkspace/learning_journal/state.json" \
  --backup-root "/mnt/c/Users/admin/Desktop/두리백업" \
  --backup-archive "$OUT" \
  --logical-prefix "full_"

echo "[OK] ${LEVEL} 백업: $OUT"
