"""
Quantro Personal AI — Backtest Service
"""
import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.backtest.repository import BacktestRepository
from apps.api.core.exceptions import NotFoundError


class BacktestService:
    """Backtest business logic and orchestration."""

    def __init__(self, db: AsyncSession):
        self.repo = BacktestRepository(db)

    async def get_results(self) -> list[dict]:
        """Get recent backtest results (summaries)."""
        results = await self.repo.get_results()
        for res in results:
            if hasattr(res.get("created_at"), "isoformat"):
                res["created_at"] = res["created_at"].isoformat()
            if hasattr(res.get("start_date"), "isoformat"):
                res["start_date"] = res["start_date"].isoformat()
            if hasattr(res.get("end_date"), "isoformat"):
                res["end_date"] = res["end_date"].isoformat()
            # Do not return full equity curve/trades in list view to save bandwidth
            res.pop("equity_curve_json", None)
            res.pop("trades_json", None)
        return results

    async def get_result(self, result_id: UUID) -> dict:
        """Get detailed backtest result."""
        result = await self.repo.get_result_by_id(result_id)
        if not result:
            raise NotFoundError(f"Backtest result '{result_id}'")
            
        if hasattr(result.get("created_at"), "isoformat"):
            result["created_at"] = result["created_at"].isoformat()
        if hasattr(result.get("start_date"), "isoformat"):
            result["start_date"] = result["start_date"].isoformat()
        if hasattr(result.get("end_date"), "isoformat"):
            result["end_date"] = result["end_date"].isoformat()
            
        return result

    async def run_backtest(self, request_data: dict) -> dict:
        """
        Orchestrate a backtest run.
        In a real implementation, this would call the actual Backtest Engine.
        For now, this is a placeholder that simulates a run and returns a mock result.
        """
        # Mock logic for demonstration
        import random
        from datetime import datetime
        
        initial_cap = request_data.get("initial_capital", 100000.0)
        final_cap = initial_cap * (1 + random.uniform(-0.1, 0.4))
        
        mock_result = {
            "strategy_name": request_data["strategy_name"],
            "strategy_type": request_data.get("strategy_type", "indicator"),
            "params_json": json.dumps(request_data.get("params", {})),
            "start_date": request_data["start_date"],
            "end_date": request_data["end_date"],
            "initial_capital": initial_cap,
            "final_capital": final_cap,
            "total_trades": random.randint(20, 100),
            "winning_trades": random.randint(10, 60),
            "losing_trades": random.randint(10, 40),
            "win_rate": random.uniform(40.0, 70.0),
            "cagr": random.uniform(-5.0, 30.0),
            "sharpe_ratio": random.uniform(0.5, 2.5),
            "sortino_ratio": random.uniform(0.8, 3.5),
            "max_drawdown": random.uniform(5.0, 25.0),
            "profit_factor": random.uniform(0.8, 2.5),
            "avg_win": random.uniform(1000, 5000),
            "avg_loss": random.uniform(500, 3000),
            "equity_curve_json": "[]", # Mock
            "trades_json": "[]", # Mock
            "metrics_json": "{}"
        }
        
        saved_result = await self.repo.save_result(mock_result)
        mock_result["id"] = saved_result["id"]
        mock_result["created_at"] = saved_result["created_at"].isoformat()
        
        # Format dates for response
        if hasattr(mock_result.get("start_date"), "isoformat"):
            mock_result["start_date"] = mock_result["start_date"].isoformat()
        if hasattr(mock_result.get("end_date"), "isoformat"):
            mock_result["end_date"] = mock_result["end_date"].isoformat()
            
        return mock_result
