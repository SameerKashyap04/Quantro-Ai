"""
Quantro Personal AI — Logging Middleware
Request/response logging for audit trail.
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("quantro.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing information."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Skip logging for static/health endpoints
        if request.url.path in ("/health", "/favicon.ico"):
            return await call_next(request)

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "%s %s → %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.1f}ms"

        return response
