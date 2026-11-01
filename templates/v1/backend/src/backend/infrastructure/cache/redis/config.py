"""Redis 连接配置。"""

from pydantic import BaseModel, Field, SecretStr, field_validator

_KEY_PREFIX_CHARS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
)


class RedisSettings(BaseModel):
    """Redis 连接与连接池参数，环境变量前缀 REDIS__。"""

    host: str = "127.0.0.1"
    port: int = Field(6382, ge=1, le=65535)
    database: int = Field(0, ge=0)
    test_database: int = Field(1, ge=0)  # 测试专用 DB 号，经 test_app.env 覆盖
    username: str | None = None
    password: SecretStr | None = None
    ssl: bool = False
    max_connections: int = Field(10, ge=1)
    socket_connect_timeout: float = Field(3.0, gt=0)
    socket_timeout: float = Field(3.0, gt=0)
    health_check_interval: int = Field(30, ge=0)
    key_prefix: str = "app"
    required: bool = False

    @field_validator("key_prefix")
    @classmethod
    def validate_key_prefix(cls, value: str) -> str:
        if not value or any(char not in _KEY_PREFIX_CHARS for char in value):
            raise ValueError("REDIS__KEY_PREFIX contains invalid characters")
        return value
