#!/usr/bin/env bash
set -euo pipefail

# 카나리 비율 단계 조정 (0.1→0.5→1.0) + 각 10분 점검
# 태스크 8: Redis 기반 핫리로드로 업데이트
RATIO=${1:-0.10}

echo "=== 🚀 카나리 승격: ${RATIO} (${RATIO%%.*}%) ==="

# 1. Redis에 카나리 비율 설정 (핫리로드)
echo "🔄 Redis에 카나리 비율 설정: ${RATIO}"
docker compose exec duri-redis redis-cli SET canary:ratio ${RATIO}

# 2. 5초 대기 (핫리로드 반영)
echo "⏰ 5초 대기 중... (핫리로드 반영)"
sleep 5

# 3. 분포 확인
echo "📊 카나리 분포 확인:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes' AND track='prod') 
 SELECT meta_model_id AS model, COUNT(*) n FROM recent GROUP BY 1 ORDER BY n DESC;"

# 4. SRM 체크
echo "🔍 SRM 체크:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes' AND track IN ('prod','cand')), 
 prod AS (SELECT COUNT(*) n FROM recent WHERE track='prod'), 
 total AS (SELECT COUNT(*) n FROM recent), 
 vars AS (SELECT ${RATIO}::numeric AS expect) 
 SELECT (SELECT n FROM prod) AS prod_n, (SELECT n FROM total) AS total_n, 
 ROUND(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0))::numeric,4) AS prod_ratio, 
 CASE WHEN abs(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0)) - (SELECT expect FROM vars)) > 0.05 
 THEN '❗ SRM suspected' ELSE 'OK' END AS srm_status;"

# 5. 상태 요약
echo "📋 상태 요약:"
echo "   - Redis canary:ratio: $(docker compose exec duri-redis redis-cli GET canary:ratio)"
echo "   - 실행 시간: $(date)"
echo "   - 다음 단계: 10분 후 ./check_srm_and_guard.sh 실행"

echo "✅ 카나리 ${RATIO} 설정 완료 (핫리로드)"
