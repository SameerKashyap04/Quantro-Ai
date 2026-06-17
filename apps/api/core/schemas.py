"""
Quantro Personal AI — Core Pydantic Schemas
Shared base models and common response schemas.
"""
from datetime import datetime
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel
from uuid import UUID

T = TypeVar("T")


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[T] = None
    message: str = "OK"
    error: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    success: bool = True
    data: list[T] = []
    total: int = 0
    page: int = 1
    page_size: int = 50
    has_next: bool = False


class PaginationParams(BaseModel):
    """Common pagination parameters."""
    page: int = 1
    page_size: int = 50

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class StockSummary(BaseModel):
    """Lightweight stock reference used across modules."""
    id: UUID
    symbol: str
    name: str
    sector: Optional[str] = None
    is_index: bool = False
    is_etf: bool = False


class OHLCVData(BaseModel):
    """Single OHLCV data point."""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, str] = {}
