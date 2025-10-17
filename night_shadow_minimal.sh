#!/bin/bash
# night_shadow_minimal.sh
set -euo pipefail

echo "=== 🚀 Shadow 훈련장 밤새 가동 준비 ==="

# 0) 워크트리 깨끗이 주차
echo "0️⃣ 워크트리 깨끗이 주차:"
git rev-parse --abbrev-ref HEAD
git stash push -u -m "nightly parking (root) $(date +%F-%T)" || true
git submodule foreach --recursive 'git stash push -u -m "nightly parking (submodule) $(date +%F-%T)" || true'
git status --porcelain --ignore-submodules=none

# 1) 밤새 돌릴 최소 서비스만 가동
echo "1️⃣ 밤새 돌릴 최소 서비스만 가동:"
docker compose up -d duri-postgres duri-redis duri_control duri_brain duri_core duri_evolution aggregation_worker
docker compose stop blackbox_exporter cadvisor node_exporter postgres_exporter redis_exporter prometheus || true

# 2) 저부하 shadow 샘플러(30초 간격 cand 1건)
echo "2️⃣ 저부하 shadow 샘플러 시작:"
nohup bash -c 'i=0; while true; do
  i=$((i+1));
  curl -s -XPOST http://localhost:8083/emotion \
    -H "Content-Type: application/json" \
    -H "X-DuRi-Shadow: 1" \
    -d "{\"user_id\":\"night_shadow_$i\",\"text\":\"야간 쉐도우 샘플 $i\"}" >/dev/null;
  sleep 30;
done' >/tmp/shadow_feeder.log 2>&1 & echo $! >/tmp/shadow_feeder.pid

# 3) 지금 상태 한 번 체크(로그+1h 표본)
echo "3️⃣ 지금 상태 한 번 체크:"
docker compose ps
echo ""
echo "aggregation_worker 최근 로그:"
docker compose logs --tail=100 aggregation_worker | egrep "\[agg:top5\]|\[agg:decision\]" || true
echo ""
echo "최근 1시간 샘플 상태:"
docker compose exec duri-postgres psql -U duri -d duri -c "
SELECT meta->>'model_id' AS model, track, COUNT(*) n
FROM v_feedback_events_clean
WHERE ts >= NOW() - INTERVAL '1 hour' AND track IN ('cand','prod')
GROUP BY 1,2 ORDER BY 1,2;"

echo ""
echo "== 🎉 Night shadow minimal is running. Feeder PID: $(cat /tmp/shadow_feeder.pid)"
echo "== 내일 아침 확인 명령:"
echo "docker compose exec duri-postgres psql -U duri -d duri -c \"SELECT model_id, decision, reason, decision_ts FROM promotion_decisions ORDER BY decision_ts DESC LIMIT 5;\""
echo "docker compose logs --tail=200 aggregation_worker | egrep \"\[agg:top5\]|\[agg:decision\]\""
echo "== 중지 명령: kill \$(cat /tmp/shadow_feeder.pid)"
