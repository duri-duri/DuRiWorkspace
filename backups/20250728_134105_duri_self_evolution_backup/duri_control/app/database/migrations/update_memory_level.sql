-- DuRi Memory System - 기억 레벨 시스템 업데이트
-- 실행일: 2025-07-25
-- 목적: 3단계 기억 레벨 시스템 구현

-- memory_level 컬럼 추가
ALTER TABLE memory_entries 
ADD COLUMN IF NOT EXISTS memory_level VARCHAR(20) DEFAULT 'short' NOT NULL;

-- memory_level 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_memory_level ON memory_entries(memory_level);

-- 만료 시간 컬럼 추가 (단기 기억용)
ALTER TABLE memory_entries 
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;

-- 만료 시간 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_memory_expires_at ON memory_entries(expires_at);

-- 승격 횟수 컬럼 추가 (중기 기억 승격 추적용)
ALTER TABLE memory_entries 
ADD COLUMN IF NOT EXISTS promotion_count INTEGER DEFAULT 0;

-- 승격 횟수 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_memory_promotion_count ON memory_entries(promotion_count);

-- 복합 인덱스 생성 (레벨별 조회 최적화)
CREATE INDEX IF NOT EXISTS idx_memory_level_created ON memory_entries(memory_level, created_at);
CREATE INDEX IF NOT EXISTS idx_memory_level_importance ON memory_entries(memory_level, importance_score);

-- 기존 데이터를 단기 기억으로 설정
UPDATE memory_entries 
SET memory_level = 'short', 
    expires_at = created_at + INTERVAL '24 hours'
WHERE memory_level IS NULL;

-- 테이블 코멘트 업데이트
COMMENT ON COLUMN memory_entries.memory_level IS '기억 레벨 (short/medium/truth)';
COMMENT ON COLUMN memory_entries.expires_at IS '만료 시간 (단기 기억용)';
COMMENT ON COLUMN memory_entries.promotion_count IS '승격 횟수 (중기 기억 승격 추적용)';

-- 만료된 단기 기억 삭제 함수
CREATE OR REPLACE FUNCTION cleanup_expired_memories()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM memory_entries 
    WHERE memory_level = 'short' 
      AND expires_at IS NOT NULL 
      AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 만료된 기억 자동 정리 (매일 실행)
-- SELECT cleanup_expired_memories(); 