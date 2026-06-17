"""
Quantro Personal AI — Market Router
Market data API endpoints.
"""
from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis_lib

from apps.api.dependencies import get_current_user, get_db_session, get_redis_client
from apps.api.market.service import MarketService
from apps.api.market.schemas import (
    StockResponse, StockWithPrice, OHLCVResponse,
    MarketRegimeResponse, ScannerResultResponse,
)
from apps.api.core.schemas import APIResponse, PaginatedResponse

router = APIRouter(prefix="/market", tags=["Market Data"])


@router.get("/stocks", response_model=APIResponse[list[StockWithPrice]])
async def get_stocks(
    sector: Optional[str] = Query(None),
    is_index: Optional[bool] = Query(None),
    is_etf: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    redis: redis_lib.Redis = Depends(get_redis_client),
    _user: dict = Depends(get_current_user),
):
    """Get all tracked stocks with latest prices."""
    service = MarketService(db, redis)
    stocks = await service.get_stocks(
        sector=sector, is_index=is_index, is_etf=is_etf, search=search
    )
    return APIResponse(data=stocks)


@router.get("/stocks/{symbol}", response_model=APIResponse[StockResponse])
async def get_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get details for a specific stock."""
    service = MarketService(db)
    stock = await service.get_stock(symbol)
    return APIResponse(data=stock)


@router.get("/ohlcv/{symbol}", response_model=APIResponse[list[OHLCVResponse]])
async def get_ohlcv(
    symbol: str,
    timeframe: str = Query("daily", description="daily, 15m, or 1h"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(365, le=2000),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get OHLCV data for charting."""
    service = MarketService(db)
    data = await service.get_ohlcv(symbol, timeframe, start_date, end_date, limit)
    return APIResponse(data=data)


@router.get("/regime", response_model=APIResponse[MarketRegimeResponse])
async def get_market_regime(
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get current market regime (bull/bear/sideways)."""
    service = MarketService(db)
    regime = await service.get_regime()
    return APIResponse(data=regime)


@router.get("/sectors", response_model=APIResponse[list[str]])
async def get_sectors(
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get all available sectors."""
    service = MarketService(db)
    sectors = await service.get_sectors()
    return APIResponse(data=sectors)
