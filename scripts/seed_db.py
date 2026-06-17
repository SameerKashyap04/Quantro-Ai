import asyncio
import sys
import os

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from apps.api.database import async_session_factory, engine

NIFTY_50_STOCKS = [
    # Top 10 for demo purposes to avoid huge data downloads initially
    ("RELIANCE.NS", "Reliance Industries", "Energy"),
    ("TCS.NS", "Tata Consultancy Services", "IT"),
    ("HDFCBANK.NS", "HDFC Bank", "Financial Services"),
    ("INFY.NS", "Infosys", "IT"),
    ("ICICIBANK.NS", "ICICI Bank", "Financial Services"),
    ("HINDUNILVR.NS", "Hindustan Unilever", "Consumer Goods"),
    ("SBIN.NS", "State Bank of India", "Financial Services"),
    ("BHARTIARTL.NS", "Bharti Airtel", "Telecommunication"),
    ("ITC.NS", "ITC", "Consumer Goods"),
    ("LARSEN.NS", "Larsen & Toubro", "Construction"),
]

INDICES = [
    ("^NSEI", "NIFTY 50", "Index"),
    ("^NSEBANK", "NIFTY BANK", "Index"),
]

async def create_schema(session):
    print("Creating schema if not exists...")
    schema_sql = """
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE TABLE IF NOT EXISTS stocks (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        symbol VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        sector VARCHAR(100),
        is_index BOOLEAN DEFAULT FALSE,
        is_etf BOOLEAN DEFAULT FALSE,
        market_cap_category VARCHAR(50),
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS ohlcv_daily (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
        date DATE NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume BIGINT,
        adj_close NUMERIC,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(stock_id, date)
    );

    CREATE TABLE IF NOT EXISTS ohlcv_intraday (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        timeframe VARCHAR(10) NOT NULL,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume BIGINT,
        UNIQUE(stock_id, timestamp, timeframe)
    );

    CREATE TABLE IF NOT EXISTS signals (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
        signal_type VARCHAR(20) NOT NULL,
        confidence NUMERIC NOT NULL,
        stop_loss_pct NUMERIC,
        target_pct NUMERIC,
        risk_level VARCHAR(20),
        strategy_name VARCHAR(100),
        reasoning_json JSONB,
        ai_bullish_prob NUMERIC,
        ai_bearish_prob NUMERIC,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS market_regime (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        date DATE NOT NULL UNIQUE,
        regime_type VARCHAR(20) NOT NULL,
        confidence NUMERIC,
        indicators_json JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS portfolio_holdings (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
        quantity NUMERIC NOT NULL DEFAULT 0,
        avg_buy_price NUMERIC NOT NULL,
        current_price NUMERIC,
        invested_value NUMERIC,
        current_value NUMERIC,
        pnl NUMERIC,
        pnl_pct NUMERIC,
        day_change NUMERIC,
        day_change_pct NUMERIC,
        source VARCHAR(20) DEFAULT 'manual',
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(stock_id, source)
    );
    """
    for statement in schema_sql.split(';'):
        stmt = statement.strip()
        if stmt:
            await session.execute(text(stmt))
    await session.commit()
    print("Schema ready.")

async def seed_data(session):
    print("Seeding NIFTY 50 and Indices...")
    
    insert_sql = text("""
        INSERT INTO stocks (symbol, name, sector, is_index, is_etf)
        VALUES (:symbol, :name, :sector, :is_index, :is_etf)
        ON CONFLICT (symbol) DO NOTHING;
    """)
    
    # Insert Indices
    for symbol, name, sector in INDICES:
        await session.execute(insert_sql, {
            "symbol": symbol, "name": name, "sector": sector, 
            "is_index": True, "is_etf": False
        })
        
    # Insert Stocks
    for symbol, name, sector in NIFTY_50_STOCKS:
        await session.execute(insert_sql, {
            "symbol": symbol, "name": name, "sector": sector, 
            "is_index": False, "is_etf": False
        })
        
    await session.commit()
    print("Seeding complete.")

async def main():
    async with async_session_factory() as session:
        await create_schema(session)
        await seed_data(session)

if __name__ == "__main__":
    asyncio.run(main())
