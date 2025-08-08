-- memory_entries.tags 컬럼을 완전히 재생성 (JSONB)
ALTER TABLE memory_entries DROP COLUMN IF EXISTS tags;
ALTER TABLE memory_entries ADD COLUMN tags JSONB; 