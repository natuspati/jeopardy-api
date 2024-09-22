import enum
from pathlib import Path
from typing import Any, Literal

import pytz
import uvicorn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from api.enums.app_state import AppEnvironmentEnum
from cutom_types.database import ISOLATION_LEVEL_TYPE

APP_ROOT = Path(__file__).parent


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    notset = "NOTSET"
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    fatal = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured with environment variables.

    Environment variables must be prefixed with value set in
    `model_config` `env_prefix`.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="JEOPARDY_",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    # Quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = True

    # Current environment
    environment: Literal["test", "local", "dev", "prod"] = "local"
    service_name: str = "Jeopardy"
    secret_key: str = "jeopardy"

    # Authentication
    algorithm: str = "HS256"
    token_type: str = "bearer"
    access_token_expire_min: int = 60  # in minutes

    # Pagination
    page_size: int = 50
    max_query_limit: int = 100

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str | None = "jeopardy"
    db_pass: str | None = "jeopardy"
    db_name: str | None = "jeopardy"
    db_echo: bool = False
    db_echo_pool: bool = False
    db_isolation_level: ISOLATION_LEVEL_TYPE = "READ COMMITTED"
    db_expire_on_commit: bool = False

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_pass: str | None = None
    redis_socket_timeout: int = 3
    redis_default_expiration_time: int | None = 60 * 60  # 1 hour
    redis_encoding: str = "utf-8"
    redis_namespace: str = "jeopardy_"
    redis_empty_value: str = "not_found"

    # Timezone as pytz timezone string
    pytz_timezone: str = "Etc/GMT-5"

    @property
    def app_environment(self) -> AppEnvironmentEnum:
        """
        Application environment.

        :return: application environment
        """
        return AppEnvironmentEnum(self.environment)

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            username=self.db_user,
            password=self.db_pass,
            database=self.db_name,
        )

    @property
    def timezone(self) -> pytz.timezone:
        """
        Get current timezone.

        :return: timezone as `pytz.timezone`
        """
        return pytz.timezone(self.pytz_timezone)


settings = Settings()


class LoggingSettings(BaseSettings):
    log_formatting: str = (
        f"%(levelname)s: [{settings.service_name}] %(asctime)s | %(name)s\n%(message)s"
    )
    date_formatting: str = "%Y-%m-%d %H:%M:%S"

    @property
    def log_level(self) -> LogLevel:
        """
        Get log level from app environment.

        :return: log level
        """
        match settings.app_environment:
            case AppEnvironmentEnum.dev:
                level = LogLevel.info
            case AppEnvironmentEnum.prod:
                level = LogLevel.warning
            case AppEnvironmentEnum.test:
                level = LogLevel.info
            case _:
                level = LogLevel.debug
        return level

    @property
    def uvicorn_config(self) -> dict[str, Any]:
        """
        Get new uvicorn config according to the configured formatting.

        :return: configuration dict
        """
        log_config = uvicorn.config.LOGGING_CONFIG
        log_config["formatters"]["access"]["fmt"] = self.log_formatting
        log_config["formatters"]["default"]["fmt"] = self.log_formatting
        return log_config


logging_settings = LoggingSettings()
