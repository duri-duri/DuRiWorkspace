-- DuRi Memory System - Memory Entries 테이블 생성
-- 실행일: 2025-07-25
-- 목적: DuRi의 기억을 저장하는 기본 테이블

CREATE TABLE IF NOT EXISTS memory_entries (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    context VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    raw_data JSONB,
    source VARCHAR(50) NOT NULL,
    tags JSONB,
    importance_score INTEGER DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_memory_type_source ON memory_entries(type, source);
CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory_entries(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_importance ON memory_entries(importance_score);
CREATE INDEX IF NOT EXISTS idx_memory_source ON memory_entries(source);
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(type);

-- JSONB 인덱스 (태그 검색용)
CREATE INDEX IF NOT EXISTS idx_memory_tags_gin ON memory_entries USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_memory_raw_data_gin ON memory_entries USING GIN(raw_data);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_memory_entries_updated_at 
    BEFORE UPDATE ON memory_entries 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 테이블 코멘트
COMMENT ON TABLE memory_entries IS 'DuRi Memory System - 기억 저장 테이블';
COMMENT ON COLUMN memory_entries.id IS '기본 식별자';
COMMENT ON COLUMN memory_entries.type IS '기억의 종류 (decision, input, log, event, error, success 등)';
COMMENT ON COLUMN memory_entries.context IS '기억의 맥락 (어떤 상황에서 생성됨)';
COMMENT ON COLUMN memory_entries.content IS '핵심 요약 내용';
COMMENT ON COLUMN memory_entries.raw_data IS '상세 데이터 (JSON 형태)';
COMMENT ON COLUMN memory_entries.source IS '이 기억을 만든 주체 (cursor_ai, user, brain, system 등)';
COMMENT ON COLUMN memory_entries.tags IS '관련 키워드들 (JSON 배열)';
COMMENT ON COLUMN memory_entries.importance_score IS '중요도 점수 (0-100)';
COMMENT ON COLUMN memory_entries.created_at IS '생성 시간';
COMMENT ON COLUMN memory_entries.updated_at IS '수정 시간'; 