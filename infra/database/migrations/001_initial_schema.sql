-- ============================================================
-- Migration 001: Core Schema
-- ============================================================
-- Users, system settings, audit logs
-- ============================================================

-- Users table (single user, but extensible)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    settings_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- System settings (key-value store)
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Risk configuration
CREATE TABLE IF NOT EXISTS risk_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    max_risk_per_trade_pct DECIMAL(5,2) DEFAULT 2.0,
    max_daily_drawdown_pct DECIMAL(5,2) DEFAULT 3.0,
    max_open_positions INTEGER DEFAULT 10,
    max_sector_exposure_pct DECIMAL(5,2) DEFAULT 30.0,
    position_size_method VARCHAR(50) DEFAULT 'kelly_capped',
    emergency_halt_drawdown_pct DECIMAL(5,2) DEFAULT 5.0,
    is_emergency_halt_active BOOLEAN DEFAULT false,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default risk config
INSERT INTO risk_config (
    max_risk_per_trade_pct, max_daily_drawdown_pct, max_open_positions,
    max_sector_exposure_pct, position_size_method, emergency_halt_drawdown_pct
) VALUES (2.0, 3.0, 10, 30.0, 'kelly_capped', 5.0)
ON CONFLICT DO NOTHING;

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
    ('trading_mode', '"paper"', 'Trading mode: paper, approval, or auto'),
    ('data_provider', '"yfinance"', 'Market data provider'),
    ('timezone', '"Asia/Kolkata"', 'System timezone'),
    ('notifications_enabled', 'true', 'Enable/disable all notifications'),
    ('telegram_enabled', 'false', 'Enable Telegram notifications'),
    ('auto_signal_generation', 'true', 'Auto-generate signals after data refresh')
ON CONFLICT (key) DO NOTHING;
