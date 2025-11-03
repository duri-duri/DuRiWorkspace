#!/usr/bin/env bash
set -euo pipefail
ARCHIVE_PATH="${1:-}"
if [[ -z "${ARCHIVE_PATH}" ]]; then
  echo "Usage: $0 /mnt/usb/두리백업/2025/10/29/FULL/FULL__2025-10-27__1851__duri-head.tar.zst" >&2; exit 2; fi
if [[ ! -f "${ARCHIVE_PATH}" ]]; then echo "E: archive not found: ${ARCHIVE_PATH}" >&2; exit 3; fi
WORKDIR="${WORKDIR:-$HOME/DuRiWorkspace}"; cd "${WORKDIR}"
log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*"; }
run(){ log "+ $*"; eval "$*"; }
log "0) 아카이브 무결성 점검(zstd -tq)"; zstd -tq "${ARCHIVE_PATH}" && log "OK: archive integrity"
TMPDIR="$(mktemp -d /tmp/rebase_def.XXXXXX)"; trap 'rm -rf "${TMPDIR}"' EXIT
log "1) 키 정의만 추출 → ${TMPDIR}"
# use unzstd for compatibility
if ! tar --use-compress-program=unzstd -xvf "${ARCHIVE_PATH}" \
  --wildcards -C "${TMPDIR}" \
  'DuRiWorkspace/docker-compose*.yml' \
  'DuRiWorkspace/start-ssh-node.sh' \
  'DuRiWorkspace/shadow/**' \
  'home/*/.config/systemd/user/*.service' \
  'home/*/.config/systemd/user/*.timer' 2>/dev/null; then true; fi
FOUND_ANY=0
for p in "${TMPDIR}/DuRiWorkspace/docker-compose.yml" "${TMPDIR}/DuRiWorkspace/start-ssh-node.sh"; do [[ -f "$p" ]] && FOUND_ANY=1 || true; done
[[ "${FOUND_ANY}" -eq 0 ]] && { echo "E: required definitions not found in archive. Abort." >&2; exit 4; }
if tar --use-compress-program=unzstd -tf "${ARCHIVE_PATH}" | grep -qE '^srv_duri/'; then
  log "WARN: srv_duri/가 아카이브에 있습니다. (CASE A 가능) — 본 스크립트는 CASE B만 수행합니다."
else
  log "CASE B 확정: 정의만 포함된 백업"
fi
TS="$(date +%Y%m%d-%H%M%S)"; BKDIR="${WORKDIR}/var/backups/rebase_caseB_${TS}"; run "mkdir -p '${BKDIR}'"
save_if_exists(){ local f="$1"; if [[ -e "$f" ]]; then run "mkdir -p '${BKDIR}/$(dirname "$f" | sed "s|${WORKDIR}/||")'"; run "cp -a '$f' '${BKDIR}/$(dirname "$f" | sed "s|${WORKDIR}/||")/'"; fi }
save_if_exists "${WORKDIR}/docker-compose.yml"; for f in ${WORKDIR}/docker-compose.*.yml; do [[ -e "$f" ]] && save_if_exists "$f"; done; save_if_exists "${WORKDIR}/start-ssh-node.sh"
USR_SYSD="${HOME}/.config/systemd/user"; if compgen -G "${USR_SYSD}/duri-*.*" >/dev/null || compgen -G "${USR_SYSD}/shadow-*.*" >/dev/null; then run "mkdir -p '${BKDIR}/.config/systemd/user'"; run "cp -a ${USR_SYSD}/duri-*.* '${BKDIR}/.config/systemd/user/' 2>/dev/null || true"; run "cp -a ${USR_SYSD}/shadow-*.* '${BKDIR}/.config/systemd/user/' 2>/dev/null || true"; fi
log "정의 파일 덮어쓰기"; run "cp -f '${TMPDIR}/DuRiWorkspace/docker-compose.yml' '${WORKDIR}/' 2>/dev/null || true"; if compgen -G "${TMPDIR}/DuRiWorkspace/docker-compose.*.yml" >/dev/null; then run "cp -f ${TMPDIR}/DuRiWorkspace/docker-compose.*.yml '${WORKDIR}/'"; fi; run "cp -f '${TMPDIR}/DuRiWorkspace/start-ssh-node.sh' '${WORKDIR}/' 2>/dev/null || true"; run "chmod +x '${WORKDIR}/start-ssh-node.sh' 2>/dev/null || true"
if [[ -d "${TMPDIR}/DuRiWorkspace/shadow" ]]; then run "rsync -a --delete '${TMPDIR}/DuRiWorkspace/shadow/' '${WORKDIR}/shadow/'"; fi
if compgen -G "${TMPDIR}/home/*/.config/systemd/user/*.service" >/dev/null || compgen -G "${TMPDIR}/home/*/.config/systemd/user/*.timer" >/dev/null; then run "mkdir -p '${USR_SYSD}'"; find "${TMPDIR}/home" -type f -path '*/.config/systemd/user/*' -print0 | xargs -0 -I{} cp -f "{}" "${USR_SYSD}/"; run "systemctl --user daemon-reload || true"; run "systemctl --user restart 'duri-*' 2>/dev/null || true"; run "systemctl --user restart 'shadow-*' 2>/dev/null || true"; fi
# docker compose restart
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi
log "docker compose 재기동"; run "$DC -f '${WORKDIR}/docker-compose.yml' down"; run "$DC -f '${WORKDIR}/docker-compose.yml' up -d"
log "헬스체크"; OKS=0; for p in 8080 8081 8082 8083; do if curl -fsS "http://localhost:${p}/health" >/dev/null 2>&1; then log "OK :${p}"; ((OKS++))||true; else log "FAIL :${p}"; fi; done; run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true"
log "요약:"; log " - 정의 rebase 완료"; log " - 런타임 데이터(/srv/duri 등)는 변경하지 않음"; log " - 헬스 통과 ${OKS}/4"; log " - 백업 스냅샷: ${BKDIR}"; [[ "${OKS}" -lt 3 ]] && log "주의: 헬스 응답이 충분하지 않습니다. 'docker logs <svc>' 점검" || true
exit 0
