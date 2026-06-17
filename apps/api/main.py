"""
Quantro Personal AI — FastAPI Application Entrypoint
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.config import get_settings
from apps.api.middleware.logging_middleware import LoggingMiddleware
from apps.api.middleware.rate_limiter import RateLimiterMiddleware
from apps.api.core.exceptions import QuantroException

# Import routers
from apps.api.auth.router import router as auth_router
from apps.api.market.router import router as market_router
from apps.api.signals.router import router as signals_router
from apps.api.portfolio.router import router as portfolio_router
from apps.api.orders.router import router as orders_router
from apps.api.backtest.router import router as backtest_router
from apps.api.settings.router import router as settings_router

settings = get_settings()


from apps.api.tasks import scheduler_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events (startup/shutdown)."""
    # Startup: Initialize connections, start scheduler, load ML models into memory
    print(f"Starting {settings.app_name} in {settings.app_env} mode...")
    scheduler_instance.start()
    yield
    # Shutdown: Clean up connections, stop scheduler
    print(f"Shutting down {settings.app_name}...")
    scheduler_instance.stop()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to frontend URL
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimiterMiddleware, max_requests=200, window_seconds=60)

# Exception Handler
@app.exception_handler(QuantroException)
async def quantro_exception_handler(request, exc: QuantroException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error": exc.__class__.__name__},
    )

# Exception Handler for Validation Errors
@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": str(exc), "error": "ValidationError"},
    )

# Include Routers
api_prefix = "/api"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(market_router, prefix=api_prefix)
app.include_router(signals_router, prefix=api_prefix)
app.include_router(portfolio_router, prefix=api_prefix)
app.include_router(orders_router, prefix=api_prefix)
app.include_router(backtest_router, prefix=api_prefix)
app.include_router(settings_router, prefix=api_prefix)


@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
