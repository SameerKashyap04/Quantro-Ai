-- ============================================================
-- Migration 004: AI Models Schema
-- ============================================================

-- AI model registry
CREATE TABLE IF NOT EXISTS ai_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'xgboost', 'lightgbm', 'ensemble'
    version INTEGER DEFAULT 1,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    feature_importance_json JSONB DEFAULT '{}',
    hyperparams_json JSONB DEFAULT '{}',
    training_samples INTEGER,
    model_path VARCHAR(500),
    is_active BOOLEAN DEFAULT false,
    trained_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_models_active ON ai_models(is_active, model_type);

-- AI predictions log
CREATE TABLE IF NOT EXISTS ai_predictions (
    id BIGSERIAL PRIMARY KEY,
    model_id UUID NOT NULL REFERENCES ai_models(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL,
    bullish_probability DECIMAL(5,2) NOT NULL,
    bearish_probability DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    predicted_direction VARCHAR(10), -- 'UP', 'DOWN', 'NEUTRAL'
    predicted_return_pct DECIMAL(8,4),
    actual_return_pct DECIMAL(8,4), -- filled after the fact for tracking
    was_correct BOOLEAN, -- filled after the fact
    features_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(model_id, stock_id, prediction_date)
);

CREATE INDEX IF NOT EXISTS idx_predictions_stock_date ON ai_predictions(stock_id, prediction_date DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON ai_predictions(model_id);
CREATE INDEX IF NOT EXISTS idx_predictions_date ON ai_predictions(prediction_date DESC);

-- Backtest results
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(50), -- 'indicator', 'ai', 'hybrid'
    params_json JSONB DEFAULT '{}',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(14,2) DEFAULT 100000,
    final_capital DECIMAL(14,2),
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5,2),
    cagr DECIMAL(8,4),
    sharpe_ratio DECIMAL(8,4),
    sortino_ratio DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    profit_factor DECIMAL(8,4),
    avg_win DECIMAL(8,4),
    avg_loss DECIMAL(8,4),
    equity_curve_json JSONB DEFAULT '[]',
    trades_json JSONB DEFAULT '[]',
    metrics_json JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy_name);
CREATE INDEX IF NOT EXISTS idx_backtest_created ON backtest_results(created_at DESC);
