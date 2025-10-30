#!/usr/bin/env bash
set -euo pipefail
ARCHIVE_PATH="${1:-}"; DRY_RUN="${2:-}"; [[ -z "${ARCHIVE_PATH}" ]] && { echo "Usage: $0 /path/FULL__YYYY-MM-DD__HHMM__duri-head.tar.zst [--dry-run]" >&2; exit 2; }
[[ ! -f "${ARCHIVE_PATH}" ]] && { echo "E: archive not found: ${ARCHIVE_PATH}" >&2; exit 3; }
WORKDIR="${WORKDIR:-$HOME/DuRiWorkspace}"; USR_SYSD="${HOME}/.config/systemd/user"; SUDO="${SUDO:-sudo}"; cd "${WORKDIR}"
log(){ printf "[%s] %s\n" "$(date '+%F %T')" "$*"; }
run(){ log "+ $*"; eval "$*"; }
log "0) 무결성"; zstd -tq "${ARCHIVE_PATH}" && log "OK"
log "CASE 판정"; tar --use-compress-program=unzstd -tf "${ARCHIVE_PATH}" | grep -q '^srv_duri/' || { echo "E: srv_duri missing (CASE B 사용)" >&2; exit 4; }
[[ "${DRY_RUN:-}" == "--dry-run" ]] && { tar --use-compress-program=unzstd -tvf "${ARCHIVE_PATH}" | head -40 || true; zstd -lv -- "${ARCHIVE_PATH}" || true; exit 0; }
run "systemctl --user stop 'duri-*' 2>/dev/null || true"; run "systemctl --user stop 'shadow-*' 2>/dev/null || true"; run "systemctl --user daemon-reload || true"
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi
[[ -f "${WORKDIR}/docker-compose.yml" ]] && { run "$DC -f '${WORKDIR}/docker-compose.yml' down || true"; } || true
TS="$(date +%Y%m%d-%H%M%S)"; CUR_SRV="/srv/duri"; BK_SRV="/srv/duri._backup_${TS}"; if [[ -d "${CUR_SRV}" ]]; then run "${SUDO} mkdir -p '${BK_SRV}'"; if command -v rsync >/dev/null 2>&1; then run "${SUDO} rsync -aHAX --numeric-ids --delete '${CUR_SRV}/' '${BK_SRV}/'"; else run "cd / && ${SUDO} tar -cpf '${BK_SRV}.tar' 'srv/duri' && ${SUDO} chown $(id -u):$(id -g) '${BK_SRV}.tar'"; fi; fi
TMPDIR="$(mktemp -d /tmp/rebaseA.XXXXXX)"; trap 'rm -rf "${TMPDIR}"' EXIT
run "tar --use-compress-program=unzstd -xvf '${ARCHIVE_PATH}' -C '${TMPDIR}' --wildcards 'DuRiWorkspace/docker-compose*.yml' 'DuRiWorkspace/start-ssh-node.sh' 'DuRiWorkspace/shadow/**' 'home/*/.config/systemd/user/*.service' 'home/*/.config/systemd/user/*.timer' 'srv_duri/**' 2>/dev/null || true"
# workspace defs
[[ -f "${TMPDIR}/DuRiWorkspace/docker-compose.yml" ]] && run "cp -f '${TMPDIR}/DuRiWorkspace/docker-compose.yml' '${WORKDIR}/'"
compgen -G "${TMPDIR}/DuRiWorkspace/docker-compose.*.yml" >/dev/null && run "cp -f ${TMPDIR}/DuRiWorkspace/docker-compose.*.yml '${WORKDIR}/'"
[[ -f "${TMPDIR}/DuRiWorkspace/start-ssh-node.sh" ]] && { run "cp -f '${TMPDIR}/DuRiWorkspace/start-ssh-node.sh' '${WORKDIR}/'"; run "chmod +x '${WORKDIR}/start-ssh-node.sh'"; }
[[ -d "${TMPDIR}/DuRiWorkspace/shadow" ]] && run "rsync -a --delete '${TMPDIR}/DuRiWorkspace/shadow/' '${WORKDIR}/shadow/'"
# systemd
run "mkdir -p '${USR_SYSD}'"; find "${TMPDIR}/home" -type f -path '*/.config/systemd/user/*' -print0 2>/dev/null | xargs -0 -I{} cp -f "{}" "${USR_SYSD}/" 2>/dev/null || true; run "systemctl --user daemon-reload || true"
# runtime replace
log "replace /srv/duri"; if [[ -d "${CUR_SRV}" ]]; then run "${SUDO} find '${CUR_SRV}' -mindepth 1 -maxdepth 1 -exec rm -rf {} +"; else run "${SUDO} mkdir -p '${CUR_SRV}'"; fi
if [[ -d "${TMPDIR}/srv_duri" ]]; then if command -v rsync >/dev/null 2>&1; then run "${SUDO} rsync -aHAX --numeric-ids '${TMPDIR}/srv_duri/' '${CUR_SRV}/'"; else run "cd '${TMPDIR}' && ${SUDO} tar -cpf - 'srv_duri' | (cd /; ${SUDO} tar -xpf -)"; run "${SUDO} mv -f '/srv_duri' '/srv/duri'"; fi; else echo "E: no srv_duri in TMPDIR" >&2; exit 5; fi
# perms hint
${SUDO} bash -c "find /srv/duri/pg -type d -exec chmod 700 {} + 2>/dev/null || true; find /srv/duri/redis -type d -exec chmod 700 {} + 2>/dev/null || true; find /srv/duri/var -type d -exec chmod 755 {} + 2>/dev/null || true" || true
# restart
[[ -f "${WORKDIR}/docker-compose.yml" ]] && run "$DC -f '${WORKDIR}/docker-compose.yml' up -d" || { echo "E: no compose" >&2; exit 6; }
run "systemctl --user restart 'duri-*' 2>/dev/null || true"; run "systemctl --user restart 'shadow-*' 2>/dev/null || true"
log "health"; OKS=0; for p in 8080 8081 8082 8083; do if curl -fsS "http://localhost:${p}/health" >/dev/null 2>&1; then log "OK :${p}"; ((OKS++))||true; else log "FAIL :${p}"; fi; done; run "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' || true"; log "backup kept at ${BK_SRV}*"; [[ "${OKS}" -lt 3 ]] && log "주의: 일부 실패—docker logs 확인" || true
exit 0
