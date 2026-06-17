"""
Quantro Personal AI — Backtest Schemas
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class BacktestRequest(BaseModel):
    """Request to run a new backtest."""
    strategy_name: str
    strategy_type: str = "indicator"  # indicator, ai, hybrid
    symbols: list[str]
    start_date: date
    end_date: date
    initial_capital: float = 100000.0
    params: dict = {}


class BacktestResultResponse(BaseModel):
    """Backtest results summary."""
    id: UUID
    strategy_name: str
    strategy_type: str
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    cagr: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    profit_factor: float
    created_at: datetime
