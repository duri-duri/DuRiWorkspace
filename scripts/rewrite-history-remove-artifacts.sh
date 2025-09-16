#!/usr/bin/env bash
set -euo pipefail

# 사용법:
#   scripts/rewrite-history-remove-artifacts.sh <REMOTE_URL>
# 예:
#   scripts/rewrite-history-remove-artifacts.sh git@github.com:org/repo.git

REMOTE_URL="${1:-}"
if [[ -z "${REMOTE_URL}" ]]; then
  echo "REMOTE_URL 을(를) 인자로 넘겨주세요."
  exit 1
fi

# 사전 확인
command -v git >/dev/null || { echo "git 필요"; exit 1; }
if ! git filter-repo -h >/dev/null 2>&1; then
  echo "git-filter-repo 미설치. (brew install git-filter-repo) 또는 (pipx install git-filter-repo)"
  exit 1
fi

WORKDIR="$(pwd)"
BACKUP_DIR="${WORKDIR}/repo-backup.git"
CLEAN_DIR="${WORKDIR}/repo-clean.git"

echo "▶ 미러 백업 생성: ${BACKUP_DIR}"
rm -rf "${BACKUP_DIR}" && git clone --mirror "${REMOTE_URL}" "${BACKUP_DIR}"

echo "▶ 클린 작업용 미러 클론: ${CLEAN_DIR}"
rm -rf "${CLEAN_DIR}" && git clone --mirror "${REMOTE_URL}" "${CLEAN_DIR}"
cd "${CLEAN_DIR}"

echo "▶ 히스토리에서 산출물 제거 (artifacts/, experiments/, *.jsonl)"
git filter-repo \
  --path DuRi_Day11_15_starter/artifacts \
  --path DuRi_Day11_15_starter/experiments \
  --path-glob '*.jsonl' \
  --invert-paths

echo "▶ 용량 변화 확인"
echo "  - BEFORE:"
git --git-dir "${BACKUP_DIR}" count-objects -vH | sed 's/^/    /'
echo "  - AFTER:"
git count-objects -vH | sed 's/^/    /'

echo "▶ 리모트에 반영 (force-with-lease + --mirror)"
git push --force-with-lease --mirror

echo "✅ 완료!"
echo "참고: 과거 커밋 SHA가 변경되었습니다. 팀원 안내 템플릿 공유를 권장합니다."
