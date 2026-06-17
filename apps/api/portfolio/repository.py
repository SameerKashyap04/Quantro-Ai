"""
Quantro Personal AI — Portfolio Repository
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class PortfolioRepository:
    """Data access layer for portfolio."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_holdings(self, source: str = "paper") -> list[dict]:
        """Get all portfolio holdings with stock info."""
        result = await self.db.execute(
            text("""
                SELECT ph.*, st.symbol, st.name, st.sector
                FROM portfolio_holdings ph
                JOIN stocks st ON ph.stock_id = st.id
                WHERE ph.quantity > 0 AND ph.source = :source
                ORDER BY ph.current_value DESC NULLS LAST
            """),
            {"source": source},
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_portfolio_snapshots(self, limit: int = 365) -> list[dict]:
        """Get portfolio value history."""
        result = await self.db.execute(
            text("SELECT * FROM portfolio_snapshots ORDER BY date DESC LIMIT :limit"),
            {"limit": limit},
        )
        rows = [dict(row._mapping) for row in result.fetchall()]
        rows.reverse()
        return rows

    async def upsert_holding(self, holding: dict) -> None:
        """Insert or update a portfolio holding."""
        await self.db.execute(
            text("""
                INSERT INTO portfolio_holdings (stock_id, quantity, avg_buy_price,
                    current_price, invested_value, current_value, pnl, pnl_pct, source)
                VALUES (:stock_id, :quantity, :avg_buy_price, :current_price,
                    :invested_value, :current_value, :pnl, :pnl_pct, :source)
                ON CONFLICT (stock_id, source) DO UPDATE SET
                    quantity = :quantity,
                    avg_buy_price = :avg_buy_price,
                    current_price = :current_price,
                    invested_value = :invested_value,
                    current_value = :current_value,
                    pnl = :pnl,
                    pnl_pct = :pnl_pct,
                    updated_at = NOW()
            """),
            holding,
        )
