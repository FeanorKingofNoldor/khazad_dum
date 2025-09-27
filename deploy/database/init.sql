-- =============================================================================
-- KHAZAD-DÛM DATABASE INITIALIZATION
-- Production PostgreSQL schema for trading system
-- =============================================================================

-- Set timezone to UTC for consistent timestamps
SET timezone = 'UTC';

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create database user (if not exists from environment)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'khazad_user') THEN
        CREATE USER khazad_user WITH ENCRYPTED PASSWORD 'secure_password_change_me';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE khazad_dum TO khazad_user;

-- =============================================================================
-- CORE TRADING TABLES
-- =============================================================================

-- Stock metrics and market data
CREATE TABLE IF NOT EXISTS stock_metrics (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    price DECIMAL(10, 2),
    volume BIGINT,
    market_cap BIGINT,
    rsi_2 DECIMAL(5, 2),
    rsi_14 DECIMAL(5, 2),
    volume_ratio DECIMAL(5, 2),
    price_change_pct DECIMAL(5, 2),
    technical_score DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),
    fear_greed_index INTEGER,
    regime VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_symbol_timestamp (symbol, timestamp),
    INDEX idx_regime (regime),
    INDEX idx_created_at (created_at)
);

-- TradingAgents analysis results
CREATE TABLE IF NOT EXISTS tradingagents_analysis_results (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    analysis_date DATE NOT NULL,
    decision VARCHAR(20) NOT NULL,
    conviction_score DECIMAL(3, 2),
    entry_price DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    stop_loss DECIMAL(10, 2),
    position_size_pct DECIMAL(5, 2),
    analysis_summary TEXT,
    fundamental_analysis JSONB,
    technical_analysis JSONB,
    sentiment_analysis JSONB,
    risk_analysis JSONB,
    pattern_id UUID,
    regime VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_batch_symbol (batch_id, symbol),
    INDEX idx_decision (decision),
    INDEX idx_analysis_date (analysis_date),
    INDEX idx_pattern_id (pattern_id)
);

-- Position tracking for live trades
CREATE TABLE IF NOT EXISTS position_tracking (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    entry_date DATE NOT NULL,
    exit_date DATE,
    entry_price DECIMAL(10, 2) NOT NULL,
    exit_price DECIMAL(10, 2),
    quantity INTEGER NOT NULL,
    position_size_dollars DECIMAL(12, 2) NOT NULL,
    stop_loss DECIMAL(10, 2),
    target_price DECIMAL(10, 2),
    conviction_score DECIMAL(3, 2),
    regime VARCHAR(20),
    pattern_id UUID,
    status VARCHAR(20) DEFAULT 'OPEN',
    pnl_dollars DECIMAL(12, 2),
    pnl_pct DECIMAL(5, 2),
    hold_days INTEGER,
    exit_reason VARCHAR(50),
    batch_id VARCHAR(50),
    ibkr_order_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_symbol_status (symbol, status),
    INDEX idx_entry_date (entry_date),
    INDEX idx_exit_date (exit_date),
    INDEX idx_pattern_id (pattern_id),
    INDEX idx_batch_id (batch_id)
);

-- =============================================================================
-- PATTERN RECOGNITION TABLES
-- =============================================================================

-- Pattern performance tracking
CREATE TABLE IF NOT EXISTS pattern_performance (
    id SERIAL PRIMARY KEY,
    pattern_id UUID NOT NULL DEFAULT uuid_generate_v4(),
    pattern_name VARCHAR(100) NOT NULL,
    pattern_type VARCHAR(50),
    regime VARCHAR(20),
    volume_profile VARCHAR(20),
    rsi_condition VARCHAR(20),
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 4),
    avg_return_pct DECIMAL(5, 2),
    avg_hold_days DECIMAL(4, 1),
    total_pnl DECIMAL(12, 2) DEFAULT 0,
    expectancy DECIMAL(5, 4),
    recent_trades INTEGER DEFAULT 0,
    recent_win_rate DECIMAL(5, 4),
    momentum DECIMAL(5, 4) DEFAULT 0,
    confidence_level VARCHAR(10),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    last_trade_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(pattern_name, regime, volume_profile, rsi_condition),
    INDEX idx_pattern_id (pattern_id),
    INDEX idx_pattern_type (pattern_type),
    INDEX idx_regime (regime),
    INDEX idx_win_rate (win_rate),
    INDEX idx_status (status)
);

