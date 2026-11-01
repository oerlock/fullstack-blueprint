import time

import pytest

from backend.core.uuid import uuid7, uuid_from_bin, uuid_to_bin


def test_uuid7_version_and_uniqueness():
    values = {uuid7() for _ in range(1000)}

    assert len(values) == 1000
    for value in values:
        assert value.version == 7


def test_uuid7_timestamp_matches_current_time():
    before_ms = time.time_ns() // 1_000_000
    value = uuid7()
    after_ms = time.time_ns() // 1_000_000

    timestamp_ms = int.from_bytes(value.bytes[:6], "big")
    assert before_ms <= timestamp_ms <= after_ms


def test_uuid_to_bin_roundtrip():
    value = uuid7()

    assert uuid_from_bin(uuid_to_bin(value)) == value


def test_uuid_from_bin_invalid_length():
    with pytest.raises(ValueError, match="16 字节"):
        uuid_from_bin(b"short")
