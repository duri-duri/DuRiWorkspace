#!/usr/bin/env bash
# 루프 공통 함수 라이브러리
set -euo pipefail

lock_and_stamp() {
  local name="$1" log="var/logs/loop_${name}.log" lock="var/locks/${name}.lock"
  mkdir -p var/locks var/logs
  umask 027   # 민감 로그 world-readable 방지
  exec 201>"$lock"; flock -n 201 || exit 0

  # 그레이스풀 종료 (선설치)
  local _trap_log="$log"
  trap 'printf "[\%(%F %T)T] stop signal\n" -1 >> "$_trap_log"; exit 0' SIGINT SIGTERM

  # [[ -f "$log" && $(wc -c <"$log") -gt 10485760 ]] && mv "$log" "${log}.$(date +%Y%m%d%H%M%S)"  # logrotate가 10MB로 처리
  echo "BUILD $(date -u +%FT%TZ) @ $(git rev-parse --short HEAD 2>/dev/null || echo nogit)" >> "$log"
}