-- Pattern memory injection log
CREATE TABLE IF NOT EXISTS pattern_memories (
    id SERIAL PRIMARY KEY,
    pattern_id UUID NOT NULL REFERENCES pattern_performance(pattern_id),
    memory_content TEXT NOT NULL,
    injection_date DATE NOT NULL,
    trades_count INTEGER,
    win_rate DECIMAL(5, 4),
    expectancy DECIMAL(5, 4),
    relevance_score DECIMAL(3, 2),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_pattern_id (pattern_id),
    INDEX idx_injection_date (injection_date),
    INDEX idx_status (status)
);

-- =============================================================================
-- PIPELINE OBSERVABILITY TABLES
-- =============================================================================

-- Complete pipeline decision tracking
CREATE TABLE IF NOT EXISTS pipeline_decisions (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    stage VARCHAR(30) NOT NULL,
    decision_data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_batch_symbol (batch_id, symbol),
    INDEX idx_stage (stage),
    INDEX idx_timestamp (timestamp)
);

-- System performance metrics
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(12, 4),
    metric_unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_metric_name (metric_name),
    INDEX idx_timestamp (timestamp)
);

-- API usage and cost tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    endpoint VARCHAR(100),
    request_count INTEGER DEFAULT 1,
    estimated_cost DECIMAL(8, 4),
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    hour INTEGER NOT NULL DEFAULT EXTRACT(HOUR FROM CURRENT_TIMESTAMP),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_provider_date (provider, date),
    INDEX idx_endpoint (endpoint),
    INDEX idx_date_hour (date, hour)
);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Active positions summary
CREATE OR REPLACE VIEW active_positions AS
SELECT 
    symbol,
    entry_date,
    entry_price,
    quantity,
    position_size_dollars,
    stop_loss,
    target_price,
    conviction_score,
    regime,
    CURRENT_DATE - entry_date AS days_held,
    CASE 
        WHEN stop_loss IS NOT NULL THEN 
            ROUND(((stop_loss - entry_price) / entry_price * 100)::numeric, 2)
        ELSE NULL 
    END AS stop_loss_pct,
    CASE 
        WHEN target_price IS NOT NULL THEN 
            ROUND(((target_price - entry_price) / entry_price * 100)::numeric, 2)
        ELSE NULL 
    END AS target_pct
FROM position_tracking 
WHERE status = 'OPEN'
ORDER BY entry_date DESC;

-- Pattern performance summary
CREATE OR REPLACE VIEW pattern_summary AS
SELECT 
    pattern_name,
    pattern_type,
    regime,
    total_trades,
    win_rate,
    avg_return_pct,
    expectancy,
    confidence_level,
    status,
    CASE 
        WHEN momentum > 0.10 THEN 'HOT'
        WHEN momentum < -0.10 THEN 'COLD'
        ELSE 'STABLE'
    END AS trend,
    last_trade_date
FROM pattern_performance 
WHERE total_trades >= 5
ORDER BY expectancy DESC, win_rate DESC;

-- Daily trading summary
CREATE OR REPLACE VIEW daily_summary AS
SELECT 
    DATE(created_at) AS trade_date,
    COUNT(*) AS total_trades,
    COUNT(CASE WHEN decision = 'BUY' THEN 1 END) AS buy_signals,
    COUNT(CASE WHEN decision = 'SELL' THEN 1 END) AS sell_signals,
    AVG(conviction_score) AS avg_conviction,
    regime
