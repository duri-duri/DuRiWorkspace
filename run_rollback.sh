#!/usr/bin/env bash
set -euo pipefail

echo "=== 🛑 즉시 롤백 실행 ==="

# 1. Redis에 카나리 비율 0 설정 (핫리로드)
echo "🔄 Redis에 카나리 비율 0 설정"
docker compose exec duri-redis redis-cli SET canary:ratio 0

# 2. 5초 대기 (핫리로드 반영)
echo "⏰ 5초 대기 중... (핫리로드 반영)"
sleep 5

# 3. 분포 확인 (10분 윈도 prod 분포 0에 수렴하는지)
echo "📊 롤백 후 분포 확인:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts>=NOW()-INTERVAL '10 minutes') 
 SELECT track, COUNT(*) FROM recent GROUP BY 1;"

# 4. 가드 상태 확인
echo "🛡️ 가드 상태:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT model_id, decision, reason, decision_ts FROM v_promotion_latest ORDER BY decision_ts DESC LIMIT 3;"

# 5. 상태 요약
echo "📋 롤백 상태 요약:"
echo "   - Redis canary:ratio: $(docker compose exec duri-redis redis-cli GET canary:ratio)"
echo "   - 실행 시간: $(date)"
echo "   - 다음 단계: 문제 해결 후 ./run_promote_canary.sh 0.10으로 재시작"

echo "✅ 롤백 완료: canary:ratio=0 (핫리로드)"
