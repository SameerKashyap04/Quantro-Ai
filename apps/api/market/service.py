"""
Quantro Personal AI — Market Service
Business logic for market data.
"""
from typing import Optional
from datetime import date
import json

from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis_lib

from apps.api.market.repository import MarketRepository
from apps.api.core.exceptions import NotFoundError


class MarketService:
    """Market data business logic."""

    def __init__(self, db: AsyncSession, redis: Optional[redis_lib.Redis] = None):
        self.repo = MarketRepository(db)
        self.redis = redis

    async def get_stocks(self, **filters) -> list[dict]:
        """Get stocks with optional filters and cached prices."""
        stocks = await self.repo.get_all_stocks(**filters)

        # Enrich with cached latest prices if Redis available
        if self.redis:
            for stock in stocks:
                cached = await self.redis.get(f"price:{stock['symbol']}")
                if cached:
                    price_data = json.loads(cached)
                    stock["current_price"] = price_data.get("price")
                    stock["change"] = price_data.get("change")
                    stock["change_pct"] = price_data.get("change_pct")

        return stocks

    async def get_stock(self, symbol: str) -> dict:
        """Get a single stock by symbol."""
        stock = await self.repo.get_stock_by_symbol(symbol)
        if not stock:
            raise NotFoundError(f"Stock '{symbol}'")
        return stock

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "daily",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 365,
    ) -> list[dict]:
        """Get OHLCV data for a stock."""
        stock = await self.repo.get_stock_by_symbol(symbol)
        if not stock:
            raise NotFoundError(f"Stock '{symbol}'")

        if timeframe == "daily":
            data = await self.repo.get_ohlcv_daily(stock["id"], start_date, end_date, limit)
        else:
            data = await self.repo.get_ohlcv_intraday(stock["id"], timeframe, limit)

        # Format dates as strings for JSON serialization
        for item in data:
            if "date" in item and hasattr(item["date"], "isoformat"):
                item["date"] = item["date"].isoformat()
            if "timestamp" in item and hasattr(item["timestamp"], "isoformat"):
                item["date"] = item["timestamp"].isoformat()
                del item["timestamp"]

        return data

    async def get_regime(self) -> dict:
        """Get current market regime."""
        regime = await self.repo.get_market_regime()
        if not regime:
            return {
                "date": date.today().isoformat(),
                "regime": "unknown",
                "confidence": 0,
                "nifty_trend": "unknown",
                "vix_level": None,
            }
        if hasattr(regime.get("date"), "isoformat"):
            regime["date"] = regime["date"].isoformat()
        return regime

    async def get_sectors(self) -> list[str]:
        """Get all available sectors."""
        return await self.repo.get_sectors()
