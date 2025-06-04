from pydantic_settings import BaseSettings
from typing import Literal
from dotenv import load_dotenv
import os


# import appropriate modules
env = os.getenv("ENV", "development")

# Load .env file only if not in production
if env != "production":
    load_dotenv(f".env.{env}")


class BaseSettingsConfig(BaseSettings):
    """
    Base Settings Configuration for the application.
    This class is used to define environment variables and application settings.
    It uses Pydantic's BaseSettings to load environment variables.
    """

    ENV: str
    DEBUG: bool = False
    DATABASE_URL: str
    MONO_BASE_URL: str
    MONO_SECRET_KEY: str
    MONO_WEBHOOK_SECRET: str
    GOOGLE_API_KEY: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TIME_ZONE: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASSWORD: str

    class Config:
        case_sensitive = True


class DevelopmentSettings(BaseSettingsConfig):
    """
    Development Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for development
      environment settings.
    """

    DEBUG: bool = True


class ProductionSettings(BaseSettingsConfig):
    """
    Production Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for production
      environment settings.
    """

    DEBUG: bool = False


class TestingSettings(BaseSettingsConfig):
    """
    Testing Settings Configuration.
    This class inherits from BaseSettingsConfig and is used for testing
      environment settings.
    """

    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"  # Example for testing, can be overridden
