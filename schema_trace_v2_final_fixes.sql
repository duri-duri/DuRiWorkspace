-- Trace v2 최종 수정: 데이터 품질 함수 + FK 복구
-- 바로 적용 가능한 정리

-- 1) 데이터 품질 함수 수정 (UUID 정규식 오류 해결)
CREATE OR REPLACE FUNCTION check_trace_data_quality()
RETURNS TABLE(check_name text, result text, detail text)
LANGUAGE plpgsql AS $$
BEGIN
  -- 1) UUID 형식 점검 (uuid 컬럼인 경우: 형식보장은 됨 → CAST로만 확인)
  RETURN QUERY
  SELECT
    'uuid_format_check',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Invalid UUIDs (regex): ' || COUNT(*)::text
  FROM trace_span
  WHERE (span_id)::text !~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';

  -- 2) NULL 필수 필드 체크
  RETURN QUERY
  SELECT
    'required_fields_check',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Missing required fields: ' || COUNT(*)::text
  FROM trace_span
  WHERE span_name IS NULL OR status IS NULL OR start_ts IS NULL;

  -- 3) 중복 span_id 체크
  RETURN QUERY
  SELECT
    'duplicate_span_check',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'Duplicate span_ids: ' || COUNT(*)::text
  FROM (
    SELECT span_id, COUNT(*)
    FROM trace_span
    GROUP BY span_id
    HAVING COUNT(*) > 1
  ) duplicates;

  -- 4) FK 위반 체크 (deploy_req_id)
  RETURN QUERY
  SELECT
    'fk_violation_check',
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END,
    'FK violations (deploy_req_id): ' || COUNT(*)::text
  FROM trace_span ts
  LEFT JOIN deploy_events de ON de.req_id = ts.deploy_req_id
  WHERE ts.deploy_req_id IS NOT NULL AND de.req_id IS NULL;
END $$;

-- 2) FK 복구 (안전하게)
-- 단계 A: FK 재추가 (검증은 나중에)
ALTER TABLE trace_span
ADD CONSTRAINT fk_span_deploy
FOREIGN KEY (deploy_req_id)
REFERENCES deploy_events(req_id)
DEFERRABLE INITIALLY DEFERRED
NOT VALID;

-- 3) 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_trace_span_deploy_req_id ON trace_span (deploy_req_id);
CREATE INDEX IF NOT EXISTS idx_deploy_events_req_id ON deploy_events (req_id);

-- 4) 데이터 정리 (FK 위반 레코드 처리)
-- 매칭 안 되는 레코드를 NULL로 정리
UPDATE trace_span ts
SET deploy_req_id = NULL
WHERE ts.deploy_req_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM deploy_events de 
    WHERE de.req_id = ts.deploy_req_id
  );

-- 5) FK 검증 수행
ALTER TABLE trace_span VALIDATE CONSTRAINT fk_span_deploy;
