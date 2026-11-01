"""统一时间能力，应用层统一使用 UTC。"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """返回当前 UTC 时间（带时区）。"""

    return datetime.now(UTC)
