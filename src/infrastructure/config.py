import os
from collections.abc import Mapping
from dataclasses import dataclass


class ConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class BotConfig:
    telegram_bot_token: str
    test_chat_id: int
    log_level: str


def load_bot_config(env: Mapping[str, str] | None = None) -> BotConfig:
    source = env if env is not None else os.environ
    token = _require(source, "TELEGRAM_BOT_TOKEN")
    chat_id = _require_int(source, "HACKERSPACE_TEST_CHAT_ID")
    log_level = source.get("HACKERSPACE_LOG_LEVEL") or "INFO"
    return BotConfig(telegram_bot_token=token, test_chat_id=chat_id, log_level=log_level)


def _require(source: Mapping[str, str], name: str) -> str:
    value = source.get(name)
    if not value:
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value


def _require_int(source: Mapping[str, str], name: str) -> int:
    value = _require(source, name)
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigurationError(f"Environment variable {name} must be an integer") from exc
