-- Coach→Bench→Learn 시스템 스키마 (실전 투입형)
-- 실험 ID: YYYYMMDD.hhmm-coachX-benchY-learnZ

-- 평가 아이템 (정답셋)
CREATE TABLE IF NOT EXISTS eval_items (
  id BIGSERIAL PRIMARY KEY,
  task TEXT NOT NULL,
  gold_answer JSONB NOT NULL,
  grader JSONB NOT NULL,         -- {type: 'rule'|'regex'|'sql', spec: {...}}
  max_latency_ms INT DEFAULT 4000,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Coach 실행 기록
CREATE TABLE IF NOT EXISTS coach_runs (
  id BIGSERIAL PRIMARY KEY,
  exp_id TEXT NOT NULL,
  ts TIMESTAMPTZ DEFAULT now(),
  sample_count INT,
  token_input BIGINT,
  token_output BIGINT,
  cost NUMERIC(10,5),
  notes TEXT
);

-- Coach 결과 (개별 아이템별)
CREATE TABLE IF NOT EXISTS coach_results (
  id BIGSERIAL PRIMARY KEY,
  exp_id TEXT NOT NULL,
  item_id BIGINT REFERENCES eval_items(id),
  prompt JSONB,
  answer JSONB,           -- {text, tool_calls:[], tool_digest:"..."}
  score NUMERIC(4,3),     -- 0~1 (partial 허용)
  latency_ms INT,
  policy_violations INT DEFAULT 0,
  tool_required BOOL,
  tool_used BOOL,
  tool_ok BOOL,
  ts TIMESTAMPTZ DEFAULT now()
);

-- 선호쌍 (DPO/RLAIF용)
CREATE TABLE IF NOT EXISTS prefs (
  id BIGSERIAL PRIMARY KEY,
  exp_id TEXT NOT NULL,
  prompt TEXT NOT NULL,
  chosen TEXT NOT NULL,
  rejected TEXT NOT NULL,
  rationale TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_coach_results_exp_id ON coach_results(exp_id);
CREATE INDEX IF NOT EXISTS idx_coach_results_ts ON coach_results(ts);
CREATE INDEX IF NOT EXISTS idx_eval_items_tags ON eval_items USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_prefs_exp_id ON prefs(exp_id);

-- PII 마스킹 함수 (데이터 보존/프라이버시)
CREATE OR REPLACE FUNCTION mask_pii(text) RETURNS text AS $$
BEGIN
  -- 전화번호 패턴 마스킹 (010-1234-5678 → 010-****-5678)
  $1 := regexp_replace($1, '(\d{3})-(\d{4})-(\d{4})', '\1-****-\3', 'g');
  -- 이메일 패턴 마스킹 (user@domain.com → u***@domain.com)
  $1 := regexp_replace($1, '([a-zA-Z])[a-zA-Z0-9._%+-]*@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', '\1***@\2', 'g');
  -- 주민번호 패턴 마스킹 (123456-1234567 → 123456-*******)
  $1 := regexp_replace($1, '(\d{6})-(\d{7})', '\1-*******', 'g');
  RETURN $1;
END;
$$ LANGUAGE plpgsql;
