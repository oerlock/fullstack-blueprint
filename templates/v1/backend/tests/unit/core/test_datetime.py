from datetime import UTC, datetime

from backend.core.datetime import utcnow


def test_utcnow_is_aware_and_utc():
    value = utcnow()

    assert value.tzinfo is UTC
    assert isinstance(value, datetime)
