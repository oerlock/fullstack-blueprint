"""统一配置入口，管理环境配置及运行参数。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncEngine

from backend.infrastructure.async_task.schemas import TasksSettings
from backend.infrastructure.cache.clients import CacheClients
from backend.infrastructure.cache.redis.config import RedisSettings
from backend.infrastructure.database.config import DatabaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class RuntimeSettings(BaseSettings):
    """Bootstrap settings used to select environment-specific env files."""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    runtime_env: Literal["local", "dev", "test", "staging", "production"] = "production"


class LoggingSettings(BaseModel):
    """Application logging options."""

    config_path: Path = Path("src/backend/config/log/logging.yaml")
    global_level: str | int | None = None


class CorsSettings(BaseModel):
    """CORS 策略配置。"""

    enabled: bool = False
    allow_origins: list[str] = Field(default_factory=list)
    allow_origin_regex: str | None = None
    allow_methods: list[str] = Field(default_factory=lambda: ["GET"])
    allow_headers: list[str] = Field(default_factory=list)
    allow_credentials: bool = False
    expose_headers: list[str] = Field(default_factory=list)
    max_age: int = Field(default=600, ge=0)

    @model_validator(mode="after")
    def validate_policy(self) -> "CorsSettings":
        if self.enabled and not self.allow_origins and self.allow_origin_regex is None:
            raise ValueError(
                "CORS requires ALLOW_ORIGINS or ALLOW_ORIGIN_REGEX when enabled"
            )
        if self.allow_credentials and "*" in self.allow_origins:
            raise ValueError(
                "CORS ALLOW_CREDENTIALS cannot be combined with wildcard origins"
            )
        return self


def _default_env_files(project_root: Path = PROJECT_ROOT) -> tuple[Path, ...]:
    app_env = project_root / ".env.d" / "app.env"
    runtime_settings = RuntimeSettings(_env_file=app_env)
    env_files: list[Path] = [app_env]
    if runtime_settings.runtime_env == "test":
        env_files.append(project_root / ".env.d" / "test_app.env")
    return tuple(env_files)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        validate_by_name=True,
    )

    project_root: Path = PROJECT_ROOT
    runtime_env: Literal["local", "dev", "test", "staging", "production"] = "production"
    base_url: str = "http://localhost:8000"

    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    tasks: TasksSettings = Field(default_factory=TasksSettings)

    _cache_clients: CacheClients | None = PrivateAttr(default=None)
    _database_engine: AsyncEngine | None = PrivateAttr(default=None)

    @property
    def cache_clients(self) -> CacheClients:
        if self._cache_clients is None:
            self._cache_clients = CacheClients(self.redis)
        return self._cache_clients

    @property
    def database_engine(self) -> AsyncEngine:
        if self._database_engine is None:
            from backend.infrastructure.database.engine import create_database_engine

            self._database_engine = create_database_engine(self.database)
        return self._database_engine

    @field_validator("base_url")
    @classmethod
    def normalize_base_url(cls, value: str) -> str:
        return value.rstrip("/")

    @property
    def logger_config_path(self) -> Path:
        if self.logging.config_path.is_absolute():
            return self.logging.config_path
        return self.project_root / self.logging.config_path


@lru_cache
def get_settings() -> Settings:
    return Settings(_env_file=_default_env_files())


class _SettingsProxy:
    def __getattr__(self, name: str):
        return getattr(get_settings(), name)

    def __dir__(self) -> list[str]:
        return dir(get_settings())


settings = cast(Settings, _SettingsProxy())
