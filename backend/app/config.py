from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Core
    app_name: str = "Café OS"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-production"

    # Database
    database_url: str = "postgresql://cafe_os:changeme@localhost:5432/cafe_os_dev"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_url: Optional[str] = None

    # Payment providers
    yandex_kassa_shop_id: Optional[str] = None
    yandex_kassa_secret_key: Optional[str] = None

    yukassa_merchant_id: Optional[str] = None
    yukassa_secret_key: Optional[str] = None

    sberpay_merchant_id: Optional[str] = None
    sberpay_secret_key: Optional[str] = None

    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
