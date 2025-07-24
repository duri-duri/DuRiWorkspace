-- DuRi System Database Initialization Script
-- This script creates the necessary tables and indexes for the DuRi system

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS brain;
CREATE SCHEMA IF NOT EXISTS evolution;
CREATE SCHEMA IF NOT EXISTS core;

-- =============================================================================
-- BRAIN SCHEMA TABLES
-- =============================================================================

-- Emotion data table
CREATE TABLE IF NOT EXISTS brain.emotions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emotion_name VARCHAR(50) NOT NULL,
    intensity FLOAT NOT NULL CHECK (intensity >= 0.0 AND intensity <= 1.0),
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    context JSONB,
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Decision data table
CREATE TABLE IF NOT EXISTS brain.decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    emotion_id UUID REFERENCES brain.emotions(id) ON DELETE CASCADE,
    decision_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    reasoning JSONB,
    session_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- EVOLUTION SCHEMA TABLES
-- =============================================================================

-- Experience patterns table
CREATE TABLE IF NOT EXISTS evolution.patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(50) NOT NULL,
    emotion_action_pair VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insights table
CREATE TABLE IF NOT EXISTS evolution.insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    insight_data JSONB,
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge base table
CREATE TABLE IF NOT EXISTS evolution.knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_type VARCHAR(50) NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    value_data JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Execution results table
CREATE TABLE IF NOT EXISTS evolution.execution_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100),
    emotion VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    success BOOLEAN NOT NULL,
    result_score FLOAT NOT NULL,
    execution_time FLOAT NOT NULL,
    feedback_text TEXT,
    context JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- CORE SCHEMA TABLES
-- =============================================================================

-- Sessions table
CREATE TABLE IF NOT EXISTS core.sessions (
    id VARCHAR(100) PRIMARY KEY,
    user_id VARCHAR(100),
    session_data JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- System logs table
CREATE TABLE IF NOT EXISTS core.system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    log_level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Emotion requests table
CREATE TABLE IF NOT EXISTS core.emotion_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    request_data JSONB NOT NULL,
    client_ip VARCHAR(45),
    user_agent TEXT,
    timestamp VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Emotion responses table
CREATE TABLE IF NOT EXISTS core.emotion_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) REFERENCES core.emotion_requests(request_id) ON DELETE CASCADE,
    response_data JSONB NOT NULL,
    processing_time FLOAT,
    status VARCHAR(20) NOT NULL,
    timestamp VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Brain indexes
CREATE INDEX IF NOT EXISTS idx_emotions_session_id ON brain.emotions(session_id);
CREATE INDEX IF NOT EXISTS idx_emotions_created_at ON brain.emotions(created_at);
CREATE INDEX IF NOT EXISTS idx_decisions_emotion_id ON brain.decisions(emotion_id);
CREATE INDEX IF NOT EXISTS idx_decisions_session_id ON brain.decisions(session_id);

-- Evolution indexes
CREATE INDEX IF NOT EXISTS idx_patterns_emotion_action ON evolution.patterns(emotion_action_pair);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON evolution.patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_insights_type ON evolution.insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_key ON evolution.knowledge(key_name);
CREATE INDEX IF NOT EXISTS idx_execution_results_session ON evolution.execution_results(session_id);
CREATE INDEX IF NOT EXISTS idx_execution_results_emotion_action ON evolution.execution_results(emotion, action);

-- Core indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON core.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON core.sessions(status);
CREATE INDEX IF NOT EXISTS idx_system_logs_service ON core.system_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON core.system_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON core.system_logs(created_at);

-- Emotion request/response indexes
CREATE INDEX IF NOT EXISTS idx_emotion_requests_request_id ON core.emotion_requests(request_id);
CREATE INDEX IF NOT EXISTS idx_emotion_requests_emotion ON core.emotion_requests(emotion);
CREATE INDEX IF NOT EXISTS idx_emotion_requests_created_at ON core.emotion_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_emotion_requests_timestamp ON core.emotion_requests(timestamp);
CREATE INDEX IF NOT EXISTS idx_emotion_responses_request_id ON core.emotion_responses(request_id);
CREATE INDEX IF NOT EXISTS idx_emotion_responses_status ON core.emotion_responses(status);
CREATE INDEX IF NOT EXISTS idx_emotion_responses_created_at ON core.emotion_responses(created_at);

-- =============================================================================
-- TRIGGERS FOR UPDATED_AT
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_emotions_updated_at BEFORE UPDATE ON brain.emotions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patterns_updated_at BEFORE UPDATE ON evolution.patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON evolution.knowledge
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON core.sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default knowledge entries
INSERT INTO evolution.knowledge (knowledge_type, key_name, value_data, metadata) VALUES
('system', 'default_learning_rate', '{"value": 0.1}', '{"description": "Default learning rate for evolution system"}'),
('system', 'max_cycles_per_session', '{"value": 100}', '{"description": "Maximum evolution cycles per session"}'),
('system', 'pattern_analysis_interval', '{"value": 300}', '{"description": "Pattern analysis interval in seconds"}')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- GRANTS (if using separate users)
-- =============================================================================

-- Uncomment and modify if using separate database users
-- GRANT USAGE ON SCHEMA brain, evolution, core TO duri_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA brain, evolution, core TO duri_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA brain, evolution, core TO duri_user; 