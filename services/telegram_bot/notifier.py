"""
Quantro Personal AI — Telegram Bot Notifier
"""
import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Interface for the backend to push asynchronous notifications to Telegram."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = str(chat_id)
        
        # Only initialize if token is provided
        if self.token and self.token != "mock_token":
            self.bot = Bot(token=self.token)
        else:
            self.bot = None

    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Push a message to the authorized user."""
        if not self.bot:
            logger.info(f"[MOCK TELEGRAM] Would send: {text}")
            return True
            
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
