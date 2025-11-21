from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None

    # Load environment variables from a .env file using new Pydantic v2 syntax
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None
    DB_FORCE_ROLL_BACK: bool = False
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")


class TestConfig(GlobalConfig):
    # Use an in-memory SQLite database for tests
    DATABASE_URL: str = "sqlite:///test.db"  # Ensure tests use a test database
    DB_FORCE_ROLL_BACK: bool = True
    model_config = SettingsConfigDict(env_prefix="TEST_")


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")


# lru_cache to avoid reloading config multiple times
@lru_cache()
def get_config(env_state: str):
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig,
    }
    return configs[env_state]()


config = get_config(BaseConfig().ENV_STATE)
