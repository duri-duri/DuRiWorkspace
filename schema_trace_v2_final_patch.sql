-- Trace v2 "마지막 다듬기" 스키마 패치
-- 선택지 A: PK 대신 UNIQUE 제약조건 사용 (파티션 키 포함 요구 회피)

-- 1) 파티션 테이블 PK 에러 수정 (선택지 A)
-- trace_span: PK 제거, span_id UNIQUE만 유지
ALTER TABLE trace_span DROP CONSTRAINT IF EXISTS trace_span_pkey;
ALTER TABLE trace_span
  ADD CONSTRAINT uq_trace_span_span_id UNIQUE (span_id);

-- eval_snapshot: PK 제거, 운영 조회용 UNIQUE 제약조건
ALTER TABLE eval_snapshot DROP CONSTRAINT IF EXISTS eval_snapshot_pkey;
ALTER TABLE eval_snapshot
  ADD CONSTRAINT uq_eval_snapshot_row UNIQUE (snapshot_id);

-- 2) autovacuum per-table 튜닝
ALTER TABLE trace_span
  SET (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);

ALTER TABLE eval_snapshot
  SET (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);

ALTER TABLE trace_edge
  SET (autovacuum_vacuum_scale_factor=0.05, autovacuum_analyze_scale_factor=0.02);

-- 3) 인덱스 & 쿼리 품질 최적화
CREATE INDEX IF NOT EXISTS idx_span_req_ts ON trace_span (deploy_req_id, start_ts DESC);
CREATE INDEX IF NOT EXISTS idx_span_labels_gin ON trace_span USING GIN (labels jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_eval_daily ON eval_snapshot (window_start, kpi_name, sample_source);
CREATE INDEX IF NOT EXISTS idx_span_status_ts ON trace_span (status, start_ts DESC);
CREATE INDEX IF NOT EXISTS idx_eval_kpi_ts ON eval_snapshot (kpi_name, created_at DESC);

-- 4) 파티션 준비 (3개월 내 적용 예정)
-- trace_span 월별 파티션 템플릿
CREATE TABLE IF NOT EXISTS trace_span_template (
  LIKE trace_span INCLUDING ALL
) PARTITION BY RANGE (start_ts);

-- eval_snapshot 주별 파티션 템플릿
CREATE TABLE IF NOT EXISTS eval_snapshot_template (
  LIKE eval_snapshot INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 5) 운영 대시보드용 추가 인덱스
CREATE INDEX IF NOT EXISTS idx_deploy_events_ts ON deploy_events (ts DESC);
CREATE INDEX IF NOT EXISTS idx_artifact_version ON artifact (version_tag, created_at DESC);

-- 6) 성능 모니터링 뷰 업데이트
CREATE OR REPLACE VIEW v_trace_performance_summary AS
SELECT 
  'trace_span' as table_name,
  count(*) as total_records,
  count(*) FILTER (WHERE start_ts >= now() - interval '1 hour') as last_hour,
  count(*) FILTER (WHERE start_ts >= now() - interval '1 day') as last_day,
  count(*) FILTER (WHERE status = 'failed') as failed_count,
  CASE 
    WHEN count(*) > 0 THEN 1.0 * count(*) FILTER (WHERE status = 'failed') / count(*)
    ELSE 0.0 
  END as error_rate
FROM trace_span
UNION ALL
SELECT 
  'eval_snapshot' as table_name,
  count(*) as total_records,
  count(*) FILTER (WHERE created_at >= now() - interval '1 hour') as last_hour,
  count(*) FILTER (WHERE created_at >= now() - interval '1 day') as last_day,
  0 as failed_count,
  0.0 as error_rate
FROM eval_snapshot;

-- 7) 데이터 품질 체크 함수
CREATE OR REPLACE FUNCTION check_trace_data_quality()
RETURNS TABLE (
  check_name TEXT,
  status TEXT,
  details TEXT
) AS $$
BEGIN
  -- UUID 형식 체크
  RETURN QUERY
  SELECT 
    'uuid_format_check'::TEXT,
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Invalid UUIDs: ' || count(*)::TEXT
  FROM trace_span 
  WHERE span_id !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
  
  -- NULL 필수 필드 체크
  RETURN QUERY
  SELECT 
    'required_fields_check'::TEXT,
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Missing required fields: ' || count(*)::TEXT
  FROM trace_span 
  WHERE span_name IS NULL OR status IS NULL OR start_ts IS NULL;
  
  -- 중복 span_id 체크
  RETURN QUERY
  SELECT 
    'duplicate_span_check'::TEXT,
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Duplicate span_ids: ' || count(*)::TEXT
  FROM (
    SELECT span_id, count(*) 
    FROM trace_span 
    GROUP BY span_id 
    HAVING count(*) > 1
  ) duplicates;
END;
$$ LANGUAGE plpgsql;
