-- Trace v2 백필: 기존 테이블에서 eval_snapshot으로 데이터 이전
-- promotion_decisions, coach_results → eval_snapshot

-- 1) promotion_decisions → eval_snapshot 백필
-- 일자 고정 윈도우로 평균 score/판정 비율 계산 후 스냅샷으로 적재
WITH base AS (
  SELECT
    date_trunc('day', decision_ts) AS day,
    COALESCE(policy->>'version','v1.0') AS policy_version,
    decision,
    count(*) AS n
  FROM promotion_decisions
  WHERE decision_ts >= now() - interval '7 days'
  GROUP BY 1,2,3
),
agg AS (
  SELECT day, policy_version,
         sum(n) AS total,
         1.0*sum(CASE WHEN decision='promote' THEN n ELSE 0 END)/NULLIF(sum(n),0) AS promote_rate
  FROM base
  GROUP BY 1,2
)
INSERT INTO eval_snapshot (snapshot_id, span_id, window_start, window_end,
                           policy_version, sample_source, kpi_name,
                           kpi_value, n_samples, meta)
SELECT
  uuid_generate_v4(),
  NULL,                    -- 연결할 span 있으면 채우세요
  day, day + interval '1 day',
  policy_version,
  'prod',
  'promote_rate',
  promote_rate,
  total,
  jsonb_build_object('source','promotion_decisions')
FROM agg;

-- 2) coach_results → eval_snapshot 백필
-- Shadow/Prod 분리 KPI(예: 평균 score) 적재
WITH w AS (
  SELECT
    date_trunc('day', ts) AS day,
    COALESCE(sample_source,'unknown') AS sample_source,
    avg(score)::numeric(12,6) AS avg_score,
    count(*) AS n
  FROM coach_results
  WHERE ts >= now() - interval '7 days'
  GROUP BY 1,2
)
INSERT INTO eval_snapshot (snapshot_id, span_id, window_start, window_end,
                           policy_version, sample_source, kpi_name,
                           kpi_value, n_samples, meta)
SELECT
  uuid_generate_v4(),
  NULL,      -- span 연동 시 업데이트
  day, day + interval '1 day',
  'v1.0',
  sample_source,
  'coach_avg_score',
  avg_score,
  n,
  jsonb_build_object('source','coach_results')
FROM w;

-- 3) 배포 이벤트 백필 (기존 deploy_events가 있다면)
-- dori-dora-exporter에서 이미 수집된 배포 이벤트들을 trace_span과 연결
INSERT INTO trace_span (span_id, parent_span_id, deploy_req_id, span_name, status, start_ts, end_ts, labels, attrs)
SELECT 
  uuid_generate_v4(),
  NULL,
  req_id,
  'deploy_root',
  'success',
  ts,
  ts,
  jsonb_build_object('service', service, 'env', env, 'source', source),
  jsonb_build_object('commit', commit, 'node_id', node_id, 'pipeline', pipeline)
FROM deploy_events
WHERE req_id NOT IN (SELECT deploy_req_id FROM trace_span WHERE deploy_req_id IS NOT NULL)
  AND ts >= now() - interval '7 days';

-- 4) 백필 결과 확인
SELECT 
  'promotion_decisions' as source_table,
  count(*) as records_backfilled
FROM eval_snapshot 
WHERE meta->>'source' = 'promotion_decisions'
UNION ALL
SELECT 
  'coach_results' as source_table,
  count(*) as records_backfilled
FROM eval_snapshot 
WHERE meta->>'source' = 'coach_results'
UNION ALL
SELECT 
  'deploy_events' as source_table,
  count(*) as records_backfilled
FROM trace_span 
WHERE span_name = 'deploy_root';
