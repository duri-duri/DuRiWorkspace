-- Trace v2 스키마 초안: ERD → 핵심 DDL → 최소 ETL 스켈레톤 → 롤업/백필
-- IMMUTABLE-safe 인덱스, 안전한 FK 제약조건, 운영 대시보드 뷰 포함

-- 0) 확장/스키마
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1) 배포 이벤트
CREATE TABLE IF NOT EXISTS deploy_events (
  req_id           text PRIMARY KEY,            -- 중복 방지용 고유 요청 ID
  env              text NOT NULL,               -- prod|staging|...
  service          text NOT NULL,
  source           text NOT NULL,               -- ci|manual|...
  commit           text NOT NULL,               -- git sha (short/long OK)
  node_id          text,                        -- 호출 노드/러너
  pipeline         text,                        -- 파이프라인 라벨
  ts               timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_deploy_events_ts ON deploy_events (ts DESC);
CREATE INDEX IF NOT EXISTS idx_deploy_events_env_ts ON deploy_events (env, ts DESC);

-- 2) 산출물(모델/이미지/스크립트 등)
CREATE TABLE IF NOT EXISTS artifact (
  artifact_id      uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  kind             text NOT NULL,              -- model|image|script|dataset
  name             text NOT NULL,
  version_tag      text,                        -- v1.2, 2025-10-17, etc.
  model_sha        text,
  pipeline_sha     text,
  meta             jsonb,                       -- 추가 속성
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_artifact_name ON artifact (name);
CREATE INDEX IF NOT EXISTS idx_artifact_kind_name ON artifact (kind, name);

-- 3) 스팬(작업/평가/잡 단위)
CREATE TABLE IF NOT EXISTS trace_span (
  span_id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  parent_span_id   uuid,                           -- 루트면 NULL
  deploy_req_id    text,                           -- deploy_events.req_id (옵션)
  artifact_id      uuid,                           -- artifact.artifact_id (옵션)
  span_name        text NOT NULL,                  -- e.g., "coach_batch", "gate_eval"
  status           text NOT NULL DEFAULT 'running',-- running|success|failed|canceled
  start_ts         timestamptz NOT NULL DEFAULT now(),
  end_ts           timestamptz,                    -- 종료 시 세팅
  labels           jsonb,                          -- {source:"shadow", node:"...", ...}
  attrs            jsonb                            -- 기타 속성(빠르게 넣고 나중에 정제)
);
ALTER TABLE trace_span
  ADD CONSTRAINT fk_span_parent FOREIGN KEY (parent_span_id) REFERENCES trace_span(span_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE trace_span
  ADD CONSTRAINT fk_span_deploy FOREIGN KEY (deploy_req_id) REFERENCES deploy_events(req_id) DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE trace_span
  ADD CONSTRAINT fk_span_artifact FOREIGN KEY (artifact_id) REFERENCES artifact(artifact_id) DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX IF NOT EXISTS idx_span_start_ts ON trace_span (start_ts DESC);
CREATE INDEX IF NOT EXISTS idx_span_end_ts ON trace_span (end_ts DESC);
CREATE INDEX IF NOT EXISTS idx_span_status_ts ON trace_span (status, start_ts DESC);
-- JSONB path 인덱스(IMMUTABLE-safe): 라벨/속성 질의용
CREATE INDEX IF NOT EXISTS idx_span_labels_gin ON trace_span USING GIN (labels jsonb_path_ops);
CREATE INDEX IF NOT EXISTS idx_span_attrs_gin  ON trace_span USING GIN (attrs  jsonb_path_ops);

-- 4) 스팬 간 엣지 (DAG/트리)
CREATE TABLE IF NOT EXISTS trace_edge (
  parent_span_id   uuid NOT NULL,
  child_span_id    uuid NOT NULL,
  PRIMARY KEY (parent_span_id, child_span_id),
  created_at       timestamptz NOT NULL DEFAULT now(),
  meta             jsonb
);
ALTER TABLE trace_edge
  ADD CONSTRAINT fk_edge_parent FOREIGN KEY (parent_span_id) REFERENCES trace_span(span_id) ON DELETE CASCADE;
ALTER TABLE trace_edge
  ADD CONSTRAINT fk_edge_child  FOREIGN KEY (child_span_id)  REFERENCES trace_span(span_id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_edge_parent ON trace_edge (parent_span_id);
CREATE INDEX IF NOT EXISTS idx_edge_child  ON trace_edge (child_span_id);

-- 5) 평가 스냅샷(윈도우/정책 고정)
CREATE TABLE IF NOT EXISTS eval_snapshot (
  snapshot_id      uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  span_id          uuid NOT NULL,             -- 어떤 span의 결과인지(배치/평가잡 등)
  window_start     timestamptz NOT NULL,
  window_end       timestamptz NOT NULL,
  policy_version   text NOT NULL,             -- v1.2 같은 문자열
  sample_source    text,                      -- shadow|prod|synthetic
  kpi_name         text NOT NULL,             -- "accuracy", "latency_p95", ...
  kpi_value        numeric(12,6) NOT NULL,
  n_samples        integer,
  meta             jsonb,
  created_at       timestamptz NOT NULL DEFAULT now()
);
ALTER TABLE eval_snapshot
  ADD CONSTRAINT fk_eval_span FOREIGN KEY (span_id) REFERENCES trace_span(span_id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_eval_span ON eval_snapshot (span_id);
CREATE INDEX IF NOT EXISTS idx_eval_kpi_window ON eval_snapshot (kpi_name, window_start, window_end);
CREATE INDEX IF NOT EXISTS idx_eval_policy ON eval_snapshot (policy_version);
CREATE INDEX IF NOT EXISTS idx_eval_src ON eval_snapshot (sample_source);
CREATE INDEX IF NOT EXISTS idx_eval_created ON eval_snapshot (created_at DESC);

-- 6) 일자 롤업 뷰(절대일 기준) - date_trunc은 VIEW에서만 사용 (인덱스 X)
CREATE OR REPLACE VIEW v_eval_daily AS
SELECT
  kpi_name,
  policy_version,
  sample_source,
  date_trunc('day', window_start) AS day,
  avg(kpi_value) AS avg_value,
  sum(n_samples) AS total_samples,
  count(*) AS windows
FROM eval_snapshot
GROUP BY 1,2,3,4;

-- 7) 운영 대시보드용 뷰들
CREATE OR REPLACE VIEW v_trace_service_daily AS
SELECT
  COALESCE(labels->>'service', 'unknown') AS service,
  date_trunc('day', start_ts)::date AS day,
  count(*) AS spans,
  avg(EXTRACT(EPOCH FROM (COALESCE(end_ts, now()) - start_ts)))::int AS avg_sec,
  sum(CASE WHEN status='failed' THEN 1 ELSE 0 END)::int AS errors
FROM trace_span
GROUP BY 1,2;

CREATE OR REPLACE VIEW v_deploy_trace_summary AS
SELECT d.req_id, d.service, d.commit, d.ts AS deploy_ts,
       t.span_id AS root_span_id,
       (SELECT count(*) FROM trace_span s WHERE s.deploy_req_id = d.req_id) AS trace_spans
FROM deploy_events d
LEFT JOIN trace_span t ON t.deploy_req_id = d.req_id AND t.parent_span_id IS NULL;
