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
            
        chunk_size = 5
        results = []
        for i in range(0, len(holdings), chunk_size):
            chunk = holdings[i:i+chunk_size]
            tasks = [fetch_stock_data(h['stock_id'], h['symbol']) for h in chunk]
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(chunk_results)
            # Short sleep to prevent rate limits/CPU spikes
            await asyncio.sleep(0.5)
            
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
                    
        # Check for failed fetches and create fallback signals
        failed_holdings = [h for h in holdings if str(h['stock_id']) not in market_data_map]
        
        if failed_holdings:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"{len(failed_holdings)} portfolio stocks failed to fetch market data. Generating fallback HOLD signals.")
            
            import json
            for h in failed_holdings:
                try:
                    await self.repo.deactivate_old_signals(h['stock_id'])
                    sig_data = {
                        "stock_id": h["stock_id"],
                        "signal_type": "HOLD",
                        "confidence": 50.0,
                        "stop_loss_pct": None,
                        "target_pct": None,
                        "risk_level": "Medium",
                        "strategy_name": "Fallback",
                        "reasoning_json": json.dumps({"error": "Failed to fetch real-time market data.", "tech_signal": "HOLD", "ai_signal": "HOLD"}),
                        "ai_bullish_prob": 0.5,
                        "ai_bearish_prob": 0.5,
                        "holding_period_days": 14
                    }
                    await self.repo.create_signal(sig_data)
                except Exception as e:
                    logger.error(f"Error creating fallback signal for {h['symbol']}: {e}")
                    
        # If we have market data, run the signal generator
        if market_data_map:
            model_manager = AIModelManager(model_dir="/tmp/models")
            generator = SignalGenerator(self.db, risk_settings={})
            generator.model_manager = model_manager
            generator.predictor.model_manager = model_manager
            
            regime_record = await self.market_repo.get_market_regime()
            current_regime = regime_record['regime_type'] if regime_record else "BULL"
            
            # Generate new signals
            signals = await generator.generate_for_market(
                market_data_map, 
                current_regime, 
                news_data_map, 
                fundamental_data_map,
                is_portfolio_analysis=True
            )
            
        await self.db.flush()
        
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
        import random
        from packages.shared.nse_universe import NIFTY_50, NIFTY_NEXT_50
        
        logger = logging.getLogger(__name__)
        logger.info("Finding new market opportunities...")
        
        # Clean up old database signals to prevent DB overload from previous days
        await self.repo.delete_old_signals(days_kept=1)
        
        # 1. Get all current portfolio symbols
        holdings = await self.portfolio_repo.get_holdings("groww")
        portfolio_symbols = {h['symbol'] for h in holdings}
        
        # 2. Get all symbols that already have recent signals in the database
        recent_signals = await self.repo.get_latest_signals(limit=200)
        recently_analyzed = {sig['symbol'] for sig in recent_signals}
        
        # 3. Combine NIFTY 50 and NIFTY NEXT 50 to form our search universe
        universe = list(set(NIFTY_50 + NIFTY_NEXT_50))
        
        # 4. Filter out portfolio symbols
        candidates = [s for s in universe if s not in portfolio_symbols]
        
        # 5. Prioritize candidates that haven't been analyzed recently
        fresh_candidates = [s for s in candidates if s not in recently_analyzed]
        
        # If we need more, fallback to candidates that WERE analyzed recently but aren't in portfolio
        if len(fresh_candidates) < limit:
            selected_symbols = fresh_candidates + random.sample(
                [s for s in candidates if s in recently_analyzed], 
                min(limit - len(fresh_candidates), len(candidates) - len(fresh_candidates))
            )
        else:
            selected_symbols = random.sample(fresh_candidates, limit)
            
        logger.info(f"Selected {len(selected_symbols)} new symbols to analyze: {selected_symbols}")

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
        await generator.generate_for_market(market_data_map, current_regime, news_data_map, fundamental_data_map)
        await self.db.flush()
        
        # Instead of returning ONLY the newly generated ones, return ALL market opportunities from the DB ranked by confidence
        # This solves the issue of showing the "same 7 stocks" and instead aggregates a growing list of opportunities
        all_market_opportunities = await self.get_latest(market_only=True, limit=50)
        
        # Format dates
        for sig in all_market_opportunities:
            if hasattr(sig.get("created_at"), "isoformat"):
                sig["created_at"] = sig["created_at"].isoformat()
                
        # Sort by confidence
        all_market_opportunities.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return all_market_opportunities
