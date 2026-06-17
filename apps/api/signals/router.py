"""
Quantro Personal AI — Signals Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_user, get_db_session
from apps.api.signals.service import SignalService
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/signals", tags=["Signals"])


@router.get("/latest")
async def get_latest_signals(
    signal_type: Optional[str] = Query(None, description="BUY, SELL, or HOLD"),
    min_confidence: Optional[float] = Query(None, ge=0, le=100),
    risk_level: Optional[str] = Query(None),
    portfolio_only: bool = Query(False),
    market_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get latest trading signals ranked by confidence."""
    service = SignalService(db)
    signals = await service.get_latest(
        signal_type=signal_type,
        min_confidence=min_confidence,
        risk_level=risk_level,
        portfolio_only=portfolio_only,
        market_only=market_only,
        limit=limit,
    )
    return APIResponse(data=signals)


@router.post("/analyze-market")
async def analyze_market(
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Dynamically generate AI signals for top market opportunities."""
    service = SignalService(db)
    try:
        signals = await service.analyze_market_opportunities(limit)
        return APIResponse(
            data=signals,
            message=f"Successfully analyzed market and generated {len(signals)} signals"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}")
async def get_signal_history(
    symbol: str,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get signal history for a specific stock."""
    service = SignalService(db)
    signals = await service.get_by_symbol(symbol, limit)
    return APIResponse(data=signals)

@router.post("/analyze-portfolio")
async def analyze_portfolio(
    source: str = Query("groww"),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Dynamically generate AI signals for all holdings in the portfolio."""
    service = SignalService(db)
    try:
        signals = await service.analyze_portfolio_holdings(source)
        return APIResponse(
            data=signals, 
            message=f"Successfully analyzed portfolio and generated {len(signals)} signals"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))
