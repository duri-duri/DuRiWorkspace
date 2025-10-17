#!/bin/bash
# Trace v2 보존·정리 스크립트
# Hot/Warm/Cold 정책, VACUUM, 월간 REINDEX

set -euo pipefail

echo "=== 🧹 Trace v2 보존·정리 ==="
echo "실행 시간: $(date)"
echo ""

# 1. 보존 정책 확인
echo "**1. 보존 정책 확인:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT * FROM v_trace_retention_policy;
"
echo ""

# 2. Hot 데이터 (90일 이내) - 유지
echo "**2. Hot 데이터 확인 (90일 이내):**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT 
  'trace_span' as table_name,
  count(*) as hot_records,
  min(start_ts) as oldest_hot,
  max(start_ts) as newest_hot
FROM trace_span 
WHERE start_ts >= now() - interval '90 days'
UNION ALL
SELECT 
  'eval_snapshot' as table_name,
  count(*) as hot_records,
  min(created_at) as oldest_hot,
  max(created_at) as newest_hot
FROM eval_snapshot 
WHERE created_at >= now() - interval '90 days';
"
echo ""

# 3. Cold 데이터 (1년 이상) - 아카이브 대상
echo "**3. Cold 데이터 확인 (1년 이상):**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT 
  'trace_span' as table_name,
  count(*) as cold_records,
  min(start_ts) as oldest_cold,
  max(start_ts) as newest_cold
FROM trace_span 
WHERE start_ts < now() - interval '1 year'
UNION ALL
SELECT 
  'eval_snapshot' as table_name,
  count(*) as cold_records,
  min(created_at) as oldest_cold,
  max(created_at) as newest_cold
FROM eval_snapshot 
WHERE created_at < now() - interval '1 year';
"
echo ""

# 4. VACUUM (ANALYZE) 실행
echo "**4. VACUUM (ANALYZE) 실행:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
VACUUM (ANALYZE) trace_span;
VACUUM (ANALYZE) eval_snapshot;
VACUUM (ANALYZE) trace_edge;
VACUUM (ANALYZE) artifact;
VACUUM (ANALYZE) deploy_events;
"
echo "✅ VACUUM 완료"
echo ""

# 5. 머티리얼라이즈드 뷰 리프레시
echo "**5. 머티리얼라이즈드 뷰 리프레시:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT refresh_trace_materialized_views();
"
echo "✅ 머티리얼라이즈드 뷰 리프레시 완료"
echo ""

# 6. 인덱스 통계 확인
echo "**6. 인덱스 통계 확인:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE tablename IN ('trace_span', 'eval_snapshot', 'trace_edge', 'artifact', 'deploy_events')
ORDER BY idx_scan DESC;
"
echo ""

# 7. 테이블 크기 확인
echo "**7. 테이블 크기 확인:**"
docker compose -p duriworkspace exec duri-postgres psql -U duri -d duri -c "
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
  pg_size_pretty(pg_relation_size(tablename::regclass)) as table_size,
  pg_size_pretty(pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass)) as index_size
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('trace_span', 'eval_snapshot', 'trace_edge', 'artifact', 'deploy_events')
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
"
echo ""

echo "✅ Trace v2 보존·정리 완료!"
