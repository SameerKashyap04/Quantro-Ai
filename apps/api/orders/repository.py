"""
Quantro Personal AI — Orders Repository
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class OrderRepository:
    """Data access layer for orders and trades."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_orders(self, status: Optional[str] = None, limit: int = 50) -> list[dict]:
        """Get recent orders."""
        query = """
            SELECT o.*, st.symbol, st.name
            FROM orders o
            JOIN stocks st ON o.stock_id = st.id
        """
        params: dict = {"limit": limit}

        if status:
            query += " WHERE o.status = :status"
            params["status"] = status.upper()

        query += " ORDER BY o.created_at DESC LIMIT :limit"

        result = await self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def create_order(self, order_data: dict) -> dict:
        """Insert a new order."""
        result = await self.db.execute(
            text("""
                INSERT INTO orders (stock_id, signal_id, order_type, order_subtype,
                    quantity, price, trigger_price, status, mode, stop_loss, target, notes)
                VALUES (:stock_id, :signal_id, :order_type, :order_subtype,
                    :quantity, :price, :trigger_price, :status, :mode, :stop_loss, :target, :notes)
                RETURNING id, status, mode, created_at
            """),
            order_data,
        )
        row = result.fetchone()
        return dict(row._mapping) if row else {}

    async def update_order_status(self, order_id: UUID, status: str, **kwargs) -> None:
        """Update order status and optionally execution details."""
        updates = ["status = :status", "updated_at = NOW()"]
        params = {"order_id": str(order_id), "status": status}
        
        if status == "EXECUTED" and "executed_at" not in kwargs:
            updates.append("executed_at = NOW()")
        elif status == "CANCELLED" and "cancelled_at" not in kwargs:
            updates.append("cancelled_at = NOW()")

        for k, v in kwargs.items():
            updates.append(f"{k} = :{k}")
            params[k] = v

        await self.db.execute(
            text(f"UPDATE orders SET {', '.join(updates)} WHERE id = :order_id"),
            params,
        )

    async def get_trades(self, limit: int = 50) -> list[dict]:
        """Get recent trades."""
        result = await self.db.execute(
            text("""
                SELECT t.*, st.symbol
                FROM trades t
                JOIN stocks st ON t.stock_id = st.id
                ORDER BY t.executed_at DESC LIMIT :limit
            """),
            {"limit": limit},
        )
        return [dict(row._mapping) for row in result.fetchall()]
