"""
Quantro Personal AI — Orders Service
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.orders.repository import OrderRepository
from apps.api.market.repository import MarketRepository
from apps.api.core.exceptions import NotFoundError, ValidationError, RiskViolationError
from apps.api.config import get_settings

settings = get_settings()


class OrderService:
    """Order management business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrderRepository(db)
        self.market_repo = MarketRepository(db)

    async def get_orders(self, status: Optional[str] = None) -> list[dict]:
        """Get recent orders."""
        orders = await self.repo.get_orders(status=status)
        for order in orders:
            for field in ["created_at", "updated_at", "placed_at", "executed_at", "cancelled_at"]:
                if order.get(field) and hasattr(order[field], "isoformat"):
                    order[field] = order[field].isoformat()
        return orders

    async def place_order(self, request_data: dict) -> dict:
        """
        Place a new order.
        Validates the stock, applies basic risk checks, and determines routing based on mode.
        """
        symbol = request_data.get("symbol", "").upper()
        stock = await self.market_repo.get_stock_by_symbol(symbol)
        
        if not stock:
            raise NotFoundError(f"Stock '{symbol}'")

        mode = settings.trading_mode
        
        # In a full implementation, we would call RiskEngine here.
        # For now, we perform basic validation.
        quantity = request_data.get("quantity", 0)
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        order_data = {
            "stock_id": str(stock["id"]),
            "signal_id": str(request_data["signal_id"]) if request_data.get("signal_id") else None,
            "order_type": request_data.get("order_type", "BUY").upper(),
            "order_subtype": request_data.get("order_subtype", "MARKET").upper(),
            "quantity": quantity,
            "price": request_data.get("price"),
            "trigger_price": request_data.get("trigger_price"),
            "status": "PENDING" if mode == "approval" else "PLACED",
            "mode": mode,
            "stop_loss": request_data.get("stop_loss"),
            "target": request_data.get("target"),
            "notes": request_data.get("notes"),
        }

        created_order = await self.repo.create_order(order_data)
        
        # If paper trading, we might want to auto-execute market orders for simulation
        if mode == "paper" and order_data["order_subtype"] == "MARKET":
            # Simulate immediate execution for paper trading market orders
            await self.repo.update_order_status(created_order["id"], "EXECUTED")
            created_order["status"] = "EXECUTED"

        if hasattr(created_order.get("created_at"), "isoformat"):
            created_order["created_at"] = created_order["created_at"].isoformat()
            
        return {
            "id": created_order["id"],
            "symbol": symbol,
            "order_type": order_data["order_type"],
            "order_subtype": order_data["order_subtype"],
            "quantity": order_data["quantity"],
            "status": created_order["status"],
            "mode": mode,
            "created_at": created_order["created_at"]
        }
