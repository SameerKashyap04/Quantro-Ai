"""
Quantro Personal AI — Signal Scheduler
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class SignalScheduler:
    """Schedules periodic signal generation."""

    def __init__(self, generator_callback):
        self.scheduler = AsyncIOScheduler()
        self.generator_callback = generator_callback

    def start(self):
        """Configure and start the scheduler."""
        
        # Run daily after market close and data update (e.g., 4:30 PM)
        self.scheduler.add_job(
            self.generator_callback,
            "cron",
            day_of_week="mon-fri",
            hour=16,
            minute=30,
            id="eod_signal_generation",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Signal Scheduler started.")

    def stop(self):
        self.scheduler.shutdown(wait=True)
        logger.info("Signal Scheduler stopped.")
