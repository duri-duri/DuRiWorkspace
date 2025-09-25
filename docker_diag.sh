#!/usr/bin/env bash
# docker_diag.sh - Docker 오해 방지용 진단/정리 v2
set -euo pipefail

C_RESET='\033[0m'; C_OK='\033[32m'; C_WARN='\033[33m'; C_ERR='\033[31m'; C_INFO='\033[36m'
ok(){ echo -e "${C_OK}✅ $*${C_RESET}"; }
warn(){ echo -e "${C_WARN}⚠️  $*${C_RESET}"; }
err(){ echo -e "${C_ERR}❌ $*${C_RESET}"; }
info(){ echo -e "${C_INFO}ℹ️  $*${C_RESET}"; }

echo "=== Docker 시스템 진단 시작 ==="

# 0) 환경판별
OSREL="$(uname -a || true)"
if grep -qiE 'microsoft|wsl' <<<"$OSREL" || [ -d /run/WSL ]; then
  ENV="WSL"
  ok "WSL 환경 감지"
else
  ENV="LINUX"
  ok "순수 Linux 환경 감지"
fi

# 1) 파일/리포 지표(설치 vs 설정 문제 분기용)
echo "— 파일 단서 수집 —"
FOUND_FILES=$( (find . -maxdepth 3 -type f -iname "*docker*" -o -iname "docker-compose*.yml" 2>/dev/null | wc -l) || echo 0 )
if [ "${FOUND_FILES}" -gt 0 ]; then
  ok "Repo 내 Docker 관련 파일 ${FOUND_FILES}개 존재 → '설치 문제'보단 '설정/데몬' 이슈일 확률↑"
  (find . -maxdepth 3 -type f -iname "*docker*" -o -iname "docker-compose*.yml" 2>/dev/null | head -5) || true
else
  warn "Repo 내 Docker 파일 미탐 → 실제 시스템 설치 여부를 더 중점 점검"
fi

# 2) 바이너리/버전/Compose
echo "— 바이너리 가용성 —"
if command -v docker >/dev/null 2>&1; then
  ok "docker CLI 감지: $(docker --version 2>/dev/null || echo '버전 조회 실패')"
else
  err "docker CLI 없음 → '설치 문제' 가능성↑"
fi

# Compose v2 플러그인 여부
if docker compose version >/dev/null 2>&1; then
  ok "'docker compose' 사용 가능(Compose v2)"
elif command -v docker-compose >/dev/null 2>&1; then
  warn "'docker-compose'(구 v1)만 존재. v2 권장"
else
  warn "Compose 미탐지. (v2 플러그인 설치 필요 가능)"
fi

# 3) 데몬/소켓/권한
echo "— 데몬/소켓/권한 —"
SOCK="/var/run/docker.sock"
if [ -S "$SOCK" ]; then
  ok "소켓 존재: $SOCK"
  ls -l "$SOCK" || true
else
  warn "소켓 없음 → 데몬 미동작/경로 상이/Rootless 미설정 가능"
fi

if command -v ps >/dev/null 2>&1; then
  ps aux | grep -E 'dockerd|rootlesskit' | grep -v grep || true
fi

# 데몬 상호작용 테스트
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker 데몬 정상 응답"
  else
    warn "docker 데몬 응답 없음 → 구체적 사유:"
    docker info 2>&1 | head -10 || true
  fi
fi

# 4) 시스템 관리자/기동경로(ENV별 분기)
echo "— 환경별 기동 경로 제안 —"
if [ "$ENV" = "WSL" ]; then
  info "WSL에서는 보통 'systemctl'이 동작하지 않음."
  if command -v wsl.exe >/dev/null 2>&1; then
    info "Windows Docker Desktop 사용 중이면: Docker Desktop에서 WSL 통합이 켜져야 함."
  fi
  # 대체 경로: rootless or 수동 dockerd
  if command -v dockerd-rootless-setuptool.sh >/dev/null 2>&1; then
    warn "rootless 경로 감지. (예: 'systemctl --user start docker' 또는 환경변수 설정)"
  else
    info "수동 기동 예: 'sudo dockerd --host=unix:///var/run/docker.sock' (테스트용)"
  fi
else
  # LINUX
  if command -v systemctl >/dev/null 2>&1; then
    info "systemctl 경로 가정: 'sudo systemctl status docker', 'sudo systemctl start docker'"
  elif command -v service >/dev/null 2>&1; then
    info "SysVinit 경로 가정: 'sudo service docker status', 'sudo service docker start'"
  else
    warn "관리 도구 미탐 → 직접 'dockerd' 실행 또는 설치 재확인"
  fi
fi

# 5) 권한(그룹) 점검
echo "— 권한(그룹) —"
if id -nG 2>/dev/null | grep -qw docker; then
  ok "현재 사용자 docker 그룹 포함"
else
  warn "현재 사용자 docker 그룹 미포함 → 'sudo usermod -aG docker $USER' 후 재로그인 필요"
fi

# 6) cgroups/커널 힌트
echo "— 커널/컨테이너 런타임 힌트 —"
if [ -f /sys/fs/cgroup/cgroup.controllers ]; then
  info "cgroup v2 환경. 현대 Docker에 적합."
fi

# 7) 백업 흔적(오해 방지 메시지 판단 근거)
echo "— 백업 흔적 —"
if [ -d /mnt/hdd ]; then
  H=$(ls -1 /mnt/hdd 2>/dev/null | grep -i docker | wc -l || echo 0)
  if [ "$H" -gt 0 ]; then ok "HDD에서 Docker 관련 흔적 탐지(${H}개)"; fi
fi
if [ -d backup_repository ]; then
  R=$(ls -1 backup_repository 2>/dev/null | grep -i docker | wc -l || echo 0)
  if [ "$R" -gt 0 ]; then ok "repo 내부 backup_repository에 Docker 흔적 탐지(${R}개)"; fi
fi

echo "=== 진단 요약 ==="
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "[메시지] 'Docker는 정상 동작 중입니다.'"
  else
    if [ -S "$SOCK" ]; then
      warn "[메시지] 'Docker 파일/소켓은 존재하나 접근/권한/환경 문제로 판단.'"
    else
      warn "[메시지] '설치 흔적은 있으나 데몬이 꺼져있거나 미기동. 환경별 기동 절차 수행 권장.'"
    fi
  fi
else
  err "[메시지] 'Docker CLI 자체가 없어 보입니다(설치 문제).' OS/패키지 매니저로 설치 요망."
fi


