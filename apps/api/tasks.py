import logging
import asyncio
import pandas as pd
from apps.api.database import async_session_factory
from services.market_data.collector import MarketDataCollector
from services.signal_engine.generator import SignalGenerator
from services.ai_engine.models import AIModelManager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

class QuantroScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def run_eod_pipeline(self):
        logger.info("Starting EOD Pipeline: Market Data -> Signal Generation")
        try:
            async with async_session_factory() as session:
                # 1. Fetch Market Data
                collector = MarketDataCollector(session)
                await collector.run_eod_collection()
                
                # 2. Query latest data for AI
                from apps.api.market.repository import MarketRepository
                repo = MarketRepository(session)
                stocks = await repo.get_all_stocks(is_index=False, is_etf=False)
                
                market_data_map = {}
                for s in stocks:
                    rows = await repo.get_ohlcv_daily(s['id'], limit=100) # Need enough data for indicators
                    if rows:
                        df = pd.DataFrame(rows)
                        if not df.empty and 'date' in df.columns:
                            # Re-calculate indicators since generator might need them, or rely on processor
                            from packages.indicators.calculator import IndicatorCalculator
                            df = IndicatorCalculator.calculate_all(df)
                            market_data_map[str(s['id'])] = df
                
                # 3. Generate Signals
                if market_data_map:
                    # Initialize model manager with correct path
                    model_manager = AIModelManager(model_dir="/app/data/models")
                    
                    generator = SignalGenerator(session, risk_settings={})
                    generator.model_manager = model_manager
                    generator.predictor.model_manager = model_manager
                    
                    regime_record = await repo.get_market_regime()
                    current_regime = regime_record['regime_type'] if regime_record else "BULL"
                    
                    signals = await generator.generate_for_market(market_data_map, current_regime)
                    
                    if signals:
                        from services.telegram_bot.notifier import TelegramNotifier
                        from apps.api.config import settings
                        notifier = TelegramNotifier(token=settings.telegram_bot_token, chat_id=settings.telegram_chat_id)
                        await notifier.send_message(f"🔔 *Quantro Personal AI: Generated {len(signals)} new trading signals!*")
                        
            logger.info("EOD Pipeline completed successfully.")
        except Exception as e:
            logger.error(f"EOD Pipeline failed: {e}")

    async def run_fundamental_scraping(self):
        logger.info("Starting Fundamental Scraping Pipeline...")
        try:
            from services.market_data.screener_scraper import ScreenerScraper
            from apps.api.market.repository import MarketRepository
            
            async with async_session_factory() as session:
                repo = MarketRepository(session)
                stocks = await repo.get_all_stocks(is_index=False, is_etf=False)
                
                logger.info(f"Scraping fundamentals for {len(stocks)} stocks...")
                for s in stocks:
                    symbol = s['symbol']
                    logger.info(f"Scraping {symbol}...")
                    
                    # Run blocking web scrapers in a thread pool so we don't freeze the FastAPI event loop
                    screener_data = await asyncio.to_thread(ScreenerScraper.fetch_screener_in_fundamentals, symbol)
                    trendlyne_data = await asyncio.to_thread(ScreenerScraper.fetch_trendlyne_metrics, symbol)
                    
                    # Simulate a brief delay to avoid rapid requests and blocks
                    await asyncio.sleep(2)
                    
            logger.info("Fundamental Scraping Pipeline completed.")
        except Exception as e:
            logger.error(f"Fundamental Scraping failed: {e}")

    async def run_frequent_analysis(self):
        logger.info("Starting Frequent Analysis (Portfolio + Market) every 5 mins...")
        try:
            from apps.api.signals.service import SignalService
            async with async_session_factory() as session:
                service = SignalService(session)
                logger.info("Running auto Analyze Portfolio...")
                await service.analyze_portfolio_holdings(source="groww")
                
                logger.info("Running auto Find Top Opportunities...")
                await service.analyze_market_opportunities(limit=15)
                
            logger.info("Frequent Analysis completed successfully.")
        except Exception as e:
            logger.error(f"Frequent Analysis failed: {e}")

    def start(self):
        # Run daily after market close
        self.scheduler.add_job(
            self.run_eod_pipeline,
            "cron",
            day_of_week="mon-fri",
            hour=16,
            minute=30,
            id="eod_pipeline",
            replace_existing=True
        )
        
        # Run fundamental scraper weekly (e.g. Saturday morning) to avoid getting blocked
        self.scheduler.add_job(
            self.run_fundamental_scraping,
            "cron",
            day_of_week="sat",
            hour=9,
            minute=0,
            id="fundamental_scraping",
            replace_existing=True
        )
        
        # Run frequent analysis every 5 minutes
        self.scheduler.add_job(
            self.run_frequent_analysis,
            "interval",
            minutes=5,
            id="frequent_analysis",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Quantro Global Scheduler started with 5-minute auto-analysis.")

    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("Quantro Global Scheduler stopped.")

scheduler_instance = QuantroScheduler()
