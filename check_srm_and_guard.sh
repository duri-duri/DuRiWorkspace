#!/usr/bin/env bash
set -euo pipefail

echo "=== 🔍 SRM + Guard 체크 요약 ==="

# 1. SRM 체크 (현재 Redis canary:ratio 기준)
RATIO=$(docker compose exec duri-redis redis-cli GET canary:ratio || echo "0.10")
echo "📊 SRM 체크 (기대 비율: ${RATIO}):"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes' AND track IN ('prod','cand')), 
 prod AS (SELECT COUNT(*) n FROM recent WHERE track='prod'), 
 total AS (SELECT COUNT(*) n FROM recent), 
 vars AS (SELECT ${RATIO}::numeric AS expect) 
 SELECT (SELECT n FROM prod) AS prod_n, (SELECT n FROM total) AS total_n, 
 ROUND(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0))::numeric,4) AS prod_ratio, 
 CASE WHEN abs(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0)) - (SELECT expect FROM vars)) > 0.05 
 THEN '❗ SRM suspected' ELSE 'OK' END AS srm_status;"

# 2. Guard 통과 상태 (N/3 규칙)
echo "🛡️ Guard 통과 상태 (N/3 규칙):"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH snaps AS (SELECT decision_ts, decision = 'promote' AS pass FROM promotion_decisions WHERE model_id='shadow_proxy' AND decision_ts >= NOW() - INTERVAL '15 minutes' ORDER BY decision_ts DESC LIMIT 3) 
 SELECT COUNT(*) FILTER (WHERE pass) AS passes, 
 CASE WHEN COUNT(*) FILTER (WHERE pass)=3 THEN 'PROMOTE_STABLE' ELSE 'HOLD' END AS gate FROM snaps;"

# 3. 최신 승격 결정
echo "📋 최신 승격 결정:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT model_id, decision, reason, decision_ts FROM v_promotion_latest ORDER BY decision_ts DESC LIMIT 3;"

# 4. 비용 안전장치
echo "💰 비용 안전장치:"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH c AS (SELECT SUM(cost_usd) cost_10m FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes'), 
 limits AS (SELECT 5.00::numeric AS usd_per_hour_cap) 
 SELECT cost_10m, ROUND((cost_10m*6)::numeric,2) AS projected_hourly, 
 CASE WHEN cost_10m*6 > (SELECT usd_per_hour_cap FROM limits) THEN 'CUTOUT' ELSE 'OK' END AS status FROM c;"

echo "✅ SRM + Guard 체크 완료"
