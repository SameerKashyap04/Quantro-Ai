"""
Quantro Personal AI — Orders Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_user, get_db_session
from apps.api.orders.service import OrderService
from apps.api.orders.schemas import OrderRequest, OrderResponse, TradeResponse
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=APIResponse[list[OrderResponse]])
async def list_orders(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """List recent orders."""
    service = OrderService(db)
    orders = await service.get_orders(status=status)
    return APIResponse(data=orders)


@router.post("/place", response_model=APIResponse[OrderResponse])
async def place_order(
    request: OrderRequest,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Place a new order (paper, approval, or real based on settings)."""
    service = OrderService(db)
    order = await service.place_order(request.model_dump())
    return APIResponse(data=order, message="Order processed successfully")
