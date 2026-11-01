"""数据库连接配置。"""

from pydantic import BaseModel, Field, SecretStr


class DatabaseSettings(BaseModel):
    """数据库连接与连接池参数，环境变量前缀 DATABASE__。"""

    host: str = "127.0.0.1"
    port: int = Field(3307, ge=1, le=65535)
    user: str = "app"
    password: SecretStr = Field(default=SecretStr(""))
    database: str = "app"
    test_database: str = "app_test"
    pool_size: int = Field(10, ge=1)
    max_overflow: int = Field(20, ge=0)
    pool_recycle: int = Field(1800, gt=0)
    pool_pre_ping: bool = True
    echo: bool = False
