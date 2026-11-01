import pytest
from pydantic import ValidationError

from backend.config.settings import CorsSettings


def test_cors_disabled_by_default():
    config = CorsSettings()

    assert config.enabled is False


def test_cors_enabled_requires_origins_or_regex():
    with pytest.raises(ValidationError, match="ALLOW_ORIGINS or ALLOW_ORIGIN_REGEX"):
        CorsSettings(enabled=True)


def test_cors_enabled_with_origin_regex():
    config = CorsSettings(enabled=True, allow_origin_regex=r"https://.*\.example\.com")

    assert config.enabled is True


def test_cors_credentials_reject_wildcard_origin():
    with pytest.raises(ValidationError, match="wildcard origins"):
        CorsSettings(enabled=True, allow_origins=["*"], allow_credentials=True)


def test_settings_normalizes_base_url():
    from backend.config.settings import Settings

    settings_ = Settings(base_url="http://localhost:8000/")

    assert settings_.base_url == "http://localhost:8000"
