"""
Quantro Personal AI — Paper Trading Adapter
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from packages.broker_adapters.base import BaseBroker

logger = logging.getLogger(__name__)


class PaperBrokerAdapter(BaseBroker):
    """
    Simulated broker for Paper Trading mode.
    Maintains a simulated internal state or relies on the database.
    """

    def __init__(self, initial_capital: float = 1000000.0):
        self.available_cash = initial_capital
        self.positions: Dict[str, Any] = {}
        self.orders: Dict[str, Any] = {}

    async def authenticate(self) -> bool:
        return True

    async def get_profile(self) -> Dict[str, Any]:
        return {"broker": "paper", "status": "active"}

    async def get_funds(self) -> Dict[str, Any]:
        return {"available_cash": self.available_cash, "utilized_margin": 0.0}

    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        order_id = str(uuid.uuid4())
        
        # Simulate execution for MARKET orders
        status = "PENDING"
        if order_params.get("order_subtype", "MARKET") == "MARKET":
            status = "EXECUTED"
            # In a real paper trader, it would fetch live price here
            
        order = {
            "order_id": order_id,
            "status": status,
            "symbol": order_params.get("symbol"),
            "quantity": order_params.get("quantity"),
            "placed_at": datetime.now().isoformat()
        }
        
        self.orders[order_id] = order
        logger.info(f"Paper Broker: Placed order {order_id} -> {status}")
        
        return order

    async def modify_order(self, order_id: str, new_params: Dict[str, Any]) -> Dict[str, Any]:
        if order_id in self.orders:
            self.orders[order_id].update(new_params)
            return self.orders[order_id]
        return {}

    async def cancel_order(self, order_id: str) -> bool:
        if order_id in self.orders and self.orders[order_id]["status"] == "PENDING":
            self.orders[order_id]["status"] = "CANCELLED"
            return True
        return False

    async def get_order_history(self) -> list[Dict[str, Any]]:
        return list(self.orders.values())

    async def get_positions(self) -> list[Dict[str, Any]]:
        return list(self.positions.values())

    async def get_holdings(self) -> list[Dict[str, Any]]:
        return []
