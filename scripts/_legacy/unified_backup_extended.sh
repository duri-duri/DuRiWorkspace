#!/usr/bin/env bash
set -euo pipefail

# ========= 기본 메타 =========
WS_ROOT="${WS_ROOT:-$PWD}"
HOST_ID="$(hostname -s || echo host)"
KST_NOW="$(TZ=Asia/Seoul date +'%Y-%m-%d__%H%M')"
Y=$(date +%Y) ; M=$(date +%m) ; D=$(date +%d)
DEST_ROOT="${DEST_ROOT:-/mnt/c/Users/admin/Desktop/두리백업/${Y}/${M}/${D}}"

# --- [패치1] 동시 실행 차단 + 프리플라이트 ---
LEVEL="EXTENDED"
LOCK="/tmp/duri-backup.${LEVEL}.lock"
exec 9>"$LOCK"
flock -n 9 || { echo "⏳ $LEVEL already running"; exit 0; }

# 최소 여유 공간(GB) – EXTENDED는 5GB 권장
REQUIRED_GB="${REQUIRED_GB:-5}"
FREE_GB=$(df -P "$DEST_ROOT" 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
[[ ${FREE_GB:-0} -lt $REQUIRED_GB ]] && { echo "❌ not enough space: need ${REQUIRED_GB}GB, have ${FREE_GB}GB"; exit 3; }

mkdir -p "${DEST_ROOT}"

ARCH_BASENAME="EXTENDED__$(date +%F)__$(date +%H%M)__host-${HOST_ID}.tar"
ARCH_ZST="${DEST_ROOT}/${ARCH_BASENAME}.zst"
ARCH_GZ="${DEST_ROOT}/${ARCH_BASENAME}.gz"

STATE_DIR="${WS_ROOT}/var/state"
mkdir -p "${STATE_DIR}"

have() { command -v "$1" >/dev/null 2>&1; }

# 존재하는 경로만 반영
add_if_exists() {
  local p="$1"
  shopt -s nullglob dotglob
  local matches=(${p})
  shopt -u nullglob dotglob
  ((${#matches[@]})) && printf '%s\n' "${matches[@]}"
}

# ========= DuRi 전용 화이트리스트 =========
# - 목적: 코드/스크립트/설정/문서/테스트 중심
# - DuRiCore 하위는 '소스만' 포함, 산출물/스냅샷/백업 제외
mapfile -t INCLUDE <<'EOF'
# 리포 루트 메타
./.editorconfig
./.gitattributes
./.gitmodules
./.env
./pytest.ini
./*.md
./LICENSE*
./README*
./docker-compose*.yml

# 최상위 코드/도구/설정/문서
./scripts/**/*
./tools/**/*
./configs/**/*
./schemas/**/*
./docs/**/*
./utils/**/*
./cursor_*/**/*

# 핵심 소스
./DuRiCore/**/*.py
./DuRiCore/**/*.json
./DuRiCore/**/*.yaml
./DuRiCore/**/*.yml
./DuRiCore/**/*.md
./DuRiCore/**/*.toml
./DuRiCore/**/*.ini
./DuRiCore/**/*.sh

# 선택적: 가벼운 데이터/샘플만
./DuRiCore/**/test_data*.csv
./DuRiCore/**/sample*.csv

# 레지스트리/상태: 현재 포인터만
./DuRiCore/modules/ml_integration/registry/current.json
./DuRiCore/modules/ml_integration/registry/version.txt

# 테스트
./tests/**/*
./DuRiCore/**/tests/**/*
./DuRiCore/test_*.py
EOF

# ========= DuRi 전용 블랙리스트(강제 제외) =========
# - 목적: 산출물/캐시/대용량 불변물/민감 로컬 상태 제거
mapfile -t EXCLUDE <<'EOF'
--exclude-vcs
--exclude=.git
--exclude=.venv
--exclude=**/.venv/**
--exclude=**/__pycache__/**
--exclude=**/.pytest_cache/**
--exclude=**/.mypy_cache/**
--exclude=**/.ruff_cache/**
--exclude=**/.ipynb_checkpoints/**
--exclude=**/.DS_Store
--exclude=**/*.pyc
--exclude=**/*.pyo

# 로그/임시/캐시/가공물
--exclude=logs/**
--exclude=**/logs/**
--exclude=tmp/**
--exclude=/tmp/**
--exclude=**/var/**
--exclude=**/cache/**

# 대용량 모델/체크포인트/임베딩
--exclude=**/models/**
--exclude=**/checkpoints/**
--exclude=**/embeddings/**
--exclude=**/vectorstore/**

# 빌드/배포 산출물
--exclude=**/dist/**
--exclude=**/build/**
--exclude=**/.tox/**

# 압축/아카이브 류(중복 백업 방지)
--exclude=**/*.zip
--exclude=**/*.7z
--exclude=**/*.xz
--exclude=**/*.zst
--exclude=**/*.tar
--exclude=**/*.tar.gz
--exclude=**/*.tar.zst
--exclude=**/*.tgz

# 바이너리/대용량 파일 형식
--exclude=**/*.pkl
--exclude=**/*.pt
--exclude=**/*.onnx
--exclude=**/*.so
--exclude=**/*.dll
--exclude=**/*.bin
--exclude=**/*.npy
--exclude=**/*.npz
--exclude=**/*.parquet
--exclude=**/*.db
--exclude=**/*.sqlite*
--exclude=**/*.h5
--exclude=**/*.ckpt

# DuRiCore 내 산출물/스냅샷/백업/리포트 (정책적으로 제외)
--exclude=DuRiCore/**/artifacts*/**
--exclude=DuRiCore/**/backups/**
--exclude=DuRiCore/**/backup_/**
--exclude=DuRiCore/**/phase*_test_results*.json
--exclude=DuRiCore/**/test_results_*.json
--exclude=DuRiCore/**/league*.{json,jsonl,csv,md}
--exclude=DuRiCore/**/snapshot_*.json
--exclude=DuRiCore/**/frozen/**
--exclude=DuRiCore/**/final_model.pkl
--exclude=DuRiCore/**/final_metrics*.json
--exclude=DuRiCore/**/performance_data_*.json
--exclude=DuRiCore/**/phase*_report*.json
--exclude=DuRiCore/**/promote_*.log
--exclude=DuRiCore/**/repro_/**
--exclude=DuRiCore/**/run_*.log

# 제품 배포물(Prod) 쪽 대용량
--exclude=DuRiCore/**/artifacts_prod/**
--exclude=DuRiCore/**/stable/**
--exclude=DuRiCore/**/latest

# 외부 런타임/환경 파일 (복원시 재생성)
--exclude=**/.env.local
--exclude=**/.envrc
--exclude=**/.python-version
--exclude=**/poetry.lock
--exclude=**/Pipfile.lock
EOF

# ========= 실제 존재 항목만 수집 =========
tmp_list="$(mktemp)"
pushd "${WS_ROOT}" >/dev/null
for pat in "${INCLUDE[@]}"; do
  add_if_exists "${pat}"
done | sed 's|^\./||' | sort -u > "${tmp_list}"
popd >/dev/null

# --- [패치5] 파일리스트 보존(결정성 증거물) ---
cp -f "${tmp_list}" "${DEST_ROOT}/filelist.${LEVEL}.${KST_NOW}.txt" 2>/dev/null || true

if [[ ! -s "${tmp_list}" ]]; then
  echo "⚠️  포함할 파일이 없습니다. 종료합니다." >&2
  exit 2
fi

# ========= 결정적 tar 옵션 =========
TAR_COMMON=( --ignore-failed-read
  --sort=name
  --mtime='@0'
  --owner=0 --group=0 --numeric-owner
  --mode='u+rwX,go+rX,go-w'
  "${EXCLUDE[@]}"
  -C "${WS_ROOT}"
  -T "${tmp_list}"
)

# ========= 압축: zstd 우선, 실패 시 gzip =========
echo "▶ EXTENDED(DuRi) 백업 생성 중..."

# --- [패치2] 해시리스트 생성 (EXTENDED는 권장) ---
if command -v sha256sum >/dev/null 2>&1; then
  HASHLIST="${DEST_ROOT}/HASHLIST.${LEVEL}.${KST_NOW}.txt"
  # 주요 폴더만 선택
  find DuRiCore scripts tools configs docs -type f -print0 2>/dev/null \
    | xargs -0 sha256sum > "${HASHLIST}" || true
fi

# 원자적 산출물 작성
TMP_ZST="${ARCH_ZST}.partial"
TMP_GZ="${ARCH_GZ}.partial"

if have zstd; then
  if tar -cf - "${TAR_COMMON[@]}" | zstd -q -19 -T0 -o "${TMP_ZST}"; then
    sync; mv "${TMP_ZST}" "${ARCH_ZST}"
    ARCHIVE="${ARCH_ZST}"
  else
    echo "zstd 압축 실패, gzip 폴백..."
    tar -cf - "${TAR_COMMON[@]}" | gzip -9 > "${TMP_GZ}"
    sync; mv "${TMP_GZ}" "${ARCH_GZ}"
    ARCHIVE="${ARCH_GZ}"
  fi
else
  tar -cf - "${TAR_COMMON[@]}" | gzip -9 > "${TMP_GZ}"
  sync; mv "${TMP_GZ}" "${ARCH_GZ}"
  ARCHIVE="${ARCH_GZ}"
fi

# --- [패치3] 불변 보관 ---
chmod a-w "$ARCHIVE" 2>/dev/null || true

# --- [패치4] 알림 ---
notify(){
  local msg="$1"; command -v curl >/dev/null 2>&1 || return 0
  [[ -n "${NTFY_TOPIC:-}" ]] || return 0
  curl -s -H "Title: DuRi Backup ${LEVEL}" -d "$msg" "https://ntfy.sh/${NTFY_TOPIC}" >/dev/null || true
}
notify "OK $(basename "$ARCHIVE") size=$(du -h "$ARCHIVE" | awk '{print $1}') host=${HOST_ID} at=${KST_NOW}"

# ========= 무결성 & 매니페스트 =========
SHA_FILE="${DEST_ROOT}/SHA256SUMS.EXTENDED.$(date +%F__%H%M).txt"
MANIFEST="${DEST_ROOT}/manifest.extended.json"

sha256sum "$(basename "${ARCHIVE}")" > "${SHA_FILE}" --tag || sha256sum "${ARCHIVE}" > "${SHA_FILE}"

cat > "${MANIFEST}" <<JSON
{
  "profile": "DuRi-EXTENDED",
  "level": "EXTENDED",
  "created_at_kst": "${KST_NOW}",
  "host": "${HOST_ID}",
  "workspace_root": "${WS_ROOT}",
  "archive": "$(basename "${ARCHIVE}")",
  "archive_full_path": "${ARCHIVE}",
  "sha256_file": "$(basename "${SHA_FILE}")",
  "entry_count": $(wc -l < "${tmp_list}"),
  "compression": "$(echo "${ARCHIVE}" | grep -o '\.zst\|\.gz$' | sed 's/^\.//')"
}
JSON

# state 갱신(있으면 갱신)
if [[ -f "${STATE_DIR}/backup_refs.json" ]]; then
  jq --arg a "${ARCHIVE}" --arg t "${KST_NOW}" --arg l "EXTENDED" \
     '.history += [{"level":$l,"time_kst":$t,"archive":$a,"profile":"DuRi-EXTENDED"}] | .last_extended=$a' \
     "${STATE_DIR}/backup_refs.json" \
     > "${STATE_DIR}/backup_refs.json.tmp" 2>/dev/null \
  && mv "${STATE_DIR}/backup_refs.json.tmp" "${STATE_DIR}/backup_refs.json" || true
fi

echo "✅ EXTENDED(DuRi) 백업 완료: ${ARCHIVE}"
echo "   - SHA256: ${SHA_FILE}"
echo "   - Manifest: ${MANIFEST}"
echo "   - 포함 항목 수: $(wc -l < "${tmp_list}")"

rm -f "${tmp_list}"
