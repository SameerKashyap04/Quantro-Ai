"""
Quantro Personal AI — Auth Router
Authentication endpoints.
"""
from fastapi import APIRouter

from apps.api.auth.schemas import LoginRequest, TokenResponse, RefreshRequest
from apps.api.auth.service import AuthService
from apps.api.core.schemas import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(request: LoginRequest):
    """Authenticate and receive JWT tokens."""
    result = AuthService.authenticate(request.username, request.password)
    return APIResponse(data=TokenResponse(**result), message="Login successful")


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(request: RefreshRequest):
    """Refresh an expired access token."""
    result = AuthService.refresh(request.refresh_token)
    return APIResponse(data=TokenResponse(**result), message="Token refreshed")
