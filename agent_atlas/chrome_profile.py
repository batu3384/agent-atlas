# -*- coding: utf-8 -*-
"""Atlas Chrome profile paths (macOS + Windows) — Reddit/Twitter cookie sync."""

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

    Priority: twitter → reddit (shared Atlas Chrome profile).
    """
    profile = config.get("twitter_chrome_profile") or config.get("reddit_chrome_profile")
    browser = (
        config.get("twitter_browser") or config.get("reddit_browser") or "chrome"
    )
    return (str(profile) if profile else None, str(browser).lower())


def chrome_cookie_file(config: Config) -> Optional[Path]:
    profile, browser = resolve_chrome_profile(config)
    if not profile or browser != "chrome":
        return None
    return _chrome_root() / profile / "Cookies"
