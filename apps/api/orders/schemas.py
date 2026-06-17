"""
Quantro Personal AI — Orders Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class OrderRequest(BaseModel):
    """Request to place a new order."""
    symbol: str
    order_type: str  # BUY, SELL
    order_subtype: str = "MARKET"  # MARKET, LIMIT, SL, SL-M
    quantity: int
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target: Optional[float] = None
    signal_id: Optional[UUID] = None
    notes: Optional[str] = None


class OrderResponse(BaseModel):
    """Order details."""
    id: UUID
    symbol: str
    order_type: str
    order_subtype: str
    quantity: int
    price: Optional[float] = None
    status: str
    mode: str
    placed_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    created_at: datetime


class TradeResponse(BaseModel):
    """Trade execution details."""
    id: UUID
    order_id: UUID
    symbol: str
    trade_type: str
    executed_quantity: int
    executed_price: float
    total_value: float
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    executed_at: datetime
