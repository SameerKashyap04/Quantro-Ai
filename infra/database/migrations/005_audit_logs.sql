-- ============================================================
-- Migration 005: Audit Logs
-- ============================================================

-- Audit trail for all important actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'auth', 'order', 'signal', 'settings', 'system'
    severity VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
    details_json JSONB DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_category ON audit_logs(category);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_logs(severity);

-- System log for scheduled jobs, errors, etc.
CREATE TABLE IF NOT EXISTS system_logs (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL, -- 'market_data', 'signal_engine', 'ai_engine', etc.
    level VARCHAR(20) NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    message TEXT NOT NULL,
    details_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_syslog_source ON system_logs(source);
CREATE INDEX IF NOT EXISTS idx_syslog_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_syslog_created ON system_logs(created_at DESC);

-- Notification log
CREATE TABLE IF NOT EXISTS notification_logs (
    id BIGSERIAL PRIMARY KEY,
    channel VARCHAR(20) NOT NULL, -- 'telegram', 'dashboard'
    notification_type VARCHAR(50) NOT NULL, -- 'signal', 'order', 'daily_summary', 'alert'
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed', 'pending'
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notif_channel ON notification_logs(channel);
CREATE INDEX IF NOT EXISTS idx_notif_created ON notification_logs(created_at DESC);
