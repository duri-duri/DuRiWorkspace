#!/usr/bin/env bash
set -euo pipefail
TS="$(date +'%Y-%m-%d__%H%M')"
HOST="$(hostname | tr '[:space:]' '-')"
LEVEL="EXTENDED"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
DAY_DIR="${DEST_ROOT}/$(date +'%Y')/$(date +'%m')/$(date +'%d')"
WORK="/tmp/du_backup_${LEVEL}_${TS}"

mkdir -p "$DAY_DIR" "$WORK"

# 사전검증(읽기전용)
python3 - <<'PY'
import os,sys
assert os.path.exists("DuRiCore"); assert os.path.exists("configs")
print("PRECHECK_OK")
PY

# include 목록 - 실제 존재하는 파일만
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
EOF

# 선택적 파일들 (존재하는 경우만)
[ -f "docker-compose.yml" ] && echo "docker-compose.yml" >> "$INC"
[ -f "Dockerfile" ] && echo "Dockerfile" >> "$INC"
[ -f "requirements.txt" ] && echo "requirements.txt" >> "$INC"
[ -f "requirements-dev.txt" ] && echo "requirements-dev.txt" >> "$INC"
[ -f "pyproject.toml" ] && echo "pyproject.toml" >> "$INC"
[ -f "poetry.lock" ] && echo "poetry.lock" >> "$INC"
[ -f "README.md" ] && echo "README.md" >> "$INC"
[ -f "CHANGELOG.md" ] && echo "CHANGELOG.md" >> "$INC"
[ -f ".github/workflows" ] && echo ".github/workflows" >> "$INC"
[ -f ".pre-commit-config.yaml" ] && echo ".pre-commit-config.yaml" >> "$INC"
[ -f "BACKUP_INFO.md" ] && echo "BACKUP_INFO.md" >> "$INC"

# 존재하는 마크다운 파일들 추가
for md_file in *.md; do
    [ -f "$md_file" ] && echo "$md_file" >> "$INC"
done

# 존재하는 YAML/JSON 파일들 추가
for yaml_file in *.yaml *.yml *.json; do
    [ -f "$yaml_file" ] && echo "$yaml_file" >> "$INC"
done

# 제외 규칙
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
    "--exclude=models"
    "--exclude=artifacts"
    "--exclude=var"
)

PAY="${WORK}/payload.tar"
tar --sort=name --mtime='@0' --numeric-owner --owner=0 --group=0 \
    "${EXC[@]}" -cf "$PAY" -T "$INC"

OUT="${DAY_DIR}/${LEVEL}__${TS}__host-${HOST}.tar.zst"
zstd -19 --long=27 --threads=0 -q -o "$OUT" "$PAY"

pushd "$DAY_DIR" >/dev/null
sha256sum "$(basename "$OUT")" > "SHA256SUMS.${LEVEL}.${TS}.txt"
popd >/dev/null

# state.json 동기화 (아티팩트 경로 참조 추가)
python3 tools/generate_or_update_state.py \
  --workspace-root "/home/duri/DuRiWorkspace" \
  --state "/home/duri/DuRiWorkspace/learning_journal/state.json" \
  --backup-root "/mnt/c/Users/admin/Desktop/두리백업" \
  --backup-archive "$OUT" \
  --logical-prefix "ext_"

echo "[OK] ${LEVEL} 백업: $OUT"
