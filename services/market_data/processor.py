"""
Quantro Personal AI — Market Data Processor
Processes raw data, calculates indicators, and writes to database.
"""
import logging
import pandas as pd
from typing import Optional
from uuid import UUID

from packages.indicators.calculator import IndicatorCalculator

logger = logging.getLogger(__name__)


class MarketDataProcessor:
    """Processes fetched data, applies indicators, and prepares for DB insert."""

    def __init__(self, db_session):
        """Pass a sqlalchemy AsyncSession."""
        self.db = db_session

    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply technical indicators."""
        if df.empty:
            return df
        return IndicatorCalculator.calculate_all(df)

    async def save_daily_ohlcv(self, stock_id: UUID, df: pd.DataFrame) -> None:
        """Save daily OHLCV and indicator data to DB."""
        if df.empty:
            return
            
        # In a real implementation, we would use bulk inserts (e.g., PostgreSQL COPY or execute_values).
        # For simplicity in this structure, we iterate or use a specialized bulk method on self.db.
        logger.info(f"Saving {len(df)} daily records for stock {stock_id}")
        print(f"DEBUG: Saving {len(df)} daily records for stock {stock_id}")
        
        # We use an ON CONFLICT DO UPDATE clause to handle duplicate dates
        from sqlalchemy import text
        
        insert_sql = text("""
            INSERT INTO ohlcv_daily (stock_id, date, open, high, low, close, volume)
            VALUES (:stock_id, :date, :open, :high, :low, :close, :volume)
            ON CONFLICT (stock_id, date) DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume;
        """)
        
        records = []
        for _, row in df.iterrows():
            # Handle timestamps properly, keeping just the date part
            row_date = row['timestamp'].date() if hasattr(row['timestamp'], 'date') else pd.to_datetime(row['timestamp']).date()
            
            records.append({
                "stock_id": str(stock_id),
                "date": row_date,
                "open": float(row['open']),
                "high": float(row['high']),
                "low": float(row['low']),
                "close": float(row['close']),
                "volume": int(row['volume'])
            })
            
        if records:
            await self.db.execute(insert_sql, records)
            await self.db.commit()
    async def save_intraday_ohlcv(self, stock_id: UUID, df: pd.DataFrame, timeframe: str) -> None:
        """Save intraday OHLCV."""
        if df.empty:
            return
        logger.info(f"Saving {len(df)} {timeframe} intraday records for stock {stock_id}")
        # Placeholder for actual SQLAlchemy bulk insert logic
        pass
