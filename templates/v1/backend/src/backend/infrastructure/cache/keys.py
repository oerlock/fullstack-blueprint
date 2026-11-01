"""缓存 key 构建与校验。"""

import re

_KEY_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def build_cache_key(prefix: str, runtime_env: str, *segments: object) -> str:
    """拼接 `{prefix}:{runtime_env}:{segment...}`，segment 非法时抛 ValueError。"""
    parts = (prefix, runtime_env, *(str(segment) for segment in segments))
    for part in parts:
        if not _KEY_SEGMENT_PATTERN.fullmatch(part):
            raise ValueError(f"Invalid cache key segment: {part!r}")
    return ":".join(parts)
