"""RedisSettings 单元测试。"""

import pytest
from pydantic import ValidationError

from backend.config.settings import Settings
from backend.infrastructure.cache.redis.config import RedisSettings


def test_defaults():
    settings = RedisSettings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 6382
    assert settings.database == 0
    assert settings.username is None
    assert settings.password is None
    assert settings.ssl is False
    assert settings.max_connections == 10
    assert settings.socket_connect_timeout == 3.0
    assert settings.socket_timeout == 3.0
    assert settings.health_check_interval == 30
    assert settings.key_prefix == "app"
    assert settings.required is False


def test_settings_redis_env_override(monkeypatch):
    monkeypatch.setenv("REDIS__HOST", "redis.example.com")
    monkeypatch.setenv("REDIS__PORT", "6400")
    monkeypatch.setenv("REDIS__PASSWORD", "secret")
    monkeypatch.setenv("REDIS__REQUIRED", "true")

    settings_ = Settings(_env_file=None)

    assert settings_.redis.host == "redis.example.com"
    assert settings_.redis.port == 6400
    assert settings_.redis.password is not None
    assert settings_.redis.password.get_secret_value() == "secret"
    assert settings_.redis.required is True


@pytest.mark.parametrize("prefix", ["", "a b", "a:b", "前缀"])
def test_invalid_key_prefix_rejected(prefix):
    with pytest.raises(ValidationError):
        RedisSettings(key_prefix=prefix)


def test_invalid_port_rejected():
    with pytest.raises(ValidationError):
        RedisSettings(port=70000)
