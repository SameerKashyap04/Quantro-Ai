"""
Quantro Personal AI — Telegram Commands
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.telegram_bot.formatters import TelegramFormatter

logger = logging.getLogger(__name__)


class BotCommands:
    """Handlers for Telegram bot commands."""

    def __init__(self, auth_chat_id: str, db_sessionmaker):
        self.auth_chat_id = str(auth_chat_id)
        self.db_sessionmaker = db_sessionmaker

    def _is_authorized(self, update: Update) -> bool:
        """Check if the user is the authorized single user."""
        chat_id = str(update.effective_chat.id)
        if chat_id != self.auth_chat_id:
            logger.warning(f"Unauthorized access attempt from chat ID: {chat_id}")
            return False
        return True

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        if not self._is_authorized(update):
            return
            
        await update.message.reply_text(
            "👋 Welcome to *Quantro Personal AI*.\n\n"
            "I am your private trading assistant. I'll send you alerts, signals, and portfolio updates.\n\n"
            "Commands:\n"
            "/status - System health and mode\n"
            "/portfolio - Current holdings summary\n"
            "/signals - Latest generated signals",
            parse_mode="Markdown"
        )

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        if not self._is_authorized(update):
            return
            
        # In full implementation, query db for Settings
        await update.message.reply_text(
            "🟢 *System Status: ONLINE*\n\n"
            "Trading Mode: Paper\n"
            "Market Fetcher: Active\n"
            "AI Engine: Loaded",
            parse_mode="Markdown"
        )

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command."""
        if not self._is_authorized(update):
            return
            
        # Mock summary. In reality, call PortfolioService.
        summary = {
            "total_value": 105000,
            "total_pnl": 5000,
            "total_pnl_pct": 5.0,
            "daily_pnl": 1200,
            "num_holdings": 4
        }
        msg = TelegramFormatter.format_portfolio_summary(summary)
        await update.message.reply_text(msg, parse_mode="Markdown")

    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command."""
        if not self._is_authorized(update):
            return
            
        await update.message.reply_text(
            "Fetching latest signals...",
            parse_mode="Markdown"
        )
        # Call SignalService here and return top 3 formatted signals
