"""build_cache_key 单元测试。"""

import pytest

from backend.infrastructure.cache.keys import build_cache_key


def test_joins_segments():
    key = build_cache_key("app", "dev", "account", "user", 1)

    assert key == "app:dev:account:user:1"


def test_accepts_allowed_characters():
    key = build_cache_key("app.eval", "local", "obj.v2", "a-b_c")

    assert key == "app.eval:local:obj.v2:a-b_c"


@pytest.mark.parametrize(
    "segment",
    ["", "a b", "a:b", "a/b", "a\nb"],
)
def test_invalid_segment_rejected(segment):
    with pytest.raises(ValueError, match="Invalid cache key segment"):
        build_cache_key("app", "dev", segment)