FROM tradingagents_analysis_results
GROUP BY DATE(created_at), regime
ORDER BY trade_date DESC;

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Update updated_at timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at column
CREATE TRIGGER update_position_tracking_updated_at 
    BEFORE UPDATE ON position_tracking 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pattern_performance_updated_at 
    BEFORE UPDATE ON pattern_performance 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate pattern performance
CREATE OR REPLACE FUNCTION update_pattern_performance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update pattern performance when position is closed
    IF NEW.status = 'CLOSED' AND OLD.status = 'OPEN' AND NEW.pattern_id IS NOT NULL THEN
        UPDATE pattern_performance 
        SET 
            total_trades = total_trades + 1,
            winning_trades = CASE WHEN NEW.pnl_pct > 0 THEN winning_trades + 1 ELSE winning_trades END,
            losing_trades = CASE WHEN NEW.pnl_pct <= 0 THEN losing_trades + 1 ELSE losing_trades END,
            win_rate = CASE WHEN total_trades + 1 > 0 THEN 
                (winning_trades + CASE WHEN NEW.pnl_pct > 0 THEN 1 ELSE 0 END)::DECIMAL / (total_trades + 1)
                ELSE 0 END,
            total_pnl = total_pnl + COALESCE(NEW.pnl_dollars, 0),
            avg_return_pct = (avg_return_pct * total_trades + COALESCE(NEW.pnl_pct, 0)) / (total_trades + 1),
            avg_hold_days = (avg_hold_days * total_trades + COALESCE(NEW.hold_days, 0)) / (total_trades + 1),
            last_trade_date = NEW.exit_date,
            updated_at = CURRENT_TIMESTAMP
        WHERE pattern_id = NEW.pattern_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply pattern performance trigger
CREATE TRIGGER update_pattern_performance_trigger 
    AFTER UPDATE ON position_tracking 
    FOR EACH ROW EXECUTE FUNCTION update_pattern_performance();

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Additional composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_stock_metrics_symbol_timestamp 
    ON stock_metrics (symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_tradingagents_batch_decision 
    ON tradingagents_analysis_results (batch_id, decision);

CREATE INDEX IF NOT EXISTS idx_position_tracking_date_status 
    ON position_tracking (entry_date DESC, status);

CREATE INDEX IF NOT EXISTS idx_pattern_performance_composite 
    ON pattern_performance (pattern_type, regime, status, win_rate DESC);

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant table permissions to khazad_user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO khazad_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO khazad_user;
GRANT SELECT ON ALL TABLES IN SCHEMA information_schema TO khazad_user;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO khazad_user;

-- Grant permissions on views
GRANT SELECT ON active_positions TO khazad_user;
GRANT SELECT ON pattern_summary TO khazad_user;
GRANT SELECT ON daily_summary TO khazad_user;

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default pattern types if they don't exist
INSERT INTO pattern_performance (pattern_name, pattern_type, regime, volume_profile, rsi_condition, status)
VALUES 
    ('Default Mean Reversion', 'mean_reversion', 'neutral', 'normal', 'oversold', 'ACTIVE'),
    ('Default Momentum', 'momentum', 'neutral', 'high', 'neutral', 'ACTIVE'),
    ('Default Breakout', 'breakout', 'neutral', 'explosive', 'neutral', 'ACTIVE'),
    ('Fear Buy Pattern', 'mean_reversion', 'extreme_fear', 'low', 'oversold', 'ACTIVE'),
    ('Greed Fade Pattern', 'mean_reversion', 'extreme_greed', 'high', 'overbought', 'ACTIVE')
ON CONFLICT (pattern_name, regime, volume_profile, rsi_condition) DO NOTHING;

-- =============================================================================
-- MAINTENANCE SETUP
-- =============================================================================

-- Create maintenance log table
CREATE TABLE IF NOT EXISTS maintenance_log (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details TEXT,
    records_affected INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

GRANT SELECT, INSERT ON maintenance_log TO khazad_user;

-- Success message
INSERT INTO maintenance_log (operation, status, details) 
VALUES ('database_initialization', 'SUCCESS', 'Database schema created successfully');

COMMIT;