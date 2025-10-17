#!/usr/bin/env bash
set -euo pipefail

# Shadow 훈련장 "자기 진화" 점검 체크리스트 (핵심만)
# 효율/안전/진화를 더 끌어올리는 메타 레벨 점검

echo "=== 🔍 Shadow 훈련장 '자기 진화' 점검 ==="
echo "실행 시간: $(date)"
echo ""

# 1. SRM(표본비율) 자동 감지 + 자동 하향/롤백 연결됨?
echo "📊 1. SRM(표본비율) 자동 감지 체크"
RATIO=$(docker compose exec duri-redis redis-cli GET canary:ratio 2>/dev/null || echo "0.10")
echo "   - 현재 canary:ratio: ${RATIO}"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH recent AS (SELECT * FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes' AND track IN ('prod','cand')), 
 prod AS (SELECT COUNT(*) n FROM recent WHERE track='prod'), 
 total AS (SELECT COUNT(*) n FROM recent), 
 vars AS (SELECT ${RATIO}::numeric AS expect) 
 SELECT (SELECT n FROM prod) AS prod_n, (SELECT n FROM total) AS total_n, 
 ROUND(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0))::numeric,4) AS prod_ratio, 
 CASE WHEN abs(((SELECT n FROM prod)::numeric / NULLIF((SELECT n FROM total),0)) - (SELECT expect FROM vars)) > 0.05 
 THEN '❗ SRM suspected' ELSE '✅ OK' END AS srm_status;" 2>/dev/null || echo "   ⚠️ SRM 체크 실패"

# 2. N/3 연속 promote 규칙이 집계 워커 로직에 내장됐나
echo ""
echo "🛡️ 2. N/3 연속 promote 규칙 체크"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH snaps AS (SELECT decision_ts, decision='promote' AS pass FROM promotion_decisions WHERE model_id='shadow_proxy' AND decision_ts >= NOW()-INTERVAL '15 minutes' ORDER BY decision_ts DESC LIMIT 3) 
 SELECT COUNT(*) FILTER (WHERE pass) AS passes, 
 CASE WHEN COUNT(*) FILTER (WHERE pass)=3 THEN '✅ PROMOTE_STABLE' ELSE '⏳ HOLD' END AS gate FROM snaps;" 2>/dev/null || echo "   ⚠️ N/3 규칙 체크 실패"

# 3. promotion_decisions 아이템포턴트 쓰기 보장
echo ""
echo "🔄 3. promotion_decisions 아이템포턴트 쓰기 체크"
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT COUNT(*) as total_decisions, 
 COUNT(DISTINCT (model_id, decision, date_trunc('hour', decision_ts))) as unique_decisions,
 CASE WHEN COUNT(*) = COUNT(DISTINCT (model_id, decision, date_trunc('hour', decision_ts))) 
 THEN '✅ No duplicates' ELSE '❗ Duplicates found' END as status
 FROM promotion_decisions 
 WHERE decision_ts >= NOW() - INTERVAL '1 hour';" 2>/dev/null || echo "   ⚠️ 아이템포턴트 체크 실패"

# 4. v_feedback_events_clean 버전 고정
echo ""
echo "🗄️ 4. v_feedback_events_clean 버전 고정 체크"
if [ -f "v_feedback_events_clean_ddl.sql" ]; then
    docker compose exec duri-postgres psql -U duri -d duri -c \
    "SELECT definition FROM pg_views WHERE viewname='v_feedback_events_clean';" -At > /tmp/current_view.sql
    if diff -q /tmp/current_view.sql v_feedback_events_clean_ddl.sql > /dev/null 2>&1; then
        echo "   ✅ DDL 일치"
    else
        echo "   ❌ DDL 불일치 감지!"
    fi
else
    echo "   ⚠️ v_feedback_events_clean_ddl.sql 없음"
fi

# 5. 카나리 핫리로드
echo ""
echo "🔥 5. 카나리 핫리로드 체크"
if docker compose exec duri-redis redis-cli PING > /dev/null 2>&1; then
    echo "   ✅ Redis 연결 OK"
    echo "   - canary:ratio: $(docker compose exec duri-redis redis-cli GET canary:ratio 2>/dev/null || echo 'N/A')"
else
    echo "   ❌ Redis 연결 실패"
fi

# 6. 비용 캡 초과 시 즉시 컷아웃 + 증빙 번들 자동 수거
echo ""
echo "💰 6. 비용 캡 체크"
docker compose exec duri-postgres psql -U duri -d duri -c \
"WITH c AS (SELECT SUM(cost_usd) cost_10m FROM v_feedback_events_clean WHERE ts >= NOW() - INTERVAL '10 minutes'), 
 limits AS (SELECT 5.00::numeric AS usd_per_hour_cap) 
 SELECT cost_10m, ROUND((cost_10m*6)::numeric,2) AS projected_hourly, 
 CASE WHEN cost_10m*6 > (SELECT usd_per_hour_cap FROM limits) THEN '🚨 CUTOUT' ELSE '✅ OK' END AS status FROM c;" 2>/dev/null || echo "   ⚠️ 비용 캡 체크 실패"

# 7. 지표 인덱싱 + 통계 쿼리 계획 확인
echo ""
echo "📈 7. 지표 인덱싱 + 통계 쿼리 계획 확인"
docker compose exec duri-postgres psql -U duri -d duri -c \
"SELECT indexname, tablename FROM pg_indexes WHERE tablename='feedback_events' AND indexname LIKE '%ts%';" 2>/dev/null || echo "   ⚠️ 인덱스 체크 실패"

# 8. 최근 로그 상태
echo ""
echo "📝 8. 최근 로그 상태"
docker compose logs --tail=10 aggregation_worker | grep -E "\[agg:(top5|decision)\]" | tail -3 || echo "   ⚠️ 로그 확인 실패"

echo ""
echo "=== ✅ Shadow 훈련장 '자기 진화' 점검 완료 ==="
echo "다음 단계: 문제 발견 시 해당 가드/스크립트 실행"
