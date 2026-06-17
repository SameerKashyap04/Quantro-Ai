"""
Quantro Personal AI — FastAPI Dependencies
Common dependency injection functions.
"""
from typing import Optional
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis_lib

from apps.api.database import get_db
from apps.api.redis_client import get_redis
from apps.api.core.security import decode_token
from apps.api.core.exceptions import AuthenticationError

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> dict:
    """Validate JWT token and return user payload."""
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")
    return payload


async def get_db_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    """Alias for database session dependency."""
    return session


async def get_redis_client(client: redis_lib.Redis = Depends(get_redis)) -> redis_lib.Redis:
    """Alias for Redis client dependency."""
    return client
