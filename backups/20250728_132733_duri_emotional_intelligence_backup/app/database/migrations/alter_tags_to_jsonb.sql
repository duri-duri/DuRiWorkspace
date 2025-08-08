-- memory_entries.tags 컬럼을 JSONB로 변경
ALTER TABLE memory_entries ALTER COLUMN tags TYPE JSONB USING tags::jsonb; 