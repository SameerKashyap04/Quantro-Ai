"""
Quantro Personal AI — Redis Client
Redis connection pool for caching.
"""
import redis.asyncio as redis

from apps.api.config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.redis_url,
    decode_responses=True,
    max_connections=20,
)


async def get_redis() -> redis.Redis:
    """Dependency: yield a Redis connection."""
    client = redis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()


async def get_redis_client() -> redis.Redis:
    """Get a Redis client directly (non-dependency use)."""
    return redis.Redis(connection_pool=redis_pool)
