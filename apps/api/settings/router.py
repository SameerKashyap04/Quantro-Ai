"""
Quantro Personal AI — Settings Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.dependencies import get_current_user, get_db_session
from apps.api.settings.service import SettingsService
from apps.api.settings.schemas import SystemSettingsUpdate, RiskSettingsUpdate
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=APIResponse[dict])
async def get_settings(
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Get all application and risk settings."""
    service = SettingsService(db)
    settings = await service.get_all_settings()
    return APIResponse(data=settings)


@router.put("/system")
async def update_system_settings(
    request: SystemSettingsUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Update system settings."""
    service = SettingsService(db)
    await service.update_system_settings(request.model_dump())
    return APIResponse(message="System settings updated")


@router.put("/risk")
async def update_risk_settings(
    request: RiskSettingsUpdate,
    db: AsyncSession = Depends(get_db_session),
    _user: dict = Depends(get_current_user),
):
    """Update risk management rules."""
    service = SettingsService(db)
    await service.update_risk_settings(request.model_dump())
    return APIResponse(message="Risk settings updated")
