-- DuRi Memory System - Analysis Tables Migration
-- 통계/패턴 분석 전용 저장소 테이블 생성

-- 1. 분석 결과 테이블
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(100) UNIQUE NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    parameters JSONB,
    results JSONB,
    execution_time_ms INTEGER,
    memory_usage_mb DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 패턴 캐시 테이블
CREATE TABLE IF NOT EXISTS pattern_cache (
    id SERIAL PRIMARY KEY,
    pattern_hash VARCHAR(64) UNIQUE NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    frequency INTEGER DEFAULT 1,
    confidence_score DECIMAL(5,4),
    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_ids INTEGER[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 성능 메트릭 테이블
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(20),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 상관관계 분석 테이블
CREATE TABLE IF NOT EXISTS correlation_analysis (
    id SERIAL PRIMARY KEY,
    correlation_id VARCHAR(100) UNIQUE NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    correlation_strength DECIMAL(5,4),
    confidence_score DECIMAL(5,4),
    sample_size INTEGER,
    analysis_window_hours INTEGER,
    correlation_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 분석 통계 테이블
CREATE TABLE IF NOT EXISTS analysis_statistics (
    id SERIAL PRIMARY KEY,
    stat_date DATE DEFAULT CURRENT_DATE,
    analysis_type VARCHAR(50) NOT NULL,
    total_analyses INTEGER DEFAULT 0,
    successful_analyses INTEGER DEFAULT 0,
    failed_analyses INTEGER DEFAULT 0,
    avg_execution_time_ms INTEGER,
    avg_memory_usage_mb DECIMAL(10,2),
    patterns_found INTEGER DEFAULT 0,
    correlations_found INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stat_date, analysis_type)
);

-- 6. 분석 작업 큐 테이블
CREATE TABLE IF NOT EXISTS analysis_queue (
    id SERIAL PRIMARY KEY,
    queue_id VARCHAR(100) UNIQUE NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    parameters JSONB,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_id ON analysis_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_type ON analysis_results(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_results_status ON analysis_results(status);
CREATE INDEX IF NOT EXISTS idx_analysis_results_timestamp ON analysis_results(analysis_timestamp);

CREATE INDEX IF NOT EXISTS idx_pattern_cache_hash ON pattern_cache(pattern_hash);
CREATE INDEX IF NOT EXISTS idx_pattern_cache_type ON pattern_cache(pattern_type);
CREATE INDEX IF NOT EXISTS idx_pattern_cache_frequency ON pattern_cache(frequency);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(metric_timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_type ON performance_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);

CREATE INDEX IF NOT EXISTS idx_correlation_analysis_id ON correlation_analysis(correlation_id);
CREATE INDEX IF NOT EXISTS idx_correlation_analysis_source ON correlation_analysis(source_type);
CREATE INDEX IF NOT EXISTS idx_correlation_analysis_target ON correlation_analysis(target_type);

CREATE INDEX IF NOT EXISTS idx_analysis_statistics_date ON analysis_statistics(stat_date);
CREATE INDEX IF NOT EXISTS idx_analysis_statistics_type ON analysis_statistics(analysis_type);

CREATE INDEX IF NOT EXISTS idx_analysis_queue_id ON analysis_queue(queue_id);
CREATE INDEX IF NOT EXISTS idx_analysis_queue_status ON analysis_queue(status);
CREATE INDEX IF NOT EXISTS idx_analysis_queue_priority ON analysis_queue(priority);

-- 트리거 함수 생성 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pattern_cache_updated_at 
    BEFORE UPDATE ON pattern_cache 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_correlation_analysis_updated_at 
    BEFORE UPDATE ON correlation_analysis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_statistics_updated_at 
    BEFORE UPDATE ON analysis_statistics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_queue_updated_at 
    BEFORE UPDATE ON analysis_queue 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 초기 데이터 삽입
INSERT INTO analysis_statistics (stat_date, analysis_type, total_analyses, successful_analyses, failed_analyses)
VALUES (CURRENT_DATE, 'pattern', 0, 0, 0),
       (CURRENT_DATE, 'correlation', 0, 0, 0),
       (CURRENT_DATE, 'performance', 0, 0, 0),
       (CURRENT_DATE, 'comprehensive', 0, 0, 0)
ON CONFLICT (stat_date, analysis_type) DO NOTHING;

-- 성능 메트릭 초기 데이터
INSERT INTO performance_metrics (metric_type, metric_name, metric_value, metric_unit)
VALUES ('system', 'total_memories', 0, 'count'),
       ('system', 'avg_importance', 0, 'score'),
       ('system', 'memory_compression_ratio', 1.0, 'ratio'),
       ('system', 'analysis_queue_size', 0, 'count')
ON CONFLICT DO NOTHING; 