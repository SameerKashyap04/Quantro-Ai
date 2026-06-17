"""
Quantro Personal AI — Telegram Bot Runner
"""
import logging
from telegram.ext import Application, CommandHandler

from services.telegram_bot.commands import BotCommands

logger = logging.getLogger(__name__)


class TelegramBotRunner:
    """Runs the Telegram bot polling loop."""

    def __init__(self, token: str, auth_chat_id: str, db_sessionmaker):
        self.token = token
        self.auth_chat_id = auth_chat_id
        self.db_sessionmaker = db_sessionmaker
        self.application = None

    def build_app(self):
        """Construct the bot application."""
        if not self.token or self.token == "mock_token":
            logger.warning("No valid Telegram token provided. Bot will not start.")
            return None
            
        self.application = Application.builder().token(self.token).build()
        commands = BotCommands(self.auth_chat_id, self.db_sessionmaker)

        # Register handlers
        self.application.add_handler(CommandHandler("start", commands.start_command))
        self.application.add_handler(CommandHandler("status", commands.status_command))
        self.application.add_handler(CommandHandler("portfolio", commands.portfolio_command))
        self.application.add_handler(CommandHandler("signals", commands.signals_command))
        
        return self.application

    async def start(self):
        """Start the bot in a non-blocking manner (suitable for ASGI)."""
        app = self.build_app()
        if app:
            logger.info("Starting Telegram Bot...")
            await app.initialize()
            await app.start()
            await app.updater.start_polling()

    async def stop(self):
        """Stop the bot."""
        if self.application:
            logger.info("Stopping Telegram Bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
