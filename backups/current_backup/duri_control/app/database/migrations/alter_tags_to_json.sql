-- memory_entries.tags 컬럼을 JSON으로 롤백
ALTER TABLE memory_entries ALTER COLUMN tags TYPE JSON USING tags::json; 