"""
Quantro Personal AI — Settings Schemas
"""
from typing import Any
from pydantic import BaseModel


class SystemSettingsUpdate(BaseModel):
    """Update system settings."""
    trading_mode: str  # paper, approval, auto
    notifications_enabled: bool
    telegram_enabled: bool
    auto_signal_generation: bool


class RiskSettingsUpdate(BaseModel):
    """Update risk configuration."""
    max_risk_per_trade_pct: float
    max_daily_drawdown_pct: float
    max_open_positions: int
    max_sector_exposure_pct: float
    position_size_method: str
    emergency_halt_drawdown_pct: float
