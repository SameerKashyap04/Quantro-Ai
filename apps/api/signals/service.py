"""
Quantro Personal AI — Signals Service
"""
from typing import Optional
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.signals.repository import SignalRepository
from apps.api.portfolio.repository import PortfolioRepository
from apps.api.market.repository import MarketRepository
from services.signal_engine.generator import SignalGenerator
from services.ai_engine.models import AIModelManager
from packages.indicators.calculator import IndicatorCalculator


class SignalService:
    """Signal retrieval business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SignalRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
        self.market_repo = MarketRepository(db)

    async def get_latest(
        self, 
        portfolio_only: bool = False, 
        market_only: bool = False, 
        source: str = "groww", 
        **filters
    ) -> list[dict]:
        """Get latest signals with filters."""
        if portfolio_only or market_only:
            holdings = await self.portfolio_repo.get_holdings(source)
            symbols = [h['symbol'] for h in holdings]
            if portfolio_only:
                if not symbols:
                    return []
                filters['symbols'] = symbols
            if market_only and symbols:
                filters['exclude_symbols'] = symbols

        signals = await self.repo.get_latest_signals(**filters)
        for sig in signals:
            if hasattr(sig.get("created_at"), "isoformat"):
                sig["created_at"] = sig["created_at"].isoformat()
        return signals

    async def get_by_symbol(self, symbol: str, limit: int = 20) -> list[dict]:
        """Get signal history for a stock."""
        signals = await self.repo.get_signals_by_symbol(symbol, limit)
        for sig in signals:
            if hasattr(sig.get("created_at"), "isoformat"):
                sig["created_at"] = sig["created_at"].isoformat()
        return signals

    async def analyze_portfolio_holdings(self, source: str = "groww") -> list[dict]:
        """Dynamically generate signals for current portfolio holdings."""
        holdings = await self.portfolio_repo.get_holdings(source)
        if not holdings:
            return []
            
        market_data_map = {}
        news_data_map = {}
        fundamental_data_map = {}
        from services.market_data.fetchers import YFinanceFetcher
        fetcher = YFinanceFetcher()
        import asyncio
        
        async def fetch_stock_data(stock_id, symbol):
            fund_task = asyncio.to_thread(fetcher.fetch_fundamentals, symbol)
            news_task = asyncio.to_thread(fetcher.fetch_news, symbol, 5)
            
            fund_data, news_data = await asyncio.gather(fund_task, news_task, return_exceptions=True)
            
            rows = await self.market_repo.get_ohlcv_daily(stock_id, limit=300)
            df = None
            if not rows:
                df_task = asyncio.to_thread(fetcher.fetch_ohlcv, symbol, "2y", "1d", False)
                df_res = await df_task
                if not isinstance(df_res, Exception) and not df_res.empty:
                    df = IndicatorCalculator.calculate_all(df_res)
            else:
                import pandas as pd
                df_res = pd.DataFrame(rows)
                if not df_res.empty and 'date' in df_res.columns:
                    df = IndicatorCalculator.calculate_all(df_res)
                    
            return stock_id, fund_data, news_data, df
            
        tasks = [fetch_stock_data(h['stock_id'], h['symbol']) for h in holdings]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if isinstance(res, Exception):
                continue
            stock_id, fund_data, news_data, df = res
            if not isinstance(fund_data, Exception) and fund_data:
                fundamental_data_map[str(stock_id)] = fund_data
            if not isinstance(news_data, Exception) and news_data:
                news_data_map[str(stock_id)] = news_data
            if df is not None:
                market_data_map[str(stock_id)] = df
                    
        if not market_data_map:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("No market data available for any holdings!")
            return []
            
        # Run the signal generator
        model_manager = AIModelManager(model_dir="/tmp/models")
        generator = SignalGenerator(self.db, risk_settings={})
        generator.model_manager = model_manager
        generator.predictor.model_manager = model_manager
        
        regime_record = await self.market_repo.get_market_regime()
        current_regime = regime_record['regime_type'] if regime_record else "BULL"
        
        # Generate new signals
        signals = await generator.generate_for_market(market_data_map, current_regime, news_data_map, fundamental_data_map)
        
        # Retrieve the newly generated signals enriched with stock info
        enriched_signals = []
        for h in holdings:
            symbol_signals = await self.repo.get_signals_by_symbol(h['symbol'], limit=1)
            if symbol_signals:
                enriched_signals.append(symbol_signals[0])
                
        # Format dates
        for sig in enriched_signals:
            if hasattr(sig.get("created_at"), "isoformat"):
                sig["created_at"] = sig["created_at"].isoformat()
                
        # Sort by confidence
        enriched_signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return enriched_signals

    async def analyze_market_opportunities(self, limit: int = 10) -> list[dict]:
        import logging
        import requests
        logger = logging.getLogger(__name__)
        logger.info("Screening multiple sources (NSE & TradingView) for real-time top gainers...")
        
        selected_symbols = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': '*/*',
            }
            session = requests.Session()
            session.headers.update(headers)
            
            # 1. Fetch from official NSE India API
            try:
                session.get("https://www.nseindia.com", timeout=5)
                res_nse = session.get("https://www.nseindia.com/api/live-analysis-variations?index=gainers", timeout=5)
                if res_nse.status_code == 200:
                    data = res_nse.json()
                    if 'FOSec' in data:
                        nse_symbols = [item['symbol'] for item in data['FOSec']['data']]
                        selected_symbols.extend(nse_symbols)
            except Exception as e:
                logger.warning(f"NSE API fetch failed: {e}")

            # 2. Fetch from TradingView Screener API (Mimics Screener.in/Tickertape/Groww)
            try:
                tv_payload = {
                    "filter": [
                        {"left": "exchange", "operation": "equal", "right": "NSE"},
                        {"left": "market_cap_basic", "operation": "egreater", "right": 50000000000}, # > 5000 Cr Market Cap
                        {"left": "volume", "operation": "egreater", "right": 1000000} # > 1M Volume
                    ],
                    "options": {"lang": "en"},
                    "markets": ["india"],
                    "symbols": {"query": {"types": []}, "tickers": []},
                    "columns": ["name"],
                    "sort": {"sortBy": "change", "sortOrder": "desc"},
                    "range": [0, limit]
                }
                res_tv = requests.post("https://scanner.tradingview.com/india/scan", json=tv_payload, headers=headers, timeout=5)
                if res_tv.status_code == 200:
                    tv_symbols = [x['d'][0] for x in res_tv.json().get('data', [])]
                    selected_symbols.extend(tv_symbols)
            except Exception as e:
                logger.warning(f"TradingView API fetch failed: {e}")
                    
            # Exclude portfolio holdings
            holdings = await self.portfolio_repo.get_holdings("groww")
            portfolio_symbols = {h['symbol'] for h in holdings}
            selected_symbols = [s for s in selected_symbols if s not in portfolio_symbols]
            
            # Remove duplicates and enforce limit
            selected_symbols = list(dict.fromkeys(selected_symbols))[:limit]
            logger.info(f"Top aggregated gainers selected: {selected_symbols}")
            
        except Exception as e:
            logger.error(f"NSE Screener fetch failed: {e}. Falling back to random NIFTY 50 sample.")
            from packages.shared.nse_universe import NIFTY_50
            import random
            holdings = await self.portfolio_repo.get_holdings("groww")
            portfolio_symbols = {h['symbol'] for h in holdings}
            non_portfolio_symbols = [s for s in NIFTY_50 if s not in portfolio_symbols]
            selected_symbols = random.sample(non_portfolio_symbols, min(limit, len(non_portfolio_symbols))) if non_portfolio_symbols else []

        if not selected_symbols:
            return []

        market_data_map = {}
        news_data_map = {}
        fundamental_data_map = {}
        from services.market_data.fetchers import YFinanceFetcher
        fetcher = YFinanceFetcher()

        selected_stocks = []
        for symbol in selected_symbols:
            # Check if stock is in DB, if not, create it
            stock = await self.market_repo.get_stock_by_symbol(symbol)
            if not stock:
                stock = await self.market_repo.create_stock(symbol, symbol)
            selected_stocks.append(stock)
            
            stock_id = stock['id']
            
            # Fetch 300 days of data so 200-period moving averages can be calculated
            rows = await self.market_repo.get_ohlcv_daily(stock_id, limit=300)
            
            import asyncio
            df_task = asyncio.to_thread(fetcher.fetch_ohlcv, symbol, "2y", "1d", False)
            fund_task = asyncio.to_thread(fetcher.fetch_fundamentals, symbol)
            news_task = asyncio.to_thread(fetcher.fetch_news, symbol, 5)
            
            if not rows:
                df = await df_task
                if not isinstance(df, Exception) and not df.empty:
                    df = IndicatorCalculator.calculate_all(df)
                    market_data_map[str(stock_id)] = df
            else:
                df = pd.DataFrame(rows)
                if not df.empty and 'date' in df.columns:
                    df = IndicatorCalculator.calculate_all(df)
                    market_data_map[str(stock_id)] = df
                    
            # Fetch News and Fundamentals concurrently
            fund_data, news_data = await asyncio.gather(fund_task, news_task, return_exceptions=True)
            if not isinstance(news_data, Exception) and news_data:
                news_data_map[str(stock_id)] = news_data
            if not isinstance(fund_data, Exception) and fund_data:
                fundamental_data_map[str(stock_id)] = fund_data
                    
        if not market_data_map:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("No market data available for market opportunities!")
            return []
            
        # Run the signal generator
        model_manager = AIModelManager(model_dir="/tmp/models")
        generator = SignalGenerator(self.db, risk_settings={})
        generator.model_manager = model_manager
        generator.predictor.model_manager = model_manager
        
        regime_record = await self.market_repo.get_market_regime()
        current_regime = regime_record['regime_type'] if regime_record else "BULL"
        
        # Generate new signals
        signals = await generator.generate_for_market(market_data_map, current_regime, news_data_map, fundamental_data_map)
        
        # Retrieve the newly generated signals enriched with stock info
        enriched_signals = []
        for s in selected_stocks:
            symbol_signals = await self.repo.get_signals_by_symbol(s['symbol'], limit=1)
            if symbol_signals:
                # Include all active signals for market opportunities
                enriched_signals.append(symbol_signals[0])
                
        # Format dates
        for sig in enriched_signals:
            if hasattr(sig.get("created_at"), "isoformat"):
                sig["created_at"] = sig["created_at"].isoformat()
                
        # Sort by confidence
        enriched_signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return enriched_signals
