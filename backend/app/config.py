"""
HSE Enterprise Backend Configuration
Multi-environment configuration with Pydantic Settings
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from app.utils.secrets import get_secret, validate_required_secrets, SecretsManager


class Settings(BaseSettings):
    """Application settings loaded from environment variables and secrets."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "HSE Enterprise Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-strong-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/hse_edw"
    DATABASE_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Alert Engine
    ALERT_EMAIL_ENABLED: bool = True
    ALERT_TELEGRAM_ENABLED: bool = False
    ALERT_WHATSAPP_ENABLED: bool = False
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    ALERT_FROM_EMAIL: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Dashboard
    DASHBOARD_REFRESH_INTERVAL_SECONDS: int = 60
    DEFAULT_SITE_ID: str = "SITE-A"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Feature Flags
    ENABLE_PREDICTIVE_ANALYTICS: bool = False
    ENABLE_WEBSOCKET: bool = True
    ENABLE_CACHING: bool = True

    # Security / RBAC
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SYMBOL: bool = True
    PASSWORD_EXPIRE_DAYS: int = 90
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    SESSION_IDLE_TIMEOUT_MINUTES: int = 30
    SESSION_ABSOLUTE_TIMEOUT_HOURS: int = 12
    REQUIRE_PASSWORD_CHANGE_ON_FIRST_LOGIN: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override sensitive settings with secrets if available
        sensitive_settings = {
            "SECRET_KEY": "SECRET_KEY",
            "DATABASE_URL": "DATABASE_URL",
            "REDIS_URL": "REDIS_URL",
            "SMTP_PASSWORD": "SMTP_PASSWORD",
            "TELEGRAM_BOT_TOKEN": "TELEGRAM_BOT_TOKEN",
        }
        for setting_name, secret_name in sensitive_settings.items():
            secret_value = get_secret(secret_name)
            if secret_value is not None:
                setattr(self, setting_name, secret_value)


settings = Settings()

# Validate required secrets in production
if os.getenv("TESTING") != "true" and not settings.DEBUG:
    try:
        validate_required_secrets(["SECRET_KEY", "DATABASE_URL"])
    except ValueError as e:
        import logging
        logging.getLogger(__name__).warning(f"Secrets validation warning: {e}")
