"""
Quantro Personal AI — Market Data Collector Entrypoint
"""
import logging
import asyncio
import json
import redis.asyncio as redis_lib

from services.market_data.fetchers import YFinanceFetcher
from services.market_data.processor import MarketDataProcessor
from packages.shared.utils import is_market_open

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Main orchestrator for the market data service."""

    def __init__(self, db_session, redis_url: str = "redis://localhost:6379/0"):
        self.db = db_session
        self.redis = redis_lib.from_url(redis_url)
        self.fetcher = YFinanceFetcher()
        self.processor = MarketDataProcessor(self.db)

    async def get_active_stocks(self) -> list[dict]:
        """Get list of active stocks from DB to monitor."""
        from apps.api.market.repository import MarketRepository
        repo = MarketRepository(self.db)
        stocks = await repo.get_all_stocks()
        return stocks

    async def run_eod_collection(self):
        """End of Day OHLCV collection."""
        logger.info("Starting EOD data collection...")
        stocks = await self.get_active_stocks()
        
        for stock in stocks:
            try:
                # Fetch 1 year of daily data
                print(f"DEBUG: Fetching {stock['symbol']}")
                df = self.fetcher.fetch_ohlcv(stock["symbol"], period="1y", interval="1d", is_index=stock["is_index"])
                if not df.empty:
                    print(f"DEBUG: df not empty for {stock['symbol']}, adding indicators")
                    df_with_indicators = self.processor.add_indicators(df)
                    print(f"DEBUG: calling save_daily_ohlcv for {stock['symbol']}")
                    await self.processor.save_daily_ohlcv(stock["id"], df_with_indicators)
                else:
                    print(f"DEBUG: df IS EMPTY for {stock['symbol']}")
            except Exception as e:
                logger.error(f"EOD fetch failed for {stock['symbol']}: {e}")
                
            # Rate limiting/courtesy pause
            await asyncio.sleep(0.5)
            
        logger.info("EOD data collection completed.")

    async def run_intraday_collection(self):
        """Intraday 15m OHLCV collection."""
        if not is_market_open():
            logger.info("Market closed, skipping intraday collection.")
            return

        logger.info("Starting intraday data collection...")
        stocks = await self.get_active_stocks()
        
        for stock in stocks:
            try:
                df = self.fetcher.fetch_ohlcv(stock["symbol"], period="5d", interval="15m", is_index=stock["is_index"])
                if not df.empty:
                    df_with_indicators = self.processor.add_indicators(df)
                    await self.processor.save_intraday_ohlcv(stock["id"], df_with_indicators, "15m")
            except Exception as e:
                logger.error(f"Intraday fetch failed for {stock['symbol']}: {e}")
                
            await asyncio.sleep(0.5)

    async def update_live_prices(self):
        """Update live prices in Redis."""
        if not is_market_open():
            return
            
        stocks = await self.get_active_stocks()
        
        for stock in stocks:
            try:
                price_data = self.fetcher.fetch_latest_price(stock["symbol"], is_index=stock["is_index"])
                if price_data:
                    # Cache in Redis with 60s expiry
                    await self.redis.setex(
                        f"price:{stock['symbol']}",
                        60,
                        json.dumps(price_data)
                    )
            except Exception as e:
                logger.error(f"Live price fetch failed for {stock['symbol']}: {e}")
                
            await asyncio.sleep(0.1)
