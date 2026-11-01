"""日志配置。"""

import sys
from collections.abc import Mapping
from logging.config import dictConfig
from pathlib import Path
from typing import Any

import yaml

_configured = False


def _merge_mappings(base: dict[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = base.copy()
    for key, override_value in override.items():
        base_value = merged.get(key)
        if isinstance(base_value, Mapping) and isinstance(override_value, Mapping):
            merged[key] = _merge_mappings(dict(base_value), override_value)
            continue

        merged[key] = override_value

    return merged


def setup_logging(config_path: Path, global_level: str | int | None = None) -> None:
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if config is None:
        config = {}
    if not isinstance(config, Mapping):
        raise TypeError(f"Logging config file must contain a mapping: {config_path}")

    merged_config = dict(config)
    override_config_path = config_path.with_name(f"{config_path.stem}.override{config_path.suffix}")
    if override_config_path.exists():
        with override_config_path.open("r", encoding="utf-8") as file:
            override_config = yaml.safe_load(file)

        if override_config is None:
            override_config = {}
        if not isinstance(override_config, Mapping):
            raise TypeError(f"Logging config file must contain a mapping: {override_config_path}")

        merged_config = _merge_mappings(merged_config, override_config)
        print(f"[logging] Applied override config: {override_config_path}", file=sys.stderr)

    if global_level is not None:
        for section_name in ("handlers", "loggers"):
            section = merged_config.get(section_name)
            if not isinstance(section, Mapping):
                continue

            for item_config in section.values():
                if isinstance(item_config, Mapping):
                    item_config["level"] = global_level

        root_config = merged_config.get("root")
        if isinstance(root_config, Mapping):
            root_config["level"] = global_level

        print(f"[logging] Applied global level: {global_level}", file=sys.stderr)

    dictConfig(merged_config)


def configure_logging(settings_: Any | None = None, *, force: bool = False) -> None:
    global _configured

    if _configured and not force:
        return

    if settings_ is None:
        from backend.config.settings import get_settings

        settings_ = get_settings()

    setup_logging(settings_.logger_config_path, settings_.logging.global_level)
    _configured = True
