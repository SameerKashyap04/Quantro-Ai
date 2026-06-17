"""
Quantro Personal AI — Execution Modes
"""
import logging
from typing import Dict, Any

from services.execution_engine.order_manager import OrderManager

logger = logging.getLogger(__name__)


class ExecutionModes:
    """Handlers for different trading modes."""

    def __init__(self, order_manager: OrderManager, telegram_service=None):
        self.order_manager = order_manager
        self.telegram = telegram_service

    async def handle_paper_mode(self, order: Dict[str, Any]):
        """Execute directly using the paper broker adapter."""
        logger.info(f"Paper Mode: Executing order {order.get('id')}")
        await self.order_manager.execute_order(order)

    async def handle_approval_mode(self, order: Dict[str, Any]):
        """Stage order as PENDING and send an interactive Telegram alert."""
        logger.info(f"Approval Mode: Order {order.get('id')} staged as PENDING.")
        
        if self.telegram:
            msg = (
                f"🚨 *TRADE APPROVAL REQUIRED*\n\n"
                f"Action: {order.get('order_type')} {order.get('symbol')}\n"
                f"Qty: {order.get('quantity')}\n"
                f"Signal Confidence: {order.get('confidence', 'N/A')}\n"
                f"Strategy: {order.get('strategy_name', 'Manual')}\n\n"
                f"Reply to this message with APPROVE or REJECT."
            )
            await self.telegram.send_message(msg)

    async def handle_auto_mode(self, order: Dict[str, Any]):
        """Execute directly using the live broker adapter."""
        logger.warning(f"AUTO Mode: Executing LIVE order {order.get('id')}")
        await self.order_manager.execute_order(order)
        
        if self.telegram:
            await self.telegram.send_message(f"✅ Executed LIVE Auto-Trade: {order.get('order_type')} {order.get('symbol')}")
