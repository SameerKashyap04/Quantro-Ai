"""
Quantro Personal AI — Backtest Router
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_user, get_db_session
from apps.api.backtest.service import BacktestService
from apps.api.backtest.schemas import BacktestRequest, BacktestResultResponse
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/backtest", tags=["Backtesting"])


@router.get("/results", response_model=APIResponse[list[BacktestResultResponse]])
async def list_results(
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """List recent backtest results."""
    service = BacktestService(db)
    results = await service.get_results()
    return APIResponse(data=results)


@router.get("/results/{result_id}")
async def get_result_detail(
    result_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get detailed backtest result including equity curve."""
    service = BacktestService(db)
    result = await service.get_result(result_id)
    return APIResponse(data=result)


@router.post("/run", response_model=APIResponse[BacktestResultResponse])
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """
    Run a new backtest. 
    In a production setting, this would queue a background task and return a job ID.
    For now, it runs a simulated synchronous backtest.
    """
    service = BacktestService(db)
    result = await service.run_backtest(request.model_dump())
    return APIResponse(data=result, message="Backtest completed")
