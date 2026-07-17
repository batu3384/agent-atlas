# -*- coding: utf-8 -*-
"""Atlas Chrome profile paths (macOS + Windows)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple

from agent_atlas.config import Config


def _chrome_root() -> Path:
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA", "")
        return Path(local) / "Google" / "Chrome" / "User Data"
    return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"


def resolve_chrome_profile(config: Config) -> Tuple[Optional[str], str]:
    """Return (profile_name, browser) from config.

    Priority: linkedin → twitter → reddit (shared Atlas profile keys).
    """
    profile = (
        config.get("linkedin_chrome_profile")
        or config.get("twitter_chrome_profile")
        or config.get("reddit_chrome_profile")
    )
    browser = (
        config.get("linkedin_browser")
        or config.get("twitter_browser")
        or config.get("reddit_browser")
        or "chrome"
    )
    return (str(profile) if profile else None, str(browser).lower())


def chrome_cookie_file(config: Config) -> Optional[Path]:
    profile, browser = resolve_chrome_profile(config)
    if not profile or browser != "chrome":
        return None
    return _chrome_root() / profile / "Cookies"


def chrome_user_data(config: Config) -> Optional[Tuple[Path, str]]:
    """Return (user_data_root, profile_directory) when Chrome profile is configured."""
    profile, browser = resolve_chrome_profile(config)
    if not profile or browser != "chrome":
        return None
    return _chrome_root(), profile


def chrome_profile_in_use() -> bool:
    """True when a live Google Chrome process is running (not a stale SingletonLock)."""
    import subprocess

    try:
        if os.name == "nt":
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            return "chrome.exe" in (out.stdout or "").lower()
        out = subprocess.run(
            ["pgrep", "-x", "Google Chrome"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return out.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
