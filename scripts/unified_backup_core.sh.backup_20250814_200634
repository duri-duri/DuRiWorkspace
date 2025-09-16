#!/usr/bin/env bash
set -euo pipefail
TS="$(date +'%Y-%m-%d__%H%M')"
HOST="$(hostname | tr '[:space:]' '-')"
LEVEL="CORE"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
DAY_DIR="${DEST_ROOT}/$(date +'%Y')/$(date +'%m')/$(date +'%d')"
WORK="/tmp/du_backup_${LEVEL}_${TS}"

mkdir -p "$DAY_DIR" "$WORK"

# 0) 사전 품질 체크 (코드 품질 저하 방지: read-only 검증)
python3 - <<'PY'
import os,sys,glob,json,subprocess
def must_exist(paths):
    miss=[p for p in paths if not os.path.exists(p)]
    if miss:
        print("MISSING:",miss); sys.exit(2)
must_exist(["DuRiCore","tests","configs"])
# 핵심 파이썬 파일 수
files=[p for p in glob.glob("**/*.py", recursive=True) if "__pycache__" not in p]
assert len(files)>200, "파이썬 파일 수 비정상적으로 적음"
print("PRECHECK_OK")
PY

# 1) GIT 스냅샷 (bundle + archive)
REPO_ROOT="$(pwd)"
BUNDLE="${WORK}/git.bundle"
ARCHIVE="${WORK}/git_worktree.tar"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Git repo 아님"; exit 1; }
git fetch --all --tags -q || true
git bundle create "$BUNDLE" --all
git archive --format=tar --output="$ARCHIVE" HEAD

# 2) 비Git 자산 수집 (CORE 레벨) - 존재하는 파일만
INCLUDE_LIST="${WORK}/include.lst"
touch "$INCLUDE_LIST"

# 공통(CORE) - 실제 존재하는 파일만
cat >>"$INCLUDE_LIST" <<'EOF'
DuRiCore
duri_brain
duri_core
duri_common
core
tools
tests
configs
.github/workflows
EOF

# 선택적 파일들 (존재하는 경우만)
[ -f "README.md" ] && echo "README.md" >> "$INCLUDE_LIST"
[ -f "CHANGELOG.md" ] && echo "CHANGELOG.md" >> "$INCLUDE_LIST"
[ -f "BACKUP_INFO.md" ] && echo "BACKUP_INFO.md" >> "$INCLUDE_LIST"
[ -f "requirements.txt" ] && echo "requirements.txt" >> "$INCLUDE_LIST"
[ -f "requirements-dev.txt" ] && echo "requirements-dev.txt" >> "$INCLUDE_LIST"
[ -f "pyproject.toml" ] && echo "pyproject.toml" >> "$INCLUDE_LIST"
[ -f "poetry.lock" ] && echo "poetry.lock" >> "$INCLUDE_LIST"
[ -f ".pre-commit-config.yaml" ] && echo ".pre-commit-config.yaml" >> "$INCLUDE_LIST"

# 3) tar 입력을 find+filter로 생성 (결정적 옵션)
PAYLOAD_TAR="${WORK}/payload.tar"

# 제외 규칙
EXCLUDES=(
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

# include.lst 기준만 담기
tar --sort=name --mtime='@0' --numeric-owner --owner=0 --group=0 "${EXCLUDES[@]}" -cf "$PAYLOAD_TAR" -T "$INCLUDE_LIST"

# 4) 아카이브 합성: [git.bundle][git_worktree.tar][payload.tar]
COMBINED_TAR="${WORK}/combined_${LEVEL}.tar"
tar --sort=name --mtime='@0' --numeric-owner --owner=0 --group=0 -cf "$COMBINED_TAR" -C "$WORK" "$(basename "$BUNDLE")" "$(basename "$ARCHIVE")" "$(basename "$PAYLOAD_TAR")"

# 5) 압축 (zstd, 재현모드)
ZSTD_OUT="${DAY_DIR}/${LEVEL}__${TS}__host-${HOST}.tar.zst"
zstd -19 --long=27 --threads=0 -q -o "$ZSTD_OUT" "$COMBINED_TAR"

# 6) 매니페스트 & 해시
pushd "$DAY_DIR" >/dev/null
sha256sum "$(basename "$ZSTD_OUT")" > "SHA256SUMS.${LEVEL}.${TS}.txt"
python3 - <<'PY'
import os,json,subprocess,sys,glob
tarz=[p for p in glob.glob("*.tar.zst")]
info=[]
for f in tarz:
    sz=os.path.getsize(f)
    sha=open(f"SHA256SUMS.{f.split('__')[0]}.{ '__'.join(f.split('__')[1:]).split('.tar.zst')[0] }.txt").read().split()[0] if os.path.exists(f"SHA256SUMS.{f.split('__')[0]}.{ '__'.join(f.split('__')[1:]).split('.tar.zst')[0] }.txt") else ""
    info.append({"file":f,"bytes":sz,"sha256":sha})
open("manifest.json","w").write(json.dumps({"files":info},indent=2,ensure_ascii=False))
print("MANIFEST_OK")
PY
popd >/dev/null

# 7) 사후 검증(간이 복원 테스트)
TESTDIR="${WORK}/restore_test"
mkdir -p "$TESTDIR"
zstd -dq -c "$ZSTD_OUT" | tar -xf - -C "$TESTDIR"
test -f "$TESTDIR/git.bundle" || { echo "복원검증 실패: bundle 없음"; exit 3; }
tar -tf "$ZSTD_OUT" >/dev/null || { echo "아카이브 손상"; exit 3; }

# 8) state.json 자동 갱신 (CORE도 코드/메타 중심이라 영향 無)
python3 tools/generate_or_update_state.py \
  --workspace-root "/home/duri/DuRiWorkspace" \
  --state "/home/duri/DuRiWorkspace/learning_journal/state.json" \
  --backup-root "/mnt/c/Users/admin/Desktop/두리백업" \
  --backup-archive "$ZSTD_OUT" \
  --logical-prefix "core_"

echo "[OK] ${LEVEL} 백업 완료 -> $ZSTD_OUT"
