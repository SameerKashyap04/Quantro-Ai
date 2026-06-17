"""
Quantro Personal AI — Shared Models (Non-ORM)
"""
from typing import Optional
from pydantic import BaseModel


class RiskConfig(BaseModel):
    """Internal representation of risk rules."""
    max_risk_per_trade_pct: float
    max_daily_drawdown_pct: float
    max_open_positions: int
    max_sector_exposure_pct: float
    position_size_method: str
    emergency_halt_drawdown_pct: float


class IndicatorParams(BaseModel):
    """Parameters for running indicators."""
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    atr_period: int = 14
    bb_period: int = 20
    bb_std: float = 2.0
    ema_short: int = 20
    ema_medium: int = 50
    ema_long: int = 200
