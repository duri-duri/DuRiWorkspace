#!/usr/bin/env bash
set -Eeuo pipefail
deadline=$((SECONDS+90))
# 헬스체크가 있는 컨테이너들
health_containers=(prometheus alertmanager grafana)
# 헬스체크가 없는 컨테이너들 (실행 상태만 확인)
running_containers=(duri_core_container duri_brain_container duri_evolution_container duri_control_container)

while :; do
  ok=1
  
  # 헬스체크가 있는 컨테이너들 확인
  for s in "${health_containers[@]}"; do
    st=$(docker inspect --format='{{.State.Health.Status}}' "$s" 2>/dev/null || echo none)
    [[ "$st" == "healthy" ]] || { ok=0; break; }
  done
  
  # 헬스체크가 없는 컨테이너들은 실행 상태만 확인
  for s in "${running_containers[@]}"; do
    st=$(docker inspect --format='{{.State.Status}}' "$s" 2>/dev/null || echo none)
    [[ "$st" == "running" ]] || { ok=0; break; }
  done
  
  (( ok==1 )) && break
  (( SECONDS > deadline )) && { echo "SMOKE FAIL"; exit 1; }
  sleep 2
done
curl -sf http://localhost:9090/-/ready >/dev/null
curl -sf http://localhost:3000/api/health >/dev/null
echo "SMOKE OK"
