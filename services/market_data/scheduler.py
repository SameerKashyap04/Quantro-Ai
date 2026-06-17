"""
Quantro Personal AI — Market Data Scheduler
Runs periodic tasks to fetch and update market data.
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class MarketDataScheduler:
    """Manages scheduled tasks using APScheduler."""

    def __init__(self, collector):
        self.scheduler = AsyncIOScheduler()
        self.collector = collector

    def start(self):
        """Configure and start the scheduler."""
        
        # 1. Intraday Updates (Every 15 minutes during market hours)
        self.scheduler.add_job(
            self.collector.run_intraday_collection,
            "cron",
            day_of_week="mon-fri",
            hour="9-15",
            minute="*/15",
            id="intraday_collection",
            replace_existing=True,
            misfire_grace_time=300
        )
        
        # 2. Daily End of Day (EOD) Update (At 4:00 PM)
        self.scheduler.add_job(
            self.collector.run_eod_collection,
            "cron",
            day_of_week="mon-fri",
            hour=16,
            minute=0,
            id="eod_collection",
            replace_existing=True,
            misfire_grace_time=3600
        )
        
        # 3. Live Price Updates (Every minute during market hours for dashboard)
        self.scheduler.add_job(
            self.collector.update_live_prices,
            "cron",
            day_of_week="mon-fri",
            hour="9-15",
            minute="*",
            id="live_price_updates",
            replace_existing=True,
            misfire_grace_time=30
        )

        self.scheduler.start()
        logger.info("Market Data Scheduler started.")

    def stop(self):
        self.scheduler.shutdown(wait=True)
        logger.info("Market Data Scheduler stopped.")
