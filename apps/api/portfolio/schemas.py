"""
Quantro Personal AI — Portfolio Schemas
"""
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class HoldingResponse(BaseModel):
    """Portfolio holding."""
    id: UUID
    symbol: str
    name: str
    sector: Optional[str] = None
    quantity: int
    avg_buy_price: float
    current_price: Optional[float] = None
    invested_value: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    day_change: Optional[float] = None
    day_change_pct: Optional[float] = None
    weight_pct: Optional[float] = None  # portfolio weight


class PortfolioSummary(BaseModel):
    """Portfolio summary stats."""
    total_value: float = 0
    invested_value: float = 0
    total_pnl: float = 0
    total_pnl_pct: float = 0
    daily_pnl: float = 0
    daily_pnl_pct: float = 0
    num_holdings: int = 0


class PortfolioHealthResponse(BaseModel):
    """Portfolio health scores."""
    health_score: float  # 0-100
    diversification_score: float  # 0-100
    concentration_risk: float  # 0-100 (lower is better)
    sector_allocation: dict  # sector -> percentage
    top_holdings: list[dict]  # top 5 by weight
    recommendations: list[str]  # improvement suggestions
