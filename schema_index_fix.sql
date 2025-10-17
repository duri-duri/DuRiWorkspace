-- SQL IMMUTABLE 에러 수정: 안전한 대체 인덱스 DDL
-- 문제 원인: 인덱스 표현식에 STABLE 함수가 들어감
-- 해결: 시간은 그 자체 컬럼에 B-Tree, JSON 라벨은 단순 추출 표현식으로 인덱싱

-- 기존 문제 인덱스 제거 (있다면)
DROP INDEX IF EXISTS idx_promo_decisions_day;

-- 시간 범위 조회(최근 24h 등)를 위한 기본 인덱스
CREATE INDEX IF NOT EXISTS idx_promo_decisions_ts
  ON promotion_decisions (decision_ts);

-- policy_version 라벨(예: jsonb 컬럼 "policy" 안에 키 "version"이라 가정)
-- ->> 추출은 IMMUTABLE 이어서 expression index 가능
CREATE INDEX IF NOT EXISTS idx_promo_policy_version
  ON promotion_decisions ((policy->>'version'));

-- coach_results: 최근 24h, exp별 집계에 유용
CREATE INDEX IF NOT EXISTS idx_coach_results_ts
  ON coach_results (ts DESC);

CREATE INDEX IF NOT EXISTS idx_coach_results_exp_ts
  ON coach_results (exp_id, ts DESC);

-- 머티리얼라이즈드 뷰로 일일 스냅샷 (운영적으로 안전)
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_promo_decisions_daily AS
SELECT date_trunc('day', decision_ts) AS d,
       count(*) AS n,
       decision,
       sample_source,
       (array_agg(policy))[1] AS sample_policy   -- 운영상 샘플 확인용
FROM promotion_decisions
GROUP BY 1, 3, 4;

-- 머티리얼라이즈드 뷰 인덱스
CREATE INDEX IF NOT EXISTS idx_mv_promo_decisions_daily_d
  ON mv_promo_decisions_daily (d DESC);

-- 주기적 REFRESH를 위한 함수 (선택사항)
CREATE OR REPLACE FUNCTION refresh_promo_daily_mv()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW mv_promo_decisions_daily;
END;
$$ LANGUAGE plpgsql;
