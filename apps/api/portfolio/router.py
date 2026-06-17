"""
Quantro Personal AI — Portfolio Router
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_user, get_db_session
from apps.api.portfolio.service import PortfolioService
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("/holdings")
async def get_holdings(
    source: str = Query("paper", description="paper or groww"),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get portfolio holdings."""
    service = PortfolioService(db)
    holdings = await service.get_holdings(source)
    return APIResponse(data=holdings)


@router.post("/upload")
async def upload_portfolio(
    file: UploadFile = File(...),
    source: str = Form("groww"),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Upload portfolio holdings from an Excel file."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
        
    contents = await file.read()
    service = PortfolioService(db)
    try:
        result = await service.upload_excel_holdings(contents, source)
        return APIResponse(data=result, message=f"Successfully imported {result['holdings_imported']} holdings")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary")
async def get_summary(
    source: str = Query("paper"),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get portfolio summary statistics."""
    service = PortfolioService(db)
    summary = await service.get_summary(source)
    return APIResponse(data=summary)


@router.get("/health")
async def get_health(
    source: str = Query("paper"),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get portfolio health scores and recommendations."""
    service = PortfolioService(db)
    health = await service.get_health(source)
    return APIResponse(data=health)


@router.get("/equity-curve")
async def get_equity_curve(
    source: str = Query("paper"),
    days: int = Query(30, le=365),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get synthetic historical equity curve."""
    service = PortfolioService(db)
    curve = await service.get_equity_curve(source, days)
    return APIResponse(data=curve)
