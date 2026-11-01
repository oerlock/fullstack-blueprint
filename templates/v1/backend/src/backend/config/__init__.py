"""配置管理。"""

__all__ = ["configure_logging", "settings"]

from backend.config.logging import configure_logging
from backend.config.settings import settings

configure_logging(settings)
