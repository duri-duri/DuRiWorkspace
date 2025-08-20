#!/usr/bin/env bash
set -euo pipefail
WS_ROOT="${WS_ROOT:-$PWD}"
DEST="${1:-/tmp/duri-smoke-restore-$(date +%s)}"
mkdir -p "${DEST}"

pick_latest() {
  # 오늘자 기준 최신 아카이브(EXTENDED→FULL→CORE 우선순) 선택
  local base="/mnt/c/Users/admin/Desktop/두리백업/$(date +%Y)/$(date +%m)/$(date +%d)"
  ls -t "${base}"/EXTENDED__*.tar.* "${base}"/FULL__*.tar.* "${base}"/CORE__*.tar.* 2>/dev/null | head -n1
}

ARCH="$(pick_latest || true)"
[[ -n "${ARCH:-}" ]] || { echo "❌ 복원 대상 아카이브를 찾지 못했습니다."; exit 3; }

echo "▶ 복원 리허설 대상: ${ARCH}"
case "${ARCH}" in
  *.tar.zst|*.zst)  zstd -dc -- "${ARCH}" | tar -xf - -C "${DEST}";;
  *.tar.gz|*.tgz|*.gz)  gzip -dc -- "${ARCH}" | tar -xf - -C "${DEST}";;
  *.tar) tar -xf "${ARCH}" -C "${DEST}";;
  *) echo "⚠️ 알 수 없는 형식: ${ARCH}" ; exit 4;;
esac

# 경로 재바인딩(있으면)
if [[ -x "${WS_ROOT}/scripts/rebind_state_paths.py" ]]; then
  python3 "${WS_ROOT}/scripts/rebind_state_paths.py" --root "${DEST}" || true
fi

# 기본 점검
echo "▶ 엔트리 샘플:"
find "${DEST}" -maxdepth 3 -type f | head -n 15

# 초경량 테스트(있으면)
if command -v pytest >/dev/null 2>&1 && ls "${DEST}"/**/test_* 1>/dev/null 2>&1; then
  echo "▶ smoke pytest 시작(최대 3분 제한 권장)"
  (cd "${DEST}" && pytest -q || true)
fi

# --- [패치6] RTO 계측 ---
STATE_DIR="${WS_ROOT}/var/state"
mkdir -p "$STATE_DIR"
echo "{\"t\":\"$(date +'%Y-%m-%d__%H%M')\",\"archive\":\"${ARCH}\",\"rto_sec\":$((SECONDS))}" >> "${STATE_DIR}/restore_slo.jsonl" || true

echo "✅ 복원 리허설 완료: ${DEST}"
