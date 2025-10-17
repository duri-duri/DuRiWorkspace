-- 평가 고정화 프로토콜 SQL 스키마 확장
-- 실제 컬럼은 없었으니 가벼운 확장 버전 제안 (기존 JSON policy 유지)

-- 1) promotion_decisions: 버전/윈도우/빌드 핀/소스
ALTER TABLE promotion_decisions
  ADD COLUMN IF NOT EXISTS policy_version text,
  ADD COLUMN IF NOT EXISTS window_start timestamptz,
  ADD COLUMN IF NOT EXISTS window_end   timestamptz,
  ADD COLUMN IF NOT EXISTS pipeline_sha text,
  ADD COLUMN IF NOT EXISTS model_sha    text,
  ADD COLUMN IF NOT EXISTS sample_source text DEFAULT 'prod';

-- (선택) policy JSON에서 추출 가능하면 백필 (키 이름은 예시)
UPDATE promotion_decisions
SET
  policy_version = COALESCE(policy->>'version', policy_version),
  window_start   = COALESCE((policy->>'window_start')::timestamptz, window_start),
  window_end     = COALESCE((policy->>'window_end')::timestamptz, window_end)
WHERE TRUE;

-- 2) coach_results: 실험 라벨·빌드 핀
ALTER TABLE coach_results
  ADD COLUMN IF NOT EXISTS model_sha    text,
  ADD COLUMN IF NOT EXISTS pipeline_sha text,
  ADD COLUMN IF NOT EXISTS sample_source text;

-- 3) 인덱스 (최근 조회 & 필터)
CREATE INDEX IF NOT EXISTS idx_promo_decisions_day ON promotion_decisions (date_trunc('day', decision_ts));
CREATE INDEX IF NOT EXISTS idx_promo_decisions_src ON promotion_decisions (sample_source);
CREATE INDEX IF NOT EXISTS idx_coach_results_src_ts ON coach_results (sample_source, ts DESC);

-- 4) 예시: 어제(UTC) 승격판정 요약 쿼리
-- 이후 리포트는 "UTC 어제 00–24h 고정" 윈도우로 뽑으세요:
/*
WITH w AS (
  SELECT date_trunc('day', now() AT TIME ZONE 'UTC')::timestamptz - interval '1 day' AS ws,
         date_trunc('day', now() AT TIME ZONE 'UTC')::timestamptz                     AS we
)
SELECT decision, count(*)
FROM promotion_decisions, w
WHERE decision_ts >= w.ws AND decision_ts < w.we
GROUP BY 1;
*/

-- 5) 추가 유용한 뷰들
CREATE OR REPLACE VIEW v_promotion_daily_summary AS
SELECT 
  date_trunc('day', decision_ts AT TIME ZONE 'UTC')::date AS decision_date,
  decision,
  sample_source,
  COUNT(*) as decision_count,
  AVG(CASE WHEN decision = 'promote' THEN 1.0 ELSE 0.0 END) as promote_rate
FROM promotion_decisions
GROUP BY 1, 2, 3
ORDER BY 1 DESC, 2, 3;

CREATE OR REPLACE VIEW v_coach_daily_summary AS
SELECT 
  date_trunc('day', ts AT TIME ZONE 'UTC')::date AS coach_date,
  sample_source,
  COUNT(*) as coach_count,
  AVG(score) as avg_score,
  MIN(score) as min_score,
  MAX(score) as max_score
FROM coach_results
GROUP BY 1, 2
ORDER BY 1 DESC, 2;
