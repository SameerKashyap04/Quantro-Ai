-- ============================================================
-- Migration 002: Market Data Schema
-- ============================================================
-- Stocks, OHLCV (daily + intraday), indices, ETFs
-- ============================================================

-- Stocks / instruments universe
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(30) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap_category VARCHAR(20), -- largecap, midcap, smallcap
    exchange VARCHAR(10) DEFAULT 'NSE',
    is_index BOOLEAN DEFAULT false,
    is_etf BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    lot_size INTEGER DEFAULT 1,
    yfinance_symbol VARCHAR(30), -- e.g., RELIANCE.NS
    metadata_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
CREATE INDEX IF NOT EXISTS idx_stocks_is_index ON stocks(is_index);
CREATE INDEX IF NOT EXISTS idx_stocks_is_etf ON stocks(is_etf);

-- Daily OHLCV data
CREATE TABLE IF NOT EXISTS ohlcv_daily (
    id BIGSERIAL PRIMARY KEY,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    open DECIMAL(12,2) NOT NULL,
    high DECIMAL(12,2) NOT NULL,
    low DECIMAL(12,2) NOT NULL,
    close DECIMAL(12,2) NOT NULL,
    volume BIGINT DEFAULT 0,
    adj_close DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_id, date)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_stock_date ON ohlcv_daily(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_daily_date ON ohlcv_daily(date DESC);

-- Intraday OHLCV data (15-min, 1-hour)
CREATE TABLE IF NOT EXISTS ohlcv_intraday (
    id BIGSERIAL PRIMARY KEY,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '15m', '1h'
    open DECIMAL(12,2) NOT NULL,
    high DECIMAL(12,2) NOT NULL,
    low DECIMAL(12,2) NOT NULL,
    close DECIMAL(12,2) NOT NULL,
    volume BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_id, timestamp, timeframe)
);

CREATE INDEX IF NOT EXISTS idx_ohlcv_intraday_stock_ts ON ohlcv_intraday(stock_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ohlcv_intraday_timeframe ON ohlcv_intraday(timeframe);

-- Computed indicators (stored for quick retrieval)
CREATE TABLE IF NOT EXISTS indicators (
    id BIGSERIAL PRIMARY KEY,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    timeframe VARCHAR(10) DEFAULT 'daily',
    indicator_name VARCHAR(50) NOT NULL,
    value_json JSONB NOT NULL, -- flexible: can store single value or multiple
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_id, date, timeframe, indicator_name)
);

CREATE INDEX IF NOT EXISTS idx_indicators_stock_date ON indicators(stock_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_indicators_name ON indicators(indicator_name);

-- Market regime tracking
CREATE TABLE IF NOT EXISTS market_regime (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    regime VARCHAR(20) NOT NULL, -- 'bull', 'bear', 'sideways'
    confidence DECIMAL(5,2),
    nifty_trend VARCHAR(20),
    breadth_positive DECIMAL(5,2),
    vix_level DECIMAL(8,2),
    indicators_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_regime_date ON market_regime(date DESC);
