"""
Quantro Personal AI — Market Repository
Database queries for market data.
"""
from typing import Optional
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MarketRepository:
    """Data access layer for market data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_stocks(
        self,
        sector: Optional[str] = None,
        is_index: Optional[bool] = None,
        is_etf: Optional[bool] = None,
        market_cap_category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> list[dict]:
        """Get all stocks with optional filters."""
        query = """
            SELECT s.*, 
                   (SELECT close FROM ohlcv_daily o WHERE o.stock_id = s.id AND o.close != 'NaN'::numeric ORDER BY date DESC LIMIT 1) as current_price,
                   (SELECT ((close - open) / NULLIF(open, 0)) * 100 FROM ohlcv_daily o WHERE o.stock_id = s.id AND o.close != 'NaN'::numeric AND o.open != 'NaN'::numeric ORDER BY date DESC LIMIT 1) as change_pct
            FROM stocks s 
            WHERE s.is_active = true
        """
        params = {}

        if sector:
            query += " AND sector = :sector"
            params["sector"] = sector
        if is_index is not None:
            query += " AND is_index = :is_index"
            params["is_index"] = is_index
        if is_etf is not None:
            query += " AND is_etf = :is_etf"
            params["is_etf"] = is_etf
        if market_cap_category:
            query += " AND market_cap_category = :market_cap"
            params["market_cap"] = market_cap_category
        if search:
            query += " AND (symbol ILIKE :search OR name ILIKE :search)"
            params["search"] = f"%{search}%"

        query += " ORDER BY symbol"

        result = await self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_stock_by_symbol(self, symbol: str) -> Optional[dict]:
        """Get a single stock by symbol."""
        result = await self.db.execute(
            text("SELECT * FROM stocks WHERE symbol = :symbol AND is_active = true"),
            {"symbol": symbol.upper()},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def create_stock(self, symbol: str, name: str) -> dict:
        """Create a new stock record."""
        result = await self.db.execute(
            text(
                "INSERT INTO stocks (symbol, name, is_active, is_index, is_etf) "
                "VALUES (:symbol, :name, true, false, false) "
                "RETURNING *"
            ),
            {"symbol": symbol.upper(), "name": name},
        )
        await self.db.commit()
        row = result.fetchone()
        return dict(row._mapping) if row else {}

    async def get_ohlcv_daily(
        self,
        stock_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 365,
    ) -> list[dict]:
        """Get daily OHLCV data for a stock."""
        query = "SELECT date, open, high, low, close, volume FROM ohlcv_daily WHERE stock_id = :stock_id"
        params: dict = {"stock_id": str(stock_id)}

        if start_date:
            query += " AND date >= :start_date"
            params["start_date"] = start_date
        if end_date:
            query += " AND date <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY date DESC LIMIT :limit"
        params["limit"] = limit

        result = await self.db.execute(text(query), params)
        rows = []
        for row in result.fetchall():
            mapping = dict(row._mapping)
            mapping["open"] = float(mapping["open"]) if mapping["open"] is not None else None
            mapping["high"] = float(mapping["high"]) if mapping["high"] is not None else None
            mapping["low"] = float(mapping["low"]) if mapping["low"] is not None else None
            mapping["close"] = float(mapping["close"]) if mapping["close"] is not None else None
            mapping["volume"] = int(mapping["volume"]) if mapping["volume"] is not None else None
            rows.append(mapping)
        
        rows.reverse()  # chronological order
        return rows

    async def get_ohlcv_intraday(
        self,
        stock_id: UUID,
        timeframe: str = "15m",
        limit: int = 100,
    ) -> list[dict]:
        """Get intraday OHLCV data."""
        result = await self.db.execute(
            text(
                "SELECT timestamp, open, high, low, close, volume FROM ohlcv_intraday "
                "WHERE stock_id = :stock_id AND timeframe = :timeframe "
                "ORDER BY timestamp DESC LIMIT :limit"
            ),
            {"stock_id": str(stock_id), "timeframe": timeframe, "limit": limit},
        )
        rows = [dict(row._mapping) for row in result.fetchall()]
        rows.reverse()
        return rows

    async def get_market_regime(self) -> Optional[dict]:
        """Get the latest market regime."""
        result = await self.db.execute(
            text("SELECT * FROM market_regime ORDER BY date DESC LIMIT 1")
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def get_sectors(self) -> list[str]:
        """Get distinct sectors."""
        result = await self.db.execute(
            text(
                "SELECT DISTINCT sector FROM stocks "
                "WHERE sector IS NOT NULL AND is_active = true AND is_index = false AND is_etf = false "
                "ORDER BY sector"
            )
        )
        return [row[0] for row in result.fetchall()]
