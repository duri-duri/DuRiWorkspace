#!/usr/bin/env bash
# 루프 공통 함수 라이브러리
set -euo pipefail
export LC_ALL=C

repo_root() {
  # 1) git 저장소면 show-toplevel, 아니면 2) 현재 파일 기준 역추적
  local here
  here="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
  (git -C "$here" rev-parse --show-toplevel 2>/dev/null) || \
  (cd "$here/../.." && pwd -P)
}

# 절대경로 빌더
abspath() { python3 - <<'PY' "$1"
import os,sys; print(os.path.realpath(sys.argv[1]))
PY
}

# 안전 chdir
cd_safe() { mkdir -p "$1" && cd "$1"; }

# 라벨 정규화 함수 (Exporter/Guard 공용)
normalize_label() {
  local label="$1"
  # - → ALL, 비문자 → _
  echo "$label" | sed 's/^-$/ALL/; s/[^[:alnum:]_]/_/g' | tr '[:lower:]' '[:upper:]'
}

# 숫자 비교 함수 (NaN/소수점/공백 이슈 방지)
compare_ge() {
  local n="$1" th="$2"
  LC_ALL=C awk -v n="$n" -v th="$th" 'BEGIN{exit !(n+0 >= th+0)}'
}

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
