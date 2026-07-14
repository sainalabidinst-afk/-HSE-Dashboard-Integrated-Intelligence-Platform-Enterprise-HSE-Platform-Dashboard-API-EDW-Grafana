"""
Secrets Management for HSE Enterprise Platform.
Supports multiple secret sources in order of precedence:
1. Docker secrets (/run/secrets/)
2. Azure Key Vault (production)
3. Environment variables (development)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Secrets that should never be logged
SENSITIVE_SECRETS = {
    "SECRET_KEY",
    "DATABASE_URL",
    "REDIS_URL",
    "SMTP_PASSWORD",
    "TELEGRAM_BOT_TOKEN",
    "POSTGRES_PASSWORD",
    "GRAFANA_PASSWORD",
    "PGADMIN_PASSWORD",
    "INFLUXDB_PASSWORD",
    "REDIS_PASSWORD",
}


def get_docker_secret(secret_name: str) -> Optional[str]:
    """
    Read secret from Docker secrets mount.
    Docker secrets are mounted at /run/secrets/<secret_name>
    """
    secret_path = f"/run/secrets/{secret_name}"
    try:
        with open(secret_path, "r") as f:
            value = f.read().strip()
            if value:
                return value
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.warning(f"Failed to read Docker secret {secret_name}: {e}")
    return None


def get_azure_key_vault_secret(secret_name: str) -> Optional[str]:
    """
    Read secret from Azure Key Vault.
    Requires AZURE_KEY_VAULT_URL environment variable.
    """
    vault_url = os.getenv("AZURE_KEY_VAULT_URL")
    if not vault_url:
        return None

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        logger.warning(f"Failed to read Azure Key Vault secret {secret_name}: {e}")
        return None


def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get secret from the highest priority source available.
    Precedence: Docker secrets > Azure Key Vault > Environment variables > default
    """
    # 1. Try Docker secrets
    value = get_docker_secret(secret_name)
    if value is not None:
        logger.info(f"Secret {secret_name} loaded from Docker secrets")
        return value

    # 2. Try Azure Key Vault
    value = get_azure_key_vault_secret(secret_name)
    if value is not None:
        logger.info(f"Secret {secret_name} loaded from Azure Key Vault")
        return value

    # 3. Try environment variables
    value = os.getenv(secret_name)
    if value is not None:
        logger.info(f"Secret {secret_name} loaded from environment variable")
        return value

    # 4. Return default
    if default is not None:
        logger.info(f"Secret {secret_name} using default value")
        return default

    return None


def validate_required_secrets(required_secrets: list[str]) -> None:
    """
    Validate that all required secrets are available.
    Raises ValueError if any required secret is missing.
    """
    missing = []
    for secret_name in required_secrets:
        value = get_secret(secret_name)
        if not value:
            missing.append(secret_name)

    if missing:
        raise ValueError(
            f"Missing required secrets: {', '.join(missing)}. "
            f"Please set them via Docker secrets, Azure Key Vault, or environment variables."
        )

    logger.info(f"All {len(required_secrets)} required secrets validated successfully")


def mask_secret(value: str) -> str:
    """Mask a secret value for logging."""
    if not value or len(value) <= 8:
        return "***"
    return value[:4] + "***" + value[-4:]


def get_safe_env_info() -> dict:
    """
    Get environment information with secrets masked.
    Useful for health checks and diagnostics.
    """
    env_info = {}
    for key in sorted(os.environ.keys()):
        if key in SENSITIVE_SECRETS:
            env_info[key] = mask_secret(os.getenv(key, ""))
        else:
            env_info[key] = os.getenv(key, "")
    return env_info


class SecretsManager:
    """
    Singleton secrets manager for the application.
    Provides centralized access to all secrets with automatic source detection.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._secrets_cache = {}

    def get(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret with caching."""
        if secret_name not in self._secrets_cache:
            self._secrets_cache[secret_name] = get_secret(secret_name, default)
        return self._secrets_cache[secret_name]

    def validate(self, required_secrets: list[str]) -> None:
        """Validate required secrets."""
        validate_required_secrets(required_secrets)

    def get_safe_config(self) -> dict:
        """Get configuration with secrets masked."""
        return get_safe_env_info()
