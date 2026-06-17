-- ============================================================
-- Migration 003: Signals & Orders Schema
-- ============================================================

-- Trading signals
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    signal_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    confidence DECIMAL(5,2) NOT NULL,
    stop_loss_pct DECIMAL(5,2),
    target_pct DECIMAL(5,2),
    risk_level VARCHAR(20), -- 'Low', 'Medium', 'High'
    strategy_name VARCHAR(50),
    reasoning_json JSONB DEFAULT '{}',
    ai_bullish_prob DECIMAL(5,2),
    ai_bearish_prob DECIMAL(5,2),
    holding_period_days INTEGER,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_signals_stock ON signals(stock_id);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_created ON signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_active ON signals(is_active, created_at DESC);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    signal_id UUID REFERENCES signals(id),
    order_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL'
    order_subtype VARCHAR(20) DEFAULT 'MARKET', -- 'MARKET', 'LIMIT', 'SL', 'SL-M'
    quantity INTEGER NOT NULL,
    price DECIMAL(12,2),
    trigger_price DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PLACED, EXECUTED, CANCELLED, REJECTED, EXPIRED
    mode VARCHAR(20) DEFAULT 'paper', -- paper, approval, auto
    broker_order_id VARCHAR(100),
    broker_response_json JSONB DEFAULT '{}',
    stop_loss DECIMAL(12,2),
    target DECIMAL(12,2),
    notes TEXT,
    placed_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_stock ON orders(stock_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_mode ON orders(mode);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC);

-- Trades (executed fills)
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    trade_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL'
    executed_quantity INTEGER NOT NULL,
    executed_price DECIMAL(12,2) NOT NULL,
    total_value DECIMAL(14,2) NOT NULL,
    brokerage DECIMAL(10,2) DEFAULT 0,
    pnl DECIMAL(14,2),
    pnl_pct DECIMAL(8,4),
    mode VARCHAR(20) DEFAULT 'paper',
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_trades_stock ON trades(stock_id);
CREATE INDEX IF NOT EXISTS idx_trades_order ON trades(order_id);
CREATE INDEX IF NOT EXISTS idx_trades_executed ON trades(executed_at DESC);

-- Portfolio holdings
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 0,
    avg_buy_price DECIMAL(12,2) NOT NULL,
    current_price DECIMAL(12,2),
    invested_value DECIMAL(14,2),
    current_value DECIMAL(14,2),
    pnl DECIMAL(14,2),
    pnl_pct DECIMAL(8,4),
    day_change DECIMAL(14,2),
    day_change_pct DECIMAL(8,4),
    source VARCHAR(20) DEFAULT 'manual', -- manual, groww, paper
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_id, source)
);

CREATE INDEX IF NOT EXISTS idx_holdings_stock ON portfolio_holdings(stock_id);

-- Daily portfolio snapshots (for P&L tracking over time)
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_value DECIMAL(14,2) NOT NULL,
    invested_value DECIMAL(14,2) NOT NULL,
    daily_pnl DECIMAL(14,2),
    daily_pnl_pct DECIMAL(8,4),
    total_pnl DECIMAL(14,2),
    total_pnl_pct DECIMAL(8,4),
    num_holdings INTEGER,
    portfolio_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshots_date ON portfolio_snapshots(date DESC);
