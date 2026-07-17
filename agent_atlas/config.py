# -*- coding: utf-8 -*-
"""Config stored in ~/.agent-atlas/config.yaml (mode 600)."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Any, Optional

import yaml

# config.yaml key → process env var (applied when agent-atlas runs)
_ENV_MAP = {
    "twitter_chrome_profile": "TWITTER_CHROME_PROFILE",
    "twitter_browser": "TWITTER_BROWSER",
    "twitter_auth_token": "TWITTER_AUTH_TOKEN",
    "twitter_ct0": "TWITTER_CT0",
    "opencli_profile": "OPENCLI_PROFILE",
    "reddit_chrome_profile": "REDDIT_CHROME_PROFILE",
    "reddit_browser": "REDDIT_BROWSER",
}


class ConfigError(ValueError):
    """Malformed or unreadable config.yaml."""


class Config:
    CONFIG_DIR = Path.home() / ".agent-atlas"
    CONFIG_FILE = CONFIG_DIR / "config.yaml"

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else self.CONFIG_FILE
        self.config_dir = self.config_path.parent
        self.data: dict = {}
        self._ensure_dir()
        self.load()

    def _ensure_dir(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            os.chmod(self.config_dir, 0o700)

    def load(self) -> None:
        if not self.config_path.exists():
            self.data = {}
            return
        try:
            with open(self.config_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as e:
            raise ConfigError(f"Cannot read {self.config_path}: {e}") from e
        if raw is None:
            self.data = {}
            return
        if not isinstance(raw, dict):
            raise ConfigError(
                f"{self.config_path} must be a YAML mapping (got {type(raw).__name__})"
            )
        self.data = raw

    def save(self) -> None:
        self._ensure_dir()
        fd = os.open(
            str(self.config_path),
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            stat.S_IRUSR | stat.S_IWUSR,
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True)
        if os.name != "nt":
            os.chmod(self.config_path, 0o600)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.data:
            return self.data[key]
        env_key = key.upper()
        if env_key in os.environ:
            return os.environ[env_key]
        mapped = _ENV_MAP.get(key)
        if mapped and mapped in os.environ:
            return os.environ[mapped]
        return default

    def disabled_channels(self) -> set[str]:
        raw = self.get("disabled_channels", [])
        if isinstance(raw, str):
            return {x.strip() for x in raw.split(",") if x.strip()}
        if isinstance(raw, list):
            return {str(x).strip() for x in raw if str(x).strip()}
        return set()

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def delete(self, key: str) -> None:
        self.data.pop(key, None)
        self.save()

    def apply_runtime_env(self, *, overwrite: bool = False) -> dict[str, str]:
        """Export config values into os.environ for upstream CLIs."""
        applied: dict[str, str] = {}
        for cfg_key, env_key in _ENV_MAP.items():
            val = self.data.get(cfg_key)
            if val is None or val == "":
                continue
            val_s = str(val)
            if not overwrite and env_key in os.environ and os.environ[env_key]:
                continue
            os.environ[env_key] = val_s
            applied[env_key] = val_s
        return applied


def apply_runtime_env(config: Config | None = None, *, overwrite: bool = False) -> dict[str, str]:
    """Load ~/.agent-atlas/config.yaml into process env (twitter-cli / OpenCLI)."""
    return (config or Config()).apply_runtime_env(overwrite=overwrite)
