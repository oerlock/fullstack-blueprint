"""Pytest 全局夹具。"""

import os

import pytest

# 测试环境：Settings 会额外加载 .env.d/test_app.env，提供测试专属覆盖
os.environ.setdefault("RUNTIME_ENV", "test")

pytest_plugins = (
    "tests.integration.cache.fixtures",
    "tests.integration.database.fixtures",
)

# marker 与对应开关：未开启时整体 skip，保证无服务环境也能跑全量测试
_MARKER_GATES = {
    "requires_database": "--with-database",
    "requires_redis": "--with-redis",
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--with-database",
        action="store_true",
        default=False,
        help="启用需要真实数据库的集成测试",
    )
    parser.addoption(
        "--with-redis",
        action="store_true",
        default=False,
        help="启用需要真实 Redis 的集成测试",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for marker_name, option_name in _MARKER_GATES.items():
        enabled = config.getoption(option_name)
        for item in items:
            if item.get_closest_marker(marker_name) and not enabled:
                marker = pytest.mark.skip(reason=f"未开启 {option_name}，跳过 {marker_name} 测试")
                item.add_marker(marker)
