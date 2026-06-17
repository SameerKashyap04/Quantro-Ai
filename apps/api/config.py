"""
Quantro Personal AI — Application Configuration
Loads settings from environment variables with Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    app_name: str = "Quantro Personal AI"
    app_env: str = "development"
    secret_key: str = "change-me-to-a-random-64-char-string"
    debug: bool = True

    # Database
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_db: str = "quantro_db"
    postgres_user: str = "quantro"
    postgres_password: str = "secretpassword"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "redis"
    redis_port: int = 6379

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    # JWT
    jwt_secret_key: str = "change-me-to-another-random-64-char-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours
    jwt_refresh_token_expire_days: int = 30

    # Admin
    admin_username: str = "admin"
    admin_password: str = "change-me-admin-password"

    # Groww
    groww_api_key: str = ""
    groww_api_secret: str = ""
    groww_access_token: str = ""
    
    # Generic Broker
    broker_api_key: str = ""
    broker_api_secret: str = ""
    broker_env: str = "sandbox"

    # Telegram
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Trading
    trading_mode: str = "paper"  # paper, approval, auto

    # Risk
    max_risk_per_trade_pct: float = 2.0
    max_daily_drawdown_pct: float = 3.0
    max_open_positions: int = 10
    max_sector_exposure_pct: float = 30.0
    emergency_halt_drawdown_pct: float = 5.0

    # Market Data
    market_data_provider: str = "yfinance"
    data_collection_timezone: str = "Asia/Kolkata"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
