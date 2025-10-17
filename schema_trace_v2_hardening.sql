-- Trace v2 스키마 고정: UNIQUE 제약조건, 인덱스 보강, 파티셔닝 준비
-- 안정 장기 운용을 위한 스키마 강화

-- 1) trace_edge 유일성 보강
ALTER TABLE trace_edge 
  ADD CONSTRAINT uk_trace_edge_parent_child UNIQUE (parent_span_id, child_span_id);

-- 2) 인덱스 보강 (성장 대비)
CREATE INDEX IF NOT EXISTS idx_trace_span_deploy_ts 
  ON trace_span (deploy_req_id, start_ts DESC);

CREATE INDEX IF NOT EXISTS idx_trace_span_name_ts 
  ON trace_span (span_name, start_ts DESC);

CREATE INDEX IF NOT EXISTS idx_eval_snapshot_kpi_created 
  ON eval_snapshot (kpi_name, created_at DESC);

-- 3) 파티셔닝 준비 (3개월 내 적용 예정)
-- trace_span 월별 파티션 준비
CREATE TABLE IF NOT EXISTS trace_span_template (
  LIKE trace_span INCLUDING ALL
) PARTITION BY RANGE (start_ts);

-- eval_snapshot 주별 파티션 준비  
CREATE TABLE IF NOT EXISTS eval_snapshot_template (
  LIKE eval_snapshot INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 4) 보존 정책 뷰 (Hot/Warm/Cold)
CREATE OR REPLACE VIEW v_trace_retention_policy AS
SELECT 
  'trace_span' as table_name,
  count(*) as total_records,
  count(*) FILTER (WHERE start_ts >= now() - interval '90 days') as hot_records,
  count(*) FILTER (WHERE start_ts >= now() - interval '1 year' AND start_ts < now() - interval '90 days') as warm_records,
  count(*) FILTER (WHERE start_ts < now() - interval '1 year') as cold_records
FROM trace_span
UNION ALL
SELECT 
  'eval_snapshot' as table_name,
  count(*) as total_records,
  count(*) FILTER (WHERE created_at >= now() - interval '90 days') as hot_records,
  count(*) FILTER (WHERE created_at >= now() - interval '1 year' AND created_at < now() - interval '90 days') as warm_records,
  count(*) FILTER (WHERE created_at < now() - interval '1 year') as cold_records
FROM eval_snapshot;

-- 5) 운영 대시보드용 머티리얼라이즈드 뷰
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_span_err_rate_1d AS
SELECT 
  COALESCE(labels->>'service', 'unknown') AS service,
  count(*) AS total,
  sum(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS errors,
  CASE 
    WHEN count(*) > 0 THEN 1.0 * sum(CASE WHEN status='failed' THEN 1 ELSE 0 END) / count(*)
    ELSE 0.0 
  END AS err_rate
FROM trace_span
WHERE start_ts >= now() - interval '1 day'
GROUP BY 1;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_span_err_rate_1d_service 
  ON mv_span_err_rate_1d (service);

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_deploy_impact AS
SELECT 
  d.req_id AS deploy_id,
  d.env,
  d.service,
  COALESCE(pre.err_rate, 0.0) AS err_rate_pre,
  COALESCE(post.err_rate, 0.0) AS err_rate_post
FROM deploy_events d
LEFT JOIN mv_span_err_rate_1d pre ON pre.service = d.service
LEFT JOIN mv_span_err_rate_1d post ON post.service = d.service
WHERE d.ts >= now() - interval '7 days';

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_deploy_impact_deploy_id 
  ON mv_deploy_impact (deploy_id);

-- 6) 정리 함수들
CREATE OR REPLACE FUNCTION refresh_trace_materialized_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_span_err_rate_1d;
  REFRESH MATERIALIZED VIEW CONCURRENTLY mv_deploy_impact;
  RAISE NOTICE 'Trace materialized views refreshed';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_trace_data()
RETURNS void AS $$
BEGIN
  -- 1년 이상 된 데이터 아카이브 (실제로는 S3로 이동)
  DELETE FROM trace_span WHERE start_ts < now() - interval '1 year';
  DELETE FROM eval_snapshot WHERE created_at < now() - interval '1 year';
  DELETE FROM trace_edge WHERE created_at < now() - interval '1 year';
  
  -- VACUUM 및 ANALYZE
  VACUUM (ANALYZE) trace_span;
  VACUUM (ANALYZE) eval_snapshot;
  VACUUM (ANALYZE) trace_edge;
  
  RAISE NOTICE 'Old trace data cleaned up and vacuumed';
END;
$$ LANGUAGE plpgsql;
