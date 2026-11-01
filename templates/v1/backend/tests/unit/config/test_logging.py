import logging

import pytest

from backend.config.logging import configure_logging, setup_logging


@pytest.fixture
def logging_config(tmp_path):
    config_file = tmp_path / "logging.yaml"
    config_file.write_text(
        """
version: 1
disable_existing_loggers: false

root:
  level: INFO

loggers:
  backend.test:
    level: INFO
""",
        encoding="utf-8",
    )
    return config_file


def test_setup_logging_applies_yaml(logging_config):
    setup_logging(logging_config)

    assert logging.getLogger("backend.test").level == logging.INFO


def test_setup_logging_merges_override_file(logging_config):
    logging_config.with_name("logging.override.yaml").write_text(
        """
loggers:
  backend.test:
    level: DEBUG
""",
        encoding="utf-8",
    )

    setup_logging(logging_config)

    assert logging.getLogger("backend.test").level == logging.DEBUG


def test_setup_logging_applies_global_level(logging_config):
    setup_logging(logging_config, global_level=logging.WARNING)

    assert logging.getLogger().level == logging.WARNING
    assert logging.getLogger("backend.test").level == logging.WARNING


def test_setup_logging_rejects_non_mapping(tmp_path):
    config_file = tmp_path / "bad.yaml"
    config_file.write_text("- just\n- a\n- list\n", encoding="utf-8")

    with pytest.raises(TypeError, match="mapping"):
        setup_logging(config_file)


def test_configure_logging_is_idempotent(logging_config):
    class StubSettings:
        logger_config_path = logging_config

        class logging:
            global_level = None

    configure_logging(StubSettings(), force=True)
    # 再次调用且未 force 时不重复执行
    configure_logging(StubSettings())
