#!/usr/bin/env bash
set -euo pipefail

# 공통 헤더 패치 (ops/shadow_on.sh, ops/shadow_off.sh, ops/create_gate_snapshot.sh, ops/rotate_gates.sh)
COMMON_HEADER='# docker compose 호환(구버전 대비)
DOCKER_BIN="$(command -v docker || echo /usr/bin/docker)"
PROJECT_DIR="/home/duri/DuRiWorkspace"
PROJECT_NAME="duriworkspace"
DC="$DOCKER_BIN compose -p $PROJECT_NAME --project-directory $PROJECT_DIR --ansi never"

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
cd "$PROJECT_DIR"'

# 각 스크립트에 공통 헤더 적용
for script in ops/shadow_on.sh ops/shadow_off.sh ops/create_gate_snapshot.sh ops/rotate_gates.sh; do
  if [ -f "$script" ]; then
    echo "패치 적용: $script"
    
    # 기존 docker compose 호환 라인 제거
    sed -i '/# docker compose 호환(구버전 대비)/,/DC="docker compose"/d' "$script"
    
    # 공통 헤더를 파일 시작 부분에 삽입
    sed -i "1i$COMMON_HEADER" "$script"
    
    # 모든 'docker compose' 호출을 '$DC'로 치환
    sed -i 's/docker compose/$DC/g' "$script"
    
    # up -d 호출에 --remove-orphans 추가
    sed -i 's/\$DC up -d/\$DC up -d --remove-orphans/g' "$script"
    
    echo "✅ $script 패치 완료"
  fi
done

echo "✅ docker compose 경로/프로젝트 고정 완료"
