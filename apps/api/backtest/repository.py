"""
Quantro Personal AI — Backtest Repository
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BacktestRepository:
    """Data access layer for backtest results."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_results(self, limit: int = 20) -> list[dict]:
        """Get recent backtest results."""
        result = await self.db.execute(
            text("SELECT * FROM backtest_results ORDER BY created_at DESC LIMIT :limit"),
            {"limit": limit},
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_result_by_id(self, result_id: UUID) -> Optional[dict]:
        """Get a specific backtest result with full details (equity curve, trades)."""
        result = await self.db.execute(
            text("SELECT * FROM backtest_results WHERE id = :id"),
            {"id": str(result_id)},
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def save_result(self, result_data: dict) -> dict:
        """Save a new backtest result."""
        result = await self.db.execute(
            text("""
                INSERT INTO backtest_results (
                    strategy_name, strategy_type, params_json, start_date, end_date,
                    initial_capital, final_capital, total_trades, winning_trades, losing_trades,
                    win_rate, cagr, sharpe_ratio, sortino_ratio, max_drawdown, profit_factor,
                    avg_win, avg_loss, equity_curve_json, trades_json, metrics_json
                ) VALUES (
                    :strategy_name, :strategy_type, :params_json::jsonb, :start_date, :end_date,
                    :initial_capital, :final_capital, :total_trades, :winning_trades, :losing_trades,
                    :win_rate, :cagr, :sharpe_ratio, :sortino_ratio, :max_drawdown, :profit_factor,
                    :avg_win, :avg_loss, :equity_curve_json::jsonb, :trades_json::jsonb, :metrics_json::jsonb
                ) RETURNING id, created_at
            """),
            result_data,
        )
        row = result.fetchone()
        return dict(row._mapping) if row else {}
