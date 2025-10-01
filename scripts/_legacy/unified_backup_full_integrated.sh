#!/usr/bin/env bash
set -euo pipefail

# === 설정 ===
WORKSPACE="/home/duri/DuRiWorkspace"
DEST_ROOT="/mnt/c/Users/admin/Desktop/두리백업"
STAMP="$(date +'%Y-%m-%d__%H%M')"
DATE_DIR="$(date +'%Y')/$(date +'%m')/$(date +'%d')"
OUT_DIR="${DEST_ROOT}/${DATE_DIR}"
HOSTN="$(hostname | tr '[:space:]' '-')"

# 임시 디렉토리 (ext4에서 먼저 작업)
TMP_ROOT="/tmp/duri_full_backup_${STAMP}"
mkdir -p "$TMP_ROOT" "$OUT_DIR"

# 출력 파일
OUT="${OUT_DIR}/FULL__${STAMP}__host-${HOSTN}.tar.zst"
TMP="${TMP_ROOT}/FULL__${STAMP}__host-${HOSTN}.tar.zst.partial"

# 메타데이터 파일
FILELIST_TMP="${TMP_ROOT}/filelist.FULL.${STAMP}.txt.partial"
HASHLIST_TMP="${TMP_ROOT}/HASHLIST.FULL.${STAMP}.txt.partial"
MANIFEST_TMP="${TMP_ROOT}/manifest.FULL.${STAMP}.json.partial"

echo "=== FULL 백업 시작 ==="
echo "📁 작업공간: $WORKSPACE"
echo "📂 출력 디렉토리: $OUT_DIR"
echo "📄 출력 파일: $(basename "$OUT")"
echo "🔄 임시 디렉토리: $TMP_ROOT"

# === 총량 계산 (진행상황 표시용) ===
echo "📊 총량 계산 중..."
TOTAL_FILES="$(find "$WORKSPACE" -xdev -type f -print0 | awk -v RS='\0' 'END{print NR}')"
TOTAL_BYTES="$(du -sb --apparent-size "$WORKSPACE" | awk '{print $1}')"

echo "📈 백업 대상:"
echo "   - 총 파일 수: $TOTAL_FILES"
echo "   - 총 크기: $(numfmt --to=iec $TOTAL_BYTES) (${TOTAL_BYTES} bytes)"

# === 시그널 핸들러 ===
cleanup() {
  echo "🧹 정리 중..."
  rm -rf "$TMP_ROOT"
  echo "✅ 정리 완료"
}
trap cleanup INT TERM EXIT

# === 메타데이터 생성 ===
echo "📝 메타데이터 생성 중..."
(
  cd "$WORKSPACE"

  # 파일 목록 생성
  echo "   - 파일 목록 생성..."
  find . -xdev -type f -print0 | tr '\0' '\n' > "$FILELIST_TMP"

  # 해시 목록 생성
  echo "   - 해시 목록 생성..."
  find . -xdev -type f -print0 | xargs -0 -I{} sha256sum "{}" > "$HASHLIST_TMP"

  # 매니페스트 생성
  echo "   - 매니페스트 생성..."
  cat > "$MANIFEST_TMP" <<EOF
{
  "backup_type": "FULL",
  "timestamp": "$(date -Iseconds)",
  "hostname": "$HOSTN",
  "workspace": "$WORKSPACE",
  "total_files": $TOTAL_FILES,
  "total_bytes": $TOTAL_BYTES,
  "compression": "zstd",
  "compression_level": 15,
  "excluded_patterns": [
    ".git", "__pycache__", ".pytest_cache", ".cache",
    "node_modules", "logs", "temp_*", "var/tmp", "var/run", "var/cache"
  ],
  "included_directories": [
    "DuRiCore", "duri_brain", "duri_core", "duri_common", "core",
    "tools", "tests", "configs", "scripts", "docs", "models", "var", "learning_journal",
    "backup", "backup_repository", "duri_snapshots", "cursor_extension",
    "duri_control", "duri_evolution", "duri_modules", "duri_tests",
    "schemas", "utils", "resources", "refactor_backups",
    "artifacts_phase1", "conversation_logs", "failure_log", "loop_data",
    "shared-scripts", "unified_conversations"
  ]
}
EOF
)

# === 본 백업 실행 ===
echo "🚀 본 백업 시작..."
echo "   - 압축 레벨: zstd -15 (최고 압축률)"
echo "   - 진행상황: pv를 사용한 실시간 표시"

(
  cd "$WORKSPACE"

  # tar → pv → zstd 파이프라인
  tar --posix --no-xattrs --no-acls --numeric-owner --owner=0 --group=0 \
      --exclude=.git \
      --exclude=__pycache__ --exclude=.pytest_cache --exclude=.cache \
      --exclude=node_modules --exclude=logs --exclude=temp_* \
      --exclude=var/tmp --exclude=var/run --exclude=var/cache \
      --sort=name --mtime='@0' \
      -cf - \
      DuRiCore duri_brain duri_core duri_common core tools tests configs scripts docs \
      models var learning_journal \
      backup backup_repository duri_snapshots cursor_extension \
      duri_control duri_evolution duri_modules duri_tests \
      schemas utils resources refactor_backups \
      artifacts_phase1 conversation_logs failure_log loop_data \
      shared-scripts unified_conversations \
  | pv -s "$TOTAL_BYTES" -p -t -e -r -b \
  | zstd -T2 -15 -q -o "$TMP"
)

# === 백업 완료 및 검증 ===
echo "✅ 백업 완료!"
echo "📏 파일 크기: $(du -h "$TMP" | awk '{print $1}')"
echo "🔍 압축률: $(( (TOTAL_BYTES - $(stat -c %s "$TMP")) * 100 / TOTAL_BYTES ))%"

# === 원자적 이동 (ext4 → NTFS) ===
echo "🔄 최종 이동 중..."
mv -f "$TMP" "$OUT"
mv -f "$FILELIST_TMP" "${OUT_DIR}/filelist.FULL.${STAMP}.txt"
mv -f "$HASHLIST_TMP" "${OUT_DIR}/HASHLIST.FULL.${STAMP}.txt"
mv -f "$MANIFEST_TMP" "${OUT_DIR}/manifest.FULL.${STAMP}.json"

# 동기화
sync

# === 해시 검증 ===
echo "🔐 해시 검증..."
( cd "$OUT_DIR" && sha256sum "$(basename "$OUT")" > "SHA256SUMS.FULL.${STAMP}.txt" )

# === 자동 보호 설정 ===
echo "🛡️ 자동 보호 설정..."
if command -v backup_guard.sh >/dev/null 2>&1; then
  backup_guard.sh protect || echo "⚠️ 보호 설정 실패 (무시)"
else
  echo "ℹ️ backup_guard.sh 미설치 - 수동 보호 필요"
fi

# === 최종 결과 ===
echo ""
echo "🎉 FULL 백업 완료!"
echo "📁 출력 파일: $OUT"
echo "📊 최종 크기: $(du -h "$OUT" | awk '{print $1}')"
echo "📈 압축률: $(( (TOTAL_BYTES - $(stat -c %s "$OUT")) * 100 / TOTAL_BYTES ))%"
echo "📋 메타데이터:"
echo "   - 파일 목록: filelist.FULL.${STAMP}.txt"
echo "   - 해시 목록: HASHLIST.FULL.${STAMP}.txt"
echo "   - 매니페스트: manifest.FULL.${STAMP}.json"
echo "   - SHA256: SHA256SUMS.FULL.${STAMP}.txt"

# === 정리 ===
cleanup
