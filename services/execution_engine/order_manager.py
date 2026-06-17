"""
Quantro Personal AI — Order Manager
"""
import logging
from typing import Dict, Any

from apps.api.orders.repository import OrderRepository
from packages.broker_adapters.base import BaseBroker

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages the lifecycle of an order with the broker and database."""

    def __init__(self, db_session, broker: BaseBroker):
        self.repo = OrderRepository(db_session)
        self.broker = broker

    async def execute_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Send the order to the broker and update the DB."""
        try:
            logger.info(f"Sending order to broker: {order}")
            
            # Broker specific formatting happens here or inside the adapter
            broker_order = await self.broker.place_order(order)
            
            # Update DB with new status
            status = broker_order.get("status", "PENDING")
            await self.repo.update_order_status(
                order_id=order["id"],
                status=status,
                broker_order_id=broker_order.get("order_id")
            )
            
            order["status"] = status
            return order
            
        except Exception as e:
            logger.error(f"Execution failed for order {order.get('id')}: {e}")
            await self.repo.update_order_status(order["id"], "REJECTED", notes=str(e))
            order["status"] = "REJECTED"
            return order
