"""
Quantro Personal AI — Signals Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class SignalResponse(BaseModel):
    """Trading signal."""
    id: UUID
    symbol: str
    name: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    stop_loss_pct: Optional[float] = None
    target_pct: Optional[float] = None
    risk_level: Optional[str] = None
    strategy_name: Optional[str] = None
    ai_bullish_prob: Optional[float] = None
    ai_bearish_prob: Optional[float] = None
    holding_period_days: Optional[int] = None
    reasoning: Optional[dict] = None
    created_at: Optional[datetime] = None


class SignalFilterRequest(BaseModel):
    """Signal filter parameters."""
    signal_type: Optional[str] = None  # BUY, SELL, HOLD
    min_confidence: Optional[float] = None
    risk_level: Optional[str] = None
    strategy_name: Optional[str] = None
    limit: int = 50
