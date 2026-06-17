"""
Quantro Personal AI — Market Schemas
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class StockResponse(BaseModel):
    """Stock instrument details."""
    id: UUID
    symbol: str
    name: str
    sector: Optional[str] = None
    market_cap_category: Optional[str] = None
    exchange: str = "NSE"
    is_index: bool = False
    is_etf: bool = False
    is_active: bool = True


class OHLCVResponse(BaseModel):
    """OHLCV candle data point."""
    date: str  # ISO date or datetime string
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockWithPrice(StockResponse):
    """Stock with latest price info."""
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None
    volume: Optional[int] = None


class MarketRegimeResponse(BaseModel):
    """Current market regime."""
    date: str
    regime: str  # 'bull', 'bear', 'sideways'
    confidence: Optional[float] = None
    nifty_trend: Optional[str] = None
    vix_level: Optional[float] = None


class ScannerResultResponse(BaseModel):
    """Market scanner result for a single stock."""
    symbol: str
    name: str
    sector: Optional[str] = None
    current_price: float
    change_pct: float
    bullish_score: float
    bearish_score: float
    volume_score: float
    momentum_score: float
    signal: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float


class StockFilterRequest(BaseModel):
    """Filter parameters for stock queries."""
    sector: Optional[str] = None
    is_index: Optional[bool] = None
    is_etf: Optional[bool] = None
    market_cap_category: Optional[str] = None
    search: Optional[str] = None
